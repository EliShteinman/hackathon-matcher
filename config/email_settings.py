from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class EmailSettings(BaseSettings):
    model_config = ConfigDict(env_prefix="EMAIL__")

    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP server hostname")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_username: str = Field(default="", description="SMTP authentication username")
    smtp_password: str = Field(default="", description="SMTP authentication password")
    from_address: str = Field(default="hackathon@example.com", description="Sender email address")
    from_name: str = Field(default="Hackathon Matcher", description="Sender display name")
    use_tls: bool = Field(default=True, description="Use STARTTLS for SMTP connection")
    enabled: bool = Field(default=False, description="Enable actual email sending")
