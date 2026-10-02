#!/usr/bin/env python3

import asyncio
import os
import sys
import re

from urllib.parse import urlparse, urljoin

import aiohttp
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm_asyncio

from crawl4ai import AsyncWebCrawler


if len(sys.argv) < 3:
    print("""
Usage:

python crawl.py <START_URL> <OUTPUT_FOLDER>

Example:

python crawl.py https://developer.hashicorp.com/vault/docs docs/vault
""")
    sys.exit(1)


START_URL = sys.argv[1]
OUTPUT_DIR = sys.argv[2]


# Tune for your Ryzen AI 9 HX 370
MAX_WORKERS = 10


visited = set()
queue = []


BASE = urlparse(START_URL)


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


def clean_filename(url):

    path = urlparse(url).path

    path = path.strip("/")

    if not path:
        path = "index"


    filename = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        path
    )

    return filename[:200] + ".md"



def allowed_url(url):

    parsed = urlparse(url)


    # same domain
    if parsed.netloc != BASE.netloc:
        return False


    # stay below starting documentation path
    if not parsed.path.startswith(
        BASE.path
    ):
        return False


    return True



async def find_sitemap():

    candidates = [

        f"{BASE.scheme}://{BASE.netloc}/sitemap.xml",

        f"{BASE.scheme}://{BASE.netloc}/sitemap_index.xml"

    ]


    async with aiohttp.ClientSession() as session:

        for sitemap in candidates:

            try:

                async with session.get(
                    sitemap,
                    timeout=10
                ) as r:


                    if r.status == 200:

                        text = await r.text()


                        urls = re.findall(
                            r"<loc>(.*?)</loc>",
                            text
                        )


                        if urls:

                            print(
                                "Sitemap found:",
                                sitemap
                            )

                            return urls


            except Exception:

                pass


    return []



def extract_links(html, current):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    links = []


    for a in soup.find_all(
        "a",
        href=True
    ):

        url = urljoin(
            current,
            a["href"]
        )


        url = url.split("#")[0]


        if allowed_url(url):

            links.append(url)


    return links



async def crawl_single(
    crawler,
    url,
    semaphore
):

    async with semaphore:

        if url in visited:
            return []


        visited.add(url)


        print(
            f"[{len(visited)}] {url}"
        )


        try:

            result = await crawler.arun(
                url=url
            )


            filename = clean_filename(
                url
            )


            with open(
                os.path.join(
                    OUTPUT_DIR,
                    filename
                ),
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    result.markdown
                )


            # recursive discovery
            return extract_links(
                result.html,
                url
            )


        except Exception as e:

            print(
                "ERROR:",
                url,
                e
            )

            return []



async def main():

    global queue


    print(
        "Searching sitemap..."
    )


    urls = await find_sitemap()


    if urls:

        urls = [
            u for u in urls
            if allowed_url(u)
        ]

        queue.extend(
            urls
        )

        print(
            f"Sitemap pages: {len(queue)}"
        )


    else:

        print(
            "No sitemap found."
        )

        print(
            "Using recursive crawling."
        )

        queue.append(
            START_URL
        )



    semaphore = asyncio.Semaphore(
        MAX_WORKERS
    )


    async with AsyncWebCrawler() as crawler:


        while queue:


            current_batch = []


            while queue:

                url = queue.pop(0)

                if url not in visited:

                    current_batch.append(
                        url
                    )


            if not current_batch:
                break



            results = await tqdm_asyncio.gather(
                *[
                    crawl_single(
                        crawler,
                        url,
                        semaphore
                    )

                    for url in current_batch
                ]
            )


            for links in results:

                for link in links:

                    if (
                        link not in visited
                        and link not in queue
                    ):

                        queue.append(
                            link
                        )



    print()
    print(
        "Finished"
    )

    print(
        "Pages downloaded:",
        len(visited)
    )



asyncio.run(main())
