baidu-tieba-crawler
===============

本项目可以抓取百度贴吧的内容，抓取内容包括标题，作者，发布时间和回复数.


## 环境安装

配置好你的Python环境,然后

```bash
$ git clone git@github.com:jasonqiao36/crawler.git
$ cd crawler/baidu_tieba
$ pip install -r requirements.txt
```

大功告成,直接跳到下一节配置和运行.


## 配置和运行

### 编辑spider.py文件

打开文件，直接拉到最后，修改kw和maxpage.

kw代表贴吧名，maxpage代表抓取的页数.

然后保存文件,在终端运行`python spider.py`

### 运行结果

抓取的内容会保存在data.txt文件.
