# -*- coding: utf-8 -*-
import json

from scrapy import Request,Spider

from weibo.items import *


class WeibocnSpider(Spider):
    name = 'weibocn'
    allowed_domains = ['m.weibo.cn']
    # 定义微博用户详情url
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'
    #定义用户关注的url
    followers_url='https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    # 定义用户粉丝列表
    fans_url='https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}'
    # 定义用户微博列表的url
    weibo_url='https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'
    # 定义开始的用户列表
    start_users=['1259110474','1312412824','2812335943']


    def start_requests(self):
        for uid in self.start_users:
            yield Request(self.user_url.format(uid=uid),callback=self.parse_user)


    def parse_user(self, response):
        # 解析用户的信息
        self.logger.debug(response)
        # 将得到的字符串转化为json格式
        result=json.loads(response.text)
        if result.get('data').get('userInfo'):
            user_info=result.get('data').get('userInfo')
            user_item=UserItem()
            # 将结果构造成字典
            # follows、fans、crawled_at这几个字段因为在后会进行提取，所以这里不做提取
            field_map={
                "id":'id',
                "name":"screen_name",
                "profile_image_url":"profile_image_url",
                "cover_image_phone":"cover_image_phone",
                "gender":"gender",
                "description":"description",
                "fans_count":"followers_count",
                "follows_count":"follow_count",
                "weibos_count":"statuses_count",
                "verified":"verified",
                "verified_reason":"verified_reason",
                "verified_type":"verified_type"
            }
            # 这里是用的遍历赋值，因为有可能我们定义的字段名称与提取的json的字段名称不同
            # 当然也可以采用逐个赋值的方法：id=user_info['id']这种方式
            for field,attr in field_map.items():
                user_item[field]=user_info.get(attr)
            yield user_item
            uid=user_info.get('id')
            # 生成关注列表，meta传参，键参数传递另一个方法，另一个方法用response.meta（）来取值,这里是传递分页页码的意思
            yield Request(self.followers_url.format(uid=uid,page=1),callback=self.parse_follows,meta={'page':1,'uid':uid})
            # 生成粉丝列表
            yield Request(self.fans_url.format(uid=uid,page=1),callback=self.parse_fans,meta={'page':1,'uid':uid})
            #生成微博信息列表
            yield Request(self.weibo_url.format(uid=uid,page=1),callback=self.parse_weibo,meta={'page':1,"uid":uid})


    def parse_follows(self,response):
    #     解析关注列表
        result=json.loads(response.text)
        # 判断能否得到这些页面信息
        if len(result.get('data').get('cards')) and result.get('data').get('cards')[-1].get('card_group'):
            # 得到关注列表所在的位置
            follows = result.get('data').get('cards')[-1].get('card_group')
            for follow in follows:
                if follow.get('user'):
                    uid=follow.get('user').get('id')
                    yield Request(self.user_url.format(uid=uid),callback=self.parse_user)
            # 这里使用meta方法得到parse_user传过来的uid信息
            uid=response.meta.get('uid')
    #         现在再解析得到在item中定义的UserRelationItem字段信息
            user_relation_item=UserRelationItem()
            # 得到被关注用的id和名称,这里被关注的用户的粉丝暂时设置为空列表
            follows=[{'id':follow.get('user').get('id'),'name':follow.get('user').get('screen_name')} for follow in follows]
            user_relation_item['id']=uid
            user_relation_item['follows']=follows
            user_relation_item['fans']=[]
            yield user_relation_item
    #         获取下一页的关注
            page=response.meta.get('page')+1
            # 这里有点绕，就是说现在传过来的是第一页的内容，我们把page加1就表示第二页的内容，然后交给回调函数（这里是自己)去处理，就可以把用户关注的人的信息全部拿到
            yield Request(self.followers_url.format(uid=uid,page=page),meta={"page":page,'uid':uid})

    def parse_fans(self,response):
    #     解析粉丝列表
    # 大体的思路跟上面解析关注列表的思路都 差不多
        result=json.loads(response.text)
        if len(result.get('data').get('cards')) and result.get('data').get('cards')[-1].get('card_group'):
            fans = result.get('data').get('cards')[-1].get('card_group')
            for fan in fans:
                if fan.get('user'):
                    # 得到第一页每个粉丝的id信息
                    uid=fan.get('user').get('id')
                    # 将解析得到的粉丝的id交给parse_user
                    yield Request(self.user_url.format(uid=uid),callback=self.parse_user)
            # 得到uid中每个粉丝的id以及name
            uid=response.meta.get('uid')
            user_relation_item=UserRelationItem()
            fans=[{'id':fan.get('user').get('id'),'name':fan.get('user').get('screen_name')} for fan in fans]
            # 生成每个用户的关注列表和粉丝列表，因为前面已经生成了关注列表，所以这里就为空，这样传到item中就组合成了
            user_relation_item['id']=uid
            user_relation_item['fans']=fans
            user_relation_item['follows']=[]
            yield user_relation_item
    #         获取下一的粉丝信息
            page=response.meta.get('page')+1
            yield Request(self.fans_url.format(uid=uid,page=page),callback=self.parse_fans,meta={'page':page,'uid':uid})

    def parse_weibo(self,response):
#         解析微博详情页面
        result=json.loads(response.text)
        # 判断是否得到页面信息
        if len('data') and result.get('data').get('cards'):
            weibos=result.get('data').get('cards')
            for weibo in weibos:
                mblog=weibo.get('mblog')
                if mblog:
                    weibo_item=WeiboItem()
                    field_map={
                        "id":'id',
                        "attitudes_count":'attitudes_count',
                        "comments_count":"comments_count",
                        "reposets_count":'reposts_count',
                        "source":"source",
                        "created_at":"created_at",
                        "text":"text",
                        "raw_text":"raw_text",
                        "picture":"original_pic",
                        "pictures":"pics",
                        "thumbnail":"thumbnail_pic"
                    }
                    # 这里还是采用的是遍历，进行批量字段的赋值
                    for field,attr in field_map.items():
                        weibo_item[field]=mblog.get(attr)
                    weibo_item['user']=response.meta.get('uid')
                    yield weibo_item
            uid=response.meta.get('uid')
            page=response.meta.get('page')+1
            yield Request(self.weibo_url.format(uid=uid,page=page),callback=self.parse_weibo,meta={'uid':uid,'page':page})




