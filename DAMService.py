
#coding=utf-8

import poster
import urllib
import urllib2
import cookielib
import json
import xml.dom.minidom

myDAMURL = "http://211.87.224.230:3000"
myURL = "http://211.87.224.230:8080/razuna"
"""
myDAMURL = "http://222.173.11.5:3000"
myURL = "http://222.173.11.5:8080/razuna"
"""
class DAMService():
 
    def __init__(self):
        print "sss"
        self.url = myURL
        self.myDAMURL = myDAMURL

    def get(self, url, params):
        url1 = self.url + url
        try:
            url1 = url1 + "?"
            for name in params:
                url1 = url1 + name + "=" + params[name] + "&"
            url2 = url1[0: len(url1) - 1]
            self.cookie = cookielib.CookieJar()
            req = urllib2.Request(url2)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
            response = opener.open(req)
            result = response.read()
            return result
        except urllib2.HTTPError, e:
            print e.code
            return False
        except urllib2.URLError, e:
            print e
            return False

    def post(self, url, params, method = None):
        url1 = self.url + url + '?'
        try:
            if method != None:
                url1 = 'method=' + method
            params_urlencode = urllib.urlencode(params)
            req = urllib2.Request(url1, params_urlencode)
            result_data = urllib2.urlopen(req)
            result = result_data.read()
            return result
        except urllib2.HTTPError, e:
            print e.code
            return False
        except urllib2.URLError, e:
            print e
            return False

    def login(self, name, password, tl = 'true', hashed = 'false'):
        url = self.myDAMURL + '/DAM/login' 
        params = {'name': name, 'pass': password, 'tl': tl, 'pass_hashed': hashed}
        try:
            params_urlencode = urllib.urlencode(params)
            req = urllib2.Request(url, params_urlencode)
            result_data = urllib2.urlopen(req)
            result = result_data.read()
            self.myApiKey = result
            print 'apikey =', self.myApiKey
            return result
        except urllib2.HTTPError, e:
            print e.code
            return '0'
        except urllib2.URLError, e:
            print e
            return '0'

    def openscene(self, folderName):
        url = self.myDAMURL + '/DAM/openScene'
        print 'key', self.myApiKey
        params = {'folderName': folderName, 'api_key': self.myApiKey}
        try:
            params_urlencode = urllib.urlencode(params)
            req = urllib2.Request(url, params_urlencode)
            result_data = urllib2.urlopen(req)
            result = result_data.read()
            print result
            return result
        except urllib2.HTTPError, e:
            print e.code
            return '0'
        except urllib2.URLError, e:
            print e
            return '0'

    def loginhost(self, name, password, hashed = '0'):
        url = '/global/api/authentication.cfc' 
        params = {'method': 'loginhost', 'name': name, 'pass': password, 'passhashed': hashed}
        return self.get(url, params)
    
    def getApiKey(self, name):
        url1 = self.myDAMURL + '/DAM/getApiKey'
        params = {'name': name}
        try:
            params_urlencode = urllib.urlencode(params)
            req = urllib2.Request(url1, params_urlencode)
            result_data = urllib2.urlopen(req)
            self.myApiKey = result_data.read()
            return True
        except urllib2.HTTPError, e:
            print e.code
            return False
        except urllib2.URLError, e:
            print e
            return False

    def getfolders(self, folderid = '0', collectionfolder = 'false'):
        url = "/global/api2/folder.cfc"
        params = {'method': 'getfolders','api_key': self.myApiKey, 'folderid': folderid,
                         'collectionfolder': collectionfolder}
        return self.get(url, params)
    
    def getfolder(self, folderid, foldername):
        url = "/global/api2/folder.cfc"
        if folderid == None:          
            params = {'method': 'getfolder','api_key': self.myApiKey, 'foldername': foldername}
        elif foldername == None:
            params = {'method': 'getfolder','api_key': self.myApiKey, 'folderid': folderid}
        else:
            params = {'method': 'getfolder','api_key': self.myApiKey, 'folderid': folderid, 'foldername': foldername}
        return self.get(url, params)

    def getassets(self, folderid, showsubfolders = 'false'):
        url = "/global/api2/folder.cfc"
        if showsubfolders :
            params = {'method': 'getassets', 'folderid': folderid, 'showsubfolders': 'true',
                                      'api_key': self.myApiKey}
        else:
            params = {'method': 'getassets', 'folderid': folderid, 'api_key': self.myApiKey}
        return self.get(url, params)

    def getasset(self, assetid, assettype):
        url = "/global/api2/asset.cfc"
        params = {'method': 'getasset', 'assetid': assetid, 'assettype': assettype, 'api_key': self.myApiKey}
        return self.get(url, params)

    def setfolder(self, folder_name, folder_related = '1', folder_colletcion = 'false'):
        url = "/global/api2/folder.cfc"
        if folder_related == '1':
            params = {'method': 'setfolder', 'folder_name': folder_name, 'api_key': self.myApiKey}
        else:
            params = {'method': 'setfolder', 'folder_name': folder_name, 'folder_colletcion': folder_colletcion,
                                     'folder_related': folder_related, 'api_key': self.myApiKey}
        print 'params =', params
        return self.get(url, params)

    def removefolder(self, folder_id):
        url = "/global/api2/folder.cfc"
        params = {'method': 'removefolder', 'folder_id': folder_id, 'api_key': self.myApiKey}
        result = self.get(url, params)
        print 'result =', result
        doc = xml.dom.minidom.parseString(result)
        status = doc.getElementsByTagName("ResponseCode")
        if status == '0':
            return True
        else:
            print doc.getElementsByTagName("message")
            return False

    def searchassets_maya(self, ext):
        url = "/global/api2/search.cfc"
        params = {'method': 'searchassets', 'api_key': self.myApiKey, 'searchfor': 'extension:(' + ext + ')',
                         'sortby': 'datechange'}
        return self.get(url, params)

    def gethosts(self):
        url = "/global/api2/hosts.cfc"
        params = {'method': 'gethosts', 'api_key': self.myApiKey}
        return self.get(url, params)

    def gethostsize(self, host_id):
        url = "/global/api2/hosts.cfc"
        params = {'method': 'gethostsize', 'host_id': host_id, 'api_key': self.myApiKey}
        return self.get(url, params)

    def upload(self, url, destfolderid, filedata):
        handlers = [poster.streaminghttp.StreamingHTTPHandler(), poster.streaminghttp.StreamingHTTPRedirectHandler(),
                            urllib2.HTTPCookieProcessor(cookielib.CookieJar())]
        urllib2.install_opener(urllib2.build_opener(*handlers))
        datagen, headers = poster.encode.multipart_encode({'fa': 'c.apiupload', 'destfolderid': destfolderid,
                            'api_key': self.myApiKey, "filedata": open(filedata, "rb")})
        request = urllib2.Request(self.url + url, datagen, headers)
        try:
            result = urllib2.urlopen(request).read()
            print 'result =', result
            doc = xml.dom.minidom.parseString(result)
            print 'doc =', doc
            status = doc.getElementsByTagName("message")
            if status == 'success':
                return True
            else:
                print doc.getElementsByTagName("message")
                return False
        except urllib2.HTTPError, e:
            print e.code
            return False
        except urllib2.URLError, e:
            print es
            return False
