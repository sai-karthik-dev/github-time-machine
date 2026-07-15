from pydantic import BaseModel

class FileHealthScore(BaseModel):
    file_path: str
    complexity_score: float # 0 to 1 (1 is very complex)
    churn_score: float # 0 to 1 (1 is high churn)
    debt_score: float # Combined 0 to 1
    health_status: str # "good", "moderate", "poor"
