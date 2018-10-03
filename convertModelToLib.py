#coding=utf-8

import sys
import os
import zipfile
import json
import urllib
import urllib2
import cookielib
import time
import re
import datetime
import xml.dom.minidom
import hashlib
import shutil
import fnmatch
import RCConfig_max
import RCService_max

rootDir = 'F:/test100GB/test'
mapsDir = 'F:/test100GB/maps'
projectName = 'test100GB'

service = RCService_max.DAMService()
result = service.myWFGetProjectInfo(projectName)
project = json.loads(result)
print project
service.setRazunaURL(project['DAMhost'], project['DAMport'], project['apiKey'])
projectID = project['projectID']

modelList = service.getfolders(projectID)

url = service.getUploadURL()
modelList = os.listdir(rootDir)
print 'ModelDirLis =', modelList
"""
for model in modelList:
    if modelDir == 'log':
        continue
    print 'assetName =', modelDir
    list = json.loads(service.myWFsearchTask(modelDir, projectName))
    if list:
        task = list[0]
    else:
        task = ''
    if modelDir.find('chr_') >= 0:
        modelClass = '角色'
    elif modelDir.find('loc_') >= 0:
        modelClass = '场景'
    elif modelDir.find('pro_') >= 0:
        modelClass = '道具'
    elif modelDir.find('lgt_') >= 0:
        modelClass = '灯光'
    else:
        modelClass = '其他'
    assetFolderID = service.makefolder(projectID, modelDir)
    if not assetFolderID:
        assetFolderID = service.setfolder(modelDir, projectID, 'false')
    textureFolderID = service.makefolder(assetFolderID, 'texture')
    if not textureFolderID:
        textureFolderID = service.setfolder('texture', assetFolderID, 'false')
    if task:
        assetID = task['assetID']
        textureZIPFileID = task['textureZIPFileID']
    else:
        assetID = ''
        textureZIPFileID = ''
    astDir = rootDir + '/' + modelDir
    astList = os.listdir(astDir)
    for ast in astList:
        ext = ast.split(".").pop()
        assetFileName = astDir + '/' + ast
        if os.path.isfile(assetFileName) and (ext == 'ma' or ext == 'mb') and not assetID:
            print '     is Uploading...', assetFileName
            ret = service.upload(url, assetFolderID, assetFileName)
            if ret['status'] == '0':
                assetID = ret['assetid']
            else:
                print ret['message']
                assetID = ''
                break
        elif ast == 'texture' and not textureZIPFileID:
            textureDir = astDir + '/texture'
            zipFileName = textureDir + '/texture.zip'
            if not os.path.isfile(zipFileName):
                zf = zipfile.ZipFile(zipFileName, "w", zipfile.ZIP_STORED, allowZip64=True)
                textureFileList = os.listdir(textureDir)
                for textureFile in textureFileList:
                    if textureFile == 'texture.zip':
                        continue
                    TXFile = textureDir + '/' + textureFile
                    zf.write(TXFile, textureFile)
                zf.close()
            print '         is Uploading...', zipFileName
            ret = service.upload(url, textureFolderID, zipFileName)
            if ret['status'] == '0':
                textureZIPFileID = ret['assetid']
            else:
                print ret['message']
                textureZIPFileID = ''
                continue
    if task:
        service.myWFSetTaskAssetID1(task['_id'], assetID, task['textureFolderID'])
        service.myWFSetTaskAssetID4(task['_id'], textureZIPFileID)
    else:
        task = {'name': modelDir,
            'projectName': projectName,
            'software': 'maya 2014',
            'diffcult': 'C',
            'executor': 'ghc',
            'checkinor': 'ghc',
            'involvesMembers': ['zy', 'gb', 'klh'],
            'stage': u'标准光',
            'modelClass': modelClass,
            'assetFolderID': assetFolderID,
            'assetID': assetID,
            'assetVersion': 0,
            'textureFolderID': textureFolderID,
            'textureZIPFileID': textureZIPFileID}
        service.myWFCreateTask(task)
    #raw_input()
    """

