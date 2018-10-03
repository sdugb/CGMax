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
import zipfile
import MaxPlus
import json
import os
import CGConfig_max

assetTypes = {
    MaxPlus.AssetType.OtherAsset : "other",
    MaxPlus.AssetType.BitmapAsset : "bitmap",
    MaxPlus.AssetType.XRefAsset : "xref",
    MaxPlus.AssetType.PhotometricAsset : "photometric",
    MaxPlus.AssetType.AnimationAsset : "animation",
    MaxPlus.AssetType.VideoPost : "video post",
    MaxPlus.AssetType.BatchRender : "batch render",
    MaxPlus.AssetType.ExternalLink : "external link",
    MaxPlus.AssetType.RenderOutput : "render output",
    MaxPlus.AssetType.PreRenderScript : "pre-render script",
    MaxPlus.AssetType.PostRenderScript : "post-render script",
    MaxPlus.AssetType.SoundAsset : "sound",
    MaxPlus.AssetType.ContainerAsset : "container",
}

def judgelogData(logJsonData, fileName, id):
    bExist = 0
    for log in logJsonData:
        if log['fileName'] == fileName and log['id'] == id:
            bExist = 2
            break
        elif log['fileName'] == fileName and log['id'] != id:
            log['id'] = id
            bExist = 1
            break
    return bExist

def openTask(service, projectDir):
    taskDir = projectDir + '/' + CGConfig_max.currentTask['name']
    if not os.path.exists(taskDir):
        os.mkdir(taskDir)
    if CGConfig_max.fileID:
        scene_fn = readTaskFile(service, projectDir, taskDir, CGConfig_max.currentTask, CGConfig_max.razuna_Texture_Dir)
        MaxPlus.FileManager.Open(scene_fn)
        return True
    else:
        if CGConfig_max.currentTask['stage'] == u'场景' and CGConfig_max.baseModelTask:
            print CGConfig_max.currentTask['name']
            taskDir = projectDir + '/' + CGConfig_max.baseModelTask['name']
            if not os.path.exists(taskDir):
                os.mkdir(taskDir)
            baseFN = readTaskFile(service, projectDir, taskDir, CGConfig_max.baseModelTask, CGConfig_max.razuna_Texture_Dir)
            MaxPlus.FileManager.Open(baseFN)
            return True
        elif CGConfig_max.currentTask['stage'] == u'场景' and CGConfig_max.baseModelFile:
            MaxPlus.FileManager.Open(CGConfig_max.baseModelFile)
            return True
        else:
            return False

def readTaskFile(service, projectDir, taskDir, task, dirName):
    logPath = projectDir + '/' + CGConfig_max.razuna_Log_Dir
    if not os.path.exists(logPath):
        os.mkdir(logPath)
    logJsonData = []
    logFilePath = logPath + '/' + task['name'] + CGConfig_max.logFileExt
    if os.path.isfile(logFilePath):
        with open(logFilePath, "r") as json_file:
            logJsonData = json.load(json_file)

    if not os.path.exists(taskDir):
        os.mkdir(taskDir)
    fn = task['name'] + '.max'
    taskFileName = taskDir + '/' + fn
    bExist = judgelogData(logJsonData, fn, task['fileID'])
    bFlag = False
    #print 'bExist =', bExist
    if not os.path.exists(taskFileName) or bExist != 2:
        print '      File is Downloading:', taskFileName
        service.getFile(taskFileName, task['fileID'])
        if bExist == 0:
            logJsonData.append({"fileName": fn, 'id': task['fileID']})
            bFlag = True
    try:
        textureFileID = task['textureFileID']
    except KeyError:
        textureFileID = ''
    if textureFileID:
        textureDir = taskDir + '/' + dirName
        if not os.path.exists(textureDir):
            os.mkdir(textureDir)
        textureZipFile = textureDir + '/texture.zip'
        bExist = judgelogData(logJsonData, fn, textureFileID)
        #print 'bExist =', bExist
        if not os.path.exists(taskFileName) or bExist != 2:
            print '      File is Downloading:', textureZipFile
            service.getFile(textureZipFile, textureFileID)
            zf = zipfile.ZipFile(textureZipFile, 'r', zipfile.ZIP_DEFLATED, allowZip64=True)
            fileList = zf.namelist()
            #print 'fileList =', fileList
            zf.extractall(textureDir)
            zf.close()
            os.remove(textureZipFile)
            if bExist == 0:
                logJsonData.append({"fileName": fn, 'id': textureFileID})
                bFlag = True

    if bFlag:
        with open(logFilePath, "w") as json_file:
            json.dump(logJsonData, json_file)
    return taskFileName

def saveTask(service, scene_fn, frameListStr, description, assetSaveFlag):
    print CGConfig_max.currentTask
    projectName = CGConfig_max.currentTask['projectName']
    sceneName = CGConfig_max.currentTask['name']
    taskID = CGConfig_max.currentTask['_id']
    textureFileID = ''
    bFileFlag = False
    if assetSaveFlag:
        assetRawList = MaxPlus.AssetManager.GetAssets()
        print "There are ", len(assetRawList), " assets"
        assetList = []
        zipFileName = MaxPlus.PathManager.GetTempDir() + '/' + 'texture.zip'
        print 'zipFileName =', zipFileName
        zf = zipfile.ZipFile(zipFileName, "w", zipfile.ZIP_STORED, allowZip64=True)
        for i in range(len(assetRawList)):
            if not (assetTypes[assetRawList[i].Type] == 'bitmap'):
                continue
            print "fileName =", assetRawList[i].ResolvedFileName
            bFlag = True
            for j in range(len(assetList)):
                if assetList[j].ResolvedFileName == assetRawList[i].ResolvedFileName:
                    bFlag = False
                    break
            if bFlag:
                assetList.append(assetRawList[i])
                if os.path.isfile(assetRawList[i].ResolvedFileName):
                    bFileFlag = True
                    arcName = os.path.basename(assetRawList[i].ResolvedFileName)
                    zf.write(assetRawList[i].ResolvedFileName, arcName)
        print "There are ", len(assetList), " assets"
        zf.close()
        if bFileFlag:
            print '     Uploading File----zipfileName', zipFileName
            textureFileID = service.putFile(zipFileName)

    Dir = os.path.dirname(scene_fn)
    iconFN = Dir + '/' + sceneName + '.png'
    print 'iconFN =', iconFN

    render = MaxPlus.RenderSettings
    render.SetWidth(CGConfig_max.IconWidth)
    render.SetHeight(CGConfig_max.IconHeight)
    render.SetOutputFile(iconFN)
    render.SetSaveFile(True)
    MaxPlus.RenderExecute.QuickRender()

    print 'scene_fn =', scene_fn
    MaxPlus.FileManager.Save(scene_fn)
    print MaxPlus.FileManager.GetFileNameAndPath()
    fileID = service.putFile(scene_fn)
    #time.sleep(2)
    note = ''
    version = ''
    pluginStr = ''
    frameListStr = ''
    if os.path.isfile(iconFN):
        print 'iconFile is upload...'
        IconFileID = service.putFile(iconFN, False)
        service.myWFSetTaskAsset(taskID, sceneName, projectName, IconFileID, fileID, textureFileID, '', version,
                                 pluginStr, frameListStr)
    else:
        print 'iconFile is not exist'
        service.myWFSetTaskAsset(taskID, sceneName, projectName, '', fileID, textureFileID, '', version,
                             pluginStr, frameListStr)

    #service.myWFSetTaskAsset(taskID, sceneName, projectName, IconURL, assetid, textureFolder_id, note, version,
    #                         pluginStr, frameListStr, CGConfig_max.currentTask['upfolderid'])

    return True

def importModel(service, projectDir, taskList):
    #
    # MaxPlus.FileManager.Open()
    for task in taskList:
        if task['importFlag']:
            print 'taskName =', task['name']
            taskDir = projectDir + '/' + task['name']
            if not os.path.exists(taskDir):
                os.mkdir(taskDir)
            scene_fn = readTaskFile(service, projectDir, taskDir, task, CGConfig_max.razuna_Texture_Dir)
            print 'scene_fn =', scene_fn
            MaxPlus.FileManager.Merge(scene_fn)
    return True

def tarTask(service, projectDir, task):
    if task['assetID']:
        readTaskFile(service, projectDir, projectDir, task, 'maps')
        return True

def submitTask(service, projectName, sceneName, task, fileList):
    projectID = service.makefolder(service, CGConfig_max.parentProjectID, projectName)
    sceneID = service.makefolder(service, projectID, sceneName)
    fileFolder_id = service.makefolder(service, sceneID, CGConfig_max.razuna_Submit_Dir)
    if not fileFolder_id:
        result = service.setfolder(CGConfig_max.razuna_Submit_Dir, sceneID)
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

    projectID = makefolder(CGConfig_max.parentProjectID, projectName)
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
        if dd[1] == CGConfig_max.razuna_Texture_Dir:
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

def outputAssets():
    assetRawList = MaxPlus.AssetManager.GetAssets()
    print "There are ", len(assetRawList), " assets"
    assetList = []
    for i in range(len(assetRawList)):
        bFlag = True
        print assetRawList[i].ResolvedFileName
        for j in range(len(assetList)):
            print '    ', assetList[j]
            if assetList[j] == assetRawList[i].ResolvedFileName:
                print '            good'
                bFlag = False
                break
        if bFlag:
            assetList.append(assetRawList[i].ResolvedFileName)
    print "     There are ", len(assetList), " assets"
