from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # WhatsApp
    WHATSAPP_PHONE_ID: str = ""
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_VERIFY_TOKEN: str = "ithara_webhook_verify"
    WHATSAPP_APP_SECRET: str = ""

    # Ithara API
    ITHARA_API_BASE: str = "http://localhost:3000"
    ITHARA_API_KEY: str = ""

    # Claude
    ANTHROPIC_API_KEY: str = ""

    # Email
    SMTP_HOST: str = "smtp.sendgrid.net"
    SMTP_PORT: int = 587
    SMTP_USER: str = "apikey"
    SMTP_PASSWORD: str = ""
    OPS_EMAIL: str = "ops@ithara.ae"
    FROM_EMAIL: str = "bookings@ithara.ae"

    # Feature flags
    DEMO_MODE: bool = True
    USE_CLAUDE_CLASSIFIER: bool = False

    # Session store
    SESSION_DB_URL: str = "sqlite+aiosqlite:///./sessions.db"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
