import logging
import os
import re
import shutil
import tempfile

from git import Repo

from app.core.config import ANALYSIS_CLONE_DEPTH

logger = logging.getLogger(__name__)

_GITHUB_URL_PATTERN = re.compile(r"^https://github\.com/[^/]+/[^/]+")


class RepoCloner:
    """Clones a GitHub repository into a temp directory and cleans it up afterwards."""

    def __init__(self, github_url: str):
        self.github_url = github_url
        self._temp_dir: str | None = None

    @staticmethod
    def validate_url(url: str | None) -> bool:
        return bool(url) and bool(_GITHUB_URL_PATTERN.match(url))

    def clone(self) -> str:
        if not self.validate_url(self.github_url):
            raise ValueError(f"Invalid GitHub URL: {self.github_url}")
        self._temp_dir = tempfile.mkdtemp(prefix="repo_")
        logger.info(f"Cloning {self.github_url} into {self._temp_dir}")
        Repo.clone_from(self.github_url, self._temp_dir, depth=ANALYSIS_CLONE_DEPTH)
        return self._temp_dir

    def cleanup(self) -> None:
        if self._temp_dir and os.path.isdir(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            logger.info(f"Cleaned up {self._temp_dir}")
            self._temp_dir = None