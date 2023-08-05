# -*- coding: utf-8 -*-

# This code shows an example of text translation from English to Simplified-Chinese.
# This code runs on Python 2.7.x and Python 3.x.
# You may install `requests` to run this code: pip install requests
# Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document

import random
import time
from hashlib import md5
from typing import List

import requests


class BaiduTextTransAPI:
    def __init__(self, appid, appkey, from_lang='en', to_lang='zh'):
        # Set your own appid/appkey.
        self.appid = appid
        self.appkey = appkey

        # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
        self.from_lang = from_lang
        self.to_lang = to_lang

        endpoint = 'http://api.fanyi.baidu.com'
        path = '/api/trans/vip/translate'
        self.url = endpoint + path

    def translate(self, query: str):
        # Generate salt and sign
        def make_md5(s, encoding='utf-8'):
            return md5(s.encode(encoding)).hexdigest()

        salt = random.randint(32768, 65536)
        sign = make_md5(self.appid + query + str(salt) + self.appkey)

        # Build request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': self.appid, 'q': query, 'from': self.from_lang, 'to': self.to_lang, 'salt': salt,
                   'sign': sign}

        # Send request
        r = requests.post(self.url, params=payload, headers=headers)
        return r.json()

    def translate_s(self, texts: List[str], callback_progress=None):
        tl = len(texts)
        items = set(texts)
        mapping = {}
        while items:
            content = ''
            for item in items:
                if len(content) + len(item) >= 6000:
                    break
                content += item + '\n\n'

            resp = self.translate(content)  # type: dict
            result = resp.get('trans_result')  # type: List[dict]

            if not result:
                raise Exception(resp)

            for item in result:
                src = item.get('src')
                if src not in items:
                    continue
                mapping[src] = item.get('dst')
                items.remove(src)

            time.sleep(1)
            if callback_progress:
                il = len(items)
                callback_progress(tl - il, tl)

        if callback_progress:
            callback_progress(tl, tl)

        return list(map(lambda text: mapping[text], texts))
