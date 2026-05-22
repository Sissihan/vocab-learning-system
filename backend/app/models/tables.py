"""Core database table definitions."""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """Learner account and static profile fields."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    level = Column(String(32), default="beginner")
    learning_goal = Column(String(128), default="general")
    cognitive_style = Column(String(64), default="visual")
    profile_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

    knowledge_states = relationship("UserKnowledge", back_populates="user")
    learning_records = relationship("LearningRecord", back_populates="user")


class Root(Base):
    """Morphological root node."""

    __tablename__ = "roots"

    id = Column(Integer, primary_key=True, index=True)
    root = Column(String(64), unique=True, nullable=False)
    meaning = Column(String(256), nullable=False)
    origin = Column(String(64), default="Latin")
    difficulty = Column(Integer, default=1)
    meta_json = Column(Text, default="{}")

    words = relationship("Vocabulary", back_populates="primary_root")


class Vocabulary(Base):
    """Vocabulary entry linked to morphology and semantics."""

    __tablename__ = "vocabulary"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(128), unique=True, nullable=False, index=True)
    meaning = Column(String(512), nullable=False)
    phonetic = Column(String(64), default="")
    difficulty = Column(Integer, default=1)
    root_id = Column(Integer, ForeignKey("roots.id"), nullable=True)
    embedding_json = Column(Text, default="[]")
    example_json = Column(Text, default="[]")

    primary_root = relationship("Root", back_populates="words")


class RootWord(Base):
    """Many-to-many root-word morphological relations."""

    __tablename__ = "root_word"
    __table_args__ = (UniqueConstraint("root_id", "word_id", name="uq_root_word"),)

    id = Column(Integer, primary_key=True)
    root_id = Column(Integer, ForeignKey("roots.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("vocabulary.id"), nullable=False)
    relation_type = Column(String(32), default="derived")


class WordSemanticLink(Base):
    """Semantic similarity edges between words."""

    __tablename__ = "word_semantic_link"
    __table_args__ = (
        UniqueConstraint("word_id1", "word_id2", name="uq_semantic_pair"),
    )

    id = Column(Integer, primary_key=True)
    word_id1 = Column(Integer, ForeignKey("vocabulary.id"), nullable=False)
    word_id2 = Column(Integer, ForeignKey("vocabulary.id"), nullable=False)
    similarity_score = Column(Float, default=0.0)


class LearningRecord(Base):
    """Per-interaction learning telemetry."""

    __tablename__ = "learning_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("vocabulary.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    scene_type = Column(String(32), default="fragment")
    score = Column(Float, default=0.0)
    response_time = Column(Float, default=0.0)
    is_correct = Column(Boolean, default=False)
    activity_type = Column(String(64), default="study")
    detail_json = Column(Text, default="{}")

    user = relationship("User", back_populates="learning_records")


class UserKnowledge(Base):
    """DKT-derived mastery state per user-word pair."""

    __tablename__ = "user_knowledge"
    __table_args__ = (UniqueConstraint("user_id", "word_id", name="uq_user_word"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("vocabulary.id"), nullable=False)
    mastery_level = Column(Float, default=0.0)
    last_review = Column(DateTime, nullable=True)
    review_count = Column(Integer, default=0)
    morph_ability = Column(Float, default=0.0)
    semantic_density = Column(Float, default=0.0)

    user = relationship("User", back_populates="knowledge_states")


class ContextLog(Base):
    """Contextual environment inference log."""

    __tablename__ = "context_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    location_type = Column(String(64), default="unknown")
    device_state = Column(String(64), default="desktop")
    inferred_scene = Column(String(32), default="fragment")
    context_json = Column(Text, default="{}")
