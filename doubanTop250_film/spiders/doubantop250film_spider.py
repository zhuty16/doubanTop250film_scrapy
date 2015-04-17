# -*- coding:utf-8 -*-
'''doubantop250film_spider'''

from scrapy.spider import Spider
from scrapy import log
from doubanTop250_film.items import Doubantop250FilmItem
from BeautifulSoup import BeautifulSoup
import re
import urllib2

class DoubanTop250FilmSpider(Spider):
    name = 'doubantop250filmspider'
    allowed_domains = ['douban.com']
    start_urls = ['http://movie.douban.com/top250?start=0']
    # print start_urls
    def parse(self, response):
        '''description'''
        pageNumber = 1
        BASE_URL = "http://movie.douban.com/top250?start={start}"
        items = []
        for pages in range(pageNumber):
            print "crawling page%d...\n" % (pages+1)
            startNum = pages * 25
            listurl = BASE_URL.format(start=startNum)
            # print listurl
            soup = BeautifulSoup(urllib2.urlopen(listurl))
            for film in soup.findAll('div',{'class':'info'}):
                item = Doubantop250FilmItem()

                item['name'] = film.find('span',{'class':'title'}).text
                item['url'] = re.search(r'<a href="(.*?)"', str(film)).group(1)
                try:
                    filmsoup = BeautifulSoup(urllib2.urlopen(item['url']))
                except Exception,e:
                    continue
                film_info = str(filmsoup.find('div',{'id':'info'}))
                # print film_info
                item['director'] = re.search(r'导演</span>: <span class="attrs"><a href=".*?">(.*?)</a>', film_info).group(1).decode('utf8')
                try:
                    item['screenwriter'] = re.search(r'编剧</span>: <span class="attrs"><a href=".*?">(.*?)</a>', film_info).group(1).decode('utf8')
                except Exception,e:
                    item['screenwriter'] = ''
                item['actor'] = re.search(r'主演</span>: <span class="attrs"><a href=".*?">(.*?)</a>', film_info).group(1).decode('utf8')
                item['nation'] = re.search(r'制片国家/地区:</span>(.*?)<br />', film_info).group(1).strip().decode('utf8')
                item['language'] = re.search(r'语言:</span>(.*?)<br />', film_info).group(1).strip().decode('utf8')
                item['releaseDate'] = re.search(r'上映日期:.*?">(.*?)</span>', film_info).group(1).decode('utf8')
                try:
                    item['length'] = re.search(r'片长:.*?">(.*?)</span>', film_info).group(1).decode('utf8')
                except Exception,e:
                    item['length'] = ''
                film_interest = filmsoup.find('div',{'id':'interest_sectl'})
                item['score'] = film_interest.find('strong',{'class':'ll rating_num'}).text
                item['scoreNum'] = film_interest.find('span',{'property':'v:votes'}).text
                
                related_info = filmsoup.find('div',{'class':'related-info'})
                item['summary'] = related_info.find('span',{'property':'v:summary'}).text
                items.append(item)
                log.msg("Appending item...",level='INFO')


        log.msg("Append done.",level='INFO')
        return items
