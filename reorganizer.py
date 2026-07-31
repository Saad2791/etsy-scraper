from bs4 import BeautifulSoup
from typing import Dict, List, Any
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class DataReorganizer:
    def __init__(self, parser: str = 'lxml'):
        self.parser = parser

    def reorganize(self, html: str, base_url: str = "") -> Dict[str, Any]:
        """
        Takes raw HTML and extracts/reorganizes the data into a structured dictionary.
        """
        if not html:
            return {"error": "Empty HTML provided"}

        try:
            soup = BeautifulSoup(html, self.parser)

            # Extract basic metadata
            title = soup.title.string.strip() if soup.title and soup.title.string else ""

            description = ""
            desc_tag = soup.find("meta", attrs={"name": "description"})
            if desc_tag and desc_tag.get("content"):
                description = desc_tag["content"].strip()

            # Extract headings
            headings = []
            for i in range(1, 7):
                for h_tag in soup.find_all(f"h{i}"):
                    text = h_tag.get_text(strip=True)
                    if text:
                        headings.append({"level": i, "text": text})

            # Extract main text
            # A simple heuristic: find all paragraphs, or extract from <main> / <article> if available
            main_text_blocks = []
            content_container = soup.find(["main", "article"])
            if not content_container:
                content_container = soup.body

            if content_container:
                for p_tag in content_container.find_all("p"):
                    text = p_tag.get_text(strip=True)
                    if text:
                        main_text_blocks.append(text)

            # Extract links
            links = []
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                text = a_tag.get_text(strip=True)
                full_url = urljoin(base_url, href)
                links.append({"text": text, "url": full_url})

            # Clean up the output structure
            structured_data = {
                "metadata": {
                    "title": title,
                    "description": description
                },
                "content": {
                    "headings": headings,
                    "paragraphs": main_text_blocks
                },
                "links": links
            }

            return structured_data

        except Exception as e:
            logger.error(f"Error reorganizing data for {base_url}: {e}")
            return {"error": str(e)}
