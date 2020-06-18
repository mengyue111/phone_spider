# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

class SpiderPipeline(object):

    def __init__(self):
        pass

    # 爬虫数据处理入口
    def process_item(self, item, spider):
        pass