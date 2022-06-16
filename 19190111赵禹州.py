import requests
import re
import json


# 爬取网址

def load_page(url):
    '''
    作用:根据url发送请求，获取服务器响应文件
    url：需要爬取的url地址
    '''
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.39"}
    request = requests.get(url, headers=headers)
    return request

if __name__ == "__main__":
    url='https://bangumi.moe/api/torrent/latest'
    response=load_page(url)
    text= response.text
    torrents= re.findall('\[.*\]',text);

    torrents=json.loads(text)['torrents']
    for torrent in torrents:
        print(torrent['title']+torrent['magnet'])
    print(torrents)
