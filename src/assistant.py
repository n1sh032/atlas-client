# the actual "brain" of atlas. this is where gemini gets told what tools it
# has and decides whether to just talk or call one of them

import json
import os
from src import config
from src.gemini_client import client

from tools import file_tools
from tools import system_tools
from tools import content_tools
from tools import calendar_tools
