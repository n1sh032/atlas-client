# the actual "brain" of atlas. this is where gemini gets told what tools it
# has and decides whether to just talk or call one of them

import json
import os

import config
from gemini_client import client

