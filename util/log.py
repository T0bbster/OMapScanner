import logging
import logging.config
from pathlib import Path
from python_log_indenter import IndentedLoggerAdapter


logging_dir = Path('logs')
logging_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=logging_dir / 'scrape_maps.log',
    format='%(levelname)7s - %(asctime)s: %(message)s'
)
log = IndentedLoggerAdapter(logging.getLogger(__name__))
