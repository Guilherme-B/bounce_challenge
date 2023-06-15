__version__ = "0.0.1"

import logging

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-6s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.INFO)
