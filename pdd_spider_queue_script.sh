#!/usr/bin/env bash

pm2 -n mall_dsr_monitor_consumer start  python -- /data/pdd-spider/consumers/ssdb/mall_dsr_monitor_consumer.py
pm2 -n pdd_spike_activity_push start  python -- /data/pdd-spider/mq_push/pdd_spike_activity_push.py
# 全网订单消费
pm2 -n common_order_push start  python -- /data/pdd-spider/mq_push/common_order_push.py

# etag生成消费
pm2 -n pdd_etag_consume start python -- /usr/local/bin/scrapy crawl pdd_etag_app
# etag激活消费
pm2 -n pdd_etag_active_consume start python -- /usr/local/bin/scrapy crawl pdd_etag_active_app
# etag重复使用脚本 old
pm2 -n pdd_etag_reuse start  python -- /data/pdd-spider/script/import_device_list_v4.py
# etag重复使用脚本 （直接使用）
pm2 -n pdd_etag_only_reuse start  python -- /data/pdd-spider/script/import_device_only_etag.py
# etag重复使用脚本 （生成anti再使用）
pm2 -n pdd_etag_anti_reuse start  python -- /data/pdd-spider/script/import_device_produce_anti.py
# 检测anti质量
pm2 -n pdd_anti_check start  python -- /data/pdd-spider/script/check_anti_device_list.py
# 检测etag质量
pm2 -n pdd_etag_check start  python -- /data/pdd-spider/script/check_only_device_list.py
# etag 失败重试
pm2 -n pdd_etag_retry_check start  python -- /data/pdd-spider/script/device_register_redo.py

# 属性榜
pm2 -n pdd_billboard_id_consume start python -- /usr/local/bin/scrapy crawl pdd_billboard_id
pm2 -n pdd_sync_mall_order_consume start python -- /usr/local/bin/scrapy crawl pdd_sync_mall_order_list
