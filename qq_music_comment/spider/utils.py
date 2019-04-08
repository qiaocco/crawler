import random

import requests
from fake_useragent import UserAgent
from lxml import etree
import string

from config import PROXIES, TIMEOUT, FAKE_USERAGENT_PATH


def choice_proxy():
    if PROXIES:
        return random.choice(PROXIES + [''])
    return ''


def get_user_agent():
    ua = UserAgent(path=FAKE_USERAGENT_PATH)
    return ua.random


def fetch(url, retry=0):
    s = requests.Session()
    proxies = {
        'http': choice_proxy()
    }
    s.headers.update({
        'User-Agent': get_user_agent()
    })
    try:
        return s.get(url, timeout=TIMEOUT, proxies=proxies)
    except requests.exceptions.RequestException:
        if retry < 3:
            fetch(url, retry=retry + 1)
        raise


def get_tree(url):
    resp = fetch(url)
    return etree.HTML(resp.text)


def create_randomString(stringLength):
    return ''.join(random.choice(string.digits) for i in range(stringLength))
