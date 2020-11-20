import sys
import os
from pathlib import Path
from dotenv import load_dotenv

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
env_path = current_path / "../.env"
load_dotenv(dotenv_path=env_path)
environment = os.environ.get("ENVIRONMENT")

sys.path.insert(0, str(current_path) + "/../../shared")
