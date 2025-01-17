# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


class ECommerceCrawlerPipeline:
    def process_item(self, item, spider):
        return item


import csv
from e_commerce_crawler import settings

def write_to_csv(item):
       writer = csv.writer(open(settings.csv_file_path, 'a',encoding="utf-8"), lineterminator='\n')
       #print(settings.product)
       #print(item.keys())
       writer.writerow([item[key] for key in item.keys()])
       
class WriteToCsv(object):
    def process_item(self, item, spider):
            write_to_csv(item)
            return item