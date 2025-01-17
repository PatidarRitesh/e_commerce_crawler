from scrapy.http import Request
import scrapy
from e_commerce_crawler import settings
import csv
import os
import json

# User inputs
product = settings.product
domains = settings.domains
csv_file_path = settings.csv_file_path
json_file_path = settings.json_file_path

class ProductSpider(scrapy.Spider):
    name = 'product_spider'
    item_count = 0  # Initialize item counter
    max_items = 100 # Maximum items to crawl
    seen_links = set()  # To store visited links and avoid duplicates


    
