from .utils import get_tree, create_randomString, fetch
from urllib.parse import quote
import json

SINGER_LIST_URL = 'https://u.y.qq.com/cgi-bin/musicu.fcg?-=getUCGI6848326043520538&g_tk=5381&loginUin=0&hostUin=0&format=json' \
                  '&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0&' \
                  'data=%7B%22comm%22%3A%7B%22ct%22%3A24%2C%22cv%22%3A0%7D%2C%22singerList%22%3A%7B%22' \
                  'module%22%3A%22Music.SingerListServer%22%2C%22method%22%3A%22get_singer_list%22%2C%22' \
                  'param%22%3A%7B%22area%22%3A-100%2C%22sex%22%3A-100%2C%22genre%22%3A-100%2C%22index%22%3A-100%2C%22' \
                  'sin%22%3A{sin}%2C%22cur_page%22%3A{cur_page}%7D%7D%7D'

ARTIST_URL = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?g_tk=5381&loginUin=0&hostUin=0&format=json&' \
             'inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&ct=24&singermid={}&' \
             'order=listen&begin=0&num=10'

COMMENT_URL = 'https://c.y.qq.com/base/fcgi-bin/fcg_global_comment_h5.fcg?g_tk=5381&loginUin=0&hostUin=0&format=json' \
              '&inCharset=utf8&outCharset=GB2312&notice=0&platform=yqq.json&needNewCode=0&cid=205360772&reqtype=2&' \
              'biztype=1&topid={}&cmd=8&needmusiccrit=0&pagenum=0&pagesize=25&lasthotcommentid=&' \
              'domain=qq.com&ct=24&cv=10101010'


def parse_artist_list(page):
    resp = fetch(SINGER_LIST_URL.format(sin=(page - 1) * 80, cur_page=page))
    resp_dict = resp.json()
    singer_list = resp_dict['singerList']['data']['singerlist']
    return [singer['singer_mid'] for singer in singer_list]


def parse_artist(singer_mid):
    resp = fetch(ARTIST_URL.format(singer_mid))
    resp_dict = resp.json()
    song_list = resp_dict['data']['list']
    for song in song_list:
        songmid = song['musicData']['songmid']
        songid = song['musicData']['songid']
        parse_song(songmid, songid)


def parse_song(songmid, songid):
    resp = fetch(COMMENT_URL.format(songid))
    resp_dict = resp.json()
    commentlist = resp_dict['hot_comment']['commentlist']
    print(commentlist[0]['rootcommentcontent'])
    print(commentlist[0]['rootcommentcontent'])