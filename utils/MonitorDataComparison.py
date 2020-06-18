import os, sys, json, time, pyssdb, random, datetime, redis
from scrapy.utils.project import get_project_settings


class Comparison(object):
    def __init__(self):
        self.ssdb_client = pyssdb.Client(get_project_settings().get('SSDB_HOST'), 8888)
        self.spider2_ssdb_client = pyssdb.Client(get_project_settings().get('SPIDER2_SSDB_HOST'), 8888)
        self.today = datetime.date.today()
        self.yesterday = self.today - datetime.timedelta(days=1)
        self.count = 0

    def goods_info_monitor_v3(self, goods, num):
        goods_info_monitor_hash_name = 'pdd_goods_info_monitor_hash{}'.format(num)
        goods_name_monitor_list_name = 'pdd_goods_title_monitor_list:' + str(self.today)
        thumb_url_monitor_list_name = 'pdd_thumb_url_monitor_list:' + str(self.today)

        goods_id = goods['goods_id']
        old_goods_info = self.spider2_ssdb_client.hget(goods_info_monitor_hash_name, goods_id)
        if old_goods_info:
            old_goods_info = json.loads(old_goods_info.decode('utf-8'))
            old_sku = old_goods_info['sku']

            #  保存有变化的goods_name
            if old_goods_info['goods_name'] != goods['goods_name']:
                new_goods_name_dict = {
                    "goods_id": goods_id,
                    "goods_title": goods['goods_name'],
                    "old_title": old_goods_info['goods_name'],
                    "update_last_time": goods['date']
                }
                self.spider2_ssdb_client.qpush_back(goods_name_monitor_list_name, json.dumps(new_goods_name_dict))

            #  保存有变化的thumb_url
            if old_goods_info['thumb_url'] != goods['thumb_url']:
                new_thumb_url_dict = {
                    "goods_id": goods_id,
                    "thumb_url": goods['thumb_url'],
                    "old_image": old_goods_info['thumb_url'],
                    "update_last_time": goods['date']
                }
                self.spider2_ssdb_client.qpush_back(thumb_url_monitor_list_name, json.dumps(new_thumb_url_dict))

            #  保存有变化的sku   type解释: 1修改价格 2修改图片 3新增sku 4修改sku 5删除sku
            today_sku_list = []  # 今天爬取的sku
            for i in goods['sku']:
                if i == {}:
                    continue
                today_sku_list.append(i['sku_id'])

            old_sku_list = []  # 昨天爬取的sku
            for i in old_sku:
                if i == {}:
                    continue
                old_sku_list.append(i['sku_id'])

            add_sku_id_list = list((set(today_sku_list) - set(old_sku_list)))
            reduce_sku_id_list = list(set(old_sku_list) - set(today_sku_list))
            date = time.strftime("%Y-%m-%d", time.localtime(goods['date']))

            # 保存变化的sku
            for each_new_sku in goods['sku']:
                if each_new_sku == {}:
                    continue
                type_list1 = []
                old = {}
                for each_old_sku in old_sku:
                    if each_old_sku == {}:
                        continue
                    if each_old_sku['sku_id'] == each_new_sku['sku_id']:
                        # (图片 规格 团购价)对比
                        if float(each_new_sku['group_price']) != float(each_old_sku['group_price']):
                            old["old_group_price"] = float(each_old_sku['group_price']) / 100
                            type_list1.append("1")

                        if each_old_sku['thumb_url'] != each_new_sku['thumb_url']:
                            old["old_image"] = each_old_sku['thumb_url']
                            type_list1.append("2")

                        if "specs" in each_old_sku and "specs" in each_new_sku:
                            is_same = self.is_goods_sku_specs_same(each_new_sku["specs"], each_old_sku["specs"])
                            if not is_same:
                                old["old_specs"] = each_old_sku['specs']
                                type_list1.append("4")

                        if len(type_list1) != 0:
                            self.save_sku(goods_id, each_new_sku, type_list1, old, date)

            # 保存新增的sku
            if add_sku_id_list:
                for each_new_sku in goods['sku']:
                    if each_new_sku == {}:
                        continue
                    if each_new_sku['sku_id'] in reduce_sku_id_list:
                        type_list2 = ["3"]
                        old = None
                        self.save_sku(goods_id, each_new_sku, type_list2, old, date)

        sku_list = []
        for i in goods["sku"]:
            sku_list.append({
                "sku_id": i["sku_id"],
                "group_price": i["group_price"],
                "thumb_url": i["thumb_url"],
                "specs": i["specs"],
            })

        new_goods_info = {
            "goods_id": goods_id,
            "goods_name": goods['goods_name'],
            "thumb_url": goods['thumb_url'],
            "sku": sku_list,
            "date": goods['date'],
        }
        self.spider2_ssdb_client.hset(goods_info_monitor_hash_name, goods_id, json.dumps(new_goods_info))

    def goods_comment_monitor_v3(self, goods):
        comment_monitor_hash_name = 'pdd_comment_monitor_hash'
        comment_monitor_list_name = 'pdd_comment_monitor_list:' + str(self.today)

        goods_id = goods['goods_id']
        comment_count_list = goods['comment_count']
        update_last_time = goods['update_last_time']
        date = time.strftime("%Y-%m-%d", time.localtime(update_last_time))

        old_goods_info = self.spider2_ssdb_client.hget(comment_monitor_hash_name, goods_id)
        if old_goods_info:
            old_goods_info = json.loads(old_goods_info.decode('utf-8'))
            old_comment_count_list = old_goods_info['comment_count']

            today_comment_name_list = []
            yesterday_comment_name_list = []
            is_change = False
            comment_diff_list = []

            for each_comment in comment_count_list:
                today_comment_name_list.append(each_comment['name'])
                for yes_each_comment in old_comment_count_list:
                    yesterday_comment_name_list.append(yes_each_comment['name'])

                    if each_comment['name'] == yes_each_comment['name']:
                        comment_diff = int(each_comment['count']) - int(yes_each_comment['count'])
                        if comment_diff != 0 and comment_diff > -10:
                            is_change = True
                        comment_diff_list.append({"name": each_comment['name'], "comment_diff": comment_diff})

            add_comment_name_list = list((set(today_comment_name_list) - set(yesterday_comment_name_list)))
            reduce_comment_name_list = list(set(yesterday_comment_name_list) - set(today_comment_name_list))

            if add_comment_name_list:
                for each_comment2 in comment_count_list:
                    if each_comment2['name'] in add_comment_name_list:
                        if each_comment2['name'] == "全部":
                            comment_diff_list.insert(
                                0, {"name": each_comment2['name'], "comment_diff": each_comment2['count']})
                        else:
                            comment_diff_list.append(
                                {"name": each_comment2['name'], "comment_diff": each_comment2['count']})

            if reduce_comment_name_list:
                for each_comment3 in old_comment_count_list:
                    if each_comment3['name'] in reduce_comment_name_list:
                        if each_comment3['name'] == "全部":
                            comment_count_list.insert(
                                0, {"name": each_comment3['name'], "count": each_comment3['count']})
                        else:
                            comment_count_list.append(
                                {"name": each_comment3['name'], "count": each_comment3['count']})

            if is_change or add_comment_name_list != [] or reduce_comment_name_list != []:
                comment_num = 0
                diff_num = 0
                comment_count_list2 = []
                comment_diff_list2 = []

                for i in comment_count_list:
                    if i["name"] == "全部":
                        comment_num = i["count"]
                    else:
                        comment_count_list2.append(i)

                for w in comment_diff_list:
                    if w["name"] == "全部":
                        diff_num = w["comment_diff"]
                    else:
                        comment_diff_list2.append(w)

                new_comment_dict = {"goods_id": goods_id,
                                    "comment_count_list": comment_count_list2,
                                    "comment_diff_list": comment_diff_list2,
                                    "add_comment_name_list": add_comment_name_list,
                                    "reduce_comment_name_list": reduce_comment_name_list,
                                    "comment_num": comment_num,
                                    "diff_num": diff_num,
                                    "update_last_time": update_last_time,
                                    "date": date
                                    }

                self.spider2_ssdb_client.qpush_back(comment_monitor_list_name, json.dumps(new_comment_dict))

        # 覆盖原表
        self.spider2_ssdb_client.hset(comment_monitor_hash_name, goods_id, json.dumps(
            {"comment_count": comment_count_list, "update_last_time": update_last_time}))

    def mall_collection_monitor(self, mall):
        d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '00:00', '%Y-%m-%d%H:%M')
        timeStamp1 = int(time.mktime(time.strptime(str(d_time1), "%Y-%m-%d %H:%M:%S")))
        d_time2 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '23:59', '%Y-%m-%d%H:%M')
        timeStamp2 = int(time.mktime(time.strptime(str(d_time2), "%Y-%m-%d %H:%M:%S")))

        pdd_mall_collection_monitor_hash_name = 'pdd_mall_collection_monitor_hash'
        collection_monitor_list_name = 'pdd_mall_collection_monitor_list:' + str(self.today)
        is_repetition = False

        mall_id = mall['mall_id']
        collection_count = mall['collection_count']
        update_last_time = mall['update_last_time']
        date = time.strftime("%Y-%m-%d", time.localtime(update_last_time))

        old_mall_info = self.spider2_ssdb_client.hget(pdd_mall_collection_monitor_hash_name, mall_id)
        if old_mall_info:
            old_mall_info = json.loads(old_mall_info.decode('utf-8'))
            old_collection_count = old_mall_info['collection_count']
            old_update_last_time = int(old_mall_info['update_last_time'])

            if timeStamp1 <= old_update_last_time <= timeStamp2:
                return
            if "万" in str(collection_count):
                collection_count = float(collection_count[:-1]) * 10000
            if "万" in str(old_collection_count):
                old_collection_count = float(old_collection_count[:-1]) * 10000
            count_diff = int(collection_count) - int(old_collection_count)
            if count_diff != 0:
                new_collection_dict = {"mall_id": mall_id, "collection_count": collection_count,
                                       "count_diff": count_diff, "update_last_time": update_last_time, "date": date}
                self.spider2_ssdb_client.qpush_back(collection_monitor_list_name, json.dumps(new_collection_dict))

        if not is_repetition:
            collection_dict = {"collection_count": collection_count, "update_last_time": update_last_time}
            self.spider2_ssdb_client.hset(pdd_mall_collection_monitor_hash_name, mall_id, json.dumps(collection_dict))

    def mall_goods_num(self, mall):
        mall_goods_count_monitor_hash = 'pdd_mall_goods_count_monitor_hash'
        mall_goods_count_monitor_list = 'pdd_mall_goods_count_monitor_list:' + str(self.today)

        mall_id = mall['mall_id']
        goods_num = mall['goods_num']
        last_update_time = mall['last_update_time']
        date = time.strftime("%Y-%m-%d", time.localtime(last_update_time))

        old_mall_info = self.spider2_ssdb_client.hget(mall_goods_count_monitor_hash, mall_id)
        if old_mall_info:
            old_mall_info = json.loads(old_mall_info.decode('utf-8'))
            old_goods_num = old_mall_info['goods_num']
            num_diff = int(goods_num) - int(old_goods_num)

            if num_diff != 0:
                new_goods_num_dict = {"mall_id": mall_id, "goods_num": goods_num,
                                      "num_diff": num_diff, "last_update_time": last_update_time, "date": date}
                self.spider2_ssdb_client.qpush_back(mall_goods_count_monitor_list, json.dumps(new_goods_num_dict))

        self.spider2_ssdb_client.hset(mall_goods_count_monitor_hash, mall_id, json.dumps(
            {"goods_num": goods_num, "last_update_time": last_update_time}))

    def mall_coupon_monitor(self, mall):
        mall_coupon_monitor_hash = 'pdd_mall_coupon_monitor_hash'
        mall_coupon_monitor_list = 'pdd_mall_coupon_monitor_list:' + str(self.today)

        mall_id = mall['mall_id']
        mall_coupons = mall['mall_coupons']
        last_update_time = mall['last_update_time']
        date = time.strftime("%Y-%m-%d", time.localtime(last_update_time))

        old_mall_info = self.spider2_ssdb_client.hget(mall_coupon_monitor_hash, mall_id)
        if old_mall_info:
            old_mall_info = json.loads(old_mall_info.decode('utf-8'))
            old_mall_coupons = old_mall_info['mall_coupons']

            today_coupons_list = []
            yes_coupons_list = []
            for each_new_coupon in mall_coupons:
                if each_new_coupon == {}:
                    continue
                today_coupons_list.append(each_new_coupon["id"])

            for each_old_coupon in old_mall_coupons:
                if each_old_coupon == {}:
                    continue
                yes_coupons_list.append(each_old_coupon["id"])

            add_coupon_id_list = list((set(today_coupons_list) - set(yes_coupons_list)))
            reduce_coupon_id_list = list((set(yes_coupons_list) - set(today_coupons_list)))

            add_coupon_list = []
            reduce_coupon_list = []

            if add_coupon_id_list:
                for each_new_coupon2 in mall_coupons:
                    if each_new_coupon2 == {}:
                        continue
                    if each_new_coupon2["id"] in add_coupon_id_list:
                        coupon_dict = {"id": each_new_coupon2["id"], "batch_name": each_new_coupon2["batch_name"],
                                       "start_time": each_new_coupon2["start_time"],
                                       "end_time": each_new_coupon2["end_time"],
                                       "rules_desc": each_new_coupon2["rules_desc"]}
                        add_coupon_list.append(coupon_dict)

            if reduce_coupon_id_list:
                for each_old_coupon2 in old_mall_coupons:
                    if each_old_coupon2 == {}:
                        continue
                    if each_old_coupon2["id"] in reduce_coupon_id_list:
                        coupon_dict = {"id": each_old_coupon2["id"], "batch_name": each_old_coupon2["batch_name"],
                                       "start_time": each_old_coupon2["start_time"],
                                       "end_time": each_old_coupon2["end_time"],
                                       "rules_desc": each_old_coupon2["rules_desc"]}
                        reduce_coupon_list.append(coupon_dict)

            if add_coupon_list != [] or reduce_coupon_list != []:
                conpon_dict = {"mall_id": mall_id, "add_coupon_list": add_coupon_list,
                               "reduce_coupon_list": reduce_coupon_list, "last_update_time": last_update_time,
                               "date": date
                               }
                self.spider2_ssdb_client.qpush_back(mall_coupon_monitor_list, json.dumps(conpon_dict))
        self.spider2_ssdb_client.hset(mall_coupon_monitor_hash, mall_id, json.dumps(
            {"mall_coupons": mall_coupons, "last_update_time": last_update_time}))

    '''函数'''
    @staticmethod
    def is_goods_sku_specs_same(new_specs, old_specs):
        if new_specs == [] and old_specs == []:
            return True

        if (new_specs != [] and old_specs == []) or (new_specs == [] and old_specs != []):
            return False

        if len(new_specs) != len(old_specs):
            return False

        for i in range(len(new_specs)):
            new_specs_dict = new_specs[i]
            old_specs_dict = old_specs[i]

            new_specs_dict_key_list = new_specs_dict.keys()
            old_specs_dict_key_list = old_specs_dict.keys()
            if "spec_key" in new_specs_dict_key_list and "spec_key" in old_specs_dict_key_list:
                if new_specs_dict["spec_key"] != old_specs_dict["spec_key"]:
                    return False

            if "spec_value" in new_specs_dict_key_list and "spec_value" in old_specs_dict_key_list:
                if new_specs_dict["spec_value"] != old_specs_dict["spec_value"]:
                    return False

            if "spec_key_id" in new_specs_dict_key_list and "spec_key_id" in old_specs_dict_key_list:
                if new_specs_dict["spec_key_id"] != old_specs_dict["spec_key_id"]:
                    return False

            if "spec_value_id" in new_specs_dict_key_list and "spec_value_id" in old_specs_dict_key_list:
                if new_specs_dict["spec_value_id"] != old_specs_dict["spec_value_id"]:
                    return False

        return True

    def save_sku(self, goods_id, each_new_sku, type_list, old, date):
        sku_monitor_list_name = 'pdd_sku_monitor_list:' + str(self.today)
        each_sku_dict = {
            "goods_id": goods_id,
            "sku_id": each_new_sku['sku_id'],
            "group_price": float(each_new_sku['group_price']) / 100,
            "image": each_new_sku['thumb_url'],
            "specs": each_new_sku['specs'],
            "old": old,
            "type": type_list,
            "date": date,
        }
        self.spider2_ssdb_client.qpush_back(sku_monitor_list_name, json.dumps(each_sku_dict))

    def mall_dsr_monitor(self, dsr_data):
        mall_id = dsr_data['mall_id']
        dsr_monitor_list_name = 'mall_dsr_monitor_list'
        dsr_hash_name = 'mall_dsr_basic_hash'
        dsr_info = self.ssdb_client.hget(dsr_hash_name, mall_id)
        if not dsr_info:
            self.ssdb_client.qpush_back(dsr_monitor_list_name, json.dumps(dsr_data))
            self.ssdb_client.hset(dsr_hash_name, mall_id, json.dumps(dsr_data))
        dsr_info = json.loads(dsr_info.decode('utf-8'))
        dsr_data_time = time.strftime("%Y-%m-%d", time.localtime(dsr_data['date']))
        dsr_info_time = time.strftime("%Y-%m-%d", time.localtime(dsr_info['date']))
        if dsr_data_time <= dsr_info_time:
            return None
        for (k, v) in dsr_data.items():
            if v != dsr_info[k]:
                self.ssdb_client.qpush_back(dsr_monitor_list_name, json.dumps(dsr_data))
                break
        self.ssdb_client.hset(dsr_hash_name, mall_id, json.dumps(dsr_data))






