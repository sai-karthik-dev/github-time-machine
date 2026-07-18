import logging
import os

from app.core.config import (
    ANALYSIS_EXCLUDE_DIRS,
    ANALYSIS_SKIP_EXTENSIONS,
    ANALYSIS_SOURCE_EXTENSIONS,
    EXTENSION_LANGUAGE_MAP,
)

logger = logging.getLogger(__name__)


class FileWalker:
    """Walks a cloned repository's working tree, filtering out vendored/binary files."""

    def walk(self, root: str) -> list[dict]:
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