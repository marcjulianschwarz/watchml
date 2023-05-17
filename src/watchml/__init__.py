import logging
import sys

from . import data
from . import file
from . import ml
from . import utils
from . import viz
from .data import *
from .file import *
from .ml import *
from .utils import *
from .viz import *

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
logging.info("Imported watchml")
