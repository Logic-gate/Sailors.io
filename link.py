import urllib2
from bs4 import BeautifulSoup



class Meta():

    def __init__(self, link):
    	self.link = link
    	self.browser = urllib2.build_opener()
    	self.browser.addheaders = [('User-Agent','Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0')]
    	self.req = self.browser.open(self.link)
    	self.response = self.req.read()
    	self.soup = BeautifulSoup(self.response)



    def get_meta(self, tag, *value):
        a = []
    	for i in value:
    		a.append(self.soup.find('head').find('meta', {tag: value}))
        return a

    def get_global_meta(self):
    	return self.soup.find('head').find('meta', {"name": "description"})['content'], self.soup.find('head').find('title').text


    def get_schema_markup(self):
    	return self.get_meta('itemprop', 'name', 'description', 'image')

    def get_twitter_data(self):
    	return self.get_meta('name', 'twitter:card', 'twitter:site',
    					 'twitter:title', 'twitter:description',
    					 'twitter:creator', 'twitter:image',
    					 'twitter:data1', 'twitter:label1',
    					 'twitter:data2',	'twitter:data2', 
    					 'twitter:label2')

    def get_open_graph(self):
    	return self.get_meta('property', 'og:title', 'og:type', 'og:url', 'og:image', 'og:description', 'og:site_name', 'og:price:amount', 'og:price:currency')
