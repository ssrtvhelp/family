# -*- coding: utf-8 -*-
import json
import requests
from urllib.parse import quote

class Spider:
    def __init__(self):
        self.name = '酷我听书'
        self.host = 'http://tingshu.kuwo.cn'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S901U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36'
        }
        self.classes = [
            {"type_name": "有声小说", "type_id": "2"},
            {"type_name": "相声评书", "type_id": "5"},
            {"type_name": "音乐", "type_id": "37"},
            {"type_name": "影视原声", "type_id": "62"},
            {"type_name": "人文社科", "type_id": "4"},
            {"type_name": "历史人文", "type_id": "9"},
        ]

        # ========== ① 只加这里：筛选定义 ==========
        self.filter_def = {
            "2": [{"key": "class", "name": "类型", "value": [
                {"n": "玄幻奇幻", "v": "44"}, {"n": "武侠仙侠", "v": "48"}, {"n": "穿越架空", "v": "52"},
                {"n": "都市传说", "v": "42"}, {"n": "科幻竞技", "v": "57"}, {"n": "幻想言情", "v": "169"},
                {"n": "独家定制", "v": "170"}, {"n": "古代言情", "v": "207"}, {"n": "影视原著", "v": "213"},
                {"n": "悬疑推理", "v": "45"}, {"n": "历史军事", "v": "56"}, {"n": "现代言情", "v": "41"},
                {"n": "青春校园", "v": "55"}, {"n": "文学名著", "v": "61"}
            ]}],
            "5": [{"key": "class", "name": "类型", "value": [
                {"n": "相声新人", "v": "222"}, {"n": "张少佐", "v": "313"}, {"n": "刘立福", "v": "314"},
                {"n": "评书大全", "v": "220"}, {"n": "小品合辑", "v": "221"}, {"n": "刘兰芳", "v": "309"},
                {"n": "连丽如", "v": "311"}, {"n": "田占义", "v": "317"}, {"n": "单口相声", "v": "219"},
                {"n": "袁阔成", "v": "310"}, {"n": "孙一", "v": "315"}, {"n": "王玥波", "v": "316"},
                {"n": "单田芳", "v": "217"}, {"n": "热门相声", "v": "218"}, {"n": "相声名家", "v": "290"},
                {"n": "粤语评书", "v": "320"}, {"n": "关永超", "v": "325"}, {"n": "马长辉", "v": "326"},
                {"n": "赵维莉", "v": "327"}, {"n": "单口相声", "v": "1536"}, {"n": "潮剧", "v": "1718"},
                {"n": "沪剧", "v": "1719"}, {"n": "晋剧", "v": "1720"}
            ]}],
            "37": [{"key": "class", "name": "类型", "value": [
                {"n": "抖音神曲", "v": "253"}, {"n": "怀旧老歌", "v": "252"}, {"n": "创作翻唱", "v": "248"},
                {"n": "催眠", "v": "254"}, {"n": "古风", "v": "255"}, {"n": "博客周刊", "v": "1423"},
                {"n": "民谣", "v": "1409"}, {"n": "纯音乐", "v": "1408"}, {"n": "3D电音", "v": "1407"},
                {"n": "音乐课程", "v": "1380"}, {"n": "音乐推荐", "v": "250"}, {"n": "音乐故事", "v": "247"},
                {"n": "情感推荐", "v": "246"}, {"n": "儿童音乐", "v": "249"}
            ]}],
            "62": [{"key": "class", "name": "类型", "value": [
                {"n": "影视广播剧", "v": "1485"}, {"n": "影视解读", "v": "1483"}, {"n": "影视原著", "v": "1486"},
                {"n": "陪你追剧", "v": "1398"}, {"n": "经典原声", "v": "1482"}
            ]}],
            "4": [{"key": "class", "name": "类型", "value": []}],
            "9": [{"key": "class", "name": "类型", "value": []}]
        }

    # ------------------- 框架接口 -------------------
    def getDependence(self): return ['requests']
    def getName(self): return self.name
    def init(self, extend=""): pass
    def isVideoFormat(self, url): return False
    def manualVideoCheck(self): pass

    # ========== ② 把 filters 带回去 ==========
    def homeContent(self, filter):
        return {"class": self.classes, "filters": self.filter_def}

    def homeVideoContent(self): return self.categoryContent("37", "1", False, {})

    # ------------------- 分类（原逻辑一字不改，只加 3 行筛选） -------------------
    def categoryContent(self, tid, pg, filter, extend):
        url = f"{self.host}/tingshu/api/filter/albums"
        params = {
            "sortType": "playCnt",
            "rn": "21",
            "categoryId": tid,
            "pn": pg
        }
        # ========== ③ 解析 extend 并塞入 classfyId ==========
        class_val = ""
        if extend:
            try:
                if isinstance(extend, dict):
                    class_val = extend.get("class", "") or extend.get("subCategoryId", "")
                elif isinstance(extend, str):
                    class_val = extend
            except Exception:
                pass
        if class_val:
            params["classifyId"] = class_val

        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=10)
            r.raise_for_status()
            data = r.json().get("data", {})
            items = data.get("data", [])
            videos = []
            for item in items:
                album_id = item.get("albumId", "")
                link = f"http://search.kuwo.cn/r.s?stype=albuminfo&albumid={album_id}&pn=0&rn=5000&show_copyright_off=1&vipver=MUSIC_8.2.0.0_BCS17&mobi=1&iskwbook=1"
                videos.append({
                    "vod_id": link,
                    "vod_name": item.get("albumName", "").strip(),
                    "vod_pic": item.get("coverImg", ""),
                    "vod_remarks": item.get("title", "")
                })
            total = data.get("total", 0)
            pagecount = (total + 20) // 21
            return {"list": videos, "page": int(pg), "pagecount": pagecount, "limit": 21, "total": total}
        except Exception as e:
            print(f"[categoryContent error] {e}")
            return self._page([], pg)

    # ------------------- 搜索 -------------------
    def searchContent(self, key, quick, pg='1'):
        url = "http://search.kuwo.cn/r.s"
        params = {
            "client": "kt",
            "all": key,
            "ft": "album",
            "newsearch": "1",
            "pn": str(int(pg) - 1),
            "rn": "21",
            "rformat": "json",
            "encoding": "utf8",
            "show_copyright_off": "1",
            "vipver": "MUSIC_8.0.3.0_BCS75",
            "show_series_listen": "1",
            "version": "9.1.8.1"
        }
        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            videos = []
            for item in data.get("albumlist", []):
                album_id = item.get("DC_TARGETID", "")
                link = f"http://search.kuwo.cn/r.s?stype=albuminfo&albumid={album_id}&pn=0&rn=5000&show_copyright_off=1&vipver=MUSIC_8.2.0.0_BCS17&mobi=1&iskwbook=1"
                videos.append({
                    "vod_id": link,
                    "vod_name": item.get("name", ""),
                    "vod_pic": item.get("img", ""),
                    "vod_remarks": ""
                })
            return {"list": videos, "page": int(pg), "pagecount": 999, "limit": 21, "total": 999999}
        except Exception as e:
            print(f"[searchContent error] {e}")
            return self._page([], pg)

    # ------------------- 详情 -------------------
    def detailContent(self, array):
        vod_url = array[0]
        try:
            r = requests.get(vod_url, headers=self.headers, timeout=10)
            r.raise_for_status()
            data = r.json()
            album = data.get("data", {})
            music_list = data.get("musiclist", [])
            play_urls = []
            for music in music_list:
                name = music.get("name", "")
                rid = music.get("musicrid", "").replace("MUSIC_", "")
                play_url = f"http://mobi.kuwo.cn/mobi.s?f=web&source=kwplayerhd_ar_4.3.0.8_tianbao_TA1_qirui.apk&type=convert_url_with_sign&rid={rid}&br=320kmp3"
                play_urls.append(f"{name}${play_url}")
            vod = {
                "vod_id": vod_url,
                "vod_name": album.get("albumName", "酷我听书"),
                "vod_pic": album.get("coverImg", ""),
                "vod_content": album.get("title", ""),
                "vod_play_from": "酷我听书",
                "vod_play_url": "#".join(play_urls)
            }
            return {"list": [vod]}
        except Exception as e:
            print(f"[detailContent error] {e}")
            return {"list": []}

    # ------------------- 播放 -------------------
    def playerContent(self, flag, id, vipFlags):
        try:
            r = requests.get(id, headers=self.headers, timeout=10)
            r.raise_for_status()
            real_url = r.json().get("data", {}).get("url", "")
            if real_url:
                return {"parse": 0, "playUrl": "", "url": real_url, "header": self.headers}
            return {"parse": 0, "playUrl": "", "url": id, "header": self.headers}
        except Exception as e:
            print(f"[playerContent error] {e}")
            return {"parse": 0, "playUrl": "", "url": id, "header": self.headers}

    # ------------------- 工具 -------------------
    def _page(self, videos, pg):
        return {"list": videos, "page": int(pg), "pagecount": 9999, "limit": 21, "total": 999999}

    config = {"player": {}, "filter": {}}
    header = property(lambda self: self.headers)

    def localProxy(self, param):
        return {}
