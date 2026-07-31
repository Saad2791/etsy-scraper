import argparse
import asyncio
import json
import sys
import logging
from scraper import HighSpeedScraper
from reorganizer import DataReorganizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run(urls: list, output_file: str, concurrency: int, timeout: int):
    scraper = HighSpeedScraper(concurrency=concurrency, timeout=timeout)
    reorganizer = DataReorganizer()

    logger.info(f"Starting scrape for {len(urls)} URLs...")
    results = await scraper.scrape(urls)

    reorganized_results = []

    for result in results:
        url = result["url"]
        if result.get("error"):
            logger.warning(f"Skipping reorganization for {url} due to error: {result['error']}")
            reorganized_results.append({
                "url": url,
                "status": "failed",
                "error": result["error"]
            })
            continue

        html = result.get("html")
        if html:
            logger.info(f"Reorganizing data for {url}")
            structured_data = reorganizer.reorganize(html, base_url=url)
            reorganized_results.append({
                "url": url,
                "status": "success",
                "data": structured_data
            })
        else:
            reorganized_results.append({
                "url": url,
                "status": "failed",
                "error": "No HTML content"
            })

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reorganized_results, f, ensure_ascii=False, indent=2)

    logger.info(f"Finished processing. Results saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="High-Speed Async Scraper and Data Reorganizer")
    parser.add_argument("--urls", nargs="+", help="List of URLs to scrape", default=[])
    parser.add_argument("--url-file", type=str, help="Path to a file containing URLs (one per line)", default=None)
    parser.add_argument("--output", type=str, help="Output JSON file path", default="output.json")
    parser.add_argument("--concurrency", type=int, help="Maximum concurrent requests", default=10)
    parser.add_argument("--timeout", type=int, help="Timeout per request in seconds", default=30)

    args = parser.parse_args()

    urls_to_scrape = args.urls.copy()

    if args.url_file:
        try:
            with open(args.url_file, 'r', encoding='utf-8') as f:
                file_urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                urls_to_scrape.extend(file_urls)
        except Exception as e:
            logger.error(f"Error reading url file {args.url_file}: {e}")
            sys.exit(1)

    if not urls_to_scrape:
        logger.error("No URLs provided. Use --urls or --url-file.")
        parser.print_help()
        sys.exit(1)

    asyncio.run(run(urls_to_scrape, args.output, args.concurrency, args.timeout))

if __name__ == "__main__":
    main()
