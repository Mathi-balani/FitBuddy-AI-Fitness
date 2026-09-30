from typing import Literal
from pydantic import BaseModel, Field

class UserInput(BaseModel):
    user_id: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=120)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=300)
    goal: str = Field(min_length=2, max_length=80)
    intensity: Literal["Low", "Medium", "High"]

class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=80)
    feedback: str = Field(min_length=3, max_length=1000)
