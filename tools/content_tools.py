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

    drafts_folder = os.path.join(os.path.expanduser("~"), "Documents", config.drafts_folder)
    os.makedirs(drafts_folder, exist_ok=True)

    safe_name = "".join(c for c in topic if c.isalnum() or c == " ").strip()[:40]
    filepath = os.path.join(drafts_folder, f"{safe_name}.docx")

    doc = Document()
    for line in content.split("\n"):
        doc.add_paragraph(line)
    doc.save(filepath)

    os.startfile(filepath)

    # importing here instead of top of file to dodge a circular import
    # (file_tools doesnt need content_tools, but this is the one spot
    # they touch)
    from file_tools import track_recent
    track_recent(filepath)

    return f"drafted and saved: {safe_name}.docx"