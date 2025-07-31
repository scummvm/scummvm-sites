import sys
import logging

sys.path.insert(0, "/home/ubuntu/projects/python/scummvm_sites_2025/scummvm-sites")

from fileset import app as application

logging.basicConfig(stream=sys.stderr)
sys.stderr = sys.stdout

if __name__ == "__main__":
    application.run()
