# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    # 解析用户的相关信息，生成相关信息
    # 这里是选择的用户的信息里面的data-->userInfo中的字段来定义
    # define the fields for your item here like:
    # name = scrapy.Field()
    collection='users'
    id=scrapy.Field()
    name=scrapy.Field()
    profile_image_url=scrapy.Field()
    cover_image_phone=scrapy.Field()
    gender=scrapy.Field()
    description=scrapy.Field()
    fans_count=scrapy.Field()
    follows_count=scrapy.Field()
    weibos_count=scrapy.Field()
    verified=scrapy.Field()
    verified_reason=scrapy.Field()
    verified_type=scrapy.Field()
    follows=scrapy.Field()
    fans=scrapy.Field()
    crawled_at=scrapy.Field()

class UserRelationItem(scrapy.Item):
#     定义用户的关注和粉\丝列表
    collection='users'
    id=scrapy.Field()
    follows=scrapy.Field()
    fans=scrapy.Field()

class WeiboItem(scrapy.Item):
#     定义微博相关的字段
    collection='weibos'
    id=scrapy.Field()
    attitudes_count=scrapy.Field()
    comments_count=scrapy.Field()
    reposets_count=scrapy.Field()
    source=scrapy.Field()
    text=scrapy.Field()
    raw_text=scrapy.Field()
    picture=scrapy.Field()
    pictures=scrapy.Field()
    thumbnail=scrapy.Field()
    user=scrapy.Field()
    created_at=scrapy.Field()
    crawled_at=scrapy.Field()


