import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from app.scheduler.scheduler import check_prices

if __name__ == "__main__":
    check_prices()
