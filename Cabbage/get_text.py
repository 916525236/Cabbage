
import bs4
import requests
from bs4 import BeautifulSoup as be

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cookie": "UM_distinctid=177b930f83ea0c-0ab19b982e9d0b-53e3566-1fa400-177b930f83f9dd; CNZZDATA1262370505=593324983-1613715709-null%7C1613715709; PPad_id_PP=1; 37cs_pidx=1; 37cs_user=37cs16928664664; bcolor=; font=; size=; fontcolor=; width=; 37cs_show=253; cscpvrich9180_fidx=1",
    # "Referer": "http://www.paoshuzw.com/modules/article/waps.php",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Proxy-Connection": "keep-alive",
    "Host": "www.paoshuzw.com",
    "Referer": "https://www.vbiquge.com/search.php?keyword=%E5%A4%A7%E6%A2%A6%E4%B8%BB"
}
# base_url = "http://www.paoshuzw.com"
base_url = "https://www.vbiquge.com/"


def get_mulu():
    # 获取章节目录
    r = requests.get(base_url + "/95_95114/").content.decode("UTF-8")
    soup = be(r, features="lxml")
    for i in soup.find_all("a"):
        if "href" in i.attrs.keys():
            if "第" in i.string and i.string not in page_list.keys():
                page_list[i.string.replace("\xa0", " ")] = i.attrs["href"]
    print(page_list)


def get_text(page):
    Page = page_list[page]
    Down_page = read_text(Page)
    is_continue = "y"
    while is_continue == "y" or "第" in is_continue:
        if is_continue == "y":
            Down_page = read_text(Down_page)
        if "第" in is_continue:
            Down_page = read_text(page_list[is_continue])
        if not Down_page:
            break
        is_continue = input("continue? :")


def read_text(path):
    down_page = ""
    if path in page_list.values():
        print(list(page_list.keys())[list(page_list.values()).index(path)])
        r = requests.get(base_url + path).content.decode("UTF-8")
        soup = be(r, features="lxml")
        for i in soup.find_all("div", id="content"):
            for m in i.contents:
                if type(m) == bs4.element.NavigableString and len(m) > 1:
                    for x in cut(m, 100):
                        print(x)
                    input()
        for i in soup.find_all("div", class_="bottem1"):
            for m in i.children:
                if m.string == "下一章":
                    down_page = m.attrs["href"]
        if len(down_page) <= 1:
            down_page = page_list[list(page_list.keys())[list(page_list.values()).index(path)]]
        return down_page
    else:
        print("input error")


def get_next_page():
    pass


def cut(obj, sec):
    return [obj[i:i + sec] for i in range(0, len(obj), sec)]


if __name__ == '__main__':
    page_list = {}  # 章节目录
    global down_page
    down_page = ""
    get_mulu()
    page = input()
    page_index = list(page_list)
    get_text(page=page)
