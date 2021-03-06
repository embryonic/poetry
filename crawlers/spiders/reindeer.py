import scrapy
import re
import json
import os, sys, traceback, time
from crawlers.spiders.base import BaseSpider

try:
    from crawlers.utils import save_to_db_poem, save_to_db_author, get_language_list_for_url
except ImportError:
    def save_to_db_poem(data):
        print(data)
    
    def save_to_db_author(data):
        print(data)
    
    def get_language_list_for_url(url):
        return []
    

def remove_tags(html, tags):
    """Returns the given HTML with given tags removed."""
    tags = [re.escape(tag) for tag in tags.split()]
    tags_re = '(%s)' % '|'.join(tags)
    starttag_re = re.compile(r'<%s(/?>|(\s+[^>]*>))' % tags_re, re.U)
    endtag_re = re.compile('</%s>' % tags_re)
    html = starttag_re.sub('', html)
    html = endtag_re.sub('', html)
    return html


class ReindeerBot(scrapy.Spider):
    '''
    @sumamry: spider bot for rekhta's new look.
    '''
    name = 'rekhta'
    allowed_domains = ['rekhta.org']
    
    # DON'T CHANGE THE start_urls, all rules depend upon this url
    start_urls = ["https://rekhta.org"]
    domain_name = "https://rekhta.org/"
    # Home Page
    home_url = "https://rekhta.org/"
    
    BASE_URL_POETS = "https://rekhta.org/poets/"
    
    # languages of the poetry to be crawled: hindi, urdu or english(default)
    LANGUAGES = ['hi', 'en', 'ur']
    
    ##
    # APIs
    
    # example of API_POETS_READ = 'https://rekhta.org/Home/Api_Poets_Read?sort=SortName-asc&page=1&pageSize=10000&lang=1&startsWith=a'
    API_POETS_READ = '/Home/Api_Poets_Read'
    
    # example of API_POET_READ = '/Home/Api_Poet_Read?sort=SortTitle-asc&page=1&lang=1&pageSize=10000&info=ghazals&id=mirza-ghalib'
    # WHERE info is in ['ghazals', 'couplets', 'nazms', 'profile', 'audio', 'video', 'ebooks']
    # id = poet slug
    # lang = 1 for eng, 2 for hindi, 3 for urdu
    API_POET_READ = '/Home/Api_Poet_Read'
    
    LOGFILE = 'log_err_reindeer.txt'
    
    # Testcase number. Change here to run a testcase.
    TESTCASE = 0
    
    def parse(self, response):
        self.logger.info('ReindeerBot got first response from %s', response.url)
        
        with open(self.LOGFILE, "a") as outfile:
            outfile.write("\n--------------------------------------------------\n")
            outfile.write("Spider name: %s\n"%(self.name))
            outfile.write("Start time: %s\n"%(time.asctime( time.localtime(time.time()) )))
            outfile.write("--------------------------------------------------\n")
        
        # Run testcase, if there is a `TESTCASE`
        if self.TESTCASE != 0:
            yield scrapy.Request(self.home_url, callback=self.run_testcase)
            return
        
        # Start main crawler
        ABCD = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u',
                'v','w', 'x','y','z',]
        
        for alphabet in ABCD:#FIXME TESTING: change back to ABCD after testing
            self.logger.debug('Listing poets %s', alphabet)
            url = self.domain_name + self.API_POETS_READ + '?' + '&sort=SortName-asc' + '&page=1' + '&lang=1' + '&pageSize=10000' + '&startsWith=' + alphabet
            
            yield scrapy.Request(url, callback=self.parse_poets_list)
            
    def run_testcase(self, response):
        '''
        @summary: Run `TESTCASE` number
        '''
        testcase = self.TESTCASE
        self.logger.info('running testcase %s.' % testcase)
        
        if testcase == 1:
            self.logger.info('testcase <Nazm by Mehdi Hassan>.')
            url = 'https://rekhta.org/nazms/dhartii-kaa-bojh-baqar-mehdi-nazms?lang=en'
            yield scrapy.Request(url, callback=self.parse_poetry)
            
        elif testcase == 2:
            self.logger.info('testcase <Big Nazm of Josh Malihabadi>.')
            url = 'https://rekhta.org/nazms/ghataa-chhaaii-to-kyaa-josh-malihabadi-nazms?lang=Hi'
            yield scrapy.Request(url, callback=self.parse_poet_page)
            
        elif testcase == 3:
            self.logger.info('testcase <bikhar jaegi sham aahista bolo... by SHAANUL HAQ HAQQI>.')
            url = 'https://rekhta.org/ghazals/bikhar-jaaegii-shaam-aahista-bolo-shaanul-haq-haqqi-ghazals'
            yield scrapy.Request(url, callback=self.parse_poet_page)
            
        elif testcase == 4:
            self.logger.info('testcase <bikhar jaegi sham aahista bolo...in Hindi... by SHAANUL HAQ HAQQI>.')
            url = 'https://rekhta.org/ghazals/bikhar-jaaegii-shaam-aahista-bolo-shaanul-haq-haqqi-ghazals?lang=hi'
            yield scrapy.Request(url, callback=self.parse_poet_page)
            
        else:
            self.logger.info('invalid testcase discarded.')
            return
    
    def parse_poets_list(self, response):
        '''
        Parse poets list and crawl to next level i.e. individual poet's page and its subsections
        '''
        i = response.url.find('&startsWith=')
        self.logger.debug('parse_poets_list: %s', response.url[i+12])
        
        data = json.loads(response.body)
        poets = data['Data']
        total = data['Total']
        errors = data['Errors']
        count = len(poets)
        self.logger.info('parse_poets_list: result has %d of %d poets', count, total)
        
        for poet in poets:
            # extract info of a poet and save
            #print poet
            poet_info = {}
            poet_info['name'] = poet['Name']
            poet_info['birth'] = poet['FromDate']
            poet_info['death'] = poet['ToDate']
            poet_info['url'] = self.BASE_URL_POETS + poet['SEOSlug'] + "/"
            
            # save poet info to db
            save_to_db_author(poet_info)
            
            # Crawl poet's page
            url_base = self.domain_name + self.API_POET_READ + '?' + '&sort=SortTitle-asc' + '&page=1' + '&lang=1' + '&pageSize=10000' + '&id=' + poet['SEOSlug']
            for info in ['ghazals', 'couplets', 'nazms',]:
                url = url_base + '&info=' + info
                yield scrapy.Request(url, callback=self.parse_poetry_list)
            
            #break #FIXME TESTING parse only one poet: remove this line after testing: 
    
    
    def parse_poetry_list(self, response):
        '''
        Parse poet's poetry list
        '''
        i = response.url.find('&id=')
        self.logger.debug('parse_poetry_list: %s', response.url[i+4:])
        
        data = json.loads(response.body)
        
        poetries = data['Data']
        total = data['Total']
        errors = data['Errors']
        count = len(poetries)
        self.logger.info('parse_poetry_list: result has %d of %d poetries', count, total)
        
        for poetry in poetries:
            # extract info of the poetry, and crawl poetry page
            #print poetry
            content_slug = poetry['ContentSlug']
            type_slug = poetry['TypeSlug']
            
            # Crate url
            url = self.domain_name + type_slug + '/' + content_slug
            
            # Check if the entry for ``url`` exist in db,
            # Also find out the list of languages in which the content is there.
            lang_list = get_language_list_for_url(url)
            
            # Now crawl poetry page only for remaining langauge
            for lang in (x for x in self.LANGUAGES if x not in lang_list):
                    url_t = url + '?lang=' + lang
                    yield scrapy.Request(url_t, callback=self.parse_poetry)
    
    
    def parse_poetry(self, response):
        '''
        Parse poetry page, extract poetry, and save.
        '''
        self.logger.debug("parse_poetry: IN.")
        try:
            # extract poem
            stanza_selectors = response.xpath("//div[contains(@class,'mainContentBody')]/div[contains(@class,'poemPageContentBody')]/div/div")
            poem = ''
            for s in stanza_selectors:
                line_selectors = s.xpath(".//p")
                for l in line_selectors:
                    line = l.xpath(".//text()").extract()
                    line = ''.join(line)
                    line = line.strip()
                    ##print line
                    poem = poem + line + '\n'
                poem = poem + '\n'
            poem = poem[0:-1]#strip last '\n' from the poem
            #print poem
            
            # extract title of the poem
            title = response.xpath("//div[contains(@class,'mainContentBody')]/div[contains(@class,'poemPageContentHeader')]/h1/text()").extract()[0]
            
            # extract poet name
            # poet name must be in english. 
            poet_href = response.xpath("//div[contains(@class,'mainContentBody')]/div[contains(@class,'poemPageContentHeader')]//a[contains(@class,'ghazalAuthor')]/@href").extract()[0]
            p = re.compile(r'poets/(.+)/') #href="/poets/anjum-tarazi/?lang=Hi"
            poet = p.search(poet_href).group(1)
            poet = poet.replace('-', ' ')
            
            # check response.url for language information: https://.....xyz/?lang=hi
            tmp = response.url
            tmp = tmp.split('?')
            url = tmp[0]
            language = tmp[1].split('=')[1]
            
            data = {}
            data['poem'] = poem
            data['url'] = url
            data['title'] = title.strip()
            data['author'] = poet.title()
            data['language'] = language
             
            # Store these information in DB
            save_to_db_poem(data)
            
        except:
            self.logger.error("parse_poetry: %s", sys.exc_info()[0])
            _trace = ''
            for frame in traceback.extract_tb(sys.exc_info()[2]):
                fname,lineno,fn,text = frame
                self.logger.error("error in %s on line %d" % (fname, lineno))
                _trace = _trace + "error in %s on line %d" % (fname, lineno)
            with open(self.LOGFILE, "a") as outfile:
                t = time.asctime( time.localtime(time.time()) )
                json.dump({'link': response.url, 'error': 'parsing poetry failed', 'trace': _trace, 'time': t}, outfile, indent=4)


class SpiderReindeer(BaseSpider):
    '''
    @summary: Class to manage ReindeerBot
    '''
    spider_name = "reindeer"
    bot = ReindeerBot

