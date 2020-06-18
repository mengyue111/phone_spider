import json, time, pyssdb, random, datetime
from scrapy.utils.project import get_project_settings


class common(object):

    def __init__(self):
        self.ssdb_client = pyssdb.Client(get_project_settings().get('SSDB_HOST'), 8888)
        self.today = datetime.date.today()

    '''检测产品销量变化'''

    def check_goods_sales(self, goods_id, goods_sales, goods_price, mall_id, from_style=1, is_force=False, date=0,
                          up1w_flag=False):
        if goods_sales > 99999:
            self.ssdb_client.zset('pdd_up10w_goods_id', str(goods_id), int(time.time()))
        if 9999 < goods_sales <= 99999:
            self.ssdb_client.zset('pdd_up1w_goods_id', str(goods_id), int(time.time()))
        if goods_sales > 9999 and not up1w_flag:
            pdd_goods_sales_up1w_list = 'pdd_goods_sales_up1w_list:' + str(self.today)
            self.ssdb_client.qpush(pdd_goods_sales_up1w_list, json.dumps({
                'goods_id': goods_id,
                'goods_sales': goods_sales,
                'goods_price': goods_price,
                'mall_id': mall_id,
                'from_style': from_style,
                'is_force': is_force,
                'date': date
            }))
            if int(mall_id) > 0:
                self.ssdb_client.zset('pdd_up1w_sales_mall', mall_id, int(time.time()))
            return None
        goods_sale_hash = 'pdd_goods_sale_hash:' + str(self.today)
        if self.ssdb_client.hget(goods_sale_hash, goods_id):
            return None
        goods_sale_list = 'pdd_goods_sale_list'
        # 有销量的数据作为需要存储的数据
        pdd_spider_goods_list = 'pdd_spider_goods_list'
        # end add
        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 销量抓取日期
        date = int(date)
        if not date:
            date = time.strftime('%Y-%m-%d')
            date = int(time.mktime(time.strptime(date, '%Y-%m-%d')))

        # 获取产品信息
        goods_info = self.get_goods_info(goods_id)
        if 'date' in goods_info.keys():
            if date <= goods_info['date']:
                return True

        last_sales = int(goods_info['sales'])
        sales_diff = goods_sales - last_sales
        if sales_diff <= 0:
            return True

        # 防止第一次初始化数据差异过大
        if sales_diff > 10000 and sales_diff == goods_sales:
            sales_diff = random.randint(1, 100)
        total_day_amount = float(goods_price * sales_diff)  # 日销售额
        # 日销售额大于500000或者销量大于1000或者销量小于100
        if (total_day_amount > 500000 or sales_diff > 500 or sales_diff < -100) and not is_force:
            return True

        # ##保存产品销量信息
        goods_info['sales'] = goods_sales
        goods_info['date'] = date

        self.save_goods_info(goods_id, goods_info)
        # 销量正数变化
        if sales_diff > 0:
            amount = float(goods_price * sales_diff)
            total_amount = float(goods_price * goods_sales)
            push_data = {'goods_id': goods_id, 'mall_id': mall_id, 'sales': sales_diff, 'amount': amount,
                         'total_sales': goods_sales, 'total_amount': total_amount}
            push_data = self.item_to_json(push_data)
            if sales_diff < 1000:
                self.ssdb_client.qpush_back(goods_sale_list, push_data)
            goods_level = 1
            if from_style == 1:
                goods_level = 2
            elif from_style == 2:
                goods_level = 1
            elif from_style == 3:
                goods_level = 2
            elif from_style == 4:
                goods_level = 4
            elif from_style == 5:
                goods_level = 2
            elif from_style == 6:
                goods_level = 4
            if goods_sales > 99999:
                goods_level = 6
            if 9999 < goods_sales <= 99999:
                goods_level = 5
            self.ssdb_client.qpush_back(pdd_spider_goods_list, json.dumps({
                'goods_id': goods_id,
                'last_update_time': now_time,
                'level': goods_level,
                'is_on_sale': 1
            }))
            self.ssdb_client.hset(goods_sale_hash, goods_id, push_data)

    # 将数据推送到队列中
    def get_goods_info(self, goods_id):
        hash_name = 'pdd_goods_sales'
        hash_key = goods_id
        i = 0
        goods_data = self.ssdb_client.hget(hash_name, hash_key)
        while i <= 3 and not goods_data:
            goods_data = self.ssdb_client.hget(hash_name, hash_key)
            i += 1

        if goods_data:
            goods_data = goods_data.decode('utf-8')
            # 新的字典类型的数据
            if len(goods_data) > 10:
                goods_data = json.loads(goods_data)
            else:
                goods_data = {'sales': goods_data}
        else:
            goods_data = {'sales': 0}

        return goods_data

    def check_goods_price(self, goods_id, goods_price):
        price_info = self.ssdb_client.hget('pdd_goods_price', goods_id)
        if price_info:
            price_info = json.loads(price_info.decode('utf-8'))
            last_price = float(price_info['price'])
            if last_price != goods_price:
                price_info['price'] = goods_price
            else:
                return True
        else:
            price_info = {'price': goods_price}

        '''将价格变化放到待推送队里'''
        push_data = {'goods_id': goods_id, 'price': goods_price}
        push_data = self.item_to_json(push_data)
        self.ssdb_client.qpush_back('pdd_goods_price_list', push_data)

        self.ssdb_client.hset('pdd_goods_price', goods_id, json.dumps(price_info))

    def save_goods_info(self, goods_id, goods_info):
        hash_name = 'pdd_goods_sales'
        hash_key = goods_id

        self.ssdb_client.hset(hash_name, hash_key, json.dumps(goods_info))

    '''将item对象转换为json格式'''

    @staticmethod
    def item_to_json(item):
        date = int(time.time())
        data = {"date": date}
        data = dict(data, **item)
        data = json.dumps(data)
        return data

    def keyword_sales_static(self, keyword_data):
        keyword_list = 'pdd_keywords_list'
        keyword_goods_hash = 'pdd_keyword_goods_hash:' + str(self.today)
        goods_sale_hash = 'pdd_goods_sale_hash:' + str(self.today)
        goods_id_list = self.ssdb_client.hget(keyword_goods_hash, keyword_data['keyword'])
        total_sales = 0
        if goods_id_list:
            for goods_id in goods_id_list:
                goods_info = self.ssdb_client.hget(goods_sale_hash, goods_id)
                if not goods_info:
                    total_sales = total_sales + goods_info['goods_info']
        keyword_data['day_total_sales'] = total_sales
        push_data = self.item_to_json(keyword_data)
        self.ssdb_client.qpush_back(keyword_list, push_data)
