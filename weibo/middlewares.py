# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import json
import logging
import requests

from scrapy import signals


class CookiesMiddleware(object):
    def __init__(self,cookies_url):
        # 初始化定义一个logger对象
        self.logger=logging.getLogger(__name__)
        self.cookies_url=cookies_url
    def get_random_cookies(self):
        # 连接cookies池，并取出cookie
        try:
            response=requests.get(self.cookies_url)
            if response.status_code==200:
                cookies=json.loads(response.text)
                return cookies
        except requests.ConnectionError:
            self.logger.debug('连接cookies池错误')
            return False
    @classmethod
    def from_crawler(cls,crawler):
        # 从settings中取到定义的cookies_url
        return cls(
            cookies_url=crawler.settings.get('COOKIES_URL')
        )
    def process_request(self,request,spider):
        self.logger.debug('正在获取Cookies')
        cookies=self.get_random_cookies()
        if cookies:
            requests.cookies=cookies
            self.logger.debug('使用Cookies'+json.dumps(cookies))


class ProxyMiddleware(object):
    def __init__(self,proxy_url):
        self.logger=logging.getLogger(__name__)
        self.proxy_url=proxy_url

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            proxy_url=crawler.settings.get('PROXY_URL')
        )
    def get_random_proxy(self):
        try:
            response=requests.get(self.proxy_url)
            if response.status_code==200:
                cookies=json.loads(response.text)
                return cookies
        except requests.ConnectionError:
            self.logger.debug('连接代理池出错')
            return False
    def process_request(self,request,spider):
        # 这里设置为只有请求失败时才使用代理,这样可以保证爬取效率，因为使用代理会降低访问速度
        # 判断上次请求中是否有retry_time，重试次数
        # retry_times:这个在scrapy的middlerware中定义的
        if request.meta.get('retry_times'):
            proxy=self.get_random_proxy()
            if proxy:
                url="https://{proxy}".format(proxy=proxy)
                self.logger.debug('使用proxy'+json.dumps(proxy))
                request.meta[proxy]=url




