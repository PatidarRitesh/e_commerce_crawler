# from scrapy.http import Request
# import scrapy
# from e_commerce_crawler import settings
# import csv
# import os
# import json
# import re
# # User inputs
# product = settings.product
# domains = settings.domains
# # csv_file_path = settings.csv_file_path
# # json_file_path = settings.json_file_path

# class ProductSpider(scrapy.Spider):
#     name = 'ProductSpider'
#     item_count = 0  # Initialize item counter
#     max_items = 20 # Maximum items to crawl
#     seen_links = set()  # To store visited links and avoid duplicates
#     custom_settings = {
#         'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
#         'PLAYWRIGHT_LAUNCH_OPTIONS': {'headless': True},
#     }

#     PRODUCT_PATTERNS = [r'/product/', r'/dp/', r'/item/', r'/p/']

#     def start_requests(self):
#         if domains:
#             for domain in domains:
#                 if "flipkart" in domain:
#                     yield Request(url=f'https://{domain}/search?q={product}', callback=self.parse_flipkart)
#                 elif "snapdeal" in domain:
#                     yield Request(url=f'https://{domain}/search?keyword={product}', callback=self.parse_snapdeal)
#                 elif "shopclues" in domain:
#                     yield Request(url=f'https://{domain}/search?q={product}', callback=self.parse_shopclues)
#                 elif "paytmmall" in domain:
#                     yield Request(url=f'https://{domain}/shop/search?q={product}', callback=self.parse_paytm)
#                 elif "ebay" in domain:
#                     yield Request(url=f'https://{domain}/sch/i.html?_nkw={product}', callback=self.parse_ebay)
               
from scrapy.http import Request
import scrapy
from e_commerce_crawler import settings
import re
import time

# User inputs
product = settings.product
domains = settings.domains

class ProductSpider(scrapy.Spider):
    name = 'ProductSpider'
    item_count = 0
    max_items = 20
    seen_links = set()
    custom_settings = {
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'PLAYWRIGHT_LAUNCH_OPTIONS': {'headless': True},
    }

    PRODUCT_PATTERNS = [r'/product/', r'/dp/', r'/item/', r'/p/',r'/p/\d+',r'/c/\d+',r'/search/result/', r'/mp/',r'/p-',                # Matches URLs like /p-mp000000016854372
    r'/mp\d+',r'/p-mp\d+']

    def start_requests(self):
        if domains:
            for domain in domains:
                if "amazon" in domain:
                    yield Request(
                        url=f'https://{domain}/s?k={product}',
                        callback=self.parse_amazon,
                        meta={"playwright": True}
                    )
                elif "flipkart" in domain:
                    yield Request(url=f'https://{domain}/search?q={product}', callback=self.parse_flipkart)
                elif "snapdeal" in domain:
                    yield Request(url=f'https://{domain}/search?keyword={product}', callback=self.parse_snapdeal)
                elif "shopclues" in domain:
                    yield Request(url=f'https://{domain}/search?q={product}', callback=self.parse_shopclues)
                elif "paytmmall" in domain:
                    yield Request(url=f'https://{domain}/shop/search?q={product}', callback=self.parse_paytm)
                elif "ebay" in domain:
                    yield Request(url=f'https://{domain}/sch/i.html?_nkw={product}', callback=self.parse_ebay)
                if "nykaa" in domain:
                    search_url = f'https://{domain}/search/result/?q={product}'
                    self.logger.info(f"Starting search at: {search_url}")
                    yield Request(
                        url=search_url,
                        callback=self.parse_nykaa,
                        meta={"playwright": True}
                    )
                if "nykaafashion" in domain:
                    search_url = f'https://{domain}/catalogsearch/result/?q={product}&searchType=ManualSearch&internalSearchTerm={product}'
                    self.logger.info(f"Starting search at: {search_url}")
                    yield Request(
                        url=search_url,
                        callback=self.parse_nykaafashion,
                        meta={"playwright": True}
                    )
                if "nykaaman" in domain:
                    search_url = f'https://{domain}/search/result/?q={product}&root=search&searchType=Manual&sourcepage=home'
                    self.logger.info(f"Starting search at: {search_url}")
                    yield Request(
                        url=search_url,
                        callback=self.parse_nykaaman,
                        meta={"playwright": True}
                    )
                if "tatacliq" in domain:
                    search_url = f'https://{domain}/search/?searchCategory=all&text={product}'
                    self.logger.info(f"Starting search at: {search_url}")
                    yield Request(
                        url=search_url,
                        callback=self.parse_tatacliq,
                        meta={"playwright": True}
                    )


    def parse_amazon(self, response):
        """
        Parser for Amazon-like pages.
        """
        links = response.css('a::attr(href)').getall()
        for link in links:
            # Stop processing if the max_items limit is reached
            if self.item_count >= self.max_items:
                # Close the spider
                self.crawler.engine.close_spider(self, reason=f"Reached {self.max_items} items")
                break  # Exit the loop
                return  # Exit immediately

            full_url = response.urljoin(link)
            if self.is_product_url(full_url):
                if full_url in self.seen_links:
                    continue
                self.seen_links.add(full_url)
                self.item_count += 1
                yield {
                    'Website': 'Amazon',
                    'Product URL': full_url
                }
            elif self.is_internal_url(full_url, response.url):
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_amazon,
                    meta={"playwright": True}
                )

    def parse_nykaa(self, response):
        links = response.css('a::attr(href)').getall()  # Get all links
        for link in links:
            # Stop if max items limit is reached
            if self.item_count >= self.max_items:
                self.crawler.engine.close_spider(self, reason=f"Reached {self.max_items} items")
                return

            full_url = response.urljoin(link)

            # Check if it's a product URL
            if self.is_product_url(full_url):
                if full_url in self.seen_links:
                    continue
                self.seen_links.add(full_url)
                self.item_count += 1
                yield {
                    'Website': 'Nykaa',
                    'Product URL': full_url
                }
            elif self.is_internal_url(full_url, response.url):  # Follow internal links
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_nykaa,
                    meta={"playwright": True}
                )

    def parse_nykaafashion(self, response):
        """
        Parse the Nykaa Fashion search results and extract product links.
        """
        links = response.css('a::attr(href)').getall()  # Get all links
        for link in links:
            # Stop if max items limit is reached
            if self.item_count >= self.max_items:
                self.crawler.engine.close_spider(self, reason=f"Reached {self.max_items} items")
                return

            full_url = response.urljoin(link)

            # Check if it's a product URL
            if self.is_product_url(full_url):
                if full_url in self.seen_links:
                    continue
                self.seen_links.add(full_url)
                self.item_count += 1
                yield {
                    'Website': 'Nykaa Fashion',
                    'Product URL': full_url
                }
            elif self.is_internal_url(full_url, response.url):  # Follow internal links
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_nykaafashion,
                    meta={"playwright": True}
                )

    # def parse_nykaaman(self, response):
    #     """
    #     Parse the Nykaaman search results and extract product links.
    #     """
    #     links = response.css('a::attr(href)').getall()  # Get all links
    #     for link in links:
    #         # Stop if max items limit is reached
    #         if self.item_count >= self.max_items:
    #             self.crawler.engine.close_spider(self, reason=f"Reached {self.max_items} items")
    #             return

    #         full_url = response.urljoin(link)

    #         # Check if it's a product URL (looking for pattern `/p/` in the link)
    #         if self.is_product_url(full_url):
    #             if full_url in self.seen_links:
    #                 continue
    #             self.seen_links.add(full_url)
    #             self.item_count += 1
    #             yield {
    #                 'Website': 'Nykaaman',
    #                 'Product URL': full_url
    #             }
    #         elif self.is_internal_url(full_url, response.url):  # Follow internal links
    #             yield scrapy.Request(
    #                 full_url,
    #                 callback=self.parse_nykaaman,
    #                 meta={"playwright": True}
    #             )

    # def parse_nykaaman(self, response):
    #     """
    #     Parse the Nykaaman search results and extract product links, also handles dynamic loading of products.
    #     """
    #     # Extract product links
    #     links = response.css('a::attr(href)').getall()
    #     for link in links:
    #         if self.item_count >= self.max_items:
    #             self.crawler.engine.close_spider(self, reason=f"Reached {self.max_items} items")
    #             return

    #         full_url = response.urljoin(link)

    #         if self.is_product_url(full_url):
    #             if full_url in self.seen_links:
    #                 continue
    #             self.seen_links.add(full_url)
    #             self.item_count += 1
    #             yield {
    #                 'Website': 'Nykaaman',
    #                 'Product URL': full_url
    #             }
    #         elif self.is_internal_url(full_url, response.url):
    #             yield scrapy.Request(
    #                 full_url,
    #                 callback=self.parse_nykaaman,
    #                 meta={"playwright": True}
    #             )

    def parse_nykaaman(self, response):
        # Extract product links
        links = response.css('a::attr(href)').getall()
        for link in links:
            if self.item_count >= self.max_items:
                self.crawler.engine.close_spider(self, reason=f"Reached {self.max_items} items")
                return

            full_url = response.urljoin(link)
            if self.is_product_url(full_url):
                if full_url in self.seen_links:
                    continue
                self.seen_links.add(full_url)
                self.item_count += 1
                yield {
                    'Website': 'Nykaaman',
                    'Product URL': full_url
                }
            elif self.is_internal_url(full_url, response.url):
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_nykaaman,
                    meta={"playwright": True}
                )

        # Click "View More" button if exists
        if self.item_count < self.max_items:
            self.logger.info("Clicking the 'View More' button to load more products.")
            view_more_button = response.css('button#load-more::attr(id)').get()
            if view_more_button:
                yield Request(
                    url=response.url,
                    callback=self.parse_nykaaman,
                    meta={
                        "playwright": True,
                        "playwright_click": 'button#load-more'
                    }
                )


        # Check if there's a "View More" button and trigger the click event to load more products
        view_more_button = response.css('button.load-more-button')  # Adjusted to use the correct selector
        if view_more_button and self.item_count < self.max_items:
            self.logger.info("Clicking 'View More' to load additional products...")
            yield response.follow(
                view_more_button.attrib['href'],  # Assuming the button has an href attribute for the next page or dynamic load
                callback=self.parse_nykaaman,
                meta={"playwright": True}
            )
        
        # Wait a bit to make sure more products load if needed
        time.sleep(2)


    def parse_tatacliq(self, response):
        # Extract product links from the search page
        links = response.css('a::attr(href)').getall()
        self.logger.info(f"Found {len(links)} links.")
        
        for link in links:
            self.logger.info(f"Checking link: {link}")
            
            if self.item_count >= self.max_items:
                self.crawler.engine.close_spider(self, reason=f"Reached {self.max_items} items")
                return

            full_url = response.urljoin(link)
            if self.is_product_url(full_url):
                if full_url in self.seen_links:
                    continue
                self.seen_links.add(full_url)
                self.item_count += 1
                yield {
                    'Website': 'TataCliq',
                    'Product URL': full_url
                }
            elif self.is_internal_url(full_url, response.url):
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_tatacliq,
                    meta={"playwright": True}
                )

        # If there's a next page, follow the pagination link
        next_page = response.css('a.pagination-next::attr(href)').get()
        if next_page and self.item_count < self.max_items:
            next_page_url = response.urljoin(next_page)
            self.logger.info(f"Following next page: {next_page_url}")
            yield scrapy.Request(
                next_page_url,
                callback=self.parse_tatacliq,
                meta={"playwright": True}
            )

    def is_product_url(self, url):
        # return any(re.search(pattern, url) for pattern in self.PRODUCT_PATTERNS)
        #   return bool(re.search(r'/p/\d+', url))
        matches = any(re.search(pattern, url) for pattern in self.PRODUCT_PATTERNS)
        self.logger.info(f"URL: {url} matches product URL: {matches}")
        # input("Press Enter to continue...")
        return matches
    

    def is_internal_url(self, url, base_url):
        return base_url.split('/')[2] in url
    
    def parse_flipkart(self, response):
        """Parser to fetch info from Flipkart"""

        path = 'https://www.flipkart.com'
        no_result = response.xpath('//div[contains(text(),"Sorry")]/text()').extract_first()
        
        if no_result:
            print(f"{no_result}. Please try correcting your spelling.")
            yield {
                'Website': 'Flipkart',
                'Stock': no_result,
                'Product': 'None',
                'Rating': 'None',
                'Original Price': 'None',
                'Current Price': 'None',
                'LINK': 'None'
            }
        else:
            items = response.xpath('//div[@data-id]')
            for item in items:
                if self.item_count >= self.max_items:
                    self.crawler.engine.close_spider(self, reason=f"Reached {self.max_items} items")
                    break

                text = item.xpath('.//div/text()').extract()
                current_price = text[text.index('₹') - 1] if '₹' in text else text[2]
                original_price = text[text.index('₹') + 1] if '₹' in text else current_price
                link = path + item.xpath('.//*/@href').extract_first()
                
                # Check if the link has already been seen
                if link in self.seen_links:
                    continue  # Skip this product if it is a duplicate

                self.seen_links.add(link)  # Add the link to the seen set
                rating = item.xpath('.//span[contains(@id,"productRating")]/div/text()').extract_first() or 'NO Rating available'
                stock = "OUT OF STOCK" if item.xpath('.//div[contains(@style,"grayscale")]').extract_first() else "IN STOCK"
                title = item.xpath('.//div/a/@title').extract_first() or item.xpath('.//*/@alt').extract_first()

                # Increment the item count after a valid item
                self.item_count += 1

                yield {
                    'Website': 'Flipkart',
                    'Stock': stock,
                    'Product': title,
                    'Rating': rating,
                    'Current Price': current_price,
                    'Original Price': original_price,
                    'LINK': link
                }

                # Write the details to the CSV file
                # self.write_to_csv('Flipkart', stock, title, rating, current_price, original_price, link)
                # self.write_to_json('Flipkart', stock, title, rating, current_price, original_price, link)

            # Follow the next page if the item count hasn't been reached
            if self.item_count < self.max_items:
                next_page = response.xpath('//a[contains(@class, "next")]/@href').extract_first()
                if next_page:
                    yield response.follow(next_page, callback=self.parse_flipkart)

            
    def parse_snapdeal(self,response):
        """
        Parser to fetch info from Snapdeal
        """
        noresult=response.xpath('//span[@class="alert-heading"]/text()').extract_first()
        if noresult:
            print(noresult + " Please try correcting your spelling")
            yield {'Website': 'Snapdeal', 'Stock': noresult, 'Product': 'None', 'Rating': 'None',
                   'Original Price': 'None', 'Current Price': 'None', 'LINK': 'None'}
        else:
            items = response.xpath('//a[@class="dp-widget-link"]')
            for item in items:
                if self.item_count >= self.max_items:
                    self.crawler.engine.close_spider(self, reason=f"Reached {self.max_items} items")
                    break

                link = item.xpath('.//@href').extract_first()
                # check if the link is a duplicate
                if link in self.seen_links:
                    continue
                title = item.xpath('.//p/text()').extract_first()
                current_price = item.xpath('.//span[contains(@class,"product-price")]/text()').extract_first()
                original_price = item.xpath('.//span[contains(@class,"product-desc-price")]/text()').extract_first()
                rating = 'NO rating available'
                stock = "IN STOCK"

                self.item_count += 1

                yield {'Website': 'Snapdeal', 'Stock': stock, 'Product': title, 'Rating': rating,
                       'Current Price': current_price, 'Original Price': original_price, 'LINK': link}

                # self.write_to_csv('Snapdeal', stock, title, rating, current_price, original_price, link)
                # self.write_to_json('Snapdeal', stock, title, rating, current_price, original_price, link)

            # Follow the next page if the item count hasn't been reached
            if self.item_count < self.max_items:
                next_page = response.xpath('//a[contains(@class, "next")]/@href').extract_first()
                if next_page:
                    yield response.follow(next_page, callback=self.parse_snapdeal)

    def parse_shopclues(self, response):
        """
        Parser to fetch info from Shopclues
        """
        noresult = response.xpath('//span[@class="no_fnd"]/text()').extract_first()
        if noresult:
            print(noresult + " Please try correcting your spelling")
            yield {'Website': 'Shopclues', 'Stock': noresult, 'Product': 'None', 'Rating': 'None',
                   'Original Price': 'None', 'Current Price': 'None', 'LINK': 'None'}
        else:
            items = response.xpath('//div[@class="column col3 search_blocks"]')
            for item in items:
                if self.item_count >= self.max_items:
                    self.crawler.engine.close_spider(self, reason=f"Reached {self.max_items} items")
                    break

                link = item.xpath('.//a/@href').extract_first()
                # check if the link is a duplicate
                if link in self.seen_links:
                    continue
                title = item.xpath('.//h2/text()').extract_first()
                current_price = item.xpath('.//div[@class="ori_price"]/span/text()').extract_first()
                ref = item.xpath('.//div[@class="refurbished_i"]/text()').extract_first()
                if ref == 'Refurbished':
                    original_price = current_price
                else:
                    original_price = item.xpath('.//div[@class="old_prices"]/span/text()').extract_first()
                rating = 'NO rating available'
                stock = "IN STOCK"

                self.item_count += 1

                yield {'Website': 'Shopclues', 'Stock': stock, 'Product': title, 'Rating': rating,
                       'Current Price': current_price, 'Original Price': original_price, 'LINK': link}

                # self.write_to_csv('Shopclues', stock, title, rating, current_price, original_price, link)
                # self.write_to_json('Shopclues', stock, title, rating, current_price, original_price, link)

            # Follow the next page if the item count hasn't been reached
            if self.item_count < self.max_items:
                next_page = response.xpath('//a[contains(@class, "next")]/@href').extract_first()
                if next_page:
                    yield response.follow(next_page, callback=self.parse_shopclues)

    def parse_paytm(self,response):
        """
        Parser to fetch info from Paytm Mall
        """
        path = 'https://paytmmall.com'
        noresult = response.xpath('//span[contains(text(),"Sorry")]/text()').extract_first()
        if noresult:
            print(noresult + " Please try correcting your spelling")
            yield {'Website': 'Paytmmall', 'Stock': 'None', 'Product': 'None', 'Rating': 'None',
                   'Original Price': 'None', 'Current Price': 'None', 'LINK': 'None'}
        else:
            items = response.xpath('//div[@class="_2i1r"]')
            for item in items:
                if self.item_count >= self.max_items:
                    self.crawler.engine.close_spider(self, reason=f"Reached {self.max_items} items")
                    break

                current_price = item.xpath('.//div[@class="_1kMS"]/span/text()').extract_first()
                if item.xpath('.//div[@class="dQm2"]/span/text()').extract_first() is None:
                    original_price = current_price
                elif item.xpath('.//div[@class="dQm2"]/span/text()').extract_first() == '-':
                    original_price = item.xpath('.//div[@class="dQm2"]/text()').extract_first()
                else:
                    original_price = item.xpath('.//div[@class="dQm2"]/span/text()').extract_first()
                link = path + item.xpath('.//div[@class="_3WhJ"]/a/@href').extract_first()
                # check if the link is a duplicate
                if link in self.seen_links:
                    continue
                title = item.xpath('.//div[@class="_2apC"]/text()').extract_first()
                rating = 'NO rating available'
                stock = 'IN STOCK'

                self.item_count += 1

                yield {'Website': 'Paytm Mall', 'Stock': stock, 'Product': title, 'Rating': rating,
                       'Current Price': current_price, 'Original Price': original_price, 'LINK': link}

                # self.write_to_csv('Paytm Mall', stock, title, rating, current_price, original_price, link)
                # self.write_to_json('Paytm Mall', stock, title, rating, current_price, original_price, link)

            # Follow the next page if the item count hasn't been reached
            if self.item_count < self.max_items:
                next_page = response.xpath('//a[contains(@class, "next")]/@href').extract_first()
                if next_page:
                    yield response.follow(next_page, callback=self.parse_paytm)


    def parse_ebay(self, response): 
        """
        Parser to fetch info from eBay
        """
        noresult = response.xpath('//h1[contains(text(),"No results for")]/text()').extract_first()
        if noresult:
            print(noresult + " Please try correcting your spelling")
            yield {'Website': 'eBay.com', 'Stock': 'No results found', 'Product': 'None', 'Rating': 'None',
                   'Original Price': 'None', 'Current Price': 'None', 'LINK': 'None'}
        else:
            items = response.xpath('//li[contains(@class, "s-item")]')
            for item in items:
                if self.item_count >= self.max_items:
                    self.crawler.engine.close_spider(self, reason=f"Reached {self.max_items} items")
                    break

                link = item.xpath('.//a[contains(@class, "s-item__link")]/@href').extract_first()
                # check if the link is a duplicate
                if link in self.seen_links:
                    continue
                title = item.xpath('.//h3[contains(@class, "s-item__title")]/text()').extract_first()
                rating = item.xpath('.//div[contains(@class, "s-item__reviews")]/span/span/text()').extract_first()
                current_price = item.xpath('.//span[contains(@class, "s-item__price")]/text()').extract_first()
                original_price = item.xpath('.//span[contains(@class, "s-item__strike")]/text()').extract_first()

                if not original_price:
                    original_price = current_price

                stock = "IN STOCK"

                self.item_count += 1

                yield {'Website': 'eBay.com', 'Stock': stock, 'Product': title, 'Rating': rating if rating else 'No rating available',
                       'Current Price': current_price, 'Original Price': original_price, 'LINK': link}

                # self.write_to_csv('eBay.com', stock, title, rating, current_price, original_price, link)
                # self.write_to_json('eBay.com', stock, title, rating, current_price, original_price, link)

            # Follow the next page if the item count hasn't been reached
            if self.item_count < self.max_items:
                next_page = response.xpath('//a[contains(@class, "pagination__next")]/@href').extract_first()
                if next_page:
                    yield response.follow(next_page, callback=self.parse_ebay)

    

    # def write_to_csv(self, website, stock, title, rating, current_price, original_price, link):
    #     """Write a row to the CSV file."""
    #     with open(csv_file_path, 'a', encoding='utf-8', newline='') as f:
    #         writer = csv.writer(f)
    #         writer.writerow([website, stock, title, rating, current_price, original_price, link])

    # def write_to_json(self, website, stock, title, rating, current_price, original_price, link):
    #     """Write the scraped data to a JSON file."""
    #     data = {
    #         "stock": stock,
    #         "title": title,
    #         "rating": rating,
    #         "current_price": current_price,
    #         "original_price": original_price,
    #         "link": link
    #     }

    #     # Open the JSON file and append the data
    #     if os.path.exists(json_file_path):
    #         with open(json_file_path, 'r+', encoding='utf-8') as f:
    #             existing_data = json.load(f)
    #             # Append data to the specific website key
    #             if website not in existing_data:
    #                 existing_data[website] = []
    #             existing_data[website].append(data)

    #             f.seek(0)
    #             json.dump(existing_data, f, indent=4, ensure_ascii=False)
    #     else:
    #         with open(json_file_path, 'w', encoding='utf-8') as f:
    #             # Initialize with empty data
    #             initial_data = {website: [data]}
    #             json.dump(initial_data, f, indent=4, ensure_ascii=False)
