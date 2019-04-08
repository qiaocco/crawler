import os

PROXIES = []
TIMEOUT = 3

HERE = os.path.abspath(os.path.dirname(__file__))
FAKE_USERAGENT_PATH = os.path.join(HERE, 'data/fake_useragent.json')
