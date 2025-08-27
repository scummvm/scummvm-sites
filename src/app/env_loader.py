from pathlib import Path
from dotenv import load_dotenv
import sys
import os

project_root = Path(__file__).resolve().parents[2]
if project_root not in sys.path:
    sys.path.insert(0, project_root)

env_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path=env_path)
