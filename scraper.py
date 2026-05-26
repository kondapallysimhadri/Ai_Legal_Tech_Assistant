import asyncio
import hashlib
import logging
import os
import re
import datetime
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
from pymongo import MongoClient, UpdateOne
import trafilatura
from newspaper import Article
from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("LegalScraper3.1")


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/legal_ai_db")
client = MongoClient(MONGO_URI)
db = client.get_database()


class LegalScraper:
    def __init__(self):
        self.sources = {
            "claimdepot": [
                "https://www.claimdepot.com/settlements",
                "https://www.claimdepot.com/no-proof-class-action-settlements",
                "https://www.claimdepot.com/data-breach",
                "https://www.claimdepot.com/investigations",
                "https://www.claimdepot.com/news",
                "https://www.claimdepot.com/learn",
            ],
            "reuters": [
                "https://www.reuters.com/legal/",
                "https://www.reuters.com/technology/",
                "https://www.reuters.com/business/",
            ],
        }
        self.target_count = 1000
        self.processed_urls = set()

    def generate_hash(self, content):
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def extract_full_text(self, html):

        try:
            downloaded = trafilatura.extract(
                html, include_links=False, include_images=False, include_tables=True
            )
            if not downloaded:
                article = Article("")
                article.set_html(html)
                article.parse()
                return article.text
            return downloaded
        except Exception as e:
            logger.error(f"❌ Extraction error: {e}")
            return ""

    async def scrape_source(self, context, url):

        page = await context.new_page()
        try:
            logger.info(f"🌐 Index Page: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(2)

            links = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a'))
                    .map(a => a.href)
                    .filter(href => {
                        const h = href.toLowerCase();
                        return (h.includes('claimdepot.com') && (h.includes('/settlements/') || h.includes('/data-breach/') || h.includes('/news/'))) ||
                               (h.includes('reuters.com') && (h.includes('/legal/') || h.includes('/technology/') || h.includes('/business/')));
                    })
            }""")

            links = list(set(links))
            logger.info(f"🔗 Found {len(links)} unique links on {url}")

            results = []
            for link in links[:30]:
                if link in self.processed_urls:
                    continue
                self.processed_urls.add(link)

                article_page = await context.new_page()
                try:
                    logger.info(f"📄 Article: {link}")
                    await article_page.goto(
                        link, wait_until="domcontentloaded", timeout=60000
                    )
                    article_html = await article_page.content()

                    full_text = self.extract_full_text(article_html)
                    title_match = re.search(r"<title>(.*?)</title>", article_html)
                    title = title_match.group(1) if title_match else "Untitled"

                    doc = {
                        "title": title.split("|")[0].split("-")[0].strip(),
                        "source_url": link,
                        "content": full_text,
                        "content_hash": self.generate_hash(full_text),
                        "scraped_at": datetime.datetime.utcnow(),
                        "source": "ClaimDepot" if "claimdepot" in link else "Reuters",
                        "category": "Settlement" if "settlement" in link else "News",
                        "risk_level": (
                            "High"
                            if any(
                                kw in full_text.lower()
                                for kw in ["leak", "breach", "exposed", "critical"]
                            )
                            else "Medium"
                        ),
                    }
                    results.append(doc)
                except Exception as e:
                    logger.error(f"❌ Failed to scrape article {link}: {e}")
                finally:
                    await article_page.close()

            return results
        except Exception as e:
            logger.error(f"❌ Error scraping source {url}: {e}")
            return []
        finally:
            await page.close()

    async def run(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )

            for site, urls in self.sources.items():
                for url in urls:
                    logger.info(f"🚀 Starting scrape for {site}: {url}")
                    page_results = await self.scrape_source(context, url)

                    if page_results:
                        ops = [
                            UpdateOne(
                                {"source_url": doc["source_url"]},
                                {"$set": doc},
                                upsert=True,
                            )
                            for doc in page_results
                        ]

                        db.settlements.bulk_write(ops, ordered=False)
                        logger.info(f"✅ Synced {len(page_results)} records from {url}")

            await browser.close()
            print(f"🏁 Final Records Count: {db.settlements.count_documents({})}")


if __name__ == "__main__":
    scraper = LegalScraper()
    asyncio.run(scraper.run())
