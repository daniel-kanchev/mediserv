import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from mediserv.items import Article


class MediservSpider(scrapy.Spider):
    name = 'mediserv'
    start_urls = ['https://mediserv.de/neues/']

    def parse(self, response):
        articles = response.xpath('//div[@class="grid-items "]/div')
        for article in articles:
            link = article.xpath('.//a[@class="read-more"]/@href').get()
            date = article.xpath('.//div[@class="element element_2 post_date "]/text()').get()
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="content-wrapper"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
