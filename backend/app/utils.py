def parse_github_url(url: str) -> tuple[str, str]:
    """Extract owner and repo name from a GitHub URL.

    Returns (owner, name) tuple.
    """
    parts = url.rstrip("/").split("/")
    owner = parts[-2] if len(parts) >= 2 else ""
    name = parts[-1].replace(".git", "") if len(parts) >= 1 else ""
    return owner, name
