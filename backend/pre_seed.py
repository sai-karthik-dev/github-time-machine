#!/usr/bin/env python3
"""
Pre-seed a demo repository for the hackathon demo.
Runs the full analysis pipeline locally and stores results in Supabase.

Usage:
    cd backend
    source venv/bin/activate
    python pre_seed.py
"""

from app.core.supabase import get_supabase
from app.services.repo_analyzer import RepoAnalyzer

DEMO_REPO = "https://github.com/tiangolo/typer"


def main():
    supabase = get_supabase()

    parts = DEMO_REPO.rstrip("/").split("/")
    owner = parts[-2]
    name = parts[-1].replace(".git", "")

    existing = (
        supabase.table("repositories")
        .select("id")
        .eq("github_url", DEMO_REPO)
        .execute()
    )
    if existing.data:
        print(f"Repository {DEMO_REPO} already exists with id {existing.data[0]['id']}")
        repo_id = existing.data[0]["id"]
    else:
        user = (
            supabase.table("users")
            .select("id")
            .eq("github_id", 0)
            .limit(1)
            .execute()
        )
        if not user.data:
            user = (
                supabase.table("users")
                .insert({"github_id": 0, "username": "demo"})
                .execute()
            )
        user_id = user.data[0]["id"]

        repo = (
            supabase.table("repositories")
            .insert({
                "github_url": DEMO_REPO,
                "user_id": user_id,
                "name": name,
                "owner": owner,
            })
            .execute()
        )
        repo_id = repo.data[0]["id"]
        print(f"Created repository: {repo_id}")

    supabase.table("analyses").insert({
        "repository_id": repo_id,
        "status": "pending",
    }).execute()

    print(f"Starting analysis for {DEMO_REPO}...")
    analyzer = RepoAnalyzer(repo_id, DEMO_REPO)
    result = analyzer.analyze()

    print(f"Done! Result: {result}")
    print(f"Repository ID: {repo_id}")
    print(f"Use: GET /repositories/{repo_id}")


if __name__ == "__main__":
    main()
