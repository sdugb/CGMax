
import os
import sys
import json
import ctypes
import MaxPlus
import CGConfig_max
if CGConfig_max.softwareVersion == '3dsMax2018' or CGConfig_max.softwareVersion == '3dsMax2019':
    from PySide2 import QtGui, QtCore
elif CGConfig_max.softwareVersion == '3dsMax2016' or CGConfig_max.softwareVersion == '3dsMax2014':
    from PySide import QtGui, QtCore
else:
    pass

import CGDialog_max
import CGService_max

class _GCProtector(object):
    widgets = []    
       
def doLogin():
    CGConfig_max.service = CGService_max.DAMService()
    result, message = CGConfig_max.service.myWFGetAllTeams()
    print 'result =', result
    if not result:
        QtGui.QMessageBox.information(u"错误信息", message)
        return
    CGConfig_max.teamList = message
    if CGConfig_max.loginFlag:
        if CGConfig_max.lang == 'zh':
            QtGui.QMessageBox.information(u"警告信息", u"退出账号!!!")
        else:
            QtGui.QMessageBox.information(u"Warning", u"logout!!!")
    else:
        win = CGDialog_max.loginWindow(CGConfig_max.service)
        _GCProtector.widgets.append(win)
        win.show()

def doLogout():
    msgBox = QtGui.QMessageBox()
    if CGConfig_max.lang == 'zh':
        msgBox.setText(u"警告信息")
        msgBox.setInformativeText(u'是否退出账号？')
    else:
        msgBox.setText(u"Warning")
        msgBox.setInformativeText(u'Is Quit??？')
    msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
    msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
    ret = msgBox.exec_()
    if ret == QtGui.QMessageBox.OK:
        if CGConfig_max.loginFlag:
            configFileName = CGConfig_max.sysStorageDir + '/' + CGConfig_max.ConfigFileName
            print 'configFileName =', configFileName
            fp = open(configFileName, 'w')
            config = {'myRootURL': CGConfig_max.myRootURL,
                      'teamName': CGConfig_max.teamName,
                      'userName': CGConfig_max.userName,
                      'password': CGConfig_max.password,
                      'storageDir': CGConfig_max.storageDir
                      }
            json.dump(config, fp)
            fp.close()
            CGConfig_max.loginFlag = False
    elif ret == QtGui.QMessageBox.Cancel:
        return
    else:
        pass
    print "doLogout"
    
def doOpen():
    if CGConfig_max.loginFlag:
        win = CGDialog_max.openWindow(CGConfig_max.service)
        _GCProtector.widgets.append(win)
        win.show()
    CGConfig_max.openFlag = True

def doSave():
    if CGConfig_max.openFlag:
        win = CGDialog_max.saveWindow(CGConfig_max.service)
        _GCProtector.widgets.append(win)
        win.show()

def doSaveAs():
    if CGConfig_max.openFlag:
        win = CGDialog_max.saveAsWindow(CGConfig_max.service)
        _GCProtector.widgets.append(win)
        win.show()

def doImportModel():
    if CGConfig_max.openFlag:
        win = CGDialog_max.importModelWindow(CGConfig_max.service)
        _GCProtector.widgets.append(win)
        win.show()

def doImportFile():
    if CGConfig_max.openFlag:
        CGDialog_max.importFile(CGConfig_max.service)

def doAsset():
    CGDialog_max.outputAssets()

def doTarchive():
    win = CGDialog_max.tarchiveWindow(CGConfig_max.service)
    _GCProtector.widgets.append(win)
    win.show()

def doSubmit():
    print "doSubmit"
    win = CGDialog_max.openWindow(CGConfig_max.service)
    _GCProtector.widgets.append(win)
    win.show()

def doRender():
    print "doRender"
    win = CGDialog_max.renderWindow(CGConfig_max.service)
    _GCProtector.widgets.append(win)
    win.show()

def doSetup():
    print "doSetup"
    win = CGDialog_max.setupWindow(CGConfig_max.service)
    _GCProtector.widgets.append(win)
    win.show()

def main():
    print 'version =', sys.version
    if CGConfig_max.dynamicStorageFlag:
        CGConfig_max.sysStorageDir = getStorageDir()
    else:
        CGConfig_max.sysStorageDir = MaxPlus.PathManager.GetUserScriptsDir()
    print 'The Scripts directory is', MaxPlus.PathManager.GetScriptsDir()
    print 'The UserScripts directory is', MaxPlus.PathManager.GetUserScriptsDir()
    print 'storageDir =', CGConfig_max.sysStorageDir
    CGConfig_max.storageDir = CGConfig_max.sysStorageDir
    configFileName = CGConfig_max.sysStorageDir + '/' + CGConfig_max.ConfigFileName
    #self.service = None
    print 'configFileName =', configFileName
    if os.path.exists(configFileName):
        fp = open(configFileName, 'r')
        config = json.load(fp)
        print 'config =', config
        fp.close()
        CGConfig_max.userName = config['userName']
        CGConfig_max.password = config['password']
        CGConfig_max.storageDir = config['storageDir']
        CGConfig_max.teamName = config['teamName']
    app = QtGui.QApplication.instance()
    if not app:
        app = QtGui.QApplication([])
    login_action = MaxPlus.ActionFactory.Create(u'登录', u'登录', doLogin)
    logout_action = MaxPlus.ActionFactory.Create(u'退出', u'退出', doLogout)
    open_action = MaxPlus.ActionFactory.Create(u'我的任务', u'我的任务', doOpen)
    save_action = MaxPlus.ActionFactory.Create(u'保存任务', u'保存任务', doSave)
    saveAs_action = MaxPlus.ActionFactory.Create(u'另存任务', u'另存任务', doSaveAs)
    importModel_action = MaxPlus.ActionFactory.Create(u'导入模型', u'导入模型', doImportModel)
    importFile_action = MaxPlus.ActionFactory.Create(u'导入文件', u'导入文件', doImportFile)
    asset_action = MaxPlus.ActionFactory.Create(u'资产查询', u'资产查询', doAsset)
    tarchive_action = MaxPlus.ActionFactory.Create(u'归档', u'归档', doTarchive)
    #submit_action = MaxPlus.ActionFactory.Create(u'提交任务', u'提交任务', doSubmit)
    #render_action = MaxPlus.ActionFactory.Create(u'渲染', u'渲染', doRender)
    setup_action = MaxPlus.ActionFactory.Create(u'设置', u'设置', doSetup)

    MaxPlus.MenuManager.UnregisterMenu(u"CGMenu")
    #CGConfig_max.storageDir = MaxPlus.PathManager.GetTempDir()

    mb = MaxPlus.MenuBuilder('CGMenu')
    mb.AddItem(login_action)
    mb.AddItem(logout_action)
    mb.AddSeparator()
    
    mb.AddItem(open_action)
    mb.AddItem(save_action)
    mb.AddItem(saveAs_action)
    #mb.AddItem(submit_action)
    mb.AddSeparator()
    mb.AddItem(importModel_action)
    mb.AddItem(importFile_action)
    #mb.AddItem(render_action)
    mb.AddSeparator()
    mb.AddItem(asset_action)
    mb.AddItem(tarchive_action)
    mb.AddSeparator()
    mb.AddItem(setup_action)
    
    menu = mb.Create(MaxPlus.MenuManager.GetMainMenu())
    #CGConfig_max.menuLogoutItem.GetActionItem().Enabled = False
    #print menu.GetItem(0).IsEnabled

def getStorageDir():
    def get_free_space_mb(folder):
        """ Return folder/drive free space (in bytes)
        """
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None,
                                                       ctypes.pointer(free_bytes))
        return free_bytes.value / 1024 / 1024 / 1024

    def drivesList():
        drive_list = []
        for drive in range(ord('A'), ord('N')):
            if os.path.exists(chr(drive) + ':'):
                drive_list.append(chr(drive))
        return drive_list

    total = 0L
    for drive in drivesList():
        size = get_free_space_mb(drive + ':\\')
        if total < size:
            total = size
            path = drive + ':\\'
    path = path + CGConfig_max.project_Dir
    if not os.path.exists(path):
        os.mkdir(path)
    return path

if __name__ == '__main__':
    main()


