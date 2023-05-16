import logging
import sys

from .file import *
from .ml import *
from .utils import *
from .viz import *


logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
logging.info("Imported watchml")
