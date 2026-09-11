import os
from pathlib import Path
from dotenv import load_dotenv

THIS_DIR = Path(__file__).parent
DASHBOARD_DIR = THIS_DIR.parent
ROOT_DIR = DASHBOARD_DIR.parent

if (ROOT_DIR / ".env").exists():
    load_dotenv(ROOT_DIR / ".env", override=False)
elif (DASHBOARD_DIR / ".env").exists():
    load_dotenv(DASHBOARD_DIR / ".env", override=False)
else:
    load_dotenv(override=False)

KALLIA_API_URL = os.getenv("KALLIA_API_URL", "http://kallia-api:1904")
if (os.path.exists("/.dockerenv") or os.environ.get("DOCKER_CONTAINER")) and "localhost" in KALLIA_API_URL:
    KALLIA_API_URL = KALLIA_API_URL.replace("localhost", "kallia-api")

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "")
TTS_VOICE = os.getenv("TTS_VOICE", "pt-BR-FranciscaNeural")
