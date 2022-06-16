import requests
import re
import json
import pandas as pd
import numpy as np
from tqdm import tqdm

# 爬取网址
current = 'https://bangumi.moe/api/bangumi/current'#目前的连载动画
search = 'https://bangumi.moe/api/torrent/search/'#搜索页面，使用post+id的方式获取搜索结果
fetch_name='https://bangumi.moe/api/tag/fetch/'#获取番剧具体信息
current_bangumi_json = './current_bangumi.json'#存放目前的连载动画
bangumi_info_json='./bangumi_info.json'#存储具体信息
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.39"}


def load_page(url):
    '''
    作用:根据url发送请求，获取服务器响应文件
    url：需要爬取的url地址
    '''
    request = requests.get(url, headers=headers)
    return request


def get_Json(url):#获取json对象
    request = requests.get(url, headers=headers)
    return request.json()


def get_current_bangumi():#获取当前番剧列表
    current_bangumi = get_Json(current)
    with open(current_bangumi_json, "w") as file:
        json.dump(current_bangumi, file)


def load_Json(file):#加载json文件
    with open(file, 'r',encoding='UTF-8') as file:
        return json.load(file)


def get_torrents():#搜索全部种子数据
    bangumi_tag_ids = get_tag_ids()
    for tag_id in tqdm(bangumi_tag_ids):
        data = {"tag_id": [tag_id]}
        res = requests.post(url=search, json=data, headers=headers)#post数据
        search_result = res.json()
        torrents = search_result['torrents']
        for i in range(2, search_result['page_count'] + 1):#翻页post
            data = {"tag_id": [tag_id], 'p': i}
            res = requests.post(url=search, json=data, headers=headers)
            torrents = torrents + res.json()['torrents']
        with open('torrents/' + tag_id + '.json', "w") as file:
            json.dump(torrents, file)


def get_tag_ids():#获取番剧id列表
    current_bangumi = load_Json(current_bangumi_json)
    bangumi_tag_ids = set()
    id2name = dict()
    for bangumi in current_bangumi:
        bangumi_tag_ids.add(bangumi['tag_id'])
        id2name[bangumi['tag_id']] = bangumi['name']
    return bangumi_tag_ids


def get_tag_id2name():#获取番剧名字
    bangumi_info = load_Json(bangumi_info_json)
    tag_id2name=dict()
    for bangumi in bangumi_info:
        if bangumi['locale'].__contains__('zh_cn'):
            tag_id2name[bangumi['_id']]=bangumi['locale']['zh_cn']
        else:
            tag_id2name[bangumi['_id']]=bangumi['name']
    return tag_id2name

def get_popularities():#统计下载量以及完成数
    # get_torrents()
    tag_ids = get_tag_ids()
    id2name = get_tag_id2name()
    bangumis=list()
    for tag_id in tag_ids:
        with open('torrents/' + tag_id + '.json', 'r') as file:
            torrents = json.load(file)
            downloads = [0] * 50
            finished = [0] * 50
            bangumi = dict()
            for torrent in torrents:
                #匹配集数信息
                ep_num = re.findall("\[\d\d\]", torrent['title'])
                ep_num = ep_num + re.findall("\[\d\dV\d\]", torrent['title'])
                ep_num = ep_num + re.findall("\[\d\]", torrent['title'])
                ep_num = ep_num + re.findall("\[\d\dv\d\]", torrent['title'])
                ep_num = ep_num + re.findall("\[\d\dEND\]", torrent['title'])
                ep_num = ep_num + re.findall("\s\d\d\s", torrent['title'])
                ep_num = ep_num + re.findall("【\d\dV2】", torrent['title'])
                ep_num = ep_num + re.findall("【\d\dv2】", torrent['title'])
                ep_num = ep_num + re.findall("【\d\d】", torrent['title'])
                ep_num = ep_num + re.findall("第\d\d話", torrent['title'])
                ep_num = ep_num + re.findall("-\s*\d\d", torrent['title'])
                ep_num = ep_num + re.findall("第\d\d话", torrent['title'])
                ep_num = ep_num + re.findall("第\d\d集", torrent['title'])

                if len(ep_num) == 0:
                    print("no match:" + torrent['title'])
                else:
                    try:
                        for ep in ep_num:
                            if str.strip(ep)!="":
                                ep_num = int(re.findall("\d\d?", ep)[0])
                                break
                        downloads[int(ep_num)] += torrent['downloads']
                        finished[int(ep_num)] += torrent['finished']
                    except IndexError or TypeError:
                        print(ep_num)
                        print(torrent['title'])
                        print(tag_id)

            bangumi['tag_id'] = tag_id;
            bangumi['downloads'] = downloads
            bangumi['finished'] = finished
            bangumi['name'] = id2name[tag_id]

            with open('result/' + tag_id + '.json', 'w') as fp:
                fp.write(json.dumps(bangumi))
                bangumis.append(bangumi)#写入
            pass;
    return bangumis

if __name__ == "__main__":
    bangumis=get_popularities()
    data=list()
    label=['序号','标题']+[str(i)+'集下载量' for i in range(1,50)]+[str(i)+'集完成量' for i in range(1,50)]
    for bangumi in bangumis:
        tmp=list()
        tmp.append(bangumi['name'])
        tmp+=bangumi['downloads'][1:]
        tmp+=bangumi['finished'][1:]
        data.append(tmp)
    pass
    data=pd.DataFrame(data)
    data.to_csv('popularity.csv',encoding="gbk",index_label=label)
    print(data)