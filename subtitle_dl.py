#!/usr/bin/env python3

import os
import collections
from time import sleep
import  zipfile
import requests
from requests.compat import urljoin
from lxml import html
from heading import banners


# SEARCH = "the+blacklist"
DOMAIN = "https://subscene.com/"
BASE_URL = "https://subscene.com/subtitles/title"
HEADERS = {"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0"}


# def search_term():
#     term = input("\n\nEnter to search for subtitles (Eg:- game of thrones, Inception..) > ")
#     query = "+".join(term.split())
#     return {"q": query,}

def search_results():
    # params = search_term()
    term = input("\n\nEnter to search for subtitles (Eg:- game of thrones, Inception..) > ")
    query = "+".join(term.split())
    response = requests.get(BASE_URL, params={"q": query,}, headers=HEADERS)
    tree = html.fromstring(response.content)
    catg_items = tree.xpath(".//div/ul/li/div[@class='title']/a")
    urls_cat = {urljoin(response.url, i.attrib["href"]):i.text for i in catg_items}
    cat_urls = sorted([(value, key) for key, value in urls_cat.items()])

    while True:
        os.system("clear||cls")
        for num, item in enumerate(cat_urls, 1):
            print(f"\t[{num}]. {item[0]}")
            sleep(0.5)
        try:
            choosed = int(input("\nEnter NUMBER > "))
            if choosed <= len(cat_urls):
                break
        except ValueError:
            pass
    print(f"\nYou have choosen {cat_urls[choosed-1][0]}")
    return cat_urls[choosed-1][1]


def subtitles_list():
    url = search_results()
    response = requests.get(url, headers=HEADERS)
    # tree = html.fromstring(response.content)
    # elements = tree.xpath(".//tbody/tr/td[@class='a1']")
    elements = (html.fromstring(response.content)).xpath(".//tbody/tr/td[@class='a1']")
    srt_info = [[urljoin(response.url, i.cssselect("a")[0].attrib["href"]),
                 i.cssselect("span")[0].text.strip(),
                 i.cssselect("span")[1].text.strip()] for i in elements]
    lang_set = set([i.cssselect("span")[0].text.strip() for i in elements])
    # srt_lang = [i.cssselect("span")[0].text.strip() for i in elements]
    # srt_name = [i.cssselect("span")[1].text.strip() for i in elements]
    # srt_ulrs = [urljoin(response.url, i.cssselect("a")[0].attrib["href"]) for i in elements]
    # srt_dict = {url:[lang, name] for lang, name, url in zip(srt_lang, srt_name, srt_ulrs)}
    srt_dict = {i[0]:i[1:] for i in srt_info}
    srt_data = [[key, value] for key, value in srt_dict.items()]
    lang_dict = collections.defaultdict()

    for lang in lang_set:
        lang_dict[lang] = {j[0]:j[1][1] for j in srt_data if j[1][0] == lang}

    #  Using ENGLISH Language now -
    try:
        eng_dict = lang_dict["English"]
        # srt_set = set(eng_dict.keys())
        # srt_list = [(name,url)]

    except KeyError:
        os.system("clear||cls")
        print("\n English subtitles are not available for this....\n")
        search_results()

    eng_srt = sorted([(key, value) for key, value in eng_dict.items()])[::-1]

    while True:
        os.system("clear||cls")
        for num, srt in enumerate(eng_srt, 1):
            print(f"\t[{num}]. {srt[1]}")
            sleep(0.1)
        try:
            chosen = int(input("\n\tEnter NUMBER > "))
            if chosen <= len(lang_dict["English"]):
                break
        except ValueError:
            pass
    os.system("clear||cls")
    print("\n\n\tYou have choosen {}".format(eng_srt[chosen-1][1]))
    return eng_srt[chosen-1][0]


    # # language selection
    # os.system("clear||cls")
    # while True:
    #     os.system("clear||cls")
    #     for num, land in enumerate(languages,1):
    #         print(f"[{num}]. lang")
    #         sleep(0.1)
    #     try:
    #         choice  = input("\nEnter > ")
    #         if type(int(choice)) == int and int(choice) <= len(name_urls):
    #             break
    #     except ValueError:
    #         pass
    # os.system("clear||cls")
    # print(f"\nYou have choosen {name_urls[choice-1][0]}")
    # return languages[choice-1][1]



def main():
    os.system("clear||cls")
    banners()
    srt_url = subtitles_list()
    tree = html.fromstring(requests.get(srt_url).text)
    rel_dlink = tree.get_element_by_id("downloadButton").get("href")
    dlink = urljoin(DOMAIN, rel_dlink)

    # Download srt

    filename = "{}.zip".format(srt_url.split("/")[-1])
    content = requests.get(dlink).content
    with open(filename, "wb") as srt:
        srt.write(content)
        # print("\n\tDownload completed..!!") # to-d0  unzip it and ask for download location
    if zipfile.is_zipfile(filename):
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall()
    print("\n\tDownload completed..!!") # to-d0  unzip it and ask for download location




if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\t Thank you....\n\n")
