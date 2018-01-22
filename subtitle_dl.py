#!/usr/bin/env python3

import os
import collections
from time import sleep
import  zipfile
import requests
from requests.compat import urljoin
from lxml import html
from heading import banners
from math import ceil

# SEARCH = "the+blacklist"
DOMAIN = "https://subscene.com/"
URL = "https://subscene.com/subtitles/title"
HDR = {"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0"}

def search_srt():
    term = input("\nEnter to search for subtitles (Eg:- game of thrones, Inception..) > ")
    query = "+".join(term.split())
    response = requests.get(URL, params={"q": query,}, headers=HDR)
    tree = html.fromstring(response.content)
    results_found = tree.xpath(".//div[@class='search-result']/h2/text()")

    if 'No results found' in results_found:
        os.system("clear||cls")
        banners()
        print("No results found ..TRY using proper title")
        search_srt()

    catg_items = tree.xpath(".//div/ul/li/div[@class='title']/a")
    urls_cat = {urljoin(URL, i.attrib["href"]):i.text for i in catg_items}
    cat_urls = sorted([(value, key) for key, value in urls_cat.items()])

    while True:
        os.system("clear||cls")

        for num, item in enumerate(cat_urls, 1):
            print(f"\t[{num}]. {item[0]}")

        try:
            choosed = int(input("\nEnter NUMBER > "))
            if choosed <= len(cat_urls):
                break
        except ValueError:
            pass
    print(f"\nYou have choosen {cat_urls[choosed-1][0]}")
    subtitles_list(cat_urls[choosed-1][1])


def subtitles_list(url):
    response = requests.get(url, headers=HDR)
    elements = (html.fromstring(response.content)).xpath(".//tbody/tr/td[@class='a1']")
    srt_info = [[urljoin(url, i.cssselect("a")[0].attrib["href"]),
                 i.cssselect("span")[0].text.strip(),
                 i.cssselect("span")[1].text.strip()] for i in elements] # ([url,lang, srt])
    lang_set = set([i.cssselect("span")[0].text.strip() for i in elements])
    lang_dict = collections.defaultdict()

    for lang in lang_set:
        lang_dict[lang] = {i[2]:i[0] for i in srt_info if i[1] == lang} #({srt_name:url})

    #  Using ENGLISH Language bydefault now -
    try:
        eng_dict = lang_dict["English"]   #({srt_name:url})

    except KeyError:
        os.system("clear||cls")
        print("\n English subtitles are not available for this....\n")
        search_srt()

    eng_srt = sorted([(url, srt_name) for srt_name, url in eng_dict.items()])[::-1]

    page_size = 50
    page_cntr = 1
    page_max = ceil(len(eng_srt) / page_size)

    while True:
        os.system("clear||cls")
        print(f"\nFound {len(eng_srt)} subtitles and displaying page {page_cntr}/{page_max}:\n")

        selected_start = page_size * (page_cntr - 1)
        selected_end = page_size * page_cntr
        sleep(1)

        for num, srt in enumerate(eng_srt[selected_start:selected_end], selected_start + 1):
            print(f"\t[{num}]. {srt[1]}")
            sleep(0.075)

        print(f"\n\tEnter NUMBER or n for the next page ({page_cntr}/{page_max})")
        chosen = input("\n\tEnter NUMBER> ")
        if chosen.lower() == 'n':
            if page_cntr >= page_max:
                page_cntr = 1
            else:
                page_cntr = page_cntr + 1
        else:
            try:
                chosen = int(chosen)
                if chosen <= len(lang_dict["English"]):
                    break
            except ValueError:
                print(f"\n\tEntered '{chosen}' Need to enter number from the list \n")
                sleep(2)

    os.system("clear||cls")
    print("\n\n\tYou have choosen {}".format(eng_srt[chosen-1][1]))
    download_srt(eng_srt[chosen-1][0])


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



def download_srt(srt_url):
    tree = html.fromstring(requests.get(srt_url).text)
    rel_dlink = tree.get_element_by_id("downloadButton").get("href")
    dlink = urljoin(DOMAIN, rel_dlink)

    # Download srt
    cur_dir = os.path.abspath(os.getcwd())  # todo - download location
    filename = "{0}/{1}.zip".format(cur_dir, srt_url.split("/")[-1])
    content = requests.get(dlink).content
    with open(filename, "wb") as srt:
        srt.write(content)
    if zipfile.is_zipfile(filename):
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall()
    os.remove(filename)
    print(f"\n\tDownload completed..!! and \n\n\tsrt file is in:{cur_dir}")

    after_dl = input("\n\n\tPress ENTER to continue OR e to EXIT >  ")
    if after_dl.lower() == 'e':
        print("\n\n\t Thank you....\n\n")
        raise SystemExit

if __name__ == '__main__':
    try:
        while True:
            os.system("clear||cls")
            banners()
            search_srt()
    except KeyboardInterrupt:
        print("\n\n\t Thank you....\n\n")
