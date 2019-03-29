import base64
import binascii
import json
import logging
import os
import queue
import random
import re
import sys
import threading
import time
from urllib.parse import urlparse

import requests
from utils import get_ua, get_proxy, sleep_random

# Numbers of downloading threads concurrently
THREADS = 5

# Retry times
RETRY = 5

FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
LOG_FILENAME = 'toutiao.log'
logging.basicConfig(
    filename=LOG_FILENAME,
    format=FORMAT,
    level=logging.INFO
)


class DownloadWorker(threading.Thread):
    def __init__(self, queue, proxies=None):
        super().__init__()
        self.queue = queue
        self.headers = {'User-Agent': get_ua()}
        self.proxies = proxies

    def run(self):
        while True:
            title, video_page_url, target_folder = self.queue.get()
            self.download(title, video_page_url, target_folder)
            self.queue.task_done()
            sleep_random(1, 3)

    def download(self, title, video_page_url, target_folder):
        vid = self.get_video_vid(video_page_url)
        signed_video_url = self.sign_video_url(vid)
        video_url = self.get_real_video_url(signed_video_url)
        self._download(video_url, title, target_folder)

    def _download(self, video_url, title, target_folder):
        video_name = title + '.mp4'
        file_path = os.path.join(target_folder, video_name)
        if not os.path.isfile(file_path):
            print(f"Downloading {video_name} from {video_url}.\n")
            retry_times = 0
            while retry_times < RETRY:
                try:
                    resp = requests.get(video_url, proxies=self.proxies, headers=self.headers)
                    if resp.status_code == 403:
                        retry_times = RETRY
                        print(f"Access Denied when retrieve {video_url}.\n")
                        raise Exception("Access Denied")
                    with open(file_path, 'wb') as f:
                        for chunk in resp.iter_content(chunk_size=1024):
                            f.write(chunk)
                    break
                except Exception as e:
                    logging.exception(f'Down error {e}', exc_info=True)
                finally:
                    retry_times += 1

    def get_video_vid(self, video_page_url):
        try:
            resp = requests.get(video_page_url, headers=self.headers, proxies=self.proxies)
            return re.search(".*?videoId: '(?P<vid>.*)'", resp.text).group('vid')
        except AttributeError:
            print('Unable to parse videoId')

    def random_with_n_digits(self, n):
        return random.randint(10 ** (n - 1), (10 ** n) - 1)

    def sign_video_url(self, vid):
        r = str(self.random_with_n_digits(16))

        url = 'https://ib.365yg.com/video/urls/v/1/toutiao/mp4/{vid}'.format(vid=vid)
        n = urlparse(url).path + '?r=' + r
        b_n = bytes(n, encoding="utf-8")
        s = binascii.crc32(b_n)
        aid = 1364
        ts = int(time.time() * 1000)
        return url + f'?r={r}&s={s}&aid={aid}&vfrom=xgplayer&callback=axiosJsonpCallback1&_={ts}'

    def get_real_video_url(self, video_url):
        resp = requests.get(video_url, proxies=self.proxies, headers=self.headers)
        resp_dict = json.loads(resp.text[20:-1])
        b64_url = resp_dict['data']['video_list']['video_1']['main_url']
        return base64.b64decode(b64_url).decode()


class CrawlerScheduler:
    def __init__(self, sites, proxies=None):
        self.sites = sites
        self.proxies = proxies
        self.headers = {'User-Agent': get_ua()}
        self.queue = queue.Queue()
        self.scheduling()

    def scheduling(self):
        for i in range(THREADS):
            worker = DownloadWorker(queue=self.queue, proxies=self.proxies)
            worker.daemon = True
            worker.start()

        for site in self.sites:
            self.get_video_page_urls(site)

    def get_video_page_urls(self, site):
        """从视频列表获取每个视频页的url"""
        self._get_video_page_urls(site)
        self.queue.join()
        print(f"Finish Downloading All the videos from {site}")

    def _get_video_page_urls(self, site):
        current_folder = os.getcwd()
        target_folder = os.path.join(current_folder, site)
        if not os.path.isdir(target_folder):
            os.mkdir(target_folder)

        base_url = 'https://www.365yg.com/c/user/article/?user_id={user_id}&max_behot_time={max_behot_time}' \
                   '&max_repin_time=0&count=20&page_type=0'
        max_behot_time = 0
        while True:
            url = base_url.format(user_id=site, max_behot_time=max_behot_time)
            logging.info(url)
            resp = requests.get(url, headers=self.headers, proxies=self.proxies)
            if resp.status_code == 404:
                print(f'Site {site} does not exist')
                break

            resp_json = resp.json()
            video_list = resp_json.get('data')
            for video in video_list:
                title = video.get('title')
                source_url = video.get('source_url')
                media_url = video.get('media_url')
                video_page_url = f'https://www.365yg.com/i{source_url.split("/")[2]}/#mid={media_url[2:-1]}'
                print(video_page_url)
                self.queue.put((title, video_page_url, target_folder))
                sleep_random(1, 3)

            if resp_json.get('has_more'):
                max_behot_time = resp_json['next']['max_behot_time']
            else:
                break


def parse_sites(filename):
    with open(filename, 'r') as f:
        raw_sites = f.read().lstrip().rstrip()

    raw_sites = raw_sites.replace('\n', ',') \
        .replace('\r', ',') \
        .replace('\t', ',') \
        .replace(' ', ',')
    raw_sites = raw_sites.split(',')

    sites = list()
    for site in raw_sites:
        site = site.lstrip().rstrip()
        if site:
            sites.append(site)
    return sites


def usage():
    print(u"未找到sites.txt文件，请创建.\n"
          u"请在文件中指定Tumblr站点名，并以 逗号/空格/tab/表格鍵/回车符 分割，支持多行.\n"
          u"保存文件并重试.\n\n"
          u"例子: site1,site2\n\n"
          u"或者直接使用命令行参数指定站点\n"
          u"例子: python tumblr-photo-video-ripper.py site1,site2")


if __name__ == '__main__':
    cur_dir = os.path.dirname(os.path.realpath(__file__))

    filename = os.path.join(cur_dir, "sites.txt")
    if os.path.exists(filename):
        sites = parse_sites(filename)
    else:
        usage()
        sys.exit(1)

    CrawlerScheduler(sites)
