import sys
import os
import logging

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app.fileset import app as application  # noqa

logging.basicConfig(stream=sys.stderr)
sys.stderr = sys.stdout

if __name__ == "__main__":
    application.run()
