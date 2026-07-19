from pydantic import BaseModel


class FileHealthScore(BaseModel):
    file_path: str
    complexity_score: float
    churn_score: float
    debt_score: float
    health_status: str
