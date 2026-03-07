#!/usr/bin/env python3
import asyncio
from scrapling.spiders import Spider, request

class NintendoSpider(Spider):
    name = 'nintendo'
    start_urls = ['https://www.nintendo.com/']

    async def parse(self, response):
        # Add your scraping logic here
        pass

# Example: Extracting product titles from the page
products = response.css('.product-title::text').getall()
print(products)
