import logging
import os
import time
import urllib.parse
from itertools import cycle
from pathlib import Path

import lxml.html
import requests
from fake_useragent import UserAgent

ua = UserAgent()

logging.basicConfig(level=logging.INFO)

url = "https://www.notice-facile.com"
SAVE_PATH = os.path.join(os.getcwd(), "pdf")
# page = "manuel-notice-mode-emploi/"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
    "Referer": "https://www.scraperapi.com/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": ua.random,
    "X-Amzn-Trace-Id": "Root=1-65279d1f-2fb2dff00400da9f086a2632",
}


ip_addresses = [
    "51.38.191.151:80",
    "163.172.85.30:80",
    "178.33.3.163:8080",
    "51.254.121.123:8088",
    "20.111.54.16:8123",
    "176.31.129.223:8080",
    "51.178.18.88:80",
    "81.250.223.126:80",
    "82.64.199.193:8118",
    "151.80.136.138:3128",
    "51.38.230.146:80",
    "162.19.50.37:80",
    "51.91.109.83:80",
    "51.83.98.90:80",
    "51.195.246.56:1080",
    "137.74.65.101:80",
]

proxy_cycle = cycle(ip_addresses)


def proxy_requests(url):
    proxy = next(proxy_cycle)
    proxies = lambda proxy: {"http": proxy, "https": proxy}
    for i in range(len(ip_addresses)):
        try :
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as err :
            logging.info(f"......Wrong status code because of {err} - Sleeping for 1 min")
            time.sleep(60)
            return False
            try:
                logging.info(f"......Requesting with {proxy} proxy")
                response = requests.get(
                    url, headers=headers, proxies=proxies(proxy), timeout=5
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as err2:
                proxy = next(proxy_cycle)
                logging.info(f"...... err: {err2}\n......Trying with another proxy")


response = proxy_requests(url)
html_element = lxml.html.fromstring(response.content)
p_list = html_element.xpath('//a[@class="marque_title"]/@href')
# # A enlever pour eviter le sur crawl #
# p_list = ["/marque/1009/A-ONE"]
# ######################################
for p in p_list:
    logging.info(f"Treating {p} brand model")
    response = proxy_requests(urllib.parse.urljoin(url, p))
    if response == False:
        break
    notices_element = lxml.html.fromstring(response.content)
    model_list = notices_element.xpath('//a[@class="notice_title"]/@href')
    # # A enlever après test
    # print(model_list)
    # model_list = ["/notice/17757/+A-ONE+DV5601HDMI+"]
    # ########################
    for model in model_list:
        logging.info(f"...Collecting documentation for {model}")
        if os.path.exists(os.path.join(SAVE_PATH, model.split('/')[-1] + ".pdf")):
            logging.info(f"......Documentation already collected\n\n")
            break
        time.sleep(5)
        response = proxy_requests(urllib.parse.urljoin(url, model))
        if response == False:
            break
        model_element = lxml.html.fromstring(response.content)
        # model_language = ' '.join(model_element.xpath('//p/a[text()="Cliquez ici"]/ancestor-or-self::p/text()'))
        # if re.search("Français", model_language):
        # logging.info(f"......documentation language : french")
        # model_notice = model_element.xpath('//a[@class="notice_title]/@href')
        # response = requests.get(urllib.parse.urljoin(url, model_notice[0]), headers = headers, proxies = proxies(proxy))
        # with open(SAVE_PATH+'shit.html', 'w') as file:
        #     file.write(response.text)
        # documentation_element = lxml.html.fromstring(response.content)
        documentation_url = model_element.xpath(
            '//a[text()="Télécharger la notice"]/@href'
        )
        if documentation_url == []:
            break
        documentation = proxy_requests(documentation_url[0])
        if documentation == False:
            break

        save_file = Path(os.path.join(SAVE_PATH, model.split('/')[-1] + ".pdf"))
        save_file.parent.mkdir(parents=True, exist_ok=True)
        with open(save_file, "wb") as s_file:
            s_file.write(documentation.content)
        logging.info(f"...Collected !\n\n")
        # else :
        # logging.info(f"...no french documentation")
