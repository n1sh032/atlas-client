"""Loopback web transport. Application operations run on one worker."""

import json
import logging
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

logger = logging.getLogger(__name__)
