from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    model: str
    api_key: str | None
    data_dir: Path
    owner_name: str
    company: str
    email: str
    phone: str
    website: str
    linkedin: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_from: str

    @property
    def smtp_enabled(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)


def load_config() -> Config:
    data_dir = Path(os.getenv("MOUNS_DATA_DIR", "./data")).expanduser().resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "drafts").mkdir(exist_ok=True)
    return Config(
        model=os.getenv("MOUNS_MODEL", "claude-opus-4-7"),
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        data_dir=data_dir,
        owner_name=os.getenv("SM_OWNER_NAME", "Mounir Stili"),
        company=os.getenv("SM_COMPANY", "SM Project"),
        email=os.getenv("SM_EMAIL", ""),
        phone=os.getenv("SM_PHONE", ""),
        website=os.getenv("SM_WEBSITE", ""),
        linkedin=os.getenv("SM_LINKEDIN", ""),
        smtp_host=os.getenv("SMTP_HOST", ""),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        smtp_from=os.getenv("SMTP_FROM", os.getenv("SM_EMAIL", "")),
    )
