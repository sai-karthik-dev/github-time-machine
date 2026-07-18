import logging
from datetime import datetime, timezone

from app.core.config import ANALYSIS_EMBED_BATCH_SIZE, ANALYSIS_EMBED_CHUNK_SIZE, ANALYSIS_MAX_FILE_SIZE
from app.core.supabase import get_supabase
from app.models.schemas import RepositoryStatus
from app.services.commit_analyzer import CommitAnalyzer
from app.services.embedding_generator import EmbeddingGenerator
from app.services.file_walker import FileWalker
from app.services.repo_cloner import RepoCloner
from app.services.symbol_extractor import SymbolExtractor
from app.utils import parse_github_url

logger = logging.getLogger(__name__)


class RepoAnalyzer:
    """Facade that orchestrates the repository analysis pipeline.

    Example:
        analyzer = RepoAnalyzer(repo_id, "https://github.com/org/repo")
        result = analyzer.analyze()  # clone -> walk -> parse -> store -> commits -> metadata

    Each stage is delegated to a focused collaborator (RepoCloner, FileWalker,
    SymbolExtractor, EmbeddingGenerator, CommitAnalyzer); this class only
    coordinates them and persists results to Supabase.
    """

    def __init__(self, repository_id: str, github_url: str):
        self.repository_id = repository_id
        self.github_url = github_url
        self.supabase = get_supabase()
        self._cloner = RepoCloner(github_url)
        self._walker = FileWalker()
        self._symbol_extractor = SymbolExtractor()
        self._embedder = EmbeddingGenerator(repository_id)

    def analyze(self) -> dict:
        """Run the full pipeline: clone -> walk -> store files -> symbols/edges -> commits -> metadata.

        Returns:
            dict with {'files_indexed': int}
        """
        self._set_status(RepositoryStatus.PROCESSING.value, started_at=datetime.now(timezone.utc).isoformat())

        try:
            clone_path = self._cloner.clone()
            files = self._walker.walk(clone_path)
            stored_count = self._store_files(files)

            file_id_map = self._build_file_id_map()
            self._extract_and_store_symbols(files, file_id_map)

            CommitAnalyzer().extract_and_store(self.repository_id, clone_path)
            self._update_repo_metadata(clone_path)

            summary_text = f"{stored_count} files indexed"
            self._set_status(
                RepositoryStatus.COMPLETED.value,
                completed_at=datetime.now(timezone.utc).isoformat(),
                summary=summary_text,
            )
            return {"files_indexed": stored_count}

        except Exception as e:
            logger.exception(f"Analysis failed for repo {self.repository_id}")
            self._set_status(RepositoryStatus.ERROR.value, error_message=str(e))
            raise
        finally:
            self._cloner.cleanup()

    def _store_files(self, files: list[dict]) -> int:
        stored_count = 0
        embed_batch = []

        for f in files:
            if not f["is_source"] or f["size"] > ANALYSIS_MAX_FILE_SIZE or f["size"] == 0:
                self._insert_file_record(f, content=None)
                stored_count += 1
                continue

            try:
                with open(f["full_path"], "rb") as fh:
                    raw = fh.read()
                content = raw.decode("utf-8", errors="replace")
            except Exception:
                self._insert_file_record(f, content=None)
                stored_count += 1
                continue

            record = self._insert_file_record(f, content=content)
            stored_count += 1

            if content.strip():
                embed_batch.append({"id": record["id"], "content": content[:ANALYSIS_EMBED_CHUNK_SIZE]})

            if len(embed_batch) >= ANALYSIS_EMBED_BATCH_SIZE:
                self._embed_and_store(embed_batch)
                embed_batch.clear()

        if embed_batch:
            self._embed_and_store(embed_batch)

        return stored_count

    def _embed_and_store(self, batch: list[dict]) -> None:
        embeddings = self._embedder.generate(batch)
        for file_id, embedding in embeddings.items():
            self.supabase.table("files").update({"embedding": embedding}).eq("id", file_id).execute()

    def _build_file_id_map(self) -> dict[str, str]:
        response = (
            self.supabase.table("files")
            .select("id, file_path")
            .eq("repository_id", self.repository_id)
            .execute()
        )
        return {row["file_path"]: row["id"] for row in (response.data or [])}

    def _extract_and_store_symbols(self, files: list[dict], file_id_map: dict[str, str]) -> None:
        """Parses each source file once with SymbolExtractor, then routes functions/classes
        to the `functions` table and imports to the `edges` table."""
        symbol_count = 0

        for f in files:
            if not f["is_source"] or f["language"] is None:
                continue

            file_id = file_id_map.get(f["file_path"])
            if file_id is None:
                continue

            for sym in self._symbol_extractor.parse_file(f["full_path"], f["language"]):
                if sym["type"] in ("function", "class"):
                    self.supabase.table("functions").upsert({
                        "file_id": file_id,
                        "repository_id": self.repository_id,
                        "name": sym["name"],
                        "start_line": sym["start_line"],
                        "end_line": sym["end_line"],
                        "is_exported": sym["is_exported"],
                    }, on_conflict="file_id, name, start_line").execute()
                    symbol_count += 1
                elif sym["type"] == "import":
                    self._store_import_edge(f["file_path"], file_id, sym["name"])

        logger.info(f"Stored {symbol_count} symbols across {len(files)} files")

    def _store_import_edge(self, source_path: str, source_file_id: str, module_name: str) -> None:
        target_record = (
            self.supabase.table("files")
            .select("id")
            .eq("repository_id", self.repository_id)
            .like("file_path", f"%{module_name.replace('.', '/')}%")
            .limit(1)
            .execute()
        )
        target_id = target_record.data[0]["id"] if target_record.data else None
        if not target_id or str(target_id) == str(source_file_id):
            return

        self.supabase.table("edges").upsert({
            "repository_id": self.repository_id,
            "source_id": source_file_id,
            "target_id": str(target_id),
            "edge_type": "imports",
            "source_name": source_path,
            "target_name": module_name,
        }, on_conflict="repository_id, source_id, target_id, edge_type").execute()

    def _insert_file_record(self, f: dict, content: str | None) -> dict:
        payload = {
            "repository_id": self.repository_id,
            "file_path": f["file_path"],
            "language": f["language"],
            "size": f["size"],
        }
        if content is not None:
            payload["content"] = content

        response = self.supabase.table("files").insert(payload).execute()
        return response.data[0]

    def _update_repo_metadata(self, clone_path: str) -> None:
        try:
            from git import Repo

            owner, name = parse_github_url(self.github_url)
            repo = Repo(clone_path)
            default_branch = repo.active_branch.name if not repo.head.is_detached else "main"

            self.supabase.table("repositories").update({
                "name": name,
                "owner": owner,
                "default_branch": default_branch,
                "last_analyzed": datetime.now(timezone.utc).isoformat(),
            }).eq("id", self.repository_id).execute()
        except Exception as e:
            logger.warning(f"Failed to update repo metadata: {e}")

    def _set_status(
        self,
        status: str,
        started_at: str | None = None,
        completed_at: str | None = None,
        error_message: str | None = None,
        summary: str | None = None,
    ) -> None:
        payload = {"status": status}
        if started_at is not None:
            payload["started_at"] = started_at
        if completed_at is not None:
            payload["completed_at"] = completed_at
        if error_message is not None:
            payload["error_message"] = error_message
        if summary is not None:
            payload["summary"] = summary
        self.supabase.table("analyses").update(payload).eq(
            "repository_id", self.repository_id
        ).execute()