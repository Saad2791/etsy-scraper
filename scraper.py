import asyncio
import aiohttp
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HighSpeedScraper:
    def __init__(self, concurrency: int = 10, timeout: int = 30):
        self.concurrency = concurrency
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.semaphore = asyncio.Semaphore(concurrency)

    async def fetch_url(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Optional[str]]:
        async with self.semaphore:
            try:
                logger.info(f"Fetching: {url}")
                async with session.get(url) as response:
                    response.raise_for_status()
                    html = await response.text()
                    logger.info(f"Successfully fetched: {url}")
                    return {"url": url, "html": html, "error": None}
            except aiohttp.ClientError as e:
                logger.error(f"ClientError fetching {url}: {e}")
                return {"url": url, "html": None, "error": str(e)}
            except asyncio.TimeoutError:
                logger.error(f"Timeout fetching {url}")
                return {"url": url, "html": None, "error": "Timeout"}
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {e}")
                return {"url": url, "html": None, "error": str(e)}

    async def scrape(self, urls: List[str]) -> List[Dict[str, Optional[str]]]:
        connector = aiohttp.TCPConnector(limit=self.concurrency)
        async with aiohttp.ClientSession(connector=connector, timeout=self.timeout) as session:
            tasks = [self.fetch_url(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
            return results
