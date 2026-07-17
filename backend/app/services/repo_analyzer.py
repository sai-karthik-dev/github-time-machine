import logging
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone

from git import Repo
from tree_sitter import Language, Parser, Node

from app.core.config import (
    EMBEDDING_DIMENSION,
    OPENAI_EMBEDDING_MODEL,
    ANALYSIS_MAX_FILE_SIZE,
    ANALYSIS_EMBED_BATCH_SIZE,
    ANALYSIS_CLONE_DEPTH,
    ANALYSIS_EMBED_CHUNK_SIZE,
    ANALYSIS_EXCLUDE_DIRS,
    ANALYSIS_SKIP_EXTENSIONS,
    ANALYSIS_SOURCE_EXTENSIONS,
    EXTENSION_LANGUAGE_MAP,
)
from app.core.supabase import get_supabase
from app.services.commit_analyzer import CommitAnalyzer
from app.utils import parse_github_url

logger = logging.getLogger(__name__)

try:
    import tree_sitter_python as tspython
    PY_LANG = Language(tspython.language())
except ImportError:
    PY_LANG = None

try:
    import tree_sitter_javascript as tsjs
    JS_LANG = Language(tsjs.language())
except ImportError:
    JS_LANG = None


class RepoAnalyzer:
    """Facade for the full repository analysis pipeline.

    Example:
        analyzer = RepoAnalyzer(repo_id, "https://github.com/org/repo")
        result = analyzer.analyze()  # clone → walk → parse → store → commits → metadata

    The only public method is analyze(). All internal steps are private and
    independently testable.
    """
    def __init__(self, repository_id: str, github_url: str):
        self.repository_id = repository_id
        self.github_url = github_url
        self.supabase = get_supabase()
        self._temp_dir = None

    def analyze(self) -> dict:
        """Run the full pipeline: clone → walk → store files → extract commits → metadata.

        Returns:
            dict with {'files_indexed': int}
        """
        self._set_status("processing", started_at=datetime.now(timezone.utc).isoformat())

        try:
            clone_path = self._clone()
            files = self._walk(clone_path)
            stored_count = self._store_files(files)
            CommitAnalyzer().extract_and_store(self.repository_id, clone_path)
            self._update_repo_metadata()

            summary_text = f"{stored_count} files indexed"
            self._set_status(
                "completed",
                completed_at=datetime.now(timezone.utc).isoformat(),
                summary=summary_text,
            )
            return {
                "files_indexed": stored_count,
            }

        except Exception as e:
            logger.exception(f"Analysis failed for repo {self.repository_id}")
            self._set_status("error", error_message=str(e))
            raise
        finally:
            self._cleanup()

    def _clone(self) -> str:
        self._validate_url(injected_url=self.github_url)
        self._temp_dir = tempfile.mkdtemp(prefix="repo_")
        logger.info(f"Cloning {self.github_url} into {self._temp_dir}")
        Repo.clone_from(self.github_url, self._temp_dir, depth=ANALYSIS_CLONE_DEPTH)
        return self._temp_dir

    @staticmethod
    def _validate_url(url: str | None = None, injected_url: str | None = None) -> bool:
        target = injected_url or url
        if not target:
            raise ValueError("GitHub URL is required")
        if not re.match(r"^https://github\.com/[^/]+/[^/]+", target):
            raise ValueError(f"Invalid GitHub URL: {target}")
        return True

    def _walk(self, root: str) -> list[dict]:
        results = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ANALYSIS_EXCLUDE_DIRS]

            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root)

                if self._is_vendored(filename, rel_path):
                    continue

                try:
                    size = os.path.getsize(full_path)
                except OSError:
                    continue

                ext = os.path.splitext(filename)[1].lower()
                language = EXTENSION_LANGUAGE_MAP.get(ext)
                is_source = ext in ANALYSIS_SOURCE_EXTENSIONS

                results.append({
                    "file_path": rel_path,
                    "language": language,
                    "size": size,
                    "full_path": full_path,
                    "is_source": is_source,
                })

        logger.info(f"Found {len(results)} files in {root}")
        return results

    def _is_vendored(self, filename: str, rel_path: str) -> bool:
        if filename.endswith(tuple(ANALYSIS_SKIP_EXTENSIONS)):
            return True
        for part in rel_path.split(os.sep):
            if part in ANALYSIS_EXCLUDE_DIRS:
                return True
        return False

    def _store_files(self, files: list[dict]) -> int:
        stored_count = 0
        embed_batch = []

        for f in files:
            if not f["is_source"] or f["size"] > ANALYSIS_MAX_FILE_SIZE or f["size"] == 0:
                self._insert_file_record(f, content=None, embedding=None)
                stored_count += 1
                continue

            try:
                with open(f["full_path"], "rb") as fh:
                    raw = fh.read()
                content = raw.decode("utf-8", errors="replace")
            except Exception:
                self._insert_file_record(f, content=None, embedding=None)
                stored_count += 1
                continue

            record = self._insert_file_record(f, content=content, embedding=None)
            stored_count += 1

            if content.strip():
                embed_batch.append({"id": record["id"], "content": content[:ANALYSIS_EMBED_CHUNK_SIZE]})

            if len(embed_batch) >= ANALYSIS_EMBED_BATCH_SIZE:
                self._generate_and_store_embeddings(embed_batch)
                embed_batch.clear()

        if embed_batch:
            self._generate_and_store_embeddings(embed_batch)

        return stored_count

    def _build_file_id_map(self, files: list[dict]) -> dict[str, str]:
        response = (
            self.supabase.table("files")
            .select("id, file_path")
            .eq("repository_id", self.repository_id)
            .execute()
        )
        return {row["file_path"]: row["id"] for row in (response.data or [])}

    def _parse_file(self, file_path: str, language: str) -> list[dict]:
        lang = self._get_lang(language)
        if lang is None:
            return []

        try:
            with open(file_path, "rb") as fh:
                source = fh.read()
        except Exception:
            return []

        parser = Parser(lang)
        tree = parser.parse(source)
        root = tree.root_node

        functions = self._extract_functions(root, source, language)
        classes = self._extract_classes(root, source, language)
        imports = self._extract_imports(root, source, language)

        result = []
        result.extend(functions)
        result.extend(classes)
        result.extend(imports)
        return result

    def _get_lang(self, language: str):
        if language in ("python",) and PY_LANG is not None:
            return PY_LANG
        if language in ("javascript", "typescript", "javascriptreact", "typescriptreact") and JS_LANG is not None:
            return JS_LANG
        return None

    def _extract_functions(self, root: Node, source: bytes, language: str) -> list[dict]:
        results = []
        query = None
        try:
            if language == "python":
                query = PY_LANG.query(
                    "(function_definition name: (identifier) @func_name body: (block) @func_body) "
                    + "(decorated_definition definition: (function_definition name: (identifier) @func_name))"
                )
            elif language in ("javascript", "typescript", "typescriptreact", "javascriptreact"):
                query = JS_LANG.query(
                    "(function_declaration name: (identifier) @func_name body: (_) @func_body) "
                    + "(method_definition name: (property_identifier) @func_name body: (_) @func_body) "
                    + "(arrow_function) @arrow"
                )

            if query is not None:
                cursor = query.captures(root)
                seen = set()
                for node, tag in cursor:
                    if tag == "func_name" and node.type == "identifier":
                        name = node.text.decode("utf-8", errors="replace")
                        func_node = node.parent
                        start_line = func_node.start_point[0] + 1
                        end_line = func_node.end_point[0] + 1
                        key = f"{name}:{start_line}:{end_line}"
                        if key not in seen:
                            seen.add(key)
                            results.append({
                                "name": name,
                                "type": "function",
                                "start_line": start_line,
                                "end_line": end_line,
                                "is_exported": False,
                            })
        except Exception as e:
            logger.debug(f"Query extraction failed: {e}")

        return results

    def _extract_classes(self, root: Node, source: bytes, language: str) -> list[dict]:
        results = []
        try:
            if language == "python":
                query = PY_LANG.query("(class_definition name: (identifier) @class_name)")
            elif language in ("javascript", "typescript", "typescriptreact", "javascriptreact"):
                query = JS_LANG.query("(class_declaration name: (identifier) @class_name)")
            else:
                return results

            cursor = query.captures(root)
            for node, tag in cursor:
                if tag == "class_name" and node.type == "identifier":
                    name = node.text.decode("utf-8", errors="replace")
                    class_node = node.parent
                    results.append({
                        "name": name,
                        "type": "class",
                        "start_line": class_node.start_point[0] + 1,
                        "end_line": class_node.end_point[0] + 1,
                        "is_exported": False,
                    })
        except Exception as e:
            logger.debug(f"Class extraction failed: {e}")

        return results

    def _extract_imports(self, root: Node, source: bytes, language: str) -> list[dict]:
        results = []
        try:
            if language == "python":
                query = PY_LANG.query(
                    "(import_statement name: (dotted_name) @import_name) "
                    + "(import_from_statement module_name: (dotted_name) @import_name)"
                )
            elif language in ("javascript", "typescript", "typescriptreact", "javascriptreact"):
                query = JS_LANG.query(
                    "(import_statement source: (string) @import_source) "
                    + "(import_statement specifier: (import_specifier name: (identifier) @import_name))"
                )
            else:
                return results

            cursor = query.captures(root)
            for node, tag in cursor:
                name = node.text.decode("utf-8", errors="replace").strip("\"'")
                results.append({
                    "name": name,
                    "type": "import",
                    "start_line": node.start_point[0] + 1,
                    "end_line": node.end_point[0] + 1,
                    "is_exported": False,
                })
        except Exception as e:
            logger.debug(f"Import extraction failed: {e}")

        return results

    def _parse_and_store_symbols(self, files: list[dict], file_id_map: dict[str, str]) -> dict[str, list[str]]:
        file_ids: dict[str, list[str]] = {}
        all_symbols: list[dict] = []

        for f in files:
            if not f["is_source"] or f["language"] is None:
                continue

            symbols = self._parse_file(f["full_path"], f["language"])
            if not symbols:
                continue

            file_id = file_id_map.get(f["file_path"])
            if file_id is None:
                continue

            file_ids[str(file_id)] = []

            for sym in symbols:
                sym["file_id"] = file_id
                sym["repository_id"] = self.repository_id
                all_symbols.append(sym)

        for sym in all_symbols:
            response = (
                self.supabase.table("functions")
                .upsert({
                    "file_id": sym["file_id"],
                    "repository_id": sym["repository_id"],
                    "name": sym["name"],
                    "start_line": sym["start_line"],
                    "end_line": sym["end_line"],
                    "is_exported": sym["is_exported"],
                }, on_conflict="file_id, name, start_line")
                .execute()
            )
            if response.data:
                file_key = str(sym["file_id"])
                if file_key in file_ids:
                    file_ids[file_key].append(response.data[0]["id"])

        logger.info(f"Stored {len(all_symbols)} symbols across {len(file_ids)} files")
        return file_ids

    def _build_edges_from_imports(self, files: list[dict], file_id_map: dict[str, str]) -> None:
        for f in files:
            if not f["is_source"] or f["language"] is None:
                continue

            symbols = self._parse_file(f["full_path"], f["language"])
            imports = [s for s in symbols if s["type"] == "import"]

            if not imports:
                continue

            source_file_id = file_id_map.get(f["file_path"])
            if source_file_id is None:
                continue

            for imp in imports:
                module_name = imp["name"]
                target_record = (
                    self.supabase.table("files")
                    .select("id")
                    .eq("repository_id", self.repository_id)
                    .like("file_path", f"%{module_name.replace('.', '/')}%")
                    .limit(1)
                    .execute()
                )

                target_id = target_record.data[0]["id"] if target_record.data else None

                if target_id:
                    self.supabase.table("edges").upsert({
                        "repository_id": self.repository_id,
                        "source_id": source_file_id,
                        "target_id": str(target_id),
                        "edge_type": "imports",
                        "source_name": f["file_path"],
                        "target_name": imp["name"],
                    }, on_conflict="repository_id, source_id, target_id, edge_type").execute()

    def _insert_file_record(self, f: dict, content: str | None, embedding: list[float] | None) -> dict:
        payload = {
            "repository_id": self.repository_id,
            "file_path": f["file_path"],
            "language": f["language"],
            "size": f["size"],
        }
        if content is not None:
            payload["content"] = content
        if embedding is not None:
            payload["embedding"] = embedding

        response = self.supabase.table("files").insert(payload).execute()
        return response.data[0]

    def _generate_and_store_embeddings(self, batch: list[dict]) -> None:
        try:
            from openai import OpenAI

            texts = [item["content"] for item in batch]
            client = OpenAI()
            response = client.embeddings.create(
                model=OPENAI_EMBEDDING_MODEL,
                input=texts,
                dimensions=EMBEDDING_DIMENSION,
            )
            for item, emb_data in zip(batch, response.data):
                self.supabase.table("files").update({
                    "embedding": emb_data.embedding,
                }).eq("id", item["id"]).execute()
        except Exception as e:
            logger.warning(f"Embedding generation failed (non-fatal): {e}")

    def _update_repo_metadata(self) -> None:
        try:
            owner, name = parse_github_url(self.github_url)

            repo = Repo(self._temp_dir)
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

    def _cleanup(self) -> None:
        if self._temp_dir and os.path.isdir(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            logger.info(f"Cleaned up {self._temp_dir}")
