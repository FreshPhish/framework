from __future__ import absolute_import
from __future__ import division
from __future__ import print_function #enforces python 3 syntax
import httplib2
from BeautifulSoup import BeautifulSoup, SoupStrainer
from urlparse import urlparse
import urllib
import requests
import csv
import os
import time
import whois
import pythonwhois
import re
import xml.etree.ElementTree
from datetime import datetime
import dateutil.parser
import StringIO as io
import sys
import dryscrape
from random import shuffle
import tldextract
import socket
socket.setdefaulttimeout(10) # or whatever timeout you want

class goPhish:
    """This class takes in a url and 
    retrieves data about the web page"""

    
    def __init__(self,url, user , password , debugging=False):

        #the URL we are testing
        self.url = url

        parsed_uri = urlparse( self.url )
        self.domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        self.domainScheme = '{uri.scheme}'.format(uri=parsed_uri)

        tldObj = tldextract.extract(self.url)
        self.domainName = tldObj.domain
        self.domainSuffix = tldObj.suffix



        #whether to print debugging info
        self.debugging = debugging

        #dmain name stored from whois lookup
        self.whoisDomainName =""

        #discard site flag
        self.discardSite = False

        #whois login
        self.user = user
        self.password = password

        #dictionary that hold the score for this URL on all tests
        self.phishScore =  {
            'havingIPAddress':0,
            'urlLength':0,
            'shorteningService':0,
            'havingAtSymbol':0,
            'doubleSlashRedirecting':0,
            'prefixSuffix':0,
            'havingSubDomain':0,
            'sslFinalState':0,
            'domainRegistrationLength':0,
            'favicon':0,
            'port':0,
            'httpsToken':0,
            'requestURL':0,
            'urlOfAnchor':0,
            'linksInTags':0,
            'sfh':0,
            'submittingToEmail':0,
            'abnormalURL':0,
            'redirect':0,
            'onMouseOver':0,
            'rightClick':0,
            'popUpWindow':0,
            'iFrame':0,
            'ageOfDomain':0,
            'dnsRecord':0,
            'webTraffic':0,
            'pageRank':0,
            'googleIndex':0,
            'linksPointingToPage':0,
            'statisticalReport':0 
        }


    
    
    def havingIP(self):
        retVal =-1
        try:
            parsed_uri = urlparse( self.url )
            domain = '{uri.netloc}'.format(uri=parsed_uri)
            checkIP=re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",domain)
            if checkIP:
                retVal =1
        except:
                printFormat("exc" , "havingIP" , "Unknown Error")
        self.phishScore['havingIP'] = retVal
        return retVal

    def getAnchorResult(self):
        """Whether the domain of anchor is different from that of the website"""
        retVal =-1
        try:
            http = httplib2.Http()
            status, response = http.request(self.url)
            positiveAnchor =0
            negativeAnchor =0
            for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
                if link.has_key('href'):
                    tldObj = tldextract.extract(link['href'])
                    if ( tldObj.domain == self.domainName and tldObj.suffix == self.domainSuffix ):
                        positiveAnchor += 1
                    else:
                        negativeAnchor += 1
            ratio = negativeAnchor /(positiveAnchor + negativeAnchor)
            if ratio > 0.5:  #site is considered Phishy
                retVal =1
            if ratio < 0.2:
                retVal =-1
        except:
            printFormat("exc","getAnchorResult","No ANchors were returned. Setting to Zero")
            pass
        self.phishScore['urlOfAnchor'] = retVal
        return retVal
    
    def getGoogleIndex(self):
        """Adapted from:
        http://searchengineland.com/check-urls-indexed-google-using-python-259773"""
        try:
            from bs4 import BeautifulSoup
            seconds = 5
            user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
            headers = { 'User-Agent' : user_agent}
            retVal=1 # default to not indexed

            query = {'q': 'info:' + self.url}
            google = "https://www.google.com/search?" + urllib.urlencode(query)
            data = requests.get(google, headers=headers)
            data.encoding = 'ISO-8859-1'
            soup = BeautifulSoup(str(data.content), "html.parser")

            check = soup.find(id="rso").find("div").find("div").find("h3").find("a")
            href = check['href']
            retVal =-1
        except AttributeError:
            printFormat("exc","getGoogleIndex" , "Site is not indexed")
        self.phishScore['googleIndex'] = retVal
        return retVal

    def getAlexaDelta(self):
        import bs4 as bs
        retVal =0
        try:
            http = httplib2.Http()
            status, response = http.request("http://data.alexa.com/data?cli=10&dat=s&url="+self.url , timeout = 3)
            delta = bs.BeautifulSoup(response,'xml').find("RANK")['DELTA']
            if delta > 0:
                retVal = 1
            else:
                retVal = -1
        except:
            retVal =1
            printFormat("exc","getAlexaDelta" , "Error happened")
        self.phishScore['pageRank'] = retVal
        return retVal

    def getRedirect(self):
        retVal =0
        try:
            r = requests.get(self.url, allow_redirects=False)
            if r.status_code==301:
                retVal = 1
            else:
                retVal = -1
        except:
            if self.debugging:
                printFormat("exc" , "getRedirect" ,"Could not Contact {}".format(self.url))

        self.phishScore['redirect'] = retVal
        return retVal

    def getLinksInTags(self):
        """Links in <Meta>, <Script> and <Link> tags  point at same domain"""
        retVal = 0
        parsed_uri = urlparse( self.url )
        domain = '{uri.netloc}'.format(uri=parsed_uri)
        try:
            http = httplib2.Http()
            status, response = http.request(self.url)
            metaTags = BeautifulSoup(response, parseOnlyThese=SoupStrainer(['meta','script','link']))
            matchedDomains =0
            unMatchedDomains =0
            for tag in metaTags:
                content =""
                if tag.has_key('content'):
                    content += (tag['content'])
                if tag.has_key('src'):
                    content += (tag['src'])
                if tag.has_key('link'):
                    content += (tag['link'])
                matchObj = re.match(r'([^a-zA-Z\d]+|http[s]?://)?([a-z0-9|-]+)\.?([a-z0-9|-]+)\.([a-z0-9|-]+)',content,re.M|re.I)
                if matchObj:
                    subdomain = matchObj.group(2)
                    midDomain = matchObj.group(3)
                    topDomain = matchObj.group(4)
                    if domain.find(midDomain) != -1:  #we have a url that matches the domain of the site
                        matchedDomains +=1
                    else:
                        unMatchedDomains +=1

            percentUnmatched = unMatchedDomains/(matchedDomains+unMatchedDomains)

            if percentUnmatched > 0.5:  #site is considered Phishy
                retVal =1
            else:
                retVal =-1
        except httplib2.ServerNotFoundError:
                printFormat("exc","getLinksInTags","Site is Down")
                pass
        except:
                printFormat("exc","getLinksInTags","No tags were returned.  Setting to Zero")
                pass
        self.phishScore['linksInTags'] = retVal
        return retVal


    def initiateWhoisDoc(self):
        """Limited to 50000 requests"""
        try:
            from xml.dom import minidom
            query = "domainName={}&username={}&password={}".format( self.domain , self.user , self.password)
            request = "https://www.whoisxmlapi.com/whoisserver/WhoisService?" + query
            #print(request)
            http = httplib2.Http()
            status, response = http.request(request)
            #print (response)
            f = io.StringIO(response)
            self.doc = minidom.parse(f)
            self.whoisDomainName = self.doc.getElementsByTagName("domainName")[0].firstChild.nodeValue
        except:
            printFormat("exc","initiateWhoisDoc" , "error in initiateWhoisDoc")

    def domainRegistrationLength(self):

        retVal =0
        try:
            registryData = self.doc.getElementsByTagName("registryData")[0]
            updatedDateNode = registryData.getElementsByTagName("updatedDate")
            updatedDateText = updatedDateNode[0].firstChild.nodeValue #27-May-1987
            updatedDate =dateutil.parser.parse(updatedDateText).replace(tzinfo=None)
            currentDate = datetime.now()
            dateDiff = currentDate-updatedDate
            dateDiffInYears = (dateDiff.days + dateDiff.seconds/86400)/365.2425
            if dateDiffInYears <= 0.5:
                retVal =1
            else:
                retVal =-1
        except:
            printFormat("exc","domainRegistrationLength" , "Error occured with domainRegistrationLength:{}".format(self.url))

        self.phishScore['domainRegistrationLength'] = retVal
        return retVal


    def hasAtSymbol(self):
        retVal = 0
        try:
            if '@' in self.url:
                retVal =-1
            else:
                retVal =1
        except:
            printFormat("exc" , "hasAtSymbol" , "Unknown Error")
        self.phishScore['havingAtSymbol'] = retVal
        return retVal

    def hasDoubleSlash(self):
        retVal = 0
        try:
            if '//' in self.url:
                retVal =1
            else:
                retVal =1
        except:
            printFormat("exc","hasDoubleSlash" , "Unknown Error")
        self.phishScore['havingAtSymbol'] = retVal
        return retVal

    def hasNonStandardPort(self):
        #This method looks for an '@' symbol in the url.
        retVal =0
        try:
            parsed_uri = urlparse( self.url )
            if (parsed_uri.port == None or  parsed_uri.port == 80 or parsed_uri.port == 443):
                retVal =-1
            else:
                retVal =1
        except:
            printFormat("exc","hasNonStandardPort","Unknown Error")

        self.phishScore['port'] = retVal
        return retVal

    def shorteningService(self):
        """
        This is functionally the same as the redirect. 
        We could use the redirect method here.
        Or we could just check through a list of shortening sites and mark it if we see
        one of those.  For now.  Just returning 0.
        """
        retVal =0
        try:
            r = requests.get(self.url, allow_redirects=False)
            if r.status_code==301:
                retVal = 1
            else:
                retVal = -1
        except:
                printFormat ("exc","shorteningService","Could not Contact {}".format(self.url))
        self.phishScore['shorteningService'] = retVal
        return retVal

    def hasPopUpWindow(self):
        """
        This method uses dryscrape which imlements webkit and can scrape a web page for Javascript has well as HTML.
        javascript has alert,confirm,prompt,window.open methods
        """
        from bs4 import BeautifulSoup
        

        retVal =0
        try:
            sess = dryscrape.Session()
            sess.visit(self.url)
            response = sess.body()
            soup = BeautifulSoup(response)
            data = soup.find('script')
            for tag in soup.findAll('script'):
                stringTag = str(tag)
                matchObj = re.search(r'.*open\(|alert\(|confirm\(|prompt\(.*',stringTag)# look for alert,confirm,prompt,open
                if matchObj:
                    retVal=1
                else:
                    retVal=-1
        except:
                printFormat ("exc","hasPopUpWindow","Pop up window exception")        
        self.phishScore['popUpWindow'] = retVal
        return retVal
    
    def hasHttpsToken(self):
        """
        This method looks for https in the url 
        http://https-www-paypal-it-webapps-mpp-home.soft-hair.com/
        """

        retVal =0
        if (self.domainScheme =="https"  ):
            retVal =1
        else:
            parsed_uri = urlparse( self.url )
            httpsDomain = 'https://{uri.netloc}/'.format(uri=parsed_uri)
            try:
                http = httplib2.Http()
                status, response = http.request(httpsDomain)
                retVal =1
            except:
                printFormat ("exc","hasHttpsToken" , "Unknown error")
                retVal =-1
            retVal =-1
        self.phishScore['httpsToken'] = retVal
        return retVal
    
    def serverFormHandler(self):
        """
        Server Form
        """
        retVal =0
        try:
            http = httplib2.Http()
            status, response = http.request(self.url)
            forms = BeautifulSoup(response, parseOnlyThese=SoupStrainer(['form']))
            for form in forms:
                if form.get('action') == "" or form.get('action') == None or form.get('action') == "about:blank":
                    retVal =1
                else:
                    retVal =-1
        except:
                printFormat ("exc","serverFormHandler","SFH exception")
        self.phishScore['sfh'] = retVal
        return retVal

    def onMouseOver(self):
        """
        This method looks for the on mouse over re-writing of links in the status bar.  This type of ruse has become less 
        effective as browsers usually ignore this.
        """
       
        from bs4 import BeautifulSoup
        
        retVal =0
        try:
            sess = dryscrape.Session()
            sess.visit(self.url)
            response = sess.body()
            soup = BeautifulSoup(response)
            for tag in soup.findAll('a'):
                if tag.has_attr('onmouseover'):
                    match = re.search(r'window.status',tag['onmouseover'])
                    if match:
                        retVal =1
                    else:
                        retVal =-1
                if tag.has_attr('href'):  #matches the href=javascript tag
                    hrefMatch = re.search(r'javascript',tag['href'])
                    if hrefMatch:
                        retVal =1
                    else:
                        retVal =-1
        except:
            printFormat ("exc","onMouseOver","On mouse over exception")
        self.phishScore['onMouseOver'] = retVal
        return retVal
    
    
    def abnormalUrl(self):
        """
        This feature can be extracted from WHOIS database [11]
        when the host name in URL does not match its claimed identity.

        To avoid a second Whois query the method getDomainRegistrationLength
        get the whois domain
        """
        retVal =0
        try:
            if not re.search(self.whoisDomainName,self.url):
                retVal =1
            else:
                retVal =-1
        except:
            printFormat ("exc","abnormalUrl" , "Unknown Error")
        self.phishScore['abnormalUrl'] = retVal
        return retVal


    def getFavIcon(self):
        """Whether the domain use a favicon for website or not"""
        retVal =1
        try:
            http = httplib2.Http()
            status, response = http.request(self.domain+'/favicon.ico')
            if (status == 200):
                retVal = -1
            else:
                retVal = 1
            #print(status.status)
        except:
                printFormat ("exc","getFavIcon","Error for finding favicon")
        self.phishScore['favicon'] = retVal
        return retVal
    
    def geturlLength(self):
        """finidng lenght of each URL"""
        retVal = 0
        try:
            if len(self.url) >= 75 :
                retVal = 1
            elif len(self.url) >= 54  :
                retVal =0
            else:
                retVal =-1
        except:
            printFormat ("exc","geturlLength","Unknown Error")

        self.phishScore['urlLength'] = retVal
        return retVal
    
    def getageOfDomain(self):
        """Get age of domain. If it is less than 10 years old, it returns 0"""
        retVal =0
        try:
            registryData = self.doc.getElementsByTagName("registryData")[0]
            createDateNode = registryData.getElementsByTagName("createdDate")
            createDateText = createDateNode[0].firstChild.nodeValue #27-May-1987
            createDate =dateutil.parser.parse(createDateText).replace(tzinfo=None)
            currentDate = datetime.now()
            dateDiff = currentDate-createDate
            dateDiffInYears = (dateDiff.days + dateDiff.seconds/86400)/365.2425
            if dateDiffInYears >= 10:
                retVal =1
            else:
                retVal =-1
        except:
            printFormat ("exc","getageOfDomain" , "Unknown Error" )
        self.phishScore['getageOfDomain'] = retVal
        return retVal

    def includePrefixSuffix(self):
        """If URL incldes '-' character, it has Prefix or Suffix  """
        retVal = 0
        try:
            if (self.url.find('-') >=0 ) :
                retVal = 1
            else:
                retVal =-1
        except:
            printFormat ("exc","includePrefixSuffix" , "UnknownError" )

        self.phishScore['prefixSuffix'] = retVal
        return retVal
    
    def usingIPAddress(self):
        """ Wether the user used IP address instead of domain name"""
        try:
            pat = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
            validate = pat.match(self.url)
            retVal = 0
            if (validate ) :
                #print("valid ip address")
                retVal = 1
            else:
                retVal =-1
        except:
            printFormat("usingIPAddress" , "Unknown Error")
        self.phishScore['usingIPAddress'] = retVal

    def usingSubDomains(self):
        """ If URL includes more than 3 dots, it is phishing web-site (except www. ) """
        tempURL = self.url
        try:
            if tempURL.startswith('www.'):
                tempURL = tempURL[4:]
            retVal = 0
            if (tempURL.count('.') > 3 ) :
                retVal = 1
            else:
                retVal = -1
        except:
            printFormat("usingSubDomains" , "Unknown error")
        self.phishScore['havingSubDomain'] = retVal


    def DNSRecord(self):
        """If DNS record in Whois is emptey, the website mighe be a phishing one"""
        retVal = 0
        try:
            registryData = self.doc.getElementsByTagName("registryData")[0]
            nameServers = registryData.getElementsByTagName("nameServers")[0]
            #print(nameServers)
            rawText = nameServers.getElementsByTagName("rawText")[0].firstChild.nodeValue
            if (len(rawText)) == 0:
                retVal =1
            else:
                retVal =-1
        except:
            printFormat ("exc","DNSRecord","Unknown error")
        self.phishScore['dnsRecord'] = retVal
        return retVal

    def getAlexaRank(self):
        try:
            import bs4 as bs
            retVal =0
            http = httplib2.Http()
            status, response = http.request("http://data.alexa.com/data?cli=10&dat=s&url="+self.url)

            rank = bs.BeautifulSoup(response,'xml').find("REACH")['RANK']
            if (rank > 10000):
                retVal =1
            else:
                retVal =-1
        except:
            retVal =1
            printFormat ("exc","getAlexaRank","Unknown error")
        self.phishScore['statisticalReport'] = retVal
        return retVal
    
    def RequestURL(self):
        """whether src link to a out-domain website or not"""
        retVal = 0
        try:
            parsed_uri = urlparse( self.url )
            domain = '{uri.netloc}'.format(uri=parsed_uri)
            http = httplib2.Http()
            status, response = http.request(self.url)
            metaTags = BeautifulSoup(response)
            tags = metaTags.findAll(attrs={"src" : True})
            matchedDomains =0
            unMatchedDomains =0
            for tag in tags:
                matchObj = re.match(r'([^a-zA-Z\d]+|http[s]?://)?([a-z0-9|-]+)\.?([a-z0-9|-]+)\.([a-z0-9|-]+)',tag['src'],re.M|re.I)              
                if matchObj:
                    subdomain = matchObj.group(2)
                    midDomain = matchObj.group(3)
                    topDomain = matchObj.group(4)
                    if domain.find(midDomain) != -1:  #we have a url that matches the domain of the site
                        matchedDomains +=1
                    else:
                        unMatchedDomains +=1
            percentUnmatched = unMatchedDomains/(matchedDomains+unMatchedDomains)
            if percentUnmatched > 0.5:  #site is considered Phishy
                retVal =1
            else:
                retVal =-1
        except:
                printFormat ("exc","RequestURL","No tags were returned.")
        self.phishScore['requestURL'] = retVal
        return retVal

def printFormat(printType,funcName , message):
    if printType == "exc":
        print( "{} - Func: {} , - Message : {}".format(printType,funcName,  message) )
    if printType == "siteName":
        print( "============={}=================".format(funcName) )
    if printType == "func":
        print( funcName )
    
def Measuringfeatures(fileName , userName , password , IsClean):

    Sites = []
    Scores=[]


    with open("../data/{}".format(fileName) ,"r") as f:
        Sites = f.read().splitlines()

    resultFile = open("../data/Data{}".format(fileName),"a")

    SiteCount=0  #Keep Track of how many sites we have scanned

    '''Rules section'''
    for site in Sites:
        #Do not let it to test more than 100 sites
        #if SiteCount >= 100 :
            #break

        gPh = goPhish( site , userName , password  , debugging = False)
        #print ("Scanning: {}".format(site))
        try:
            http = httplib2.Http()
            status, response = http.request(site)
            SiteCount += 1
        except:
            print("Not Accessible")
            gPh.discardSite=True
            continue
        printFormat("siteName",site,"")
        gPh.url=site
        printFormat("func","initiateWhoisDoc","")
        gPh.initiateWhoisDoc()
        printFormat("func","getAnchorResult","")
        gPh.getAnchorResult()
        printFormat("func","havingIP","")
        gPh.havingIP()
        printFormat("func","getGoogleIndex","")
        gPh.getGoogleIndex()
        printFormat("func","getAlexaRank","")
        gPh.getAlexaRank()  #Page Rank """
        printFormat("func","getAlexaDelta","")
        gPh.getAlexaDelta() # Change of rank of website
        printFormat("func","domainRegistrationLength","")
        gPh.domainRegistrationLength() #this has a 500 query free limit
        printFormat("func","getRedirect","")
        gPh.getRedirect()
        printFormat("func","getLinksInTags","")
        gPh.getLinksInTags()
        printFormat("func","hasAtSymbol","")
        gPh.hasAtSymbol()
        printFormat("func","hasNonStandardPort","")
        gPh.hasNonStandardPort()
        printFormat("func","shorteningService","")
        gPh.shorteningService()
        printFormat("func","hasPopUpWindow","")
        gPh.hasPopUpWindow()
        printFormat("func","hasHttpsToken","")
        gPh.hasHttpsToken()
        printFormat("func","serverFormHandler","")
        gPh.serverFormHandler()
        printFormat("func","onMouseOver","")
        gPh.onMouseOver()
        printFormat("func","abnormalUrl","")
        gPh.abnormalUrl()
        printFormat("func","getFavIcon","")
        gPh.getFavIcon()
        printFormat("func","geturlLength","")
        gPh.geturlLength()
        printFormat("func","getageOfDomain","")
        gPh.getageOfDomain()
        printFormat("func","includePrefixSuffix","")
        gPh.includePrefixSuffix()
        printFormat("func","usingIPAddress","")
        gPh.usingIPAddress()
        printFormat("func","usingSubDomains","")
        gPh.usingSubDomains()
        printFormat("func","DNSRecord","")
        gPh.DNSRecord()
        printFormat("func","RequestURL","")
        gPh.RequestURL()
        
        resultFile.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(gPh.phishScore['havingIPAddress'],gPh.phishScore['urlLength'],gPh.phishScore['shorteningService'],gPh.phishScore['havingAtSymbol'],gPh.phishScore['doubleSlashRedirecting'],gPh.phishScore['prefixSuffix'],gPh.phishScore['havingSubDomain'],gPh.phishScore['sslFinalState'],gPh.phishScore['domainRegistrationLength'],gPh.phishScore['favicon'],gPh.phishScore['port'],gPh.phishScore['httpsToken'],gPh.phishScore['requestURL'],gPh.phishScore['urlOfAnchor'],gPh.phishScore['linksInTags'],gPh.phishScore['sfh'],gPh.phishScore['submittingToEmail'],gPh.phishScore['abnormalURL'],gPh.phishScore['redirect'],gPh.phishScore['onMouseOver'],gPh.phishScore['rightClick'],gPh.phishScore['popUpWindow'],gPh.phishScore['iFrame'],gPh.phishScore['ageOfDomain'],gPh.phishScore['dnsRecord'],gPh.phishScore['webTraffic'],gPh.phishScore['pageRank'],gPh.phishScore['googleIndex'],gPh.phishScore['linksPointingToPage'],gPh.phishScore['statisticalReport'] , IsClean, site ))

        print (site, gPh.phishScore['googleIndex'])
        
        resultFile.flush()


    resultFile.close()


if __name__=='__main__' :
    # make sure you have xvfb installed necesary for headless scraping
    dryscrape.start_xvfb()
    # sys.argv[1] = name of file contains  , sys.argv[2] = username for XMPApi , sys.argv[3] = Password for XMLAPI , sys.argv[4] = add label for total data item. 0 : phishing, 1 : clean
    print (sys.argv[1] , sys.argv[2] , sys.argv[3])
    Measuringfeatures( sys.argv[1] , sys.argv[2] , sys.argv[3] , sys.argv[4])

