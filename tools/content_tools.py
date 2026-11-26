# google search and writing/drafting stuff, since both are more "content"
# related than app control

import os
import webbrowser
from urllib.parse import quote_plus
from docx import Document

from src import config
from src.gemini_client import client


def google_search(query):
    url = f"https://www.google.com/search?q={quote_plus(query)}"
    webbrowser.open(url)
    return f"searching google for {query}"


def draft_document(topic):
    res = client.models.generate_content(
        model=config.draft_model,
        contents=f"write the following, just the content, no preamble: {topic}"
    )
    content = res.text.strip()
