import json
import re

import pandas as pd
import scrapy


class TargetSpider(scrapy.Spider):
    name = "target"
    allowed_domains = ["example.com"]
    # start_urls = ["https://example.com"]
    output_df = pd.DataFrame()

    def start_requests(self):
        try:
            urls = ['https://www.target.com/p/-/A-79344798','https://www.target.com/p/-/A-13493042',
                    'https://www.target.com/p/-/A-85781566']
            headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                       "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"}
            for url in urls:
                yield scrapy.FormRequest(url, callback=self.parsedata, headers=headers, dont_filter=True)
                # break
        except Exception as e:
            print(e)

    def parsedata(self, response):

        response_data = re.findall(r"'__TGT_DATA__'(.*?)'__WEB_CLUSTER__'",response.text, re.DOTALL)[0]
        data = re.findall(r'JSON.parse\("(.*?)"\)\),', response_data)[0]
        try:
            data = data.encode('utf-8').decode('unicode-escape')
            jdata = json.loads(data)
            products = jdata['__PRELOADED_QUERIES__']['queries'][2][1]

            url = products['product']['item']['enrichment']['buy_url']

            tcin = products['product']['tcin']

            try:
                upc = products['product']['item']['primary_barcode']
            except:
                upc = products['product']['children'][0]['item']['primary_barcode']
            try:
                price_amount = products['product']['price']['current_retail']
            except:
                price_amount = products['product']['price']['current_retail_min']

            bullets = products['product']['item']['product_description']['soft_bullet_description'].replace('&bull;', '').replace('<br>', '\n')

            currency = 'USD'
            description = jdata['__PRELOADED_QUERIES__']['queries'][0][1]['data']['metadata']['seo_data']['seo_description']
            specs = None

            if tcin == '85781566':
                features = [itm.replace('<B>', '').replace('</B>', '') for itm in
                            products['product']['children'][0]['item']['product_description']['bullet_descriptions']]
            else:
                features = [itm.replace('<B>','').replace('</B>','') for itm in products['product']['item']['product_description']['bullet_descriptions']]

            tmpdf = pd.DataFrame({'url':url, 'tcin':tcin,'upc':upc, 'price_amount':price_amount, 'currency':currency,
                                  'description':description, 'specs':specs, 'ingredients':'[]', 'bullets':bullets,
                                  'features':str(features)}, index=[0])

            self.output_df = pd.concat([self.output_df, tmpdf])
            self.output_df.to_json('taget_task_data_08_08_2023.json', orient='records')

        except Exception as e:
            print(e)

from scrapy import cmdline
cmdline.execute("scrapy crawl target".split())