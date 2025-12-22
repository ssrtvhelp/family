# coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import json
import re

try:
    import ujson
except ImportError:
    ujson = json

class Spider(Spider):
    def __init__(self):
        self.host = "https://www.fanxinzhui.com"
        self.header = {
            "Referer": self.host,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def getName(self):
        return "追新番"

    def init(self, extend=""):
        pass

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "最新影视": "list",
            "日剧": "list?channel=tv",
            "电影": "list?channel=movie"
        }
        classes = []
        for k in cateManual:
            classes.append({'type_name': k, 'type_id': cateManual[k]})
        result['class'] = classes
        return result

    def homeVideoContent(self):
        rsp = self.fetch(self.host, headers=self.header)
        doc = self.html(rsp.text)
        videos = []
        items = doc.xpath("//div[@class='resource_recommend']//div[@class='res']")
        for item in items:
            name = item.xpath(".//div[@class='text']/a/text()")[0]
            href = item.xpath(".//div[@class='text']/a/@href")[0]
            pic = item.xpath(".//div[@class='image']//img/@src")[0]
            sid = self.regStr(href, r"/rr/(\d+)")
            videos.append({"vod_id": sid, "vod_name": name, "vod_pic": pic, "vod_remarks": "推荐"})
        return {'list': videos}

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        url = f"{self.host}/{tid}"
        url += f"&p={pg}" if '?' in tid else f"?p={pg}"
        rsp = self.fetch(url, headers=self.header)
        doc = self.html(rsp.text)
        videos = []
        items = doc.xpath("//ul[@class='resource_list']/li")
        for item in items:
            try:
                name = item.xpath(".//dd[@class='cnname']/a/text()")[0]
                href = item.xpath(".//dd[@class='cnname']/a/@href")[0]
                pic = item.xpath(".//dl[@class='image']//img/@src")[0]
                remark = item.xpath(".//dd[@class='remark'][1]/span/text()")
                sid = self.regStr(href, r"/rr/(\d+)")
                videos.append({"vod_id": sid, "vod_name": name, "vod_pic": pic, "vod_remarks": remark[0] if remark else ""})
            except: continue
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 999
        return result

    def detailContent(self, array):
        tid = array[0]
        url = f"{self.host}/rr/{tid}"
        rsp = self.fetch(url, headers=self.header)
        doc = self.html(rsp.text)
        
        title = doc.xpath("//div[@class='resource_title']/h2/text()")[0].strip()
        pic = doc.xpath("//div[@class='image']/a/img/@src")[0]
        
        
        episode_items = doc.xpath("//ul[@class='item_list']/li")
        
        
        episode_items.reverse() 
        
        vodItems = []
        for ep in episode_items:
            
            ep_title_list = ep.xpath(".//span[@class='season']/text()")
            if not ep_title_list: continue
            ep_title = ep_title_list[0].strip()
         
            ways = ep.xpath(".//p[@class='way']/span")
            target_url = ""
            for way in ways:
                
                links = way.xpath(".//a")
                for l in links:
                    l_text = l.xpath("./text()")
                    l_href = l.xpath("./@href")
                    if l_text and "网盘" in l_text[0] and l_href and "baidu.com" in l_href[0]:
                        target_url = l_href[0]
                       
                        pwd_node = way.xpath(".//a[@class='password']/text()")
                        if pwd_node:
                            pwd = pwd_node[0].strip()
                            sep = "&" if "?" in target_url else "?"
                            target_url = f"{target_url}{sep}pwd={pwd}"
                        break
                if target_url: break 
            
            if target_url:
                vodItems.append(f"{ep_title}${target_url}")

        vod = {
            "vod_id": tid,
            "vod_name": title,
            "vod_pic": pic,
            "vod_play_from": "百度网盘",
            "vod_play_url": "#".join(vodItems),
            "vod_content": "".join(doc.xpath("//div[@class='intro_text']/text()")).strip()
        }
        return {'list': [vod]}

    def searchContent(self, key, quick):
        url = f"{self.host}/list?k={key}"
        rsp = self.fetch(url, headers=self.header)
        doc = self.html(rsp.text)
        videos = []
        items = doc.xpath("//ul[@class='resource_list']/li")
        for item in items:
            try:
                name = item.xpath(".//dd[@class='cnname']/a/text()")[0]
                href = item.xpath(".//dd[@class='cnname']/a/@href")[0]
                pic = item.xpath(".//dl[@class='image']//img/@src")[0]
                sid = self.regStr(href, r"/rr/(\d+)")
                videos.append({"vod_id": sid, "vod_name": name, "vod_pic": pic})
            except: continue
        return {'list': videos}

    def playerContent(self, flag, id, vipFlags):
        
        return {
            "parse": 0,
            "playUrl": "",
            "url": f"push://{id}",
            "header": ""
        }

    def regStr(self, input_str, pattern):
        match = re.search(pattern, input_str)
        if match: return match.group(1)
        return ""