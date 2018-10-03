
# -*- coding: utf-8 -*-
#coding=utf-8

import urllib
import urllib2
import cookielib
import xml.dom.minidom
import time
import re
import streaminghttp
import encode
import os

import hashlib
import json
from PySide import QtGui

import CGConfig_max

from pymongo import MongoClient
from gridfs import *
from bson.objectid import ObjectId
import bson.binary
from cStringIO import StringIO

monthInfo = {u'一月': 'January', u'二月': 'February', u'三月': 'March', u'四月':'April',
                u'五月': 'May', u'六月': 'June', u'七月': 'July', u'八月': 'Aguest',
                u'九月': 'September', u'十月': 'October', u'十一月': 'November', u'十二月': 'December'}

class DAMService():
    def init(self):
        pass

    def send_noToken(self, url, params, timeout=0):
        try:
            headers = {'Content-Type': 'Application/json'}
            data = json.dumps(params)
            req = urllib2.Request(url, data, headers)
            if timeout > 0:
                time.sleep(timeout)
            result_data = urllib2.urlopen(req)
            result = result_data.read()
            result_data.close()
            return json.loads(result)
        except urllib2.HTTPError, e:
            print 'url1 =', url, e.code
            return {'status': 1, 'message': u'HTTP Error'}
        except urllib2.URLError, e:
            print 'url2 =', url, e
            return {'status': 1, 'message': u'应用服务器没有启动。。。。'}

    def send(self, url, params = '', timeout = 0):
        headers = {'Authorization': 'JWT ' + CGConfig_max.userToken['teamToken']}
        try:
            data = urllib.urlencode(params)
            req = urllib2.Request(url, data, headers)
            if timeout > 0:
                time.sleep(timeout)
            result_data = urllib2.urlopen(req)
            result = result_data.read()
            result_data.close()
            return result
        except urllib2.HTTPError, e:
            print 'url =', url, e.code
            return '0'
        except urllib2.URLError, e:
            print 'url =', url, e.code
            return '1'

    def login(self, name, password):
        result = self.send_noToken(CGConfig_max.myRootURL + '/cgserver/login',
                                 {'username': name, 'password': password, 'team': CGConfig_max.teamName})
        if result['status'] == 1:
            if result['message'].find('User') > 0:
                return False, u'用户不存在！！！'
            elif result['message'].find('password') > 0:
                return False, u'密码不正确！！！'
        CGConfig_max.userToken = result
        CGConfig_max.teamInfo = CGConfig_max.userToken['team']
        #print 'teamInfo =', CGConfig_maya.teamInfo
        self.myDAMURL = CGConfig_max.teamInfo['apiUrl']
        return True, None

    def myWFGetAllTeams(self):
        print 'myWFGetAllTeams'
        result = self.send_noToken(CGConfig_max.myRootURL + '/cgserver/getAllTeams', {})
        print result
        if result['status'] == 1:
            return False, result['message']
        else:
            return True, result['team']

    def getuser(self):
        print 'apiKey =', self.myApiKey
        return self.send(self.myDAMURL + '/DAM/getUser', {'apiKey': self.myApiKey})

    def openscene(self, folderName):
        return self.send(self.myDAMURL + '/DAM/openScene',
                                 {'folderName': folderName, 'api_key': self.myApiKey})

    def submitjob(self, userName, jobName, projectName, sceneName, pluginName, frameList):
        return self.send(self.myDAMURL + '/rest/jobSubmit',
                                 {'user': userName, 'job': jobName, 'project': projectName, 'scene': sceneName,
                                                'engine': pluginName, 'frameList': frameList})

    def getOuputDir(self, userName, jobName, projectName, sceneName):
        return self.send(self.myDAMURL + '/rest/getOuputDir',
                                 {'user': userName, 'job': jobName, 'project': projectName, 'scene': sceneName})

    def makeOutputDir(self, userName, jobName, projectName, sceneName):
        return self.send(self.myDAMURL + '/rest/makeOutputDir',
                                 {'user': userName, 'job': jobName, 'project': projectName, 'scene': sceneName})

    def copyfiles(self, userName, jobName, projectName, sceneName, mayaPathList, texturePathList):
        return self.send(self.myDAMURL + '/DAM/copyFiles',
            {'userName': userName, 'jobName': jobName, 'project': projectName, 'sceneName': sceneName,
                                                'mayaPathList': mayaPathList, 'texturePathList': texturePathList})

    def TBAuth(self):
        return self.send(self.myDAMURL + '/TB/auth')

    def myWFGetMyTask(self, user):
        return self.send(self.myDAMURL + '/cgteam/getMyTasks', {'user': user})

    def myWFGetProjects(self, user):
        return self.send(self.myDAMURL + '/cgteam/getProjects', {'user': user})

    def myWFGetTasksOfProjectByStage(self, projectName, stage):
        print projectName, stage
        return self.send(self.myDAMURL + '/cgteam/getTasksOfProjectByStage', {'projectName': projectName, 'stage': stage})

    def myWFGetTasksOfProject(self, projectName):
        return self.send(self.myDAMURL + '/cgteam/getTasksOfProject', {'projectName': projectName})

    def myWFGetInvolvesTask(self, user):
        return self.send(self.myDAMURL + '/cgteam/getMyInvolvesTasks', {'user': user})

    def myWFGetProjectTask(self, projectName):
        return self.send(self.myDAMURL + '/cgteam/getTasksOfProject', {'projectName': projectName})

    def myWFGetParentProjectInfo(self, projectName):
        return self.send(self.myDAMURL + '/cgteam/getParentProjectInfo', {'projectName': projectName})

    def myWFGetProjectInfo(self, projectName):
        return self.send(self.myDAMURL + '/cgteam/getProjectInfo', {'name': projectName})

    def myWFSubmitTask(self, task):
        return self.send(self.myDAMURL + '/cgteam/submitTask', {'taskName': task['name'], 'projectName': task['projectName']})

    def myWFReturnTask(self, taskName, projectName, upfolderid):
        return self.send(self.myDAMURL + '/DAM/returnTask', {'taskName': taskName, 'projectName': projectName, 'upfolderid': upfolderid})

    def myWFLightTask(self, taskName, projectName, upfolderid):
        return self.send(self.myDAMURL + '/DAM/lightTask', {'taskName': taskName, 'projectName': projectName, 'upfolderid': upfolderid})

    def myWFSetTaskAsset(self, id, taskName, projectName, IconFileID, fileID, textureFileID, note, assetVersion, plugin, frameList):
        return self.send(self.myDAMURL + '/cgteam/setTaskAsset', {'id': id, 'taskName': taskName, 'projectName': projectName,
                                'IconFileID': IconFileID, 'fileID': fileID, 'textureFileID': textureFileID,
                                'note': note, 'assetVersion': assetVersion, 'plugin': plugin, 'frameList': frameList})

    def myWFSetTaskAssetID4(self, id, textureZIPFileID):
        return self.send(self.myDAMURL + '/cgteam/setTaskAssetID4', {'id': id, 'textureZIPFileID': textureZIPFileID})

    def TBUpdateTaskStatus(self, task, status):
        return self.send(self.myDAMURL + '/TB/updateTaskStatus', {'taskID': task['_id'], 'status': status})

    def TBSubmitTask(self, taskID):
        return self.send(self.myDAMURL + '/TB/submitTask', {'taskID': taskID})

    def loginhost(self, name, password, hashed = '0'):
        url = '/global/api/authentication.cfc'
        params = {'method': 'loginhost', 'name': name, 'pass': password, 'passhashed': hashed}
        return self.get(url, params)

    def getApiKey(self, name):
        result = self.send(self.myDAMURL + '/DAM/getApiKey', {'name': name})
        #self.myApiKey = result
        return result

    def getfolders(self, folderid = '0', collectionfolder = 'false'):
        url = "/global/api2/folder.cfc"
        print 'myApiKey =', self.myApiKey
        if folderid ==  '0':
            params = {'method': 'getfolders','api_key': self.myApiKey}
        else:
            params = {'method': 'getfolders','api_key': self.myApiKey, 'folderid': folderid,
                         'collectionfolder': collectionfolder}
        return self.get(url, params)

    def getallfolders(self, projectList):
        return self.send(self.myDAMURL + '/DAM/getAllFolders', {'projectIDList': projectList})

    def getfolder(self, folderid, foldername):
        url = "/global/api2/folder.cfc"
        if folderid == '':
            params = {'method': 'getfolder','api_key': self.myApiKey, 'foldername': foldername}
        elif foldername == '':
            params = {'method': 'getfolder','api_key': self.myApiKey, 'folderid': folderid}
        else:
            params = {'method': 'getfolder','api_key': self.myApiKey, 'folderid': folderid, 'foldername': foldername}
        return self.get(url, params)
    """
    def getassets(self, folderid, show = 'all'):
        url = "/global/api2/folder.cfc"
        params = {'method': 'getassets', 'folderid': folderid, 'show': show, 'api_key': self.myApiKey}
        return self.get(url, params)
    """
    def getassets(self, folderid, show = 'all'):
        url = "/global/api2/folder.cfc"
        params = {'method': 'getassets', 'folderid': folderid, 'show': show, 'api_key': self.myApiKey}
        result = self.get(url, params)
        dataList = json.loads(result)
        if dataList['DATA'][0][0] == '1':
            return []
        assetList = []
        for asset in dataList['DATA']:
            #print asset
            assetList.append({'id': asset[0], 'name': asset[1], 'URL': asset[19]})
        return assetList

    def getassets_last(self, folderid, show = 'all'):
        url = "/global/api2/folder.cfc"
        params = {'method': 'getassets', 'folderid': folderid, 'show': show, 'api_key': self.myApiKey}
        result = self.get(url, params)
        data = json.loads(result)
        if data['DATA'][0][0] == '1':
            return '', ''
        fileList = []
        if show == 'doc':
            for arr in data['DATA']:
                ext = arr[1].split('.').pop()
                if ext == 'mb' or ext == 'ma':
                    fileList.append(arr)
        elif show == 'img':
            for arr in data['DATA']:
                ext = arr[1].split('.').pop()
                if ext == 'png':
                    fileList.append(arr)

        array = []
        timeStamp1 = 0
        fn = None
        for arr in fileList:
            if arr[0] == '1':
                return None
            l = arr[17]
            ll = l.split(',')
            lll = ll[0]
            #汉字
            if re.match('[ \u4e00 -\u9fa5]+', ll[0]) == None:
                mm = monthInfo[lll]
            else:
                mm = ll[0]
            #print mm
            if mm != None:
                str = mm + ', ' + ll[1]
            ti2 = time.strptime(str, "%B, %d %Y %H:%M:%S")
            timeStamp2 = int(time.mktime(ti2))
            if timeStamp2 > timeStamp1:
                array = arr
                timeStamp1 = timeStamp2
        return array[19], array[0]

    def removeasset(self, assetid):
        url = "/global/api2/asset.cfc"
        params = {'method': 'remove', 'assetid': assetid, 'api_key': self.myApiKey}
        return self.get(url, params)

    def convert(self, strDate):
        ll = strDate.split(',')
        lll = ll[0]
        # 汉字
        if re.match('[ \u4e00 -\u9fa5]+', ll[0]) == None:
            mm = monthInfo[lll]
        else:
            mm = ll[0]
        # print mm
        if mm != None:
            str = mm + ', ' + ll[1]
        ti = time.strptime(str, "%B, %d %Y %H:%M:%S")
        return int(time.mktime(ti))

    def myCompare(self, a, b):
        ti1 = self.convert(a[17])
        ti2 = self.convert(b[17])
        if ti1 > ti2:
            return 1
        elif ti1 < ti2:
            return -1
        else:
            return 0

    def getassets_sort(self, folderid, show='all'):
        url = "/global/api2/folder.cfc"
        params = {'method': 'getassets', 'folderid': folderid, 'show': show, 'api_key': self.myApiKey}
        result = self.get(url, params)
        data = json.loads(result)
        if data['DATA'][0][0] == '1':
            return []
        list = []
        for arr in data['DATA']:
            list.append(arr)
        list.sort(cmp = self.myCompare)
        return list

    def getassets_last_all(self, folderid):
        url = "/global/api2/folder.cfc"
        params = {'method': 'getassets', 'folderid': folderid, 'show': 'all', 'api_key': self.myApiKey}
        retList = []
        result = self.get(url, params)
        data = json.loads(result)
        #print 'data=', data['DATA']
        if data['DATA'][0][0] == '1':
            return retList

        for arr in data['DATA']:
            #print arr[1]
            bExist = False
            for ret in retList:
                if ret['fileName'] == arr[1]:
                    bExist = True
                    break
            if bExist:
                continue

            fileList = []
            for arr1 in data['DATA']:
                if arr[1] == arr1[1]:
                    fileList.append(arr1)

            #print 'fileList =', fileList
            if len(fileList) == 1:
                retList.append({'fileName': arr[1], 'URL': fileList[0][19], 'ID': fileList[0][0]})
                continue

            array = []
            timeStamp1 = 0
            fn = None
            #print 'fileList =', fileList
            for arr2 in fileList:
                l = arr2[17]
                ll = l.split(',')
                lll = ll[0]
                #汉字
                if re.match('[ \u4e00 -\u9fa5]+', ll[0]) == None:
                    mm = monthInfo[lll]
                else:
                    mm = ll[0]
                #print mm
                if mm != None:
                    str = mm + ', ' + ll[1]
                ti2 = time.strptime(str, "%B, %d %Y %H:%M:%S")
                timeStamp2 = int(time.mktime(ti2))
                if timeStamp2 > timeStamp1:
                    array = arr2
                    timeStamp1 = timeStamp2
            if array:
                retList.append({'fileName': arr[1], 'URL': array[19], 'ID': array[0]})
        return retList

    def getasset(self, assetid, assettype):
        url = "/global/api2/asset.cfc"
        params = {'method': 'getasset', 'assetid': assetid, 'assettype': assettype, 'api_key': self.myApiKey}
        #print 'params =', params
        result = self.get(url, params)
        assetData = json.loads(result)
        return {'id': assetData['DATA'][0][0], 'name': assetData['DATA'][0][2], 'URL': assetData['DATA'][0][21]}

    def setfolder(self, folder_name, folder_related = '1', folder_colletcion = 'false'):
        url = "/global/api2/folder.cfc"
        if folder_related == '1':
            params = {'method': 'setfolder', 'folder_name': folder_name, 'api_key': self.myApiKey}
        else:
            params = {'method': 'setfolder', 'folder_name': folder_name, 'folder_colletcion': folder_colletcion,
                                     'folder_related': folder_related, 'api_key': self.myApiKey}
        result = self.get(url, params)
        array = json.loads(result)
        print 'self.myApiKey =', self.myApiKey
        print 'result =', result
        if array["responsecode"] == 0:
            return array["folder_id"]
        else:
            print 'setfolder is error'
            return None

    def removefolder(self, folder_id):
        url = "/global/api2/folder.cfc"
        params = {'method': 'removefolder', 'folder_id': folder_id, 'api_key': self.myApiKey}
        result = self.get(url, params)
        doc = xml.dom.minidom.parseString(result)
        status = doc.getElementsByTagName("ResponseCode")
        if status == '0':
            return True
        else:
            print doc.getElementsByTagName("message")
            return False

    def searchassets_ext(self, ext):
        url = "/global/api2/search.cfc"
        params = {'method': 'searchassets', 'api_key': self.myApiKey, 'searchfor': 'extension:(' + ext + ')'}
        return self.get(url, params)

    def searchassets_ext(self, ext):
        url = "/global/api2/search.cfc"
        params = {'method': 'searchassets', 'api_key': self.myApiKey, 'searchfor': 'extension:(' + ext + ')'}
        return self.get(url, params)

    def adduser(self, username, password, email):
        url = "/global/api2/user.cfc"
        params = {'method': 'add', 'api_key': self.myApiKey, 'user_first_name': username,
                           'user_last_name': username, 'user_email': email,
                           'user_name': username, 'userpass': password, 'user_active': 'true'}
        return self.get(url, params)

    def gethosts(self):
        url = "/global/api2/hosts.cfc"
        params = {'method': 'gethosts', 'api_key': self.myApiKey}
        return self.get(url, params)

    def gethostsize(self, host_id):
        url = "/global/api2/hosts.cfc"
        params = {'method': 'gethostsize', 'host_id': host_id, 'api_key': self.myApiKey}
        return self.get(url, params)

    def setmetadata(self, assetid, assettype, assetmetadata):
        url = "/global/api2/asset.cfc"
        params = {'method': 'setmetadata', 'assetid': assetid, 'assettype': assettype,
                                     'assetmetadata': assetmetadata,'api_key': self.myApiKey}
        return self.get(url, params)

    def getmetadata(self, assetid, assettype, assetmetadata):
        url = "/global/api2/asset.cfc"
        params = {'method': 'getmetadata', 'assetid': assetid, 'assettype': assettype,
                                     'assetmetadata': assetmetadata,'api_key': self.myApiKey}
        return self.get(url, params)

    def upload(self, url, destfolderid, filedata, zip_extract = 'false'):
        handlers = [streaminghttp.StreamingHTTPHandler(), streaminghttp.StreamingHTTPRedirectHandler(),
                            urllib2.HTTPCookieProcessor(cookielib.CookieJar())]
        urllib2.install_opener(urllib2.build_opener(*handlers))
        datagen, headers = encode.multipart_encode({'fa': 'c.apiupload', 'destfolderid': destfolderid, 'zip_extract': zip_extract,
                            'api_key': self.myApiKey, "filedata": open(filedata, "rb")})
        request = urllib2.Request(self.url + url, datagen, headers)
        try:
            result = urllib2.urlopen(request).read()
            doc = xml.dom.minidom.parseString(result)
            #print doc.getElementsByTagName("responsecode")[0].firstChild.data
            if doc.getElementsByTagName("responsecode")[0].firstChild.data == '0':
                ret = {'status': '0', 'message': doc.getElementsByTagName("message")[0].firstChild.data,
                                      'assetid': doc.getElementsByTagName("assetid")[0].firstChild.data,
                                      'filetype': doc.getElementsByTagName("filetype")[0].firstChild.data}
                print 'ret =', ret
                return ret
            else:
                ret = {'status': '1', 'message': doc.getElementsByTagName("message")[0].firstChild.data}
                return ret
        except urllib2.HTTPError, e:
            ret = {'status': '2', 'message': 'HTTPError'}
            print e.code
            return ret
        except urllib2.URLError, e:
            ret = {'status': '3', 'message': 'URLError'}
            print 'url:', url
            print e
            return ret

    def makefolder(self, upfolder_id, folder_name):
        result = self.getfolders(upfolder_id)
        data = json.loads(result)
        folder_id = None
        if data['DATA'] != []:
            for array in data['DATA']:
                if folder_name == array[1]:
                    folder_id = array[0]
                    break
        return folder_id

    def myDownload(self, url1, fileName, flag=True):
        if flag and os.path.isfile(fileName):
            return

        url = url1.replace('\\', '/')
        try:
            url_opener = urllib2.urlopen(url)
            # print url_opener
        except Exception, e:
            print 'open url error---1'
            print url
            print e
            return False
        if url_opener.code != 200:
            print 'return code is:%d' % (url_opener.code)
            return False
        if not url_opener.headers.has_key('Content-Length'):
            print 'no content length'
            return False
        content_length = long(url_opener.headers['Content-Length'])

        # gMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar');
        if CGConfig_max.lang == 'zh':
            status = u'正在下载文件：' + url[url.rfind('/') + 1:]
        else:
            status = u'download File：' + url[url.rfind('/') + 1:]
        """
        cmds.progressBar( gMainProgressBar,
                                    edit=True,
                                    beginProgress=True,
                                    isInterruptable=True,
                                    status=status
                                    )
        """
        download_size = 0
        target_file = open(fileName, 'wb')
        while download_size < content_length:
            try:
                str_content = url_opener.read(1024)
            except Exception, e:
                print 'read error:%s' % (str(e))
                return
            if not str_content or len(str_content) == 0:
                print 'read error, connection close'
                return
            target_file.write(str_content)
            download_size += len(str_content)

            # cmds.progressBar(gMainProgressBar, edit=True, step=int(float(download_size)/float(content_length)*100.0))
        # cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
        print 'file has download: ', fileName
        return True

    def getUploadURL(self):
        """
        result = self.service.gethosts()
        data = json.loads(result)
        for array in data['DATA']:
            if array[0] == '1':
                return None
            if array[1] == 'Demo':
                hostPath = array[2]
                break
        url = '/' + hostPath + '/dam/index.cfm'
        """
        url = '/raz1/dam/index.cfm'
        return url

    def userActionLog(self, user, projectName, sceneName, action):
        count = 0
        return self.send(self.myDAMURL + '/rest/userActionLog', {'user': user,
                            'projectName': projectName, 'sceneName': sceneName, 'action': action, 'mouseCount': count})

    def setRazunaURL(self, host, port, appKey, uploadURL):
        self.url = 'http://'+ host + ':' + port + '/razuna'
        self.myApiKey = appKey
        CGConfig_max.myDAMURL = appKey
        CGConfig_max.uploadURL = uploadURL

    def DBOpen(self, pramaDB):
        print 'pramaDB =', pramaDB
        print 'teamInfo =', CGConfig_max.teamInfo
        client = MongoClient(CGConfig_max.teamInfo['mongoDBUrl_Out'])
        db = client[pramaDB]
        client.admin.authenticate(CGConfig_max.teamInfo['mongoDBUser'],
                                  CGConfig_max.teamInfo['mongoDBPassword'],
                                  mechanism='SCRAM-SHA-1', source='admin')
        return db


    def putFile(self, uploadFile, bType=True):
        db = self.DBOpen(CGConfig_max.teamInfo['mongoFileDBName'])
        filename = os.path.basename(uploadFile)
        with open(uploadFile, "rb") as f:
            if bType:
                fs = GridFS(db, collection='LargeFiles')
                invoice = fs.put(f.read(), encoding='utf-8', filename=filename)
            else:
                coll = db.SmallFiles
                content = StringIO(f.read())
                invoice = coll.save(dict(content=bson.binary.Binary(content.getvalue()), filename=filename))
        return invoice

    def getFileName(self, fileID, bType=True):
        if bType:
            db = self.DBOpen(CGConfig_max.teamInfo['mongoFileDBName'])
        else:
            db = self.DBOpen(CGConfig_max.teamInfo['mongoDBName'])

        if bType:
            fs = GridFS(db, collection='LargeFiles')
            file = fs.find_one({"_id": ObjectId(fileID)})
        else:
            coll = db.SmallFiles
            file = coll.find_one({"_id": ObjectId(fileID)})
            print fileID, file.filename
        return file.filename

    def getFile(self, localFile, fileID, bType=True):
        print 'localFile =', localFile
        if bType:
            db = self.DBOpen(CGConfig_max.teamInfo['mongoFileDBName'])
        else:
            db = self.DBOpen(CGConfig_max.teamInfo['mongoDBName'])

        if bType:
            fs = GridFS(db, collection='LargeFiles')
            with open(localFile, "wb") as f:
                data = fs.get(ObjectId(fileID)).read()
                f.write(data)
        else:
            coll = db.SmallFiles
            file = coll.find_one({"_id": ObjectId(fileID)})
            f = open(localFile.decode('utf-8'), "wb")
            f.write(file['content'])
        f.close()

    def listMaxFile(self, name):
        db = self.DBOpen(CGConfig_max.teamInfo['mongoFileDBName'])
        fs = GridFS(db, collection='LargeFiles')
        list = fs.find({'$or': [{'filename': name + '.max'}]})
        returnList =[]
        for ll in list:
            returnList.append({'id': ll._id, 'filename': ll.filename, 'uploadDate': ll.uploadDate})
        return returnList
