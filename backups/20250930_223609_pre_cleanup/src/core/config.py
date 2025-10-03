from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Model Configurations
    vision_model_name: str = "apple/FastVLM-7B"
    vision_model_type: str = "aim"
    tts_model_voice: str = "chatterbox"
    stt_model_name: str = "base"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
