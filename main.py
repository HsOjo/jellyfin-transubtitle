import base64
import os
import re
import time
from datetime import datetime
from io import StringIO
from typing import List, Dict

import ass
import requests
from dotenv import load_dotenv
from requests import Response

from Baidu_Text_transAPI import BaiduTextTransAPI

load_dotenv()

USER_NAME = os.getenv("USER_NAME")
BASE_URI = os.getenv("BASE_URI")
API_TOKEN = os.getenv("API_TOKEN")
JELLYFIN_TARGET_LANG = os.getenv("JELLYFIN_TARGET_LANG")
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL"))

btt_api = BaiduTextTransAPI(
    os.getenv('BAIDU_APP_ID'),
    os.getenv('BAIDU_APP_KEY'),
    'auto',
    os.getenv('BAIDU_TARGET_LANG'),
)


def jellyfin(path, method='get', **kwargs) -> 'Response':
    return getattr(requests, method)(
        f'{BASE_URI}/{path}',
        headers={'X-MediaBrowser-Token': API_TOKEN},
        **kwargs
    )


users = jellyfin('Users').json()  # type: List[dict]
users_name_mapping = {user.get('Name'): user for user in users}  # type: Dict[str, dict]
user_id = users_name_mapping.get(USER_NAME).get('Id')


def scan(FOLDER_ID=None, callback=None):
    resp = jellyfin(f'Users/{user_id}/Items', params=dict(
        Fields='Path', ParentId=FOLDER_ID
    )).json()  # type: dict
    items = resp.get('Items')
    for item in items:
        item: dict
        if item.get('IsFolder'):
            print(datetime.now(), '- scanning:', item.get('Name'))
            scan(item.get('Id'), callback)
        else:
            item = jellyfin(f'Users/{user_id}/Items/{item.get("Id")}').json()  # type: dict
            if item.get('HasSubtitles'):
                if callback:
                    callback(item)


def translate_ass(content: str, progress_title='Translating...'):
    doc = ass.parse_string(content)

    for style in doc.styles:
        style.fontname = 'FZZhengHei-M-GBK'

    tag_strs = []
    texts = []
    for event in doc.events:
        text = event.text
        tags = re.findall(r'\{.+?\}', text)
        tag_str = ''.join(tags)
        for tag in tags:
            text = text.replace(tag, '')
        text = text.replace(r'\N', '\n')
        text = re.sub(r'\s+', ' ', text)

        tag_strs.append(tag_str)
        texts.append(text)

    trans = btt_api.translate_s(
        texts, callback_progress=lambda now, end: print(
            f'\r[{int(now / end * 100)}%] {progress_title}',
            end='' if now < end else '\n'
        ))

    for index, event in enumerate(doc.events):
        event.text = tag_strs[index] + trans[index]

    with StringIO() as io:
        doc.dump_file(io)
        io.seek(0)
        result = io.read()

    return result


def translate_subtitle(item: dict):
    item_id = item.get('Id')
    item_name = item.get('Name')
    streams = item.get('MediaStreams')  # type: List[dict]

    # Ass format subtitle support only current.
    streams = list(filter(
        lambda stream: (stream.get('Type') == 'Subtitle' and stream.get('Codec') == 'ass'), streams
    ))

    langs = set(map(lambda stream: stream.get('Language'), streams))
    if JELLYFIN_TARGET_LANG in langs:
        return

    for stream in streams:
        index = stream.get('Index')
        resp = jellyfin(f'Videos/{item_id}/{item_id}/Subtitles/{index}/Stream.ass')
        content = resp.content.decode('utf-8')
        content = translate_ass(content, progress_title=item_name)
        jellyfin(f'Videos/{item_id}/Subtitles', method='post', json=dict(
            data=base64.b64encode(content.encode('utf-8')).decode(),
            format='ass',
            isForced=False,
            language=JELLYFIN_TARGET_LANG,
        ))


try:
    while True:
        scan(callback=translate_subtitle)
        time.sleep(SCAN_INTERVAL)
except KeyboardInterrupt:
    pass
