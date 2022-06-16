import requests
import re
import json
from tqdm import tqdm

# 爬取网址
current = 'https://bangumi.moe/api/bangumi/current'
search = 'https://bangumi.moe/api/torrent/search/'
fetch_name='https://bangumi.moe/api/tag/fetch/'
current_bangumi_json = './current_bangumi.json'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.39"}


def load_page(url):
    '''
    作用:根据url发送请求，获取服务器响应文件
    url：需要爬取的url地址
    '''
    request = requests.get(url, headers=headers)
    return request


def get_Json(url):
    request = requests.get(url, headers=headers)
    return request.json()


def get_current_bangumi():
    current_bangumi = get_Json(current)
    with open(current_bangumi_json, "w") as file:
        json.dump(current_bangumi, file)


def load_Json(file):
    with open(file, 'r') as file:
        return json.load(file)


def get_torrents():
    bangumi_tag_ids = get_tag_ids()
    for tag_id in tqdm(bangumi_tag_ids):
        data = {"tag_id": [tag_id]}
        res = requests.post(url=search, json=data, headers=headers)
        search_result = res.json()
        torrents = search_result['torrents']
        for i in range(2, search_result['page_count'] + 1):
            data = {"tag_id": [tag_id], 'p': i}
            res = requests.post(url=search, json=data, headers=headers)
            torrents = torrents + res.json()['torrents']
        with open('torrents/' + tag_id + '.json', "w") as file:
            json.dump(torrents, file)


def get_tag_ids():
    current_bangumi = load_Json(current_bangumi_json)
    bangumi_tag_ids = set()
    id2name = dict()
    for bangumi in current_bangumi:
        bangumi_tag_ids.add(bangumi['tag_id'])
        id2name[bangumi['tag_id']] = bangumi['name']
    return bangumi_tag_ids


def get_tag_id2name():
    current_bangumi = load_Json(current_bangumi_json)
    bangumi_tag_ids = set()
    _ids=list()
    id2tag_id=dict()
    tag_id2name = dict()
    for bangumi in current_bangumi:
        bangumi_tag_ids.add(bangumi['tag_id'])
        id2tag_id[bangumi['_id']]=bangumi['tag_id']
        _ids.append(bangumi['_id'])

    data = {"_ids": _ids}
    res = requests.post(url=fetch_name, json=data, headers=headers)
    fetch_results=res.json()
    for fetch in fetch_results:
        id=fetch['_id']
        tag_id2name[id2tag_id[id]] = fetch['name']
    return tag_id2name


if __name__ == "__main__":
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

                ep_num = re.findall("\[\d\d\]", torrent['title'])
                ep_num = ep_num + re.findall("\[\d\dV\d\]", torrent['title'])
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
                                ep_num = int(re.findall("\d\d", ep)[0])
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
                bangumis.append(bangumi)
            pass;

    print(bangumis)