import logging
import os

log_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
os.makedirs(log_dir, exist_ok=True)

log_path = os.path.join(log_dir, 'log.txt')

logging.basicConfig(
    filename=log_path,
    filemode='a',
    format='%(asctime)s | %(levelname)s | %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)
