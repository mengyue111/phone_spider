#!/usr/bin/env bash


pm2 -n live_monitor_room_with_mall start  python -- /data/pdd-spider/mq_push/pdd_live_monitor_room_with_mall_push.py

pm2 -n live_monitor_room_with_user start  python -- /data/pdd-spider/mq_push/pdd_live_monitor_room_with_user_push.py

pm2 -n live_monitor_room_with_promotion start  python -- /data/pdd-spider/mq_push/pdd_live_monitor_room_with_promotion_push.py

pm2 -n live_monitor_goods_map_room start  python -- /data/pdd-spider/mq_push/pdd_live_goods_map_room_push.py

pm2 -n live_monitor_user_detail start  python -- /data/pdd-spider/mq_push/pdd_live_monitor_user_detail_push.py
