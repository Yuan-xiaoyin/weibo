# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import time

import pymongo

from weibo.items import *


class TimePipeline():
    def process_item(self,item,spider):
        '''因为在item中并没有对crawled_at这个字段赋值，这里我们把这个字段赋值为爬取的时间
        这里先进行判断，因为在item中只有Useritem和weiboitem中又crawled_at字段
        就是说如果事这两个item就把爬取的时间赋值给他'''
        if isinstance(item,UserItem) or isinstance(item,WeiboItem):
            now=time.strftime('%Y-%m-%d %h:%M',time.localtime())
            item['crawled_at']=now
            return item

class weiboPipeline():
    '''这里先进行时间数据的清洗,然后再生成item'''
    def parse_time(self,date):
        if re.match('刚刚',date):
            date=time.strftime('%Y-%m-%d %h:%M',time.localtime(time.time()))
        if re.match('\d+分钟前',date):
            # 如果出现几分钟前这种时间，就匹配分钟数，然后用当前时间的秒数减去分钟的秒数，就生成几分钟前的格式化时间
            minute=re.match('(\d+)',date).group(1)
            # time.time()返回的是当前时间的秒数
            date=time.strftime('%Y-%m-%d %h:%M',time.localtime(time.time()-float(minute)*60))
        if re.match('\d+小时前',date):
            hour=re.match('(\d+)',date).group(1)
            date=time.strftime('%Y-%m-%d %h:%M',time.localtime(time.time()-float(hour)*60*60))
        if re.match('昨天.*',date):
            date=re.match('昨天(.*)',date).group(1).strip()
            date=time.strftime('%Y-%m-%d',time.localtime(time.time()-float(24*60*60))+' '+'date')
        if re.match('\d{2}-\d{2}',date):
            # 匹配出现10-23 10:23这样的时间
            date=time.strftime('%Y-',time.localtime())+date+' 00:00'
        return date

    def process_item(self,item,spider):
#         因为只有微博的具体信息中会有时间这类的数据,所以这里就对微博item中的数据进行清洗
        if isinstance(item,WeiboItem):
            if item.get('created_at'):
                item['created_at']=item['created_at'].strip()
                item['created_at']=self.parse_time(item.get('created_at'))
        return item

class MongoPipeline(object):
    def __init__(self,mongo_url,mongo_db):
        self.mongo_url=mongo_url
        self.mong_db=mongo_db
    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self,spider):
        # 连接数据库
        self.client=pymongo.MongoClient(self.mongo_url)
        self.db=self.client[self.mong_db]
        # 为weiboitem与useritem这两个item添加索引，这样可以提高检索的效率
        self.db[UserItem.collection].create_index([('id',pymongo.ASCENDING)])
        self.db[WeiboItem.collection].create_index([('id',pymongo.ASCENDING)])

    def process_item(self,item,spider):
        if isinstance(item,UserItem) or isinstance(item,WeiboItem):
            # 对爬取重复的数据进行更新，所以这里用到了update，$set：对重复的数据进行更新，同时不会删除已存在的字段
            # 第三个参数传入true表示如果数据不存在，则插入数据，如果已经存在，就进行替换
            # 这里是通过判断用户的id来进行数据的去重
            self.db[item.collection].update({'id':item.get('id')},{'$set':item},True)
        if isinstance(item,UserRelationItem):
            # 用到更新操作
            self.db[item.collection].update(
                {'id':item.get('id')},
                # '$addToSet':在一个list下面，添加元素，同时不影响list并且去重‘$each’：遍历数据中的元素
                {"$addToSet":
                        {
                            'follows':{'$each':item['follows']},
                            'fans':{'$each':item['fans']}
                        }
                },True
            )
        return item
    def close_spider(self,spider):
        self.client.close()


