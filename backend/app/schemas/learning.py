"""Learning and recommendation schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class RecommendQuery(BaseModel):
    scene_type: str = "fragment"
    context: dict = Field(default_factory=dict)
    limit: int = 10


class RecommendItem(BaseModel):
    word_id: int
    word: str
    meaning: str
    score: float
    r_sim: float
    s_sim: float
    alpha: float
    explanation: str
    scene_config: dict


class RecommendResponse(BaseModel):
    scene_type: str
    alpha: float
    items: list[RecommendItem]
    scene_adaptation: dict


class LearningRecordCreate(BaseModel):
    word_id: int | None = None
    scene_type: str = "fragment"
    score: float = 0.0
    response_time: float = 0.0
    is_correct: bool = False
    activity_type: str = "study"
    detail: dict = Field(default_factory=dict)


class KnowledgeStatus(BaseModel):
    mastery: float
    morph_ability: float
    semantic_density: float
    engagement: float
    cognitive_load: float
    words: list[dict]
    graph: dict


class ContentGenerateQuery(BaseModel):
    word_id: int
    level: str = "intermediate"
    scene_type: str = "focus"
