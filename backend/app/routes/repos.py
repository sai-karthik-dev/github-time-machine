import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
import httpx
from app.dependencies import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/repos", tags=["repos"])

class ConnectRequest(BaseModel):
    github_access_token: str = Field(..., description="The user's GitHub access token")

@router.post("/connect", summary="Connect GitHub account", tags=["auth"])
async def connect_repository(
    body: ConnectRequest,
    authorization: Optional[str] = Header(None),
    supabase = Depends(get_db),
):
    """
    Validates the Supabase Auth session token, retrieves details from the GitHub user API,
    and inserts/updates the user record in the users database table.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header. Expected Bearer token."
        )
    
    supabase_jwt = authorization.split(" ")[1]

    # 1. Validate session against Supabase Auth
    # supabase-py is a sync client; offload it so it doesn't block the event loop
    # (this route also awaits httpx calls below) — see Starlette's run_in_threadpool.
    try:
        user_response = await run_in_threadpool(supabase.auth.get_user, supabase_jwt)
        supabase_user = user_response.user
        if not supabase_user:
            raise Exception("No user found in the returned session.")
    except Exception as e:
        logger.error(f"Supabase auth validation failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session."
        )
        
    # 2. Retrieve user information from GitHub API using the access token
    try:
        async with httpx.AsyncClient() as client:
            github_response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {body.github_access_token}"}
            )
            if github_response.status_code != 200:
                logger.error(f"GitHub validation failed with status {github_response.status_code}: {github_response.text}")
                raise HTTPException(
                    status_code=401,
                    detail="GitHub token validation failed."
                )
            github_user = github_response.json()
    except Exception as e:
        logger.error(f"GitHub profile retrieval failed: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail="Failed to communicate with GitHub."
        )

    github_id = github_user.get("id")
    username = github_user.get("login")
    email = github_user.get("email")
    avatar_url = github_user.get("avatar_url")
    
    # Fallback to query user's private emails if public email is not set/private
    if not email:
        try:
            logger.info("Public email not found in GitHub profile. Fetching user email list...")
            async with httpx.AsyncClient() as client:
                emails_response = await client.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"Bearer {body.github_access_token}"}
                )
                if emails_response.status_code == 200:
                    emails_list = emails_response.json()
                    # Find primary & verified email
                    primary_verified = next(
                        (e["email"] for e in emails_list if e.get("primary") and e.get("verified")),
                        None
                    )
                    # Fallback to first email if no primary verified exists
                    if not primary_verified and emails_list:
                        primary_verified = emails_list[0].get("email")
                    if primary_verified:
                        email = primary_verified
        except Exception as email_err:
            logger.warning(f"Failed to retrieve private emails from GitHub: {email_err}")
    
    if github_id is None or not username:
        raise HTTPException(
            status_code=500,
            detail="Invalid user profile returned from GitHub"
        )
        
    # 3. Create or update user record in users database table
    try:
        user_id = str(supabase_user.id)
        db_user_payload = {
            "id": user_id,
            "github_id": github_id,
            "username": username,
            "email": email,
            "avatar_url": avatar_url,
        }
        
        await run_in_threadpool(
            lambda: supabase.table("users").upsert(db_user_payload, on_conflict="id").execute()
        )
    except Exception as e:
        logger.error(f"Failed to upsert user record: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to save user profile."
        )
        
    # 4. Return the user profile + session info
    return {
        "user": {
            "id": user_id,
            "github_id": github_id,
            "username": username,
            "email": email,
            "avatar_url": avatar_url
        }
    }
