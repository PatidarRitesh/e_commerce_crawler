# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


import os
import json

class EcommerceCrawlerPipeline:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path

    @classmethod
    def from_crawler(cls, crawler):
        # Get the JSON file path from settings
        return cls(json_file_path=crawler.settings.get('JSON_FILE_PATH'))

    def open_spider(self, spider):
        # Initialize the JSON file if it doesn't exist
        if not os.path.exists(self.json_file_path):
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=4, ensure_ascii=False)

    def process_item(self, item, spider):
        # Write the scraped data to the JSON file
        with open(self.json_file_path, 'r+', encoding='utf-8') as f:
            existing_data = json.load(f)
            website = item.get('Website')

            # Append the item to the appropriate website list
            if website not in existing_data:
                existing_data[website] = []
            existing_data[website].append(dict(item))

            # Write back to the JSON file
            f.seek(0)
            json.dump(existing_data, f, indent=4, ensure_ascii=False)

        return item
