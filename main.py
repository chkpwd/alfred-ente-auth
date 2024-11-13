import os
import sys
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Add the vendor directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vendor'))


if __name__ == "__main__":
    # need to improve this
