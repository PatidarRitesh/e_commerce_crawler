from scrapy.http import Request
import scrapy
from e_commerce_crawler import settings
import csv
import os
import json

# User inputs
product = settings.product
domains = settings.domains
# csv_file_path = settings.csv_file_path
# json_file_path = settings.json_file_path

class ProductSpider(scrapy.Spider):
    name = 'ProductSpider'
    item_count = 0  # Initialize item counter
    max_items = 20 # Maximum items to crawl
    seen_links = set()  # To store visited links and avoid duplicates


    def start_requests(self):
        if domains:
            for domain in domains:
                if "flipkart" in domain:
                    yield Request(url=f'https://{domain}/search?q={product}', callback=self.parse_flipkart)
                elif "snapdeal" in domain:
                    yield Request(url=f'https://{domain}/search?keyword={product}', callback=self.parse_snapdeal)
                elif "shopclues" in domain:
                    yield Request(url=f'https://{domain}/search?q={product}', callback=self.parse_shopclues)
                elif "paytmmall" in domain:
                    yield Request(url=f'https://{domain}/shop/search?q={product}', callback=self.parse_paytm)
                elif "ebay" in domain:
                    yield Request(url=f'https://{domain}/sch/i.html?_nkw={product}', callback=self.parse_ebay)

    
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
