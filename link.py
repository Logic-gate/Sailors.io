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



    def get_meta(self, tag, value):
    	return self.soup.find('head').find('meta', {tag: value})

#self.get_meta('name', 'twitter:card', 'twitter:site',
 #                        'twitter:title', 'twitter:description',
  #                       'twitter:creator', 'twitter:image',
   #                      'twitter:data1', 'twitter:label1',
    #                     'twitter:data2',   'twitter:data2', 
     #                    'twitter:label2')


# return self.get_meta('property', 'og:title', 'og:type', 'og:url', 'og:image', 'og:description', 'og:site_name', 'og:price:amount', 'og:price:currency')

# 
       # return self.get_meta('itemprop', 'name', 'description', 'image')


    def get_global_meta(self):
    	return self.soup.find('head').find('meta', {"name": "description"})['content'], self.soup.find('head').find('title').text

    def get_xkcd(self):
        return self.soup.find('div', attrs={'id':'comic'}).img


