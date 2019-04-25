import requests
from lxml import html

from utils import get_ua


def fetch(url):
    headers = {'User-Agent': get_ua()}
    r = requests.get(url, headers=headers)
    r.encoding = 'utf8'
    return r.text


def get_main(url):
    """获取所有小说的url"""
    resp = fetch(url)
    root = html.fromstring(resp)
    cates = root.xpath('//div[contains(@class, "index_toplist")]')
    url_list = []

    for cate in cates:
        cate_name = cate.xpath('div[@class="toptab"]/span[1]/text()')[0]
        with open('book_urls.txt', 'a') as f:
            f.write(f'{cate_name}\n')

        book_list = cate.xpath('div/div[@class="topbooks"]//a')
        book_list = list(set(book_list))
        for book in book_list:
            title = book.xpath('text()')[0]
            url = book.xpath('@href')[0]
            url = f'https://www.qu.la{url}'
            url_list.append(url)
            # with open('book_urls.txt', 'a') as f:
            #     f.write(f'{title}: {url}\n')
    return url_list


def get_book_urls(url):
    """获取该小说每一章的url"""
    resp = fetch(url)
    root = html.fromstring(resp)
    book_name = root.xpath('//h1/text()')[0]
    urls = root.xpath('//dd/a[starts-with(@href, "/book")]/@href')
    return urls, book_name


def get_content(url, book_name):
    resp = fetch(url)
    root = html.fromstring(resp)
    chap_title = root.xpath('//div[@class="bookname"]/h1/text()')[0]
    content_list = root.xpath('//div[@id="content"]/text()')
    with open(f'books/{book_name}.txt', 'a') as f:
        f.write(f'{chap_title}\n\n')
        f.write('\n'.join(content_list))
        f.write('\n\n')
        print(f'{book_name} {chap_title}下载完毕')


def main():
    url = 'https://www.qu.la/paihangbang/'
    main_urls = get_main(url)
    for url in main_urls:
        chap_urls, book_name = get_book_urls(url)
        for chap_url in chap_urls:
            chap_url = f'https://www.qu.la{chap_url}'
            get_content(chap_url, book_name)


if __name__ == '__main__':
    main()
