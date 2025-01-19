# E-Commerce Crawler

## Requirements

- Python 3.8+
- Scrapy
- Scrapy-Playwright for rendering JavaScript-heavy websites.

### How to run this project
#### 1. Install the requirements
```bash
pip install -r requirements.txt
```
#### 2. Go to settings.py and change the output json file path  based on your OS
```python
dir = r"C:\Users\HXP\Dropbox\PC\Documents\Python Scripts\e_commerce_crawler"
csv_file_path = os.path.join(dir, filename)
```
#### 3. Run the spider
```bash
scrapy crawl ProductSpider
```
#### 4. On runnig the spider, it will ask for product name like : mobile phone, laptop, etc.
```bash
Enter the product name: mobile phone
```
#### 5. After entering the product name , it will ask for domain name like : amazon.in, flipkart.com, etc. (ypu can enter multiple domain names)
```bash
Enter the domain name: amazon.in
```
#### 6. After entering the details , the output will be in the form of json file in the specified path in settings.py file.
```bash
Output file: C:\Users\HXP\Dropbox\PC\Documents\Python Scripts\e_commerce_crawler\output.json
```
#### 7. For demo purposes, you can check the [output.json](./e_commerce_crawler/e_commerce_crawler/output.json) file for the output.


## Aprroach :




1. **Identifying URL Patterns**:
   - I examined various e-commerce websites to identify common patterns in product URLs. This was done by analyzing the structure of their URLs.
   - I created a list of regular expressions to capture the product URLs across different websites. For example:
     ```python
     PRODUCT_PATTERNS = [
         r'/product/', r'/dp/', r'/item/', r'/p/', r'/p/\d+', r'/c/\d+', 
         r'/search/result/', r'/mp/', r'/p-', r'/mp\d+', r'/p-mp\d+'
     ]
     ```
   - Based on these patterns, I designed the crawler to start with search URLs like:
     ```python
     search_url = f'https://{domain}/search/result/?q={product}'
     ```

2. **Choosing Scrapy for Scalability**:
   - I selected **Scrapy** for this assignment due to its scalability and efficiency in handling large web scraping tasks.
   - For pages requiring dynamic content rendering, I integrated **Playwright** into Scrapy for handling JavaScript content.

3. **Parsing Product Links**:
   - I created functions to parse product links and other essential details from the search results.
   - For this, I used the Scrapy selector to extract all href attributes:
     ```python
     response.css('a::attr(href)').getall()
     ```

4. **Regular Expression to Filter Product URLs**:
   - To ensure I only extract product links, I employed a regular expression method to filter URLs that match the product patterns.
     ```python
     def is_product_url(self, url):
         matches = any(re.search(pattern, url) for pattern in self.PRODUCT_PATTERNS)
         self.logger.info(f"URL: {url} matches product URL: {matches}")
         return matches
     ```

5. **User Input and Dynamic Domain Handling**:
   - I designed the crawler to accept dynamic input for the product name and the target e-commerce domains.
   - In `settings.py`, I added logic to handle user input for:
     - Product name
     - List of domains (e.g., Flipkart, Amazon, etc.)
     - Output file path for saving the results.

6. **Pipeline for Output Storage**:
   - I set up a pipeline in `pipelines.py` to store the scraped data in a JSON file.
   - The output file path is dynamically written in `settings.py` based on the user input.
     ```python
     JSON_FILE_PATH = os.path.join(os.path.dirname(__file__), 'output.json')
     ```

7. **XPath for Specific Website Parsing**:
   - For websites where URL patterns were not sufficient, I used **XPath** to precisely extract product details.
   - For instance, on some websites, I utilized:
     ```python
     items = response.xpath('//div[@data-id]')
     ```
   - This ensured that the data extraction was tailored to each website's unique structure.
