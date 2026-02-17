from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    site_password: str = ""
    media_trainer_url: str = "http://media-trainer.railway.internal:8000"
    lulea_tool_url: str = "http://lulea-tool.railway.internal:8080"
    svenska_roster_url: str = "http://svenska-roster.railway.internal:8000"
    buss49p_tool_url: str = "http://buss49p-tool.railway.internal:8081"
    decision_engine_url: str = "http://decision-engine.railway.internal:8080"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

# Map tool slugs to their internal URLs
TOOL_ROUTES = {
    "media-trainer": settings.media_trainer_url,
    "lulea": settings.lulea_tool_url,
    "svenska-roster": settings.svenska_roster_url,
    "buss49p": settings.buss49p_tool_url,
    "decision-engine": settings.decision_engine_url,
}
