# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

'''产品信息'''
class SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    goods_id	= scrapy.Field()
    mall_id		= scrapy.Field()
    goods_type	= scrapy.Field()
    category1	= scrapy.Field()
    category2   = scrapy.Field()
    category3 	= scrapy.Field()
    goods_name	= scrapy.Field()
    market_price= scrapy.Field()
    price 		= scrapy.Field()
    is_on_sale   = scrapy.Field()
    max_group_price   = scrapy.Field()
    min_group_price   = scrapy.Field()
    max_normal_price  = scrapy.Field()
    min_normal_price  = scrapy.Field()
    thumb_url        = scrapy.Field()
    publish_date     = scrapy.Field()
    total_sales     =  scrapy.Field()
    total_amount    =  scrapy.Field()
    #goods_list = scrapy.Field()

'''店铺信息'''
class MallItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    mall_id		= scrapy.Field()
    mall_name	= scrapy.Field()
    goods_num	= scrapy.Field()
    score_avg	= scrapy.Field()
    mall_sales	= scrapy.Field()
    is_open		= scrapy.Field()
    status		= scrapy.Field()
    province	= scrapy.Field()
    city 		= scrapy.Field()
    area   		= scrapy.Field()
    street      = scrapy.Field()
    logo    	= scrapy.Field()
    staple_id   = scrapy.Field()
    mall_coupons= scrapy.Field()

'''产品销量信息'''
class GoodsSalesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    goods_list = scrapy.Field()
    mall_id    = scrapy.Field()
    cache_key = scrapy.Field()
    response_data = scrapy.Field()

'''活动及分类信息'''
class CategoryItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #first_name = scrapy.Field()
    #second_name= scrapy.Field()
    cat_list   = scrapy.Field()
    keyword_list = scrapy.Field()

'''分类下产品信息'''
class CategoryGoodsItem(scrapy.Item):
    pass
    # define the fields for your item here like:
    # name = scrapy.Field()
    goods_lists = scrapy.Field()
    cache_key = scrapy.Field()
    response_data = scrapy.Field()

'''秒杀信息'''
class PddSeckillItem(scrapy.Item):
    pass
    # define the fields for your item here like:
    # name = scrapy.Field()
    goods_list = scrapy.Field()
    goods_rank_list = scrapy.Field()
    goods_seckill_info = scrapy.Field()
    
'''查询关键字后产品列表'''
class KeywordGoodsList(scrapy.Item):
    goods_list = scrapy.Field()
    page = scrapy.Field()
    keyword = scrapy.Field()
    response_data = scrapy.Field()

'''秒杀活动商品信息'''
class SpikeGoodsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    goods_id	= scrapy.Field()
    goods_name	= scrapy.Field()
    thumb_url	= scrapy.Field()
    hd_thumb_url = scrapy.Field()
    cat_id = scrapy.Field()
    cat_id_1 = scrapy.Field()
    cat_id_2 = scrapy.Field()
    cat_id_3	= scrapy.Field()
    start_time = scrapy.Field()
    end_time = scrapy.Field()
    all_quantity = scrapy.Field()
    spike_price = scrapy.Field()
    normal_price = scrapy.Field()
    total_sales = scrapy.Field()
    spike_sales = scrapy.Field()
    mall_id = scrapy.Field()
    sold_out_time = scrapy.Field()
    group_price = scrapy.Field()
    tab_id = scrapy.Field()
    spider_time = scrapy.Field()


class BillboardInfoItem(scrapy.Item):
    """榜单信息"""
    # define the fields for your item here like:
    # name = scrapy.Field()
    """push_data = {'billboard_id': ext['billboard_id'], 'billboard_name': ext['billboard_name'],
                         'billboard_url': ext['billboard_url'], 'opt_id': opt_id}"""
    billboard_id = scrapy.Field()
    billboard_name = scrapy.Field()
    billboard_url = scrapy.Field()
    opt_id = scrapy.Field()


class DuoDuoJinBaoItem(scrapy.Item):
    """ 进宝商品信息"""
    goods_list = scrapy.Field()
    cate_list = scrapy.Field()

class CommentMonitorItem(scrapy.Item):
    """ 商品评论数监控信息"""
    goods_id = scrapy.Field()
    comment_count = scrapy.Field()
    comment_count_list = scrapy.Field()

class MallCollectionMonitorItem(scrapy.Item):
    """ 店铺收藏数监控信息"""
    mall_id = scrapy.Field()
    collection_count = scrapy.Field()

class BillboardRankListItem(scrapy.Item):
    """ 排行榜单数据"""
    goods_list = scrapy.Field()

class SyncMallListItem(scrapy.Item):
    """ 排行榜单数据"""
    sync_list = scrapy.Field()
    pass_id   = scrapy.Field()

class SyncMallOrderItem(scrapy.Field):
    sync_data = scrapy.Field()

class LiveUserDetailItem(scrapy.Item):
    '''直播间详情数据'''
    room_id = scrapy.Field()
    source_id = scrapy.Field()
    user_name = scrapy.Field()
    user_picture = scrapy.Field()
    gender = scrapy.Field()
    age = scrapy.Field()
    address = scrapy.Field()
    user_sign = scrapy.Field()
    fans_count = scrapy.Field()
    update_time = scrapy.Field()

class LiveRoomDetailItem(scrapy.Item):
    '''直播间详情数据'''
    room_id = scrapy.Field()          # 直播间id
    anchor_type = scrapy.Field()      # 直播间类型
    source_id = scrapy.Field()        # (类似)用户id
    mall_id = scrapy.Field()          # 商铺id
    goods_count = scrapy.Field()      # 上架数
    browse_count = scrapy.Field()     # 浏览量
    update_time = scrapy.Field()      # 抓取时间
    live_date = scrapy.Field()        # 直播日期

class LiveGoodsItem(scrapy.Item):
    '''直播间商品列表'''
    item_list = scrapy.Field()

class LiveUserProfileItem(scrapy.Item):
    pass

class LiveRoomNearby(scrapy.Item):
    item_list = scrapy.Field()

'''手机etag注册'''
class EtagItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    device_id	= scrapy.Field()
    etag	    = scrapy.Field()
    api_uid     = scrapy.Field()
