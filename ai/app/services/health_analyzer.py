from __future__ import annotations
import logging

from app.mock.data_provider import DataProvider
from app.models.health import FileHealthScore

logger = logging.getLogger(__name__)

async def compute_file_health(repo_id: str, file_path: str, data: DataProvider) -> FileHealthScore:
    """Compute complexity, churn, and debt scores for a file."""
    
    file_obj = await data.get_file_by_path(repo_id, file_path)
    commits = await data.get_commits(repo_id, file_path=file_path)
    
    # 1. Complexity Score (Normalize from 0-100 to 0-1)
    complexity = (file_obj.complexity_score / 100.0) if file_obj else 0.0
    complexity = min(1.0, max(0.0, complexity))
    
    # 2. Churn Score (Based on commit frequency relative to a typical threshold, e.g., 20 commits = 1.0)
    commit_count = len(commits)
    churn = min(1.0, commit_count / 20.0)
    
    # 3. Debt Score (Based on the ratio of fix commits to total commits, and sheer volume of fixes)
    fix_commits = [c for c in commits if c.is_fix_commit]
    fix_count = len(fix_commits)
    
    # A mix of absolute fixes and ratio of fixes
    debt_from_ratio = (fix_count / commit_count) if commit_count > 0 else 0.0
    debt_from_absolute = min(1.0, fix_count / 10.0)
    debt = min(1.0, (debt_from_ratio * 0.4) + (debt_from_absolute * 0.6))
    
    # Calculate overall health status
    avg_score = (complexity + churn + debt) / 3.0
    
    if avg_score > 0.66:
        status = "poor"
    elif avg_score > 0.33:
        status = "moderate"
    else:
        status = "good"
        
    return FileHealthScore(
        file_path=file_path,
        complexity_score=complexity,
        churn_score=churn,
        debt_score=debt,
        health_status=status
    )
