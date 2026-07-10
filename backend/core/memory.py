from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pathlib import Path

DB_PATH = Path.home() / ".jarvis" / "jarvis.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(16))  # user | assistant | tool
    content = Column(Text)
    tool_name = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_message(role: str, content: str, tool_name: Optional[str] = None) -> None:
    with SessionLocal() as db:
        db.add(Message(role=role, content=content, tool_name=tool_name))
        db.commit()


def get_history(limit: int = 20) -> list[dict]:
    with SessionLocal() as db:
        rows = (
            db.query(Message)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
    return [
        {"role": r.role, "content": r.content, "created_at": r.created_at.isoformat()}
        for r in reversed(rows)
    ]


def get_conversation_messages(limit: int = 10) -> list[dict]:
    """Returns messages in Anthropic API format (user/assistant only)."""
    with SessionLocal() as db:
        rows = (
            db.query(Message)
            .filter(Message.role.in_(["user", "assistant"]))
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
    return [{"role": r.role, "content": r.content} for r in reversed(rows)]
