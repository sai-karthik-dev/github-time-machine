import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _int_env(key: str, default: int) -> int:
    """Read an integer env var safely — returns *default* on missing or invalid value."""
    value = os.getenv(key, "")
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning(f"{key}={value!r} is not a valid integer, using default {default}")
        return default


# ── Supabase ──────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# ── CORS ──────────────────────────────────────────────────────────────
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

# ── Embeddings / pgvector ─────────────────────────────────────────────
EMBEDDING_DIMENSION = _int_env("EMBEDDING_DIMENSION", 1536)
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# ── Repository Analysis ───────────────────────────────────────────────
ANALYSIS_MAX_FILE_SIZE = _int_env("ANALYSIS_MAX_FILE_SIZE", 1_000_000)
ANALYSIS_EMBED_BATCH_SIZE = _int_env("ANALYSIS_EMBED_BATCH_SIZE", 20)
ANALYSIS_CLONE_DEPTH = _int_env("ANALYSIS_CLONE_DEPTH", 1)
ANALYSIS_EMBED_CHUNK_SIZE = _int_env("ANALYSIS_EMBED_CHUNK_SIZE", 8000)

# ── Analysis filter constants (centralized, single source of truth) ───
ANALYSIS_EXCLUDE_DIRS: set[str] = {
    ".git", "node_modules", "venv", ".venv", "__pycache__",
    "dist", "build", ".next", ".turbo", "target", "vendor",
    ".idea", ".vscode", ".DS_Store",
}

ANALYSIS_SKIP_EXTENSIONS: set[str] = {
    ".min.js", ".bundle.js", ".map", ".lock", ".pyc", ".pyo",
    ".bin", ".exe", ".dll", ".so", ".dylib", ".class",
    ".jar", ".war", ".zip", ".tar", ".gz", ".bz2", ".7z",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv",
    ".ttf", ".woff", ".woff2", ".eot", ".otf",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
}

ANALYSIS_SOURCE_EXTENSIONS: set[str] = {".py", ".js", ".ts", ".tsx", ".jsx"}

EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescriptreact",
    ".jsx": "javascriptreact",
}
