#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
import xml.dom.minidom
import time
import re
import streaminghttp
import encode
import hashlib
import MaxPlus
import json
import os
import RCConfig_max

def judgelogData(logJsonData, fileName, id):
    bExist = False
    for log in logJsonData:
        if log['fileName'] == fileName:
            if log['id'] == id:
                bExist = True
                log['id'] = id
                break
    return bExist

def openScene(service, projectName, sceneName, projectDir):
    sceneID = RCConfig_max.currentTask['assetFolderID']
    try:
        assetID = RCConfig_max.currentTask['assetID']
        textFolderID = RCConfig_max.currentTask['textureFolderID']
    except KeyError:
        textFolderID = ''
        assetID = ''
    if not textFolderID:
        textFolderID = service.makefolder(sceneID, RCConfig_max.razuna_Texture_Dir)

    if not os.path.exists(projectDir):
        os.mkdir(projectDir)
    textureDir = projectDir + '/' + RCConfig_max.razuna_Images_Dir
    if not os.path.exists(textureDir):
        os.mkdir(textureDir)

    logJsonData = []
    logPath = projectDir + '/' + RCConfig_max.razuna_Log_Dir
    if not os.path.exists(logPath):
        os.mkdir(logPath)
    logFilePath = logPath + '/' + sceneName + RCConfig_max.logFileExt
    if os.path.isfile(logFilePath):
        with open(logFilePath, "r") as json_file:
            logJsonData = json.load(json_file)

    bLog = False
    if textFolderID:
        textureList = service.getassets_last_all(textFolderID)
        for texture in textureList:
            bExist = judgelogData(logJsonData, texture['fileName'], texture['ID'])
            # ffn = os.path.join(textureDir, texture['fileName'])
            ffn = textureDir + '/' + texture['fileName']
            if os.path.isfile(ffn) and bExist:
                continue
            #print '      File is Downloading:', ffn
            service.myDownload(texture['URL'], ffn)
            logJsonData.append({"fileName": texture['fileName'], 'id': texture['ID']})
            bLog = True

    if bLog:
        with open(logFilePath, "w") as json_file:
            json.dump(logJsonData, json_file)

    if assetID:
        assetData = service.getasset(assetID, 'doc')
        url = assetData['URL']
    else:
        url = service.getassets_last(sceneID, 'doc')
    if not url:
        return False
    fn = url[url.rfind('/')+1:]
    #scene_fn = os.path.join(projectDir, fn)
    #scene_fn = projectDir + '/' + fn
    scene_fn = projectDir + '/' + sceneName
    #print 'File download: ', scene_fn
    service.myDownload(url, scene_fn, False)
    MaxPlus.FileManager.Open(scene_fn)

    MaxPlus.PathManager.SetImageDir(textureDir)
    #imageDir = MaxPlus.PathManager.GetImageDir()
    #print 'imageDir =', imageDir
    """
    assets = MaxPlus.AssetManager.GetAssets()
    print "There are ", len(assets), " assets"
    for i in range(len(assets)):
        print "    fileName =", assets[i].SpecifiedFileName
        #assets[i].ResolvedFileName = os.path.basename(assets[i].SpecifiedFileName)
        #print "fileName =", assets[i].SpecifiedFileName
    """
    return True

def saveScene(service, projectName, sceneName, scene_fn, pixmap, description):
    print RCConfig_max.currentTask
    projectName = RCConfig_max.currentTask['projectName']
    sceneName = RCConfig_max.currentTask['name']
    parentProjectID = RCConfig_max.currentTask['upfolderid']
    projectID = service.makefolder(parentProjectID, projectName)
    if not projectID:
        projectID = service.setfolder(projectName)
    sceneID = RCConfig_max.currentTask['assetFolderID']
    if not sceneID:
        sceneID = service.setfolder(sceneName, projectID)
    taskID = RCConfig_max.currentTask['_id']

    #print 'sceneID =', sceneID
    url = service.getUploadURL()
    result = service.upload(url, sceneID, scene_fn)
    assetid = result['assetid']

    Dir = os.path.dirname(scene_fn)
    iconFN = os.path.join(Dir, sceneName + '.png')

    render = MaxPlus.RenderSettings
    render.SetWidth(RCConfig_max.IconWidth)
    render.SetHeight(RCConfig_max.IconHeight)
    render.SetOutputFile(iconFN)
    render.SetSaveFile(True)
    MaxPlus.RenderExecute.QuickRender()
    service.upload(url, sceneID, iconFN)

    textureID = service.makefolder(sceneID, RCConfig_max.razuna_Texture_Dir)
    if not textureID:
        textureID = service.setfolder(RCConfig_max.razuna_Texture_Dir, sceneID)

    textAssetFileList1 = service.getassets(textureID)
    assets = MaxPlus.AssetManager.GetAssets()
    print "There are ", len(assets), " assets"
    for i in range(len(assets)):
        #print "fileName =", assets[i].ResolvedFileName
        textFile = assets[i].ResolvedFileName
        bExisted = True
        for textAssetFile in textAssetFileList1:
            if textAssetFile['name'] == os.path.basename(textFile):
                bExisted = False
                break
        if bExisted:
            if os.path.isfile(textFile):
                print '    textureFile is Uploading...', textFile
                #print 'textureID =', textureID
                ret = service.upload(url, textureID, textFile)
            else:
                print 'textureFile is not exist', textFile

    service.setmetadata(assetid, 'doc', '[["file_desc","' + description + '"]]')
    IconURL, id = service.getassets_last(sceneID, 'img')
    #service.myWFSetTaskAsset(sceneName, projectName, IconURL, sceneID, assetid)
    note = ''
    version = ''
    pluginStr = ''
    frameListStr = ''
    upFolderID = ''
    service.myWFSetTaskAsset(taskID, sceneName, projectName, IconURL, assetid, textureID, '', version,
                             pluginStr, frameListStr, upFolderID)
    return True

def submitTask(service, projectName, sceneName, task, fileList):
    projectID = service.makefolder(service, RCConfig_max.parentProjectID, projectName)
    sceneID = service.makefolder(service, projectID, sceneName)
    fileFolder_id = service.makefolder(service, sceneID, RCConfig_max.razuna_Submit_Dir)
    if not fileFolder_id:
        result = service.setfolder(RCConfig_max.razuna_Submit_Dir, sceneID)
        array = json.loads(result)
        fileFolder_id = array["folder_id"]
    print 'fileFolder_id =', fileFolder_id
    url = service.getUploadURL()
    for file in fileList:
        result = service.upload(url, fileFolder_id, file)
        if result['status'] != '0':
            continue

    result = service.myWFSubmitTask(task)

"""
def renderScene(service, userName, jobName, projectName, sceneName, PluginName, FrameList):
    plugin = PluginName
    frame = FrameList
    mayaPathList = ''
    texturePathList = ''

    projectID = makefolder(RCConfig_max.parentProjectID, projectName)
    sceneID = makefolder(projectID, sceneName)

    mayaPathList = service.getassets_last(sceneID, 'doc')
    result = self.getfolders(sceneID, 'false')
    data = json.loads(result)
    for dd in data['DATA']:
        result = self.getfolders(projectID, 'false')
        data1 = json.loads(result)
        for arr in data1['DATA']:
            if dd[1] == arr[1]:
                url = self.getassets_last(arr[0], 'doc')
                mayaPathList = mayaPathList + ',' + url.split('//')[2]
                break
    print 'mayaPath =', mayaPathList

    n = 0
    result = self.getfolders(projectID, 'false')
    data = json.loads(result)
    for dd in data['DATA']:
        if dd[1] == RCConfig_max.razuna_Texture_Dir:
            result = self.getassets(dd[0])
            data1 = json.loads(result)
            for arr in data1['DATA']:
                if arr[0] == '1':
                    continue
                fn = arr[19]
                fnl = fn.split('//')
                if n == 0:
                    texturePathList = fnl[2]
                else:
                    texturePathList = texturePathList + ',' + fnl[2]
                n = n + 1

    print 'texturePath =', texturePathList
    self.makeOutputDir(userName, jobName, projectName, sceneName)
    self.copyfiles(userName, jobName, projectName, sceneName, mayaPathList, texturePathList)

    sceneFileName = ''
    fileList = mayaPathList.split(',')
    f = fileList.pop()
    while f != '':
        fn = f.split('//').pop()
        ff = os.path.basename(fn)
        ffn = ff.split('.')
        if ffn[0] == sceneName:
            sceneFileName = ff
            break
        f = fileList.pop()
    print 'sceneFileName =', sceneFileName

    self.submitjob(userName, jobName, projectName, sceneFileName, plugin, frame)
"""
