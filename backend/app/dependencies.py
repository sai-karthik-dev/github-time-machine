from app.core.supabase import get_supabase
from supabase import Client


def get_db() -> Client:
    """FastAPI dependency — injects the Supabase client into route handlers."""
    return get_supabase()
