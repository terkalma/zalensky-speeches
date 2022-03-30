import scrapy
import re
from datetime import datetime

white_spaces = re.compile("\s+")
war_start_date = datetime(2022, 2, 23, 23, 59, 59)


class ZalenskySpider(scrapy.Spider):
    name = 'zalensky'
    start_urls = ['https://www.president.gov.ua/en/news/speeches']

    def parse(self, response):
        for s_link in response.css('div.item_stat_headline > h3 > a'):
            yield response.follow(s_link, self.parse_speech)

        found_active = False
        for pag in response.css('div.pagination a.pag'):
            if found_active:
                if pag.attrib['href'] != 'javascript:void(0);':
                    yield response.follow(pag, self.parse)
                break
            if 'act' in pag.attrib['class']:
                found_active = True


    def parse_speech(self, response):
        full_text = ''

        date = response.css('div.article p.date').css('::text').get()
        date = white_spaces.sub(' ', date).strip()
        date = datetime.strptime(date, '%d %B %Y - %H:%M')

        if date > war_start_date:
            for t in response.css('.article_content p'):
                full_text += t.css('::text').get()
                full_text += ' '

            return { date.isoformat(): white_spaces.sub(' ', full_text).strip() }
        return None