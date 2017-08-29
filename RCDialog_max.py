#!/usr/bin/python
# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore
import MaxPlus
import urllib2
import shutil
import copy
import os
import json
import RCConfig_max
import RCFunction_max
import RCService_max
#from timer import Timer


class pngDialog(QtGui.QDialog):
    def __init__(self, fileName, parent =None):
        super(pngDialog, self).__init__(parent)

        self.super_layout = QtGui.QHBoxLayout()
        self.main_layout = QtGui.QVBoxLayout()

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.image = QtGui.QImage()
        self.image.load(fileName)
        self.imageLabel = QtGui.QLabel('', self)
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.image))

        self.layout.addWidget(self.imageLabel)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.button = QtGui.QPushButton(u'关闭', self)
        else:
            self.button = QtGui.QPushButton(u'Close', self)

        self.layout.addWidget(self.button)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)
        self.button.clicked.connect(self.onClose)

        self.setLayout(self.main_layout)
        self.setGeometry(350, 350, 700, 700)
        self.show()

    def onClose(self):
        self.close()

class loginWindow(QtGui.QDialog):
    def __init__(self, service, parent = None):
        super(loginWindow, self).__init__(parent)
        # And now set up the UI
        self.setup_ui()
        self.service = service

    def setup_ui(self):
        self.main_layout =QtGui.QVBoxLayout()
        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.nameLabel = QtGui.QLabel(u'账号', self)
        self.nameText = QtGui.QLineEdit('zy', self)
        self.nameText.setEnabled(True)
        self.layout.addWidget(self.nameLabel, 0, 0)
        self.layout.addWidget(self.nameText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.passLabel = QtGui.QLabel(u'密码', self)
        self.passText = QtGui.QLineEdit('zy1234', self)
        self.passText.setEchoMode(QtGui.QLineEdit.Password)
        self.layout.addWidget(self.passLabel, 0, 0)
        self.layout.addWidget(self.passText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.button1 = QtGui.QPushButton(u'登录', self)
        self.button2 = QtGui.QPushButton(u'取消', self)
        self.layout.addWidget(self.button1, 1, 1)
        self.layout.addWidget(self.button2, 1, 0)
        self.button1.clicked.connect(self.onLogin)
        self.button2.clicked.connect(self.onCancel)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.setLayout(self.main_layout)
        self.setWindowTitle(u'用户登录')
        self.setGeometry(300, 300, 400, 200)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)

    def onLogin(self):
        username = self.nameText.text()
        password = self.passText.text()
        result = self.service.login(username, password)
        if result == '1':
            if RCConfig_max.lang == 'zh':
                QtGui.QMessageBox.information(self, u"错误信息", u"帐号或密码不正确!!!")
            else:
                QtGui.QMessageBox.information(self, u"Error", u"UserName or Password is not correct!!!")
        elif result == '2':
            if RCConfig_max.lang == 'zh':
                QtGui.QMessageBox.information(self, u"提示信息", u"后台应用服务未开启")
            else:
                QtGui.QMessageBox.information(self, u"Prompt", u"Portal Service is not opened")
        else:
            RCConfig_max.userName = username
            RCConfig_max.password = password
            #self.doCall(RCConfig_maya.userName, RCConfig_maya.password)
            #self.service.userActionLog(RCConfig_max.userName, '', '', 'login')
            self.close()

    def onCancel(self):
        self.close()

class openWindow(QtGui.QDialog):
    def __init__(self, service, parent = None):
        super(openWindow, self).__init__(parent)
        self.service = service
        self.taskFlag = False
        self.projectID = None
        self.sceneID = None
        self.textureID = None
        self.fileList = []
        self.returnFileList = []
        self.fileListIndex = -1
        self.bTaskSelected = False
        self.loadFlag = True
        self.setup_ui()

    def setup_ui(self):
        self.super_layout = QtGui.QHBoxLayout()
        self.main_layout = QtGui.QVBoxLayout()

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.projectLabel = QtGui.QLabel(u'项目', self)
            self.stageLabel = QtGui.QLabel(u'阶段', self)
            self.noteLabel = QtGui.QLabel(u'说明', self)
        else:
            self.projectLabel = QtGui.QLabel(u'Project', self)
            self.stageLabel = QtGui.QLabel(u'Stage', self)
            self.noteLabel = QtGui.QLabel(u'Note', self)
        self.projectText = QtGui.QLineEdit('', self)
        self.projectText.setEnabled(False)
        self.stageText = QtGui.QLineEdit('', self)
        self.stageText.setEnabled(False)
        self.noteText = QtGui.QLineEdit('', self)
        self.noteText.setEnabled(False)

        self.layout.addWidget(self.projectLabel, 0, 0)
        self.layout.addWidget(self.projectText, 0, 1)
        self.layout.addWidget(self.stageLabel, 0, 2)
        self.layout.addWidget(self.stageText, 0, 3)
        self.layout.addWidget(self.noteLabel, 0, 4)
        self.layout.addWidget(self.noteText, 0, 5)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)
        
        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setIconSize(QtCore.QSize(60, 60))

        self.GetTasks()
        self.main_layout.addWidget(self.listWidget)
        self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemDoubleClicked (QListWidgetItem*)"), self.onDoubleClickItem)
        self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemClicked (QListWidgetItem*)"), self.onClickItem)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.listWidget1 = QtGui.QListWidget(self)
        self.row_Hbox.setLayout(self.layout)
        self.layout.addWidget(self.listWidget1, 0, 0)
        self.main_layout.addWidget(self.row_Hbox)
        self.listWidget1.hide()

        self.listWidget1.connect(self.listWidget1, QtCore.SIGNAL("itemDoubleClicked (QListWidgetItem*)"),
                                 self.onDoubleClickItem1)
        self.listWidget1.connect(self.listWidget1, QtCore.SIGNAL("itemClicked (QListWidgetItem*)"), self.onClickItem1)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.radiobutton3 = QtGui.QRadioButton(u'版本文件', self)
            #self.radiobutton4 = QtGui.QRadioButton(u'灯光文件', self)
            self.radiobutton5 = QtGui.QRadioButton(u'回退文件', self)
            self.radiobutton6 = QtGui.QRadioButton(u'关闭', self)
            self.checkBox7 = QtGui.QCheckBox(u'装载', self)
        else:
            self.radiobutton3 = QtGui.QRadioButton(u'VersionFile', self)
            #self.radiobutton4 = QtGui.QRadioButton(u'LightFile', self)
            self.radiobutton5 = QtGui.QRadioButton(u'ReturnFile', self)
            self.radiobutton6 = QtGui.QRadioButton(u'Close', self)
            self.checkBox7 = QtGui.QCheckBox(u'Load', self)
        self.radiobutton3.setChecked(False)
        #self.radiobutton4.setChecked(False)
        self.radiobutton5.setChecked(False)
        self.radiobutton6.setChecked(True)
        if self.loadFlag:
            self.checkBox7.setChecked(True)
        else:
            self.checkBox7.setChecked(False)

        self.layout.addWidget(self.radiobutton3, 0, 0)
        self.layout.addWidget(self.radiobutton5, 0, 1)
        self.layout.addWidget(self.radiobutton6, 0, 2)
        self.layout.addWidget(self.checkBox7, 0, 3)
        self.radiobutton3.clicked.connect(self.onSetVersion)
        #self.radiobutton4.clicked.connect(self.onSetLight)
        self.radiobutton5.clicked.connect(self.onSetReturn)
        self.radiobutton6.clicked.connect(self.onSetClose)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        row = self.listWidget.currentRow()
        self.row_Hbox = QtGui.QGroupBox()
        layout1 = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.button1 = QtGui.QPushButton(u'打开', self)
            self.button2 = QtGui.QPushButton(u'取消', self)
            self.button3 = QtGui.QPushButton(u'刷新', self)
        else:
            self.button1 = QtGui.QPushButton(u'Open', self)
            self.button2 = QtGui.QPushButton(u'Cancel', self)
            self.button3 = QtGui.QPushButton(u'Refresh', self)
        layout1.addWidget(self.button3, 1, 0)
        layout1.addWidget(self.button1, 1, 2)
        layout1.addWidget(self.button2, 1, 1)
        self.button1.clicked.connect(self.onOpen)
        self.button2.clicked.connect(self.onCancel)
        self.button3.clicked.connect(self.onRefresh)
        self.row_Hbox.setLayout(layout1)
        self.main_layout.addWidget(self.row_Hbox)

        if RCConfig_max.lang == 'zh':
            self.setWindowTitle(u'打开任务')
        else:
            self.setWindowTitle(u'Open Task')

        self.setLayout(self.main_layout)
        self.setGeometry(350, 350, 650, 650)

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def myCompare(self, a, b):
        str1 = a['name'].lower()
        str2 = b['name'].lower()
        return cmp(str1, str2)

    def GetTasks(self):
        self.listWidget.clear()
        #with Timer() as t:
        print RCConfig_max.userName
        result = self.service.myWFGetMyTask(RCConfig_max.userName)
        #print "=> elasped : %s s" % t.secs

        if not result:
            return None
        RCConfig_max.tasks = []
        taskList = json.loads(result)
        #print 'tasks =', RCConfig_max.tasks

        taskList.sort(cmp = self.myCompare)
        textFont = QtGui.QFont("song", 16, QtGui.QFont.Normal)
        #print 'storageDir =', RCConfig_max.storageDir
        iconLogFilePath = os.path.join(RCConfig_max.storageDir, RCConfig_max.userName + RCConfig_max.iconLogFileExt)
        #print iconLogFilePath
        logJsonData = []
        if os.path.isfile(iconLogFilePath):
            with open(iconLogFilePath, "r") as json_file:
                logJsonData = json.load(json_file)
        bLog = False
        #with Timer() as t:
        for task in taskList:
            #if not task or not task['name']:
                #continue
            str = task['name']
            try:
                if not task['software'] == '3dsMax 2014':
                    continue
            except KeyError:
                continue
            #print str
            try:
                if task['isReturn']:
                    str = str.ljust(40, ' ') + 'X'
                else:
                    str = str.ljust(40, ' ')
            except KeyError:
                str = str.ljust(40, ' ')
            try:
                url = task['IconURL']
            except KeyError or ValueError:
                url = ''
            #print 'url =', url
            if url:
                fn = url.split('/').pop()
                iconFile = os.path.join(RCConfig_max.storageDir, fn)
                #iconFile = RCConfig_maya.storageDir + '/' + fn
                bExist = False
                for log in logJsonData:
                    if log['fileName'] == fn and log['URL'] == url:
                        bExist = True
                        break
                if not os.path.exists(iconFile) or not bExist:
                    try:
                        fp = urllib2.urlopen(url, timeout = 20)
                        stream = fp.read()
                        fp.close()
                        fw = open(iconFile, "wb")
                        fw.write(stream)
                        fw.close()
                        logJsonData.append({"fileName": fn, 'URL': url})
                        bLog = True
                    except  urllib2.HTTPError,e:
                        Dir = MaxPlus.PathManager.GetUserScriptsDir()
                        #print "Dir =", Dir
                        iconFile = Dir + 'aa.png'
            else:
                Dir = MaxPlus.PathManager.GetUserScriptsDir()
                #print 'Dir =', Dir
                #Dir = cmds.internalVar(userScriptDir = True)
                iconFile = Dir + '/aa.png'
            icon = QtGui.QIcon(iconFile)
            item = QtGui.QListWidgetItem(icon, '  ' + str)
            #item = QtGui.QListWidgetItem(str)
            item.setFont(textFont)
            self.listWidget.addItem(item)
            RCConfig_max.tasks.append(task)

        #print "=> elasped : %s s" % t.secs
        if bLog:
            with open(iconLogFilePath, "w") as json_file:
                json.dump(logJsonData, json_file)
        #print iconLogFilePath

    def onSetVersion(self):
        if not self.bTaskSelected:
            return
        #cmds.waitCursor(state=True)
        self.radiobutton3.setChecked(True)
        self.radiobutton5.setChecked(False)
        self.radiobutton6.setChecked(False)
        row = self.listWidget.currentRow()
        if not RCConfig_max.tasks[row]['assetFolderID']:
            projectID = self.service.makefolder(RCConfig_max.tasks[row]['upfolderid'], RCConfig_max.tasks[row]['projectName'])
            self.folderID = self.service.makefolder(projectID, RCConfig_max.tasks[row]['name'])
        else:
            self.folderID = RCConfig_max.tasks[row]['assetFolderID']
        self.assetData = self.service.getassets_sort(self.folderID, 'doc')
        self.listWidget1.show()
        textFont = QtGui.QFont("song", 12, QtGui.QFont.Normal)
        self.listWidget1.clear()
        for arr in self.assetData:
            desStr = arr[5]
            desStr = desStr.ljust(30, ' ') + arr[17] + '     ' + arr[0]
            item = QtGui.QListWidgetItem(desStr)
            item.setFont(textFont)
            self.listWidget1.addItem(item)
        #cmds.waitCursor(state=False)

    def onSetReturn(self):
        if not self.bTaskSelected:
            return
        row = self.listWidget.currentRow()
        self.listWidget1.show()
        self.listWidget1.clear()
        try:
            if not RCConfig_max.tasks[row]['isReturn']:
                self.listWidget1.hide()
                return
            self.radiobutton3.setChecked(False)
            #self.radiobutton4.setChecked(False)
            self.radiobutton5.setChecked(True)
            self.radiobutton6.setChecked(False)
            if not self.returnFileList:
                for i in range(0, len(self.returnFileList)):
                    self.returnFileList.pop()
        except KeyError:
            return
        result = self.service.myWFReturnTask(RCConfig_max.tasks[row]['name'], RCConfig_max.tasks[row]['projectName'],
                                                  RCConfig_max.tasks[row]['upfolderid'])
        self.returnFileList = json.loads(result)
        textFont = QtGui.QFont("song", 12, QtGui.QFont.Bold)
        for file in self.returnFileList:
            item = QtGui.QListWidgetItem(file['name'])
            item.setFont(textFont)
            self.listWidget1.addItem(item)

    def onSetClose(self):
        self.radiobutton3.setChecked(False)
        self.radiobutton5.setChecked(False)
        self.radiobutton6.setChecked(True)
        self.listWidget1.clear()
        self.listWidget1.hide()

    def onDoubleClickItem(self, item):
        self.onOpen()

    def onClickItem(self, item):
        row = self.listWidget.currentRow()
        self.projectText.setText(RCConfig_max.tasks[row]['projectName'])
        self.stageText.setText(RCConfig_max.tasks[row]['stage'])
        self.noteText.setText(RCConfig_max.tasks[row]['note'])
        self.fileListIndex = row
        self.noteText.setText(RCConfig_max.tasks[row]['note'])
        self.listWidget1.clear()
        RCConfig_max.assetID = ''
        result = self.service.myWFGetParentProjectInfo(RCConfig_max.tasks[row]['projectName'])
        parentProject = json.loads(result)
        """
        try:
            timeUnit = parentProject['timeUnit']
        except KeyError or ValueError:
            timeUnit = 'pal:25fps'
        if not timeUnit:
            time = timeUnit.split(':')[0]
            print 'time =', time
            cmds.currentUnit(time=time)
        """
        self.service.setRazunaURL(parentProject['DBHost'], parentProject['DBPort'], parentProject['appKey'])
        """
        try:
            url = RCConfig_maya.tasks[row]['IconURL']
        except KeyError or ValueError:
            url = ''
        try:
            RCConfig_maya.frameList = RCConfig_maya.tasks[row]['frameList']
        except KeyError or ValueError:
            RCConfig_maya.frameList = ''
        
        if not url:
            url, id = self.service.getassets_last(RCConfig_maya.tasks[row]['assetFolderID'], 'img')
            if url:
                try:
                    note = RCConfig_maya.tasks[row]['note']
                except KeyError or ValueError:
                    note = ''
                try:
                    version = RCConfig_maya.tasks[row]['version']
                except KeyError or ValueError:
                    version = ''
                try:
                    assetID = RCConfig_maya.tasks[row]['assetID']
                except KeyError or ValueError:
                    assetID = ''
                try:
                    plugin = RCConfig_maya.tasks[row]['plugin']
                except KeyError or ValueError:
                    plugin = ''
                self.service.myWFSetTaskAsset(RCConfig_maya.tasks[row]['_id'], RCConfig_maya.tasks[row]['name'],
                                              RCConfig_maya.tasks[row]['projectName'], url, assetID,
                                              id, note, version, plugin, RCConfig_maya.frameList,
                                              RCConfig_maya.tasks[row]['upfolderid'])
            if url:
                fp = urllib2.urlopen(url, timeout=20)
                stream = fp.read()
                fp.close()
                iconFile = os.path.join(RCConfig_maya.storageDir, url.split('/').pop())
                fw = open(iconFile, "wb")
                fw.write(stream)
                fw.close()
        # print RCConfig_maya.frameList
        if RCConfig_maya.frameList and (RCConfig_maya.tasks[row]['stage'] == u'布局' or \
                                                    RCConfig_maya.tasks[row]['stage'] == u'动画' or
                                                RCConfig_maya.tasks[row]['stage'] == u'灯光'):
            self.stageText.setText(RCConfig_maya.tasks[row]['stage'] + '(' + RCConfig_maya.frameList + ')')

        if RCConfig_maya.tasks[row]['stage'] == u'灯光':
            self.listWidget1.show()
            self.radiobutton4.setEnabled(True)
            self.radiobutton3.setChecked(False)
            self.radiobutton4.setChecked(True)
            self.radiobutton5.setChecked(False)
            self.radiobutton6.setChecked(False)
            self.listWidget1.clear()

            self.folderID = RCConfig_maya.tasks[row]['assetFolderID']
            self.loadLightFile()
        else:
            self.radiobutton4.setEnabled(False)
        """
        self.bTaskSelected = True

        if self.radiobutton3.isChecked():
            self.onSetVersion()

    def onDoubleClickItem1(self, item):
        self.fileListIndex = self.listWidget.currentRow()
        row = self.listWidget.currentRow()
        RCConfig_max.currentTask = self.taskList[row]
        try:
            RCConfig_max.assetID = RCConfig_max.currentTask['assetID']
        except KeyError:
            RCConfig_max.assetID = ''
        self.onOpen()
        """
        row = self.listWidget1.currentRow()
        RCConfig_max.currentTask = self.taskList[self.fileListIndex]
        folderid = RCConfig_max.currentTask['assetFolderID']
        if folderid == None or folderid == '':
            upfolderid = self.makefolder('', RCConfig_max.tasks[self.fileListIndex]['projectName'])
            if upfolder == None:
                return
            folderid = self.makefolder(upfolderid, RCConfig_max.tasks[self.fileListIndex]['name'])
        result = self.service.getfolders(folderid, 'false')
        data = json.loads(result)
        return_folderid = ''
        for dd in data['DATA']:
            if dd[1] == RCConfig_max.razuna_Return_Dir:
                return_folderid = dd[0]
                break
        if return_folderid == '':
            return
        url = self.service.getassets_last(return_folderid, 'img')
        print url
        if url != None:
            fn = url.split('/').pop()
            print 'fn =', fn
            ffn = os.path.join(RCConfig_max.storageDir, fn)
            self.myDownload(url, ffn)
            pngDialog(ffn)
        """

    def onClickItem1(self, item):
        pass

    def onCancel(self):
        #self.menu.setEnable(True)
        self.close()

    def onRefresh(self):
        self.GetTasks()

    def onOpen(self):
        currentRow = self.listWidget.currentRow()
        self.currentTask = copy.deepcopy(RCConfig_max.tasks[currentRow])
        RCConfig_max.currentTask = RCConfig_max.tasks[currentRow]
        #RCConfig_max.frameList = ''
        taskName = self.currentTask['name']
        RCConfig_max.sceneName = taskName
        projectName = self.currentTask['projectName']
        RCConfig_max.projectName = projectName
        RCConfig_max.taskIndex = self.fileListIndex

        result = self.service.myWFGetParentProjectInfo(projectName)
        ret = json.loads(result)
        RCConfig_max.parentProjectID = ret['parentProjectID']
        result = self.service.myWFGetProjectInfo(projectName)
        list = json.loads(result)
        RCConfig_max.project = list[0]
        # projectDir = os.path.join(RCConfig_maya.storageDir, projectName)
        projectDir = RCConfig_max.storageDir + '/' + projectName
        if not os.path.exists(projectDir):
            os.mkdir(projectDir)

        if not RCConfig_max.currentTask:
            self.close()
            return

        self.loadFlag = self.checkBox7.isChecked()
        if not self.loadFlag:
            self.close()
            return

        if not RCFunction_max.openScene(self.service, RCConfig_max.projectName, RCConfig_max.sceneName, projectDir):
            print 'Scene File is None'
            self.close()
            return

        self.service.userActionLog(RCConfig_max.userName, RCConfig_max.projectName, RCConfig_max.sceneName, 'open')
        self.close()

class saveWindow(QtGui.QDialog):
    def __init__(self, service, parent = None):
        super(saveWindow, self).__init__(parent)
        self.service = service
        self.fileNums = 0
        self.fileList = []
        self.setup_ui()

    def setup_ui(self):
        self.super_layout = QtGui.QHBoxLayout()
        self.main_layout = QtGui.QVBoxLayout()
        self.root_layout = QtGui.QVBoxLayout()

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.projectLabel = QtGui.QLabel(u'项目', self)
        else:
            self.projectLabel = QtGui.QLabel(u'Project', self)
        self.projectText = QtGui.QLineEdit(RCConfig_max.projectName, self)
        self.projectText.setEnabled(False)

        self.layout.addWidget(self.projectLabel, 0, 0)
        self.layout.addWidget(self.projectText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)


        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.sceneLabel = QtGui.QLabel(u'任务', self)
        else:
            self.sceneLabel = QtGui.QLabel(u'Scene', self)
        self.sceneText = QtGui.QLineEdit(RCConfig_max.sceneName, self)
        self.sceneText.setEnabled(False)
        self.layout.addWidget(self.sceneLabel, 0, 0)
        self.layout.addWidget(self.sceneText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.descriptionLabel = QtGui.QLabel(u'描述', self)
        else:
            self.descriptionLabel = QtGui.QLabel(u'Description', self)
        self.descriptionText = QtGui.QLineEdit('', self)
        self.sceneText.setEnabled(False)
        self.layout.addWidget(self.descriptionLabel, 0, 0)
        self.layout.addWidget(self.descriptionText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox1 = QtGui.QGroupBox()
        self.row_Hbox1.setLayout(self.main_layout)
        self.imageLabel = QtGui.QLabel()
        self.imageLabel.adjustSize()
        self.super_layout.addWidget(self.imageLabel)
        self.super_layout.addWidget(self.row_Hbox1)

        self.row_Hbox2 = QtGui.QGroupBox()
        self.row_Hbox2.setLayout(self.super_layout)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout4 = QtGui.QGridLayout()
        self.listWidget = QtGui.QListWidget(self)
        self.row_Hbox.setLayout(self.layout4)
        self.root_layout.addWidget(self.row_Hbox2, 0, 0)
        self.root_layout.addWidget(self.listWidget, 1, 0)
        self.listWidget.hide()

        self.row_Hbox = QtGui.QGroupBox()
        self.layout5 = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            #self.button3 = QtGui.QPushButton(u'截屏', self)
            self.button5 = QtGui.QPushButton(u'选择', self)
            self.button1 = QtGui.QPushButton(u'保存', self)
            self.button2 = QtGui.QPushButton(u'取消', self)
            self.button4 = QtGui.QPushButton(u'保存并提交', self)
        else:
            #self.button3 = QtGui.QPushButton(u'Capture', self)
            self.button5 = QtGui.QPushButton(u'Select', self)
            self.button1 = QtGui.QPushButton(u'Save', self)
            self.button2 = QtGui.QPushButton(u'Cancel', self)
            self.button4 = QtGui.QPushButton(u'Save&Submit', self)
        self.layout5.addWidget(self.button1, 2, 3)
        self.layout5.addWidget(self.button2, 2, 0)
        #self.layout5.addWidget(self.button3, 2, 0)
        self.layout5.addWidget(self.button4, 2, 2)
        self.layout5.addWidget(self.button5, 2, 1)
        self.button1.clicked.connect(self.onSave)
        self.button2.clicked.connect(self.onCancel)
        #self.button3.clicked.connect(self.onCapture)
        self.button4.clicked.connect(self.onSaveSubmit)
        self.button5.clicked.connect(self.onSelect)
        self.row_Hbox.setLayout(self.layout5)
        self.root_layout.addWidget(self.row_Hbox, 2, 0)

        self.setLayout(self.root_layout)
        #self.setLayout(self.main_layout)

        if RCConfig_max.lang == 'zh':
            self.setWindowTitle(u'保存任务')
        else:
            self.setWindowTitle(u'Save Task')
        self.setGeometry(300, 300, 600, 200)
        self.image = None

        """
        winptr = OpenMayaUI.MQtUtil.mainWindow()
        if winptr is None:
            raise RuntimeError('No Maya window found.')
        self.win = wrapinstance(winptr)
        #self.paint = QtGui.QPainter(self.win)
        #self.paint.setPen(QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
       
        pixmap1 = QtGui.QPixmap.grabWindow(self.win.winId())
        pixmap = pixmap1.scaled(60, 60)
        self.imageLabel.setPixmap(QtGui.QPixmap(pixmap))

        view = OpenMayaUI.M3dView.active3dView()
        widget_ptr = view.widget()
        widget = sip.wrapinstance(long(widget_ptr), QtCore.QObject)
        pixmap1 = QtGui.QPixmap.grabWidget(widget)
        pixmap = pixmap1.scaled(60, 60)
        self.imageLabel.setPixmap(QtGui.QPixmap(pixmap))
       
        Dir = os.path.join(RCConfig_max.storageDir, 'tmp.png')
        ret = cmds.playblast(frame = cmds.currentTime(q = True),
                       f = Dir,
                       fo = True, fmt = 'image', viewer = False,
                       c = 'PNG', quality = 60)
        print 'ret =', ret
        tmpFile = Dir + '.0000.png'
        print tmpFile
        pix = QtGui.QPixmap(tmpFile)
        pixmap = pix.scaled(RCConfig_max.IconWidth, RCConfig_max.IconHeight)
        self.imageLabel.setPixmap(QtGui.QPixmap(pixmap))
        """

    def onSave(self):
        projectDir = os.path.join(RCConfig_max.storageDir, RCConfig_max.projectName)
        if not os.path.exists(projectDir):
            os.mkdir(projectDir)

        fn = os.path.join(projectDir, RCConfig_max.sceneName)

        fm = MaxPlus.FileManager
        scene_fn = os.path.join(RCConfig_max.storageDir, fn + '.max')
        print 'scenn_fn =', scene_fn
        fm.Save(scene_fn)
        print fm.GetFileNameAndPath()
        if not RCFunction_max.saveScene(self.service, RCConfig_max.projectName, RCConfig_max.sceneName, scene_fn,
                                         None, self.descriptionText.text()):
            self.close()
            return
        self.service.userActionLog(RCConfig_max.userName, RCConfig_max.projectName, RCConfig_max.sceneName, 'save')
        self.close()

    def onSaveSubmit(self):
        if self.fileNums == 0:
            if RCConfig_max.lang == 'zh':
                QtGui.QMessageBox.information( self, u"提示信息", u"没有选择单帧效果图!!!")
            else:
                QtGui.QMessageBox.information( self, u"Prompt", u"NO File Upload!!!")
        else:
            self.onSave()
            RCFunction_max.submitTask(self.service, RCConfig_max.projectName, RCConfig_max.sceneName,
                                      RCConfig_max.currentTask, self.fileList)

            self.service.userActionLog(RCConfig_max.userName, RCConfig_max.projectName, RCConfig_max.sceneName, 'submit')
            self.close()

    def onCancel(self):
        self.close()
        
    def onCapture(self):
        if RCConfig_max.lang == 'zh':
            dialog = QtGui.QFileDialog(self, "选择截屏文件", ".", "所有File(*.*)")
        else:
            dialog = QtGui.QFileDialog(self, "Select File", ".", "all File(*.*)")
        dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        if dialog.exec_():
            file = dialog.selectedFiles()
            print 'file =', file[0]
            pix = QtGui.QPixmap(file[0])
            pixmap = pix.scaled(60, 60)
            self.imageLabel.setPixmap(QtGui.QPixmap(pixmap))

    def onSelect(self):
        self.listWidget.show()
        fm = MaxPlus.FileManager
        fm.Open()
        print fm.GetFileNameAndPath()
        """
        if RCConfig_max.lang == 'zh':
            dialog = QtGui.QFileDialog(self, "选择文件", ".", "*.*")
        else:
            dialog = QtGui.QFileDialog(self, "Select Scene File", ".", "*.*")
        dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        if dialog.exec_():
            self.submitFiles = dialog.selectedFiles()
            for file in self.submitFiles:
                newItem = QtGui.QListWidgetItem()
                newItem.setText(file)
                self.fileList.append(file)
                self.listWidget.insertItem(self.fileNums, newItem)
                self.fileNums = self.fileNums + 1
        """
        
class saveAsWindow(QtGui.QDialog):
    def __init__(self, service, parent=None):
        super(saveAsWindow, self).__init__(parent)
        self.service = service
        self.fileNums = 0
        self.fileList = []
        self.setup_ui()

    def setup_ui(self):
        self.super_layout = QtGui.QHBoxLayout()
        self.main_layout = QtGui.QVBoxLayout()
        self.root_layout = QtGui.QVBoxLayout()

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.projectLabel = QtGui.QLabel(u'项目', self)
        else:
            self.projectLabel = QtGui.QLabel(u'Project', self)
        self.projectText = QtGui.QLineEdit(RCConfig_max.projectName, self)
        self.projectText.setEnabled(False)

        self.layout.addWidget(self.projectLabel, 0, 0)
        self.layout.addWidget(self.projectText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.sceneLabel = QtGui.QLabel(u'另存任务名', self)
        else:
            self.sceneLabel = QtGui.QLabel(u'Scene', self)
        self.sceneText = QtGui.QLineEdit(RCConfig_max.sceneName, self)
        #self.sceneText.setEnabled(False)
        self.layout.addWidget(self.sceneLabel, 0, 0)
        self.layout.addWidget(self.sceneText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.descriptionLabel = QtGui.QLabel(u'描述', self)
        else:
            self.descriptionLabel = QtGui.QLabel(u'Description', self)
        self.descriptionText = QtGui.QLineEdit('', self)
        self.sceneText.setEnabled(False)
        self.layout.addWidget(self.descriptionLabel, 0, 0)
        self.layout.addWidget(self.descriptionText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout5 = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.button1 = QtGui.QPushButton(u'另存', self)
            self.button2 = QtGui.QPushButton(u'取消', self)
        else:
            self.button1 = QtGui.QPushButton(u'SaveAs', self)
            self.button2 = QtGui.QPushButton(u'Cancel', self)
        self.layout5.addWidget(self.button1, 2, 3)
        self.layout5.addWidget(self.button2, 2, 0)
        self.button1.clicked.connect(self.onSave)
        self.button2.clicked.connect(self.onCancel)
        self.row_Hbox.setLayout(self.layout5)
        self.root_layout.addWidget(self.row_Hbox, 2, 0)

        self.setLayout(self.root_layout)
        # self.setLayout(self.main_layout)

        if RCConfig_max.lang == 'zh':
            self.setWindowTitle(u'另存任务')
        else:
            self.setWindowTitle(u'Save Task')
        self.setGeometry(300, 300, 600, 200)
        self.image = None

    def onSaveAs(self):
        projectDir = os.path.join(RCConfig_max.storageDir, RCConfig_max.projectName)
        if not os.path.exists(projectDir):
            os.mkdir(projectDir)

        fn = os.path.join(projectDir, self.sceneText.text())

        fm = MaxPlus.FileManager
        scene_fn = os.path.join(RCConfig_max.storageDir, fn + '.max')
        print 'scenn_fn =', scene_fn
        fm.Save(scene_fn)
        print fm.GetFileNameAndPath()
        if not RCFunction_max.saveScene(self.service, RCConfig_max.projectName, RCConfig_max.sceneName, scene_fn,
                                        None, self.descriptionText.text()):
            self.close()
            return
        self.service.userActionLog(RCConfig_max.userName, RCConfig_max.projectName, RCConfig_max.sceneName, 'save')
        self.close()

    def onCancel(self):
        self.close()

class renderSceneWindow(QtGui.QDialog):
    def __init__(self, service, parent=None):
        super(renderSceneWindow, self).__init__(parent)
        self.service = service
        self.projectID = None
        self.sceneID = None
        self.textureID = None
        self.mayaPathList = ''
        self.texturePathList = ''
        self.setup_ui()

    def setup_ui(self):
        self.super_layout = QtGui.QHBoxLayout()
        self.main_layout = QtGui.QVBoxLayout()

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.jobLabel = QtGui.QLabel(u'作业名', self)
        else:
            self.jobLabel = QtGui.QLabel(u'Job', self)
        self.jobText = QtGui.QLineEdit('test', self)

        self.layout.addWidget(self.jobLabel, 0, 0)
        self.layout.addWidget(self.jobText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.projectLabel = QtGui.QLabel(u'项目', self)
        else:
            self.projectLabel = QtGui.QLabel(u'Project', self)
        self.projectText = QtGui.QLineEdit(RCConfig_maya.projectName, self)
        self.projectText.setEnabled(False)

        self.layout.addWidget(self.projectLabel, 0, 0)
        self.layout.addWidget(self.projectText, 0, 1)

        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.sceneLabel = QtGui.QLabel(u'场景任务', self)
        else:
            self.sceneLabel = QtGui.QLabel(u'Scene', self)
        self.sceneText = QtGui.QLineEdit(RCConfig_maya.sceneName, self)
        self.sceneText.setEnabled(False)

        self.layout.addWidget(self.sceneLabel, 0, 0)
        self.layout.addWidget(self.sceneText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)
        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.frameLabel = QtGui.QLabel(u'帧序列', self)
        else:
            self.frameLabel = QtGui.QLabel(u'FrameList', self)
        #startFrame = str(cmds.getAttr('defaultRenderGlobals.startFrame'))
        #endFrame = str(cmds.getAttr('defaultRenderGlobals.endFrame'))
        #frame = startFrame.split('.')[0] + '-' + endFrame.split('.')[0]
        #self.frameText = QLineEdit(frame, self)
        self.frameText = QLineEdit('', self)

        self.layout.addWidget(self.frameLabel, 0, 0)
        self.layout.addWidget(self.frameText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.button1 = QtGui.QPushButton(u'提交', self)
            self.button2 = QtGui.QPushButton(u'取消', self)
        else:
            self.button1 = QtGui.QPushButton(u'Submit', self)
            self.button2 = QtGui.QPushButton(u'Cancel', self)
        self.layout.addWidget(self.button1, 1, 1)
        self.layout.addWidget(self.button2, 1, 0)
        self.button1.clicked.connect(self.onSubmit)
        self.button2.clicked.connect(self.onCancel)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.setLayout(self.main_layout)
        if RCConfig_max.lang == 'zh':
            self.setWindowTitle(u'提交渲染作业')
        else:
            self.setWindowTitle(u'Submit Render Job')
        self.setGeometry(300, 300, 450, 100)

    def setProjectName(self, projectName):
        self.projectText.setText(projectName)
        RCConfig_max.projectName = projectName

    def setSceneName(self, sceneName):
        self.sceneText.setText(sceneName)
        RCConfig_max.sceneName = sceneName

    def setSceneID(self, sceneID):
        self.sceneID = sceneID

    def onSubmit(self):
        RCConfig_max.projectName = self.projectText.text()
        RCConfig_max.sceneName = self.sceneText.text()
        """"
        RCOperation_max.renderScene(self.service, RCConfig_max.userName, self.jobText.text(), RCConfig_max.projectName,
                                 RCConfig_max.sceneName, '', self.frameText.text())

        self.service.userActionLog(RCConfig_max.userName, RCConfig_max.projectName,
                                   RCConfig_max.sceneName, 'RenderScene')
        self.menu.setEnable(True)
        self.close()
        """
    def onCancel(self):
        self.menu.setEnable(True)
        self.close()

class setupWindow(QtGui.QDialog):
    def __init__(self, service, parent=None):
        super(setupWindow, self).__init__(parent)
        # And now set up the UI
        self.service = service
        #self.menu = menu
        #self.menu.setEnable(False)
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QtGui.QVBoxLayout()

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.Label = QtGui.QLabel(u'团队：', self)
        self.teamText = QtGui.QLineEdit(RCConfig_ma.teamName, self)
        self.layout.addWidget(self.teamLabel, 1, 0)
        self.layout.addWidget(self.teamText, 1, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        if self.service:
            self.row_Hbox = QtGui.QGroupBox()
            self.layout = QtGui.QGridLayout()
            self.storageLabel = QtGui.QLabel(u'缓冲区路径：', self)
            self.storageText = QtGui.QLineEdit(RCConfig_max.storageDir, self)
            self.layout.addWidget(self.storageLabel, 1, 0)
            self.layout.addWidget(self.storageText, 1, 1)
            self.row_Hbox.setLayout(self.layout)
            self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if RCConfig_max.lang == 'zh':
            self.button1 = QtGui.QPushButton(u'设置', self)
            self.button2 = QtGui.QPushButton(u'取消', self)
            self.button3 = QtGui.QPushButton(u'清除缓冲区', self)
        else:
            self.button1 = QtGui.QPushButton(u'Setup', self)
            self.button2 = QtGui.QPushButton(u'Cancel', self)
            self.button3 = QtGui.QPushButton(u'ClearBuffer', self)
        self.layout.addWidget(self.button1, 1, 2)
        self.layout.addWidget(self.button2, 1, 1)
        self.layout.addWidget(self.button3, 1, 0)
        self.button1.clicked.connect(self.onSetup)
        self.button2.clicked.connect(self.onCancel)
        self.button3.clicked.connect(self.onClear)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)
        if not self.service:
            self.button3.setEnabled(False)
        else:
            self.button3.setEnabled(True)

        self.setLayout(self.main_layout)
        if RCConfig_max.lang == 'zh':
            self.setWindowTitle(u'设置')
        else:
            self.setWindowTitle(u'Setup')
        self.setGeometry(300, 300, 450, 200)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)

    def onClear(self):
        RCConfig_max.storageDir = self.storageText.text()
        if os.path.exists(RCConfig_max.storageDir):
            reply = QtGui.QMessageBox.question(self, u"问题", u"是否删除目录?",
                        QtGui.QMessageBox.StandardButton.Yes | QtGui.QMessageBox.StandardButton.No)
            if reply == QtGui.QMessageBox.Yes:
                shutil.rmtree(RCConfig_max.storageDir)
                os.rmkdir(RCConfig_max.storageDir)
        self.service.userActionLog(RCConfig_max.userName, '', '', '', RCConfig_max.RCMaya_Action_ClearBuffer)
        self.close()

    def onSetup(self):
        RCConfig_max.teamName = self.teamText.text()
        if not self.service:
            self.service = RCService_max.DAMService()
            if not self.service.status:
                return None
        self.service.userActionLog(RCConfig_max.userName, '', '', '', RCConfig_max.RCMaya_Action_Setup)
        self.close()

    def onCancel(self):
        #self.menu.setEnable(True)
        self.close()

