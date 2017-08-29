
import os
import json
import ctypes
from PySide import QtGui
import MaxPlus
import RCConfig_max
import RCDialog_max
import RCService_max

class _GCProtector(object):
    widgets = []    
       
def doLogin():
    win = RCDialog_max.loginWindow(RCConfig_max.service)
    _GCProtector.widgets.append(win)
    win.show()

def doLogout():
    print "doLogout"
    
def doOpen():
    #RCConfig_max.storageDir = MaxPlus.PathManager.GetUserScriptsDir()
    win = RCDialog_max.openWindow(RCConfig_max.service)
    _GCProtector.widgets.append(win)
    win.show()

def doSave():
    win = RCDialog_max.saveWindow(RCConfig_max.service)
    _GCProtector.widgets.append(win)
    win.show()

def doSaveAs():
    win = RCDialog_max.saveAsWindow(RCConfig_max.service)
    _GCProtector.widgets.append(win)
    win.show()

def doSubmit():
    print "doSubmit"
    win = RCDialog_max.openWindow(RCConfig_max.service)
    _GCProtector.widgets.append(win)
    win.show()

def doRender():
    print "doRender"
    win = RCDialog_max.renderWindow(RCConfig_max.service)
    _GCProtector.widgets.append(win)
    win.show()

def doSetup():
    print "doSetup"
    win = RCDialog_max.setupWindow(RCConfig_max.service)
    _GCProtector.widgets.append(win)
    win.show()

def main():
    if RCConfig_max.dynamicStorageFlag:
        RCConfig_max.sysStorageDir = getStorageDir()
    else:
        RCConfig_max.sysStorageDir = MaxPlus.PathManager.GetUserScriptsDir()

    print 'storageDir =', RCConfig_max.sysStorageDir
    RCConfig_max.storageDir = RCConfig_max.sysStorageDir
    configFileName = RCConfig_max.sysStorageDir + RCConfig_max.ConfigFileName
    #self.service = None
    if os.path.exists(configFileName):
        fp = open(configFileName, 'r')
        config = json.load(fp)
        fp.close()
        RCConfig_max.userName = config['userName']
        RCConfig_max.password = config['password']
        RCConfig_max.storageDir = config['storageDir']
        try:
            RCConfig_max.teamName = config['teamName']
        except KeyError:
            pass

    if not RCConfig_max.teamName:
        print 'Error--Please Input the TeamName'
        return None

    app = QtGui.QApplication.instance()
    if not app:
        app = QtGui.QApplication([])

    RCConfig_max.service = RCService_max.DAMService()

    login_action = MaxPlus.ActionFactory.Create(u'登录', u'登录', doLogin)
    #login_action.Execute()
          
    logout_action = MaxPlus.ActionFactory.Create(u'退出', u'退出', doLogout)
    #logout_action.Execute()
    
    open_action = MaxPlus.ActionFactory.Create(u'我的任务', u'我的任务', doOpen)
    #open_action.Execute()

    save_action = MaxPlus.ActionFactory.Create(u'保存任务', u'保存任务', doSave)
    #save_action.Execute()

    save_action = MaxPlus.ActionFactory.Create(u'另存任务', u'另存任务', doSaveAs)
    #submit_action = MaxPlus.ActionFactory.Create(u'提交任务', u'提交任务', doSubmit)
    #submit_action.Execute()
    
       #render_action = MaxPlus.ActionFactory.Create(u'渲染', u'渲染', doRender)
    #render_action.Execute()

    setup_action = MaxPlus.ActionFactory.Create(u'设置', u'设置', doSetup)
    #setup_action.Execute()
            
    #print "Removing any previously left 'menu items'"
    MaxPlus.MenuManager.UnregisterMenu(u"RCMenu")
    #RCConfig_max.storageDir = MaxPlus.PathManager.GetTempDir()

    mb = MaxPlus.MenuBuilder('RCMenu')
    mb.AddItem(login_action)
    mb.AddItem(logout_action)
    mb.AddSeparator()
    
    mb.AddItem(open_action)
    mb.AddItem(save_action)
    #mb.AddItem(submit_action)
    mb.AddSeparator()
    #mb.AddItem(render_action)
    mb.AddSeparator()
    mb.AddItem(setup_action)
    
    menu = mb.Create(MaxPlus.MenuManager.GetMainMenu())


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
    path = path + RCConfig_max.project_Dir
    if not os.path.exists(path):
        os.mkdir(path)
    return path

if __name__ == '__main__':
    main()


