import os

from dotenv import load_dotenv

load_dotenv()

print(
    "[INFO] Environment keys loaded:",
    {
        "OPENAQ_KEY": bool(os.getenv("OPEN_AQ_KEY")),
        "OPENWEATHER_KEY": bool(os.getenv("OPENWEATHER_KEY")),
        "TEMPO_KEY": bool(os.getenv("TEMPO_KEY")),
        "EARTH_ACCESS_KEY": bool(os.getenv("EARTH_ACCESS_KEY")),
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "OPENAI_MODEL": bool(os.getenv("OPENAI_MODEL")),
        "OPENAI_TEMPERATURE": bool(os.getenv("OPENAI_TEMPERATURE")),
    },
)


def _get_env(name: str, default: str | None = None) -> str | None:
    """Wrapper around os.getenv so we can patch/test easily."""

    return os.getenv(name, default)


OPENAQ_KEY = _get_env("OPEN_AQ_KEY")
TEMPO_KEY = _get_env("TEMPO_KEY")
EARTH_ACCESS_KEY = _get_env("EARTH_ACCESS_KEY")
OPENWEATHER_KEY = _get_env("OPENWEATHER_KEY")
OPENAI_API_KEY = _get_env("OPENAI_KEY")
OPENAI_MODEL = _get_env("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = _get_env("OPENAI_TEMPERATURE", "0.2")


