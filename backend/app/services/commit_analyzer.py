import logging
import os
from datetime import datetime, timezone
from uuid import UUID
from git import Repo
from app.core.supabase import get_supabase

logger = logging.getLogger(__name__)

class CommitAnalyzer:
    def extract_and_store(self, repository_id: str, repo_path: str, max_commits: int = 500) -> None:
        """
        Extracts commit history from a cloned git repository on disk
        and stores the commits in Supabase. Updates the analysis status.
        """
        # 1. Input Validation: Validate that repository_id is a valid UUID
        try:
            UUID(str(repository_id))
        except ValueError as e:
            logger.error(f"Invalid repository_id format: {repository_id}")
            raise ValueError(f"repository_id must be a valid UUID: {e}")

        supabase = get_supabase()
        repo_id = str(repository_id)

        # Update analysis status to "processing"
        supabase.table("analyses").update({
            "status": "processing",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }).eq("repository_id", repo_id).execute()

        try:
            # 2. Path safety validation: Canonicalize and verify directory existence
            if not repo_path:
                raise ValueError("Repository path cannot be empty")
            
            canonical_path = os.path.realpath(repo_path)
            if not os.path.exists(canonical_path):
                raise ValueError(f"Repository path does not exist: {repo_path}")
            if not os.path.isdir(canonical_path):
                raise ValueError(f"Repository path is not a directory: {repo_path}")

            logger.info(f"Opening repository at {canonical_path} for repo_id {repo_id}")
            repo = Repo(canonical_path)

            # Check if repository is empty (no valid HEAD reference)
            if not repo.head.is_valid():
                logger.info(f"Repository {canonical_path} is empty or has no commits.")
                supabase.table("analyses").update({
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }).eq("repository_id", repo_id).execute()
                return

            commits_to_insert = []
            logger.info(f"Iterating commits for repo_id {repo_id} (max_count={max_commits})")
            for commit in repo.iter_commits(max_count=max_commits):
                sha = commit.hexsha
                author_name = commit.author.name if commit.author else None
                author_email = commit.author.email if commit.author else None
                committer_name = commit.committer.name if commit.committer else None
                committer_email = commit.committer.email if commit.committer else None
                message = commit.message
                summary = commit.summary
                commit_date = datetime.fromtimestamp(commit.committed_date, tz=timezone.utc).isoformat()

                commits_to_insert.append({
                    "repository_id": repo_id,
                    "commit_sha": sha,
                    "author": author_name,
                    "author_email": author_email,
                    "committer_name": committer_name,
                    "committer_email": committer_email,
                    "message": message,
                    "summary": summary,
                    "commit_date": commit_date,
                })

            if commits_to_insert:
                chunk_size = 100
                logger.info(f"Upserting {len(commits_to_insert)} commits in chunks of {chunk_size} for repo_id {repo_id}")
                for i in range(0, len(commits_to_insert), chunk_size):
                    chunk = commits_to_insert[i:i + chunk_size]
                    supabase.table("commits").upsert(
                        chunk,
                        on_conflict="repository_id, commit_sha"
                    ).execute()
            else:
                logger.info(f"No commits found to insert for repo_id {repo_id}")

            # Update analysis status to "completed"
            supabase.table("analyses").update({
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }).eq("repository_id", repo_id).execute()

        except Exception as e:
            logger.exception(f"Failed to analyze commits for repository {repo_id} at {repo_path}")
            supabase.table("analyses").update({
                "status": "error",
                "error_message": str(e),
            }).eq("repository_id", repo_id).execute()
            raise e
