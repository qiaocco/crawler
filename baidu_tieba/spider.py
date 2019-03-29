import logging
import queue
import threading
from urllib.parse import quote, urljoin

import requests
import utils
from lxml import html

logging.basicConfig(filename='baidu.log', level=logging.INFO)

# Numbers of downloading threads concurrently
THREADS = 10


def get_post_urls(q, kw, maxpage):
    for page in range(maxpage):
        # print(f'crawler page {page}')
        url = f'https://tieba.baidu.com/f?kw={quote(kw)}&ie=utf-8&pn={page * 50}'
        resp = requests.get(url)
        root = html.fromstring(resp.content)
        article_url_list = root.xpath('//div[contains(@class, "threadlist_title")]//a/@href')
        # print(article_url_list)
        for url in article_url_list:
            print(url)
            q.put(url)


def get_post_detail(q):
    while not q.empty():
        post_dict = utils.Attrdict()
        url = q.get()
        base_url = 'https://tieba.baidu.com'
        full_url = urljoin(base_url, url)
        resp = requests.get(full_url)
        root = html.fromstring(resp.text)
        post_dict['title'] = root.xpath('//h3[contains(@class, "core_title_txt")]/text()')[0]
        post_dict['author'] = root.xpath('//a[contains(@class, "p_author_name")]')[0].text
        post_dict['pubdate'] = root.xpath('//div[@class="post-tail-wrap"]/span[last()]/text()')[0]
        post_dict['replynum'] = \
            root.xpath('//ul[@class="l_posts_num"]')[0].xpath('//li[@class="l_reply_num"]//span')[2].text
        print(post_dict)
        write2file(post_dict)
        q.task_done()


def write2file(post_dict):
    lock = threading.Lock()
    with lock:
        with open('data.txt', 'a+') as f:
            f.write(
                f'title:{post_dict.title}, author:{post_dict.author}, pubdate:{post_dict.pubdate}, replynum:{post_dict.replynum}\n')


def main(kw, maxpage):
    urls_queue = queue.Queue()
    get_urls_thread = threading.Thread(target=get_post_urls, args=(urls_queue, kw, maxpage))
    get_urls_thread.start()
    get_urls_thread.join()

    thread_list = []
    for i in range(THREADS):
        t = threading.Thread(target=get_post_detail, args=(urls_queue,))
        t.daemon = True
        t.start()
        thread_list.append(t)

    urls_queue.join()

    print('finished!')


if __name__ == '__main__':
    kw = '金庸'
    maxpage = 10
    main(kw, maxpage)
