"""Auth-related schemas."""
from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    level: str = "beginner"
    learning_goal: str = "general"
    cognitive_style: str = "visual"
    language: str | None = "zh-CN"


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileUpdate(BaseModel):
    level: str | None = None
    learning_goal: str | None = None
    cognitive_style: str | None = None
    vocab_level: int | None = None
    preferred_scene: str | None = None
    language: str | None = None


class UserProfile(BaseModel):
    id: int
    username: str
    level: str
    learning_goal: str
    cognitive_style: str
    profile: dict
    dimensions: dict
    level_label: str | None = None
    dimension_labels: dict | None = None
    lang: str | None = None

    class Config:
        from_attributes = True
