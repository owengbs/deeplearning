import urllib2,urllib,json,re
import xml.etree.ElementTree as ET
from scrapy.spider import Spider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.http import FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from tutorial.items import DmozItem
title_global = []
class DmozSpider(CrawlSpider):
    name = "dmoz"
    #allowed_domains = ["zhihu.com"]
    start_urls = [
        "http://www.zhihu.com/topics"
        #"http://www.dmoz.org/Computers/Programming/Languages/Python/Books/"
    ]
    """
    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        #Rule(SgmlLinkExtractor(allow=('\/topic\/'))),
        Rule(SgmlLinkExtractor(allow=('\/topic\/', )), callback='parse_item'),
    )
    """
    """
    def parse(self, response):
        items = []
        sel = Selector(response)
        sites = sel.xpath('//ul/li')
        labels = sel.xpath('//div[@class="blk"]')
        for site in sites:
            item = DmozItem()
            item['url'] = site.xpath('a/@href').extract()
            category = site.xpath('a/text()').extract()
            if category:
                #title = category
                title = category[0].encode('utf-8')
                item['title'] = title
                print title+"\n"
                items.append(item)
        for label in labels:
            item = DmozItem()
            category = site.xpath('a/strong/text()').extract()
            if category:
                #title = category
                title = category[0].encode('utf-8')
                ggitem['title'] = title
                print "label"+title+"\n"
                items.append(item)

        return items
        """
    def parse_start_url(self, response):
        urlstr = "http://www.zhihu.com/node/TopicsPlazzaListV2"
        sel = Selector(response)
        ids = sel.xpath("//li").re(r'data-id=\"(\d+)\"\><a.*>(.*?)</a></li>')
        req_list = []
        for k in range(len(ids)/2):
            cid = ids[2*k]
            name = ids[2*k+1]
            #print name
            for i in range(0, 20):
                a = { 
                    "method" : 'next',
                    "params" : '{"hash_id":"","offset":'+str(i*20)+',"topic_id":'+str(cid)+'}',
                    "_xsrf":'147d38e7995d4e0380b9952fa7511bc7'
                }   
                data = urllib.urlencode(a) 
                #request =  Request(url, method="POST", body=data, callback=self.parse_item)  
                callback=lambda response, name=name: self.parse_ajax(response, name)
                req_list.append(FormRequest(url=urlstr,
                        formdata=a,
                        callback = callback))
        return req_list
        #request =  [FormRequest(url, method="POST", body=data, callback=self.parse_item)  
        #yield request
    def parse_ajax(self, response, name):
        print name
        res_json = json.loads(response.body)
        msg = res_json['msg']
        req_list = []
        for cont in msg:
            oneline = cont.encode('utf-8').replace("\n",'')
            m = re.match(r".*<a.*href=\"(\/topic.*?)\">.*", oneline)
            subfix = m.group(1)
            for page in range(1,50):
                urlstr = "http://www.zhihu.com"+subfix+"?page="+str(page)
                print urlstr
                m = re.match(r".*<strong>(.*?)<\/strong>.*", oneline)
                topic = m.group(1)
                #open("./zhihu_topics/"+name.encode('utf-8'),"ab").write(topic+"\n")
                req_list.append(Request(url=urlstr, callback= lambda r,topic=topic: self.parse_item(r, topic)))
                #print m.group(1)
        return req_list 
        #sel = Selector(res_json['msg'])
        #topics = sel.xpath("//div").extract()
    def parse_item(self, response, topic):
        sel = Selector(response)
        #title = sel.xpath("//div[@id='zh-topic-title']/h1").extract()[0].encode('utf-8')
        titles = sel.xpath("//a[@class='question_link']/text()").extract()
        for title in titles:
            if title not in title_global:
                title_global.append(title)
                print title.encode('utf-8')
                open("./zhihu_topics/"+topic,"ab").write(title.encode('utf-8')+"\n")
        self.log('Hi, this is an item page! %s %s' % (title, response.url))
        item = DmozItem()
        #item['id'] = sel.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        #item['name'] = sel.xpath('//td[@id="item_name"]/text()').extract()
        #item['description'] = sel.xpath('//td[@id="item_description"]/text()').extract()
        return item 
