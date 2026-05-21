from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_TRANSCRIPTS: str = "meeting.transcripts"
    KAFKA_TOPIC_SPEAKERS: str = "meeting.speakers"
    KAFKA_TOPIC_SUMMARIES: str = "meeting.summaries"
    KAFKA_TOPIC_ACTION_ITEMS: str = "meeting.action_items"
    KAFKA_TOPIC_ALERTS: str = "meeting.alerts"

    CHROMA_PERSIST_DIR: str = "./data/chroma"
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/meetings.db"
    WHISPER_MODEL: str = "base"

    class Config:
        env_file = ".env"

settings = Settings()
