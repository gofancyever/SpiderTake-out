import requests

import sqlite3
import time


class Meituan:
    page = 0
    delay = 2
    conn = sqlite3.connect('takeout.db')
    cursor = conn.cursor()
    begain = True
    uuid = ''

    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def callback(self, state):
        print('去读成功')
        self.begain = state
        if state:
            print(state)
            time.sleep(self.delay)
            print('开始读取{}'.format(self.page))
            self.send_request(self.callback)

        else:
            print('end')
            self.cursor.close()
            self.conn.close()

    def loadUUID(self, response):
        try:
            self.uuid = response.cookies['w_uuid']
        except:
            self.uuid = ''

    def start(self):
        self.send_request(self.callback)

    def send_request(self, callback):
        # Request (2)
        # POST http://i.waimai.meituan.com/ajax/v6/poi/filter
        try:
            response = requests.post(
                url="http://i.waimai.meituan.com/ajax/v6/poi/filter",
                params={
                    "lat": self.lat,
                    "lng": self.lng,
                    'page_index': self.page,
                    'platform': '3',
                    'partner': '4',
                    'apage': '1',
                    'uuid': self.uuid
                },
                headers={
                    'Host': 'i.waimai.meituan.com',
                    'Connection': 'close',
                    'User-Agent': 'Paw/3.0.14 (Macintosh; OS X/10.12.2) GCDHTTPRequest',
                    'Content-Length': '0',
                    "Cookie": "utm_source=0; w_cid=140402; w_cpy_cn=\"%E5%9F%8E%E5%8C%BA\"; w_cpy=chengqu; w_latlng=36210870,113136890; JSESSIONID=162dsfekzjvvu1xhheciqr7lf8; mtsi-real-ip=114.248.164.216; mtsi-cur-time=\"2017-06-09 10:27:23\"; w_visitid=df8ad014-d60d-498e-bec0-c31a6bca244d; terminal=i; w_utmz=\"utm_campaign=(direct)&utm_source=5000&utm_medium=(none)&utm_content=(none)&utm_term=(none)\"; w_uuid=YGFBavqhy_KMVj4VxVg8MSQcrwBBnzDlOQA0d5mNtqaO6qoKirOkt8Dmd5F7U4tS",
                },
            )

            self.loadUUID(response)
            print('设置uuid{}'.format(self.uuid))
            try:
                json = response.json()
                data = json['data']
                poilist = data['poilist']
                for item in poilist:
                    self.insertData(item)
                    print(item['name'])
                cursor = self.conn.cursor()
                self.conn.commit()
                Meituan.page += 1
                callback(data['poi_has_next_page'])
            except:
                print('===================error==================')
                print(response.content)
                callback(False)

        except requests.exceptions.RequestException:
            print('HTTP Request failed')

    def insertData(self, dict):
        spider_date = time.strftime("%Y-%m-%d", time.localtime())
        self.cursor.execute(
            'INSERT OR IGNORE INTO takeout (spider_date,data_id, mt_poi_id,wm_poi_view_id,name,mt_delivery_time,pic_url,min_price_tip,shipping_fee_tip,distance,latitude,longitude,month_sale_num) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (spider_date, dict['id'], dict['mt_poi_id'], dict['wm_poi_view_id'], dict['name'], dict['mt_delivery_time'],
             dict['pic_url'], dict['min_price_tip'], dict['shipping_fee_tip'], dict['distance'], dict['latitude'],
             dict['longitude'], dict['month_sale_num']))


meituan = Meituan(36.21087, 113.13689)
meituan.delay = 4
meituan.start()
