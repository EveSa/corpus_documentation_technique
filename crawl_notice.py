import requests
import lxml.html
import urllib.parse
import logging
import re
import time

logging.basicConfig(level=logging.INFO)

url = "https://mesnotices.20minutes.fr/"
save_path = "/people/sauvage/Documents/Crawl/pdf/"
page = "manuel-notice-mode-emploi/"
response = requests.get(urllib.parse.urljoin(url, page))
html_element = lxml.html.fromstring(response.content)
p_list = html_element.xpath('//div[@id="list_p"]/p/a/@href')
# A enlever pour eviter le sur crawl #
p_list = ['SAMSUNG']
######################################
for p in p_list:
    logging.info(f"Treating {p} brand model")
    response = requests.get(urllib.parse.urljoin(url, p))
    notices_element = lxml.html.fromstring(response.content)
    model_list = notices_element.xpath('//table[@class="taille_notice"]//a/@href')
    # A enlever après test
    model_list = ["/manuel-notice-mode-emploi/SAMSUNG/WMF200GNB-_F"]
    ########################
    for model in model_list:
        time.sleep(5)
        logging.info(f"...Collecting documentation for {model}")
        response = requests.get(urllib.parse.urljoin(url, model))
        model_element = lxml.html.fromstring(response.content)
        model_language = ' '.join(model_element.xpath('//p/a[text()="Cliquez ici"]/ancestor-or-self::p/text()'))
        if re.search("Français", model_language):
            logging.info(f"......documentation language : french")
            model_notice = model_element.xpath('//p/a[text()="Cliquez ici"]/@href')
            response = requests.get(urllib.parse.urljoin(url, model_notice[0]))
            with open(save_path+'shit.html', 'w') as file:
                file.write(response.text)
            documentation_element = lxml.html.fromstring(response.content)
            documentation_url = documentation_element.xpath('//a[text()="Télécharger la notice"]/@href')
            if documentation_url == []:
                break
            documentation = requests.get(documentation_url[0])
            with open(save_path+model.replace('/', '_')+'.pdf', "wb") as save_file:
                save_file.write(documentation.content)
            logging.info(f'...Collected !\n\n')
