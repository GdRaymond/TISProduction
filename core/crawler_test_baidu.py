# coding:utf-8
import urllib
from bs4 import BeautifulSoup
import codecs


def get_contents(url_pre,tag,word=None):
    # 前半部分的链接(注意是http，不是https)
    #url_pre = 'http://www.baidu.com/s'

    # GET参数
    params = {}
    params['pn'] = 20  # 设置这个每页可以获取10个内容

    url = url_pre
    # all str in python 3 is unicode
    if word:
        params['wd'] = word.encode('utf-8')
        url_params = urllib.parse.urlencode(params)
        url = '%s?%s' % (url, url_params)

    # GET请求完整链接


    # 打开链接，获取响应
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)

    # 获取响应的html
    html = response.read()

    # 解析内容
    soup = BeautifulSoup(html, 'lxml')
    items = soup.select(tag)

    # 写入文件
    f = codecs.open('test2.txt', 'w', 'utf-8')
    for item in items:
        print(item)
        f.write('%s\r\n\r\n' % item.header.a['alt'])
        f.write('%s\r\n' % ''.join(item.stripped_strings))
    f.close()


if __name__ == '__main__':
    get_contents('https://www.ritemate.com.au/products/category/PWYSCWMS-short-sleeve','.products .product')
    get_contents('https://www.realestate.com.au/rent/in-qld+4131/list-1','#searchResultsTb1 article')