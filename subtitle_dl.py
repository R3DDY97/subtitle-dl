#!/usr/bin/env python3

import os
import collections
from time import sleep
import  zipfile
from math import ceil
import requests
from requests.compat import urljoin
from lxml import html
from heading import banners

DOMAIN = "https://subscene.com/"
URL = "https://subscene.com/subtitles/title"
HDR = {"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0"}

def search_srt():
    print("\nPress CTRL+C to exit anytime")
    term = input("\n\nEnter to search for subtitles (Eg:- game of thrones, Inception..) > ")
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
        print("\n\nChoose title from the search list:\n")
        for num, item in enumerate(cat_urls, 1):
            print("\t[{}]. {}".format(num, item[0]))

        choice = input('''\n\n\tEnter title NUMBER between 1 to {} or
                    \n\tFor new search Enter : S\n\nEnter >  '''.format(len(cat_urls)))
        if choice.upper() == 'S':
            os.system("clear||cls")
            search_srt()
        try:
            choosed = int(choice)
            if choosed <= len(cat_urls):
                break
        except ValueError:
            pass
    print("\nYou have choosen {}".format(cat_urls[choosed-1][0]))
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

    # print("Press Enter key for English subtitles")
    # lang_choice = input("Enter 'l' to choose other language > ")
    # lang_list = list(lang_set)
    # lang_list.remove("English")
    # if lang_choice.lower() == 'l':
    #     language = select_language(lang_list)
    #     eng_dict = lang_dict[language]
    # else:
        #  Using ENGLISH Language bydefault now -
    if "English" in lang_set:
        eng_dict = lang_dict["English"]   #({srt_name:url})
    else:
        os.system("clear||cls")
        print("\n English subtitles are not available for this....\n")
        search_srt()

    eng_srt = sorted([(url, srt_name) for srt_name, url in eng_dict.items()])[::-1]

    page_size = 50
    page_cntr = 1
    page_max = ceil(len(eng_srt) / page_size)

    while True:
        os.system("clear||cls")
        print("\n{} subtitles were found:\n".format(len(eng_srt)))
        sleep(1)

        selected_start = page_size * (page_cntr - 1)
        selected_end = page_size * page_cntr

        for num, srt in enumerate(eng_srt[selected_start:selected_end], selected_start + 1):
            print("\t[{}]. {}".format(num, srt[1]))
            sleep(0.075)

        print("\n\tTo download Enter NUMBER or\n\tFor Next page ({}/{}) : N\n\t\tNew search  : S".format(page_cntr, page_max))
        chosen = input("\n\tEnter NUMBER > ")
        if chosen.upper() == 'S':
            os.system("clear||cls")
            search_srt()
        if chosen.lower() == 'N':
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
    if os.sys.platform == 'linux' or os.sys.platform == 'darwin':
        default_path = "{}/Downloads".format(os.path.expanduser("~"))
    else:
        default_path = "{}\\Downloads".format(os.path.expanduser("~"))

    down_path = os.path.expanduser(input('\n\tChoose download directory path: '))
    # while not os.path.isdir(down_path) or not os.access(down_path, os.W_OK):
    #     if not os.access(down_path, os.W_OK):
    #         down_path = input('\n\tWrite permission not available.\n\tChoose another directory:')
    #     elif not os.path.isdir(down_path):
    #         down_path = input('\n\tDirectory does not exists.\n\tChoose download directory:')
    if not os.path.isdir(down_path) or not os.access(down_path, os.W_OK):
        print("\n\n\t {} is either doesn't exist or with no write permissions".format(down_path))
        print("\n\tDownloading in default Downloads folder")
        download_srt(eng_srt[chosen-1][0], default_path)
    else:
        download_srt(eng_srt[chosen-1][0], down_path)


def select_language(lang_list):
    while True:
        os.system("clear||cls")
        print("\n\n\tChoose language from the list :\n")
        for num, lang in enumerate(lang_list, 1):
            print("\t[{}]. {}".format(num, lang))
            sleep(0.1)
        try:
            choice = int(input("\nEnter > "))
        except ValueError:
            continue
        if choice <= len(lang_list):
            break
    return lang_list[choice-1]



def download_srt(srt_url,down_path):
    tree = html.fromstring(requests.get(srt_url).text)
    rel_dlink = tree.get_element_by_id("downloadButton").get("href")
    dlink = urljoin(DOMAIN, rel_dlink)
    # Download srt
    cur_dir = down_path  # todo - download location
    filename = "{0}/{1}.zip".format(cur_dir, srt_url.split("/")[-1])
    content = requests.get(dlink).content
    with open(filename, "w+b") as srt:
        srt.write(content)
    if zipfile.is_zipfile(filename):
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(cur_dir)
    os.remove(filename)
    # print("\n\tDownload completed..!! and \n\n\tFile location:{}".format(cur_dir))
    print("\n\tDownloaded and the file is in {}".format(cur_dir))
    sleep(3)


if __name__ == '__main__':
    try:
        while True:
            os.system("clear||cls")
            banners()
            search_srt()
    except KeyboardInterrupt:
        print("\n\n\t Thank you....\n\n")
