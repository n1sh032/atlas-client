import argparse
import os
from pathlib import Path

from src.web_runtime import serve


class AtlasApplication:
    actions = {"chat", "listen"}

    def describe(self):
        from dotenv import load_dotenv
