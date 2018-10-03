#!/usr/bin/python
# -*- coding: utf-8 -*-

import MaxPlus
import urllib2
import shutil
import copy
import os
import json
import CGConfig_max
if CGConfig_max.softwareVersion == '3dsMax2018' or CGConfig_max.softwareVersion == '3dsMax2019':
    from PySide2 import QtGui
    from PySide2 import QtCore
elif CGConfig_max.softwareVersion == '3dsMax2014' or CGConfig_max.softwareVersion == '3dsMax2016':
    from PySide import QtGui
    from PySide import QtCore
else:
    pass
import CGFunction_max
import CGService_max
#from timer import Timer

def judgelogData(logJsonData, id):
    fileName = ''
    bExist = False
    for log in logJsonData:
        if log['id'] == id:
            fileName = log['fileName']
            bExist = True
            break
    return bExist, fileName

class _GCProtector(object):
    widgets = []

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
        if CGConfig_max.lang == 'zh':
            self.button = QtGui.QPushButton(u'关闭', self)
        else:
            self.button = QtGui.QPushButton(u'Close', self)

        self.layout.addWidget(self.button)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)
        self.button.clicked.connect(self.onClose)

        self.setLayout(self.main_layout)
        self.setGeometry(400, 350, 700, 700)
        self.show()

    def onClose(self):
        self.close()
        
class baseModelDialog(QtGui.QDialog):
    def __init__(self, service, projectName, parent):
        super(baseModelDialog, self).__init__(parent)
        self.service = service
        self.projectName = projectName
        self.parent = parent
        self.modelTaskList = []
        self.main_layout = QtGui.QVBoxLayout()
        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setIconSize(QtCore.QSize(60, 60))

        self.GetTasks()
        self.main_layout.addWidget(self.listWidget)
        self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemDoubleClicked (QListWidgetItem*)"),
                                self.onDoubleClickItem)
        self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemClicked (QListWidgetItem*)"), self.onClickItem)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.button1 = QtGui.QPushButton(u'选择', self)
            self.button2 = QtGui.QPushButton(u'取消', self)
        else:
            self.button1 = QtGui.QPushButton(u'Select', self)
            self.button2 = QtGui.QPushButton(u'Cancel', self)

        self.layout.addWidget(self.button1, 0, 1)
        self.layout.addWidget(self.button2, 0, 0)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)
        self.button1.clicked.connect(self.onSelect)
        self.button2.clicked.connect(self.onCancel)

        self.setLayout(self.main_layout)
        self.setGeometry(600, 350, 300, 500)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)
        #self.show()

    def myCompare(self, a, b):
        str1 = a['name'].lower()
        str2 = b['name'].lower()
        return cmp(str1, str2)

    def GetTasks(self):
        self.listWidget.clear()
        print 'projectName =', self.projectName
        result = self.service.myWFGetTasksOfProject(self.projectName)
        if not result:
            return None
        for task in json.loads(result):
            print task['name'], task['stage']
            if task['stage'] == u'模型':
                self.modelTaskList.append(task)
        self.modelTaskList.sort(cmp=self.myCompare)
        textFont = QtGui.QFont("song", 16, QtGui.QFont.Normal)
        for task in self.modelTaskList:
            item = QtGui.QListWidgetItem(task['name'])
            item.setFont(textFont)
            self.listWidget.addItem(item)

    def onDoubleClickItem(self, item):
        row = self.listWidget.currentRow()
        CGConfig_max.baseModelTask = self.modelTaskList[row]
        self.parent.baseModelText.setText(CGConfig_max.baseModelTask['name'])
        self.parent.selectFlag = 'Model'
        self.close()

    def onClickItem(self, item):
        row = self.listWidget.currentRow()
        CGConfig_max.baseModelTask = self.modelTaskList[row]

    def onSelect(self):
        row = self.listWidget.currentRow()
        CGConfig_max.baseModelTask = self.modelTaskList[row]
        self.parent.baseModelText.setText(CGConfig_max.baseModelTask['name'])
        self.parent.selectFlag = 'Model'
        self.close()

    def onCancel(self):
        CGConfig_max.baseModelTask = None
        self.parent.selectFlag = ''
        self.close()

class SuperDuperText(QtGui.QLineEdit):
    def focusInEvent(self, event):
        MaxPlus.CUI.DisableAccelerators()

    def focusOutEvent(self, event):
        MaxPlus.CUI.EnableAccelerators()

class loginWindow(QtGui.QDialog):
    def __init__(self, service, parent = None):
        super(loginWindow, self).__init__(parent)
        # And now set up the UI
        print 'ggg'

        self.service = service
        result, message = service.myWFGetAllTeams()
        print 'result =', result
        if not result:
            QtGui.QMessageBox.information(self, u"错误信息", message)
            #cmds.confirmDialog(title=u'错误信息', message=message, defaultButton=u'确认')
            return
        self.teamList = message
        self.setup_ui()
        
    def setup_ui(self):
        if CGConfig_max.lang == 'zh':
            self.setWindowTitle(u'用户登录')
            self.teamLabel = QtGui.QLabel(u'团队', self)
            self.nameLabel = QtGui.QLabel(u'帐号', self)
            self.passLabel = QtGui.QLabel(u'密码', self)
            self.button1 = QtGui.QPushButton(u'登录', self)
            self.button2 = QtGui.QPushButton(u'取消', self)
        else:
            self.setWindowTitle(u'User Login')
            self.teamLabel = QtGui.QLabel(u'TeamName', self)
            self.nameLabel = QtGui.QLabel(u'UserName', self)
            self.passLabel = QtGui.QLabel(u'Password', self)
            self.button1 = QtGui.QPushButton(u'Login', self)
            self.button2 = QtGui.QPushButton(u'Cancel', self)
        self.teamBox = QtGui.QComboBox(self)
        for team in self.teamList:
            self.teamBox.addItem(team['alias'])
        print CGConfig_max.teamName
        if CGConfig_max.teamName:
            for index in range(0, len(self.teamList)):
                if self.teamList[index]['name'] == CGConfig_max.teamName:
                    print 'index =', index
                    self.teamBox.setCurrentIndex\
                        (index)
                    break
        self.teamBox.currentIndexChanged.connect(self.onTeamSelect)
        self.nameText = SuperDuperText()
        self.passText = SuperDuperText()
        self.nameText.setText(CGConfig_max.userName)
        self.passText.setText(CGConfig_max.password)

        self.passText.setEchoMode(QtGui.QLineEdit.Password)
        self.button1.clicked.connect(self.onLogin)
        self.button2.clicked.connect(self.onCancel)

        #self.main_layout = QtGui.QVBoxLayout()
        self.main_layout = QtGui.QGridLayout()
        self.row_Hbox1 = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.teamLabel, 0, 0, 1, 1)
        self.layout.addWidget(self.teamBox, 0, 1, 1, 6)
        self.layout.addWidget(self.nameLabel, 1, 0, 1, 1)
        self.layout.addWidget(self.nameText, 1, 1, 1, 6)
        self.layout.addWidget(self.passLabel, 2, 0, 1, 1)
        self.layout.addWidget(self.passText, 2, 1, 1, 6)
        self.row_Hbox1.setLayout(self.layout)

        self.row_Hbox2 = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.button1, 0, 1)
        self.layout.addWidget(self.button2, 0, 0)
        self.row_Hbox2.setLayout(self.layout)

        self.main_layout.addWidget(self.row_Hbox1, 0, 0, 3, 1)
        self.main_layout.addWidget(self.row_Hbox2, 4, 0, 1, 1)
        self.setLayout(self.main_layout)

        self.setGeometry(400, 400, 400, 200)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)

    def onTeamSelect(self, n):
        CGConfig_max.teamName = self.teamList[n]['name']

    def onLogin(self):
        CGConfig_max.teamName = self.teamList[self.teamBox.currentIndex()]['name']
        result, message = self.service.login(self.nameText.text(), self.passText.text())
        if result:
            CGConfig_max.userName = self.nameText.text()
            CGConfig_max.password = self.passText.text()
            CGConfig_max.loginFlag = True
            self.close()
        else:
            if CGConfig_max.lang == 'zh':
                QtGui.QMessageBox.information(self, u"错误信息", message)
            else:
                QtGui.QMessageBox.information(self, u"Error", message)

    def onCancel(self):
        self.close()

    def closeEvent(self, event):
        event.accept() # let the window close

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
        CGConfig_max.currentTask = None
        self.selectFlag = ''
        self.setup_ui()

    def setup_ui(self):
        self.super_layout = QtGui.QHBoxLayout()
        self.main_layout = QtGui.QVBoxLayout()

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
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

        self.layout.addWidget(self.projectLabel, 0, 0, 1, 1)
        self.layout.addWidget(self.projectText, 0, 1, 1, 1)
        self.layout.addWidget(self.stageLabel, 0, 2, 1, 1)
        self.layout.addWidget(self.stageText, 0, 3, 1, 1)
        self.layout.addWidget(self.noteLabel, 1, 0, 1, 1)
        self.layout.addWidget(self.noteText, 1, 1, 1, 3)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)
        
        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setIconSize(QtCore.QSize(60, 60))

        self.GetTasks()
        self.main_layout.addWidget(self.listWidget)
        self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemDoubleClicked (QListWidgetItem*)"), self.onDoubleClickItem)
        self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemClicked (QListWidgetItem*)"), self.onClickItem)

        self.treeWidget = QtGui.QTreeWidget(self)
        self.main_layout.addWidget(self.treeWidget)
        self.treeWidget.hide()
        self.treeWidget.itemClicked.connect(self.onClickItem1)
        self.treeWidget.itemDoubleClicked.connect(self.onDoubleClickItem1)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.radiobutton3 = QtGui.QRadioButton(u'版本文件', self)
            self.radiobutton5 = QtGui.QRadioButton(u'回退文件', self)
            self.radiobutton6 = QtGui.QRadioButton(u'关闭', self)
            self.checkBox7 = QtGui.QCheckBox(u'装载', self)
            self.checkBox8 = QtGui.QCheckBox(u'图标', self)
        else:
            self.radiobutton3 = QtGui.QRadioButton(u'VersionFile', self)
            self.radiobutton5 = QtGui.QRadioButton(u'ReturnFile', self)
            self.radiobutton6 = QtGui.QRadioButton(u'Close', self)
            self.checkBox7 = QtGui.QCheckBox(u'Load', self)
            self.checkBox8 = QtGui.QCheckBox(u'Icon', self)

        self.radiobutton3.setChecked(False)
        #self.radiobutton4.setChecked(False)
        self.radiobutton5.setChecked(False)
        self.radiobutton6.setChecked(True)
        if self.loadFlag:
            self.checkBox7.setChecked(True)
        else:
            self.checkBox7.setChecked(False)

        if CGConfig_max.IconFlag:
            self.checkBox8.setChecked(True)
        else:
            self.checkBox8.setChecked(False)

        self.layout.addWidget(self.radiobutton3, 0, 0)
        self.layout.addWidget(self.radiobutton5, 0, 1)
        self.layout.addWidget(self.radiobutton6, 0, 2)
        self.layout.addWidget(self.checkBox8, 0, 3)
        self.layout.addWidget(self.checkBox7, 0, 4)
        self.radiobutton3.clicked.connect(self.onSetVersion)
        self.radiobutton5.clicked.connect(self.onSetReturn)
        self.radiobutton6.clicked.connect(self.onSetClose)
        self.checkBox7.clicked.connect(self.onSetLoad)
        self.checkBox8.clicked.connect(self.onSetIcon)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)
        self.modelBox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.modelLabel = QtGui.QLabel(u'初始模型', self)
            self.selectButton1 = QtGui.QPushButton(u'选择模型', self)
            self.selectButton2 = QtGui.QPushButton(u'选择文件', self)
        else:
            self.modelLabel = QtGui.QLabel(u'initModel', self)
            self.selectButton1 = QtGui.QPushButton(u'SelectModel', self)
            self.selectButton2 = QtGui.QPushButton(u'SelectFile', self)
        self.baseModelText = QtGui.QLineEdit('', self)
        self.layout.addWidget(self.modelLabel, 0, 0)
        self.layout.addWidget(self.baseModelText, 0, 1)
        self.layout.addWidget(self.selectButton1, 0, 2)
        self.layout.addWidget(self.selectButton2, 0, 3)
        self.modelBox.setLayout(self.layout)
        self.modelBox.hide()
        self.main_layout.addWidget(self.modelBox)
        self.selectButton1.clicked.connect(self.onSetSelectModel)
        self.selectButton2.clicked.connect(self.onSetSelectFile)
        self.row_Hbox = QtGui.QGroupBox()
        layout1 = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
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
        if CGConfig_max.lang == 'zh':
            self.setWindowTitle(u'打开任务')
        else:
            self.setWindowTitle(u'Open Task')

        self.setLayout(self.main_layout)
        self.setGeometry(400, 350, 650, 650)

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def myCompare(self, a, b):
        str1 = a['name'].lower()
        str2 = b['name'].lower()
        return cmp(str1, str2)

    def GetTasks(self):
        self.listWidget.clear()
        #with Timer() as t:
        print 'userName =', CGConfig_max.userName
        result = self.service.myWFGetMyTask(CGConfig_max.userName)
        #print "=> elasped : %s s" % t.secs

        if not result:
            return None
        CGConfig_max.tasks = json.loads(result)
        print 'tasks =', CGConfig_max.tasks
        CGConfig_max.tasks.sort(cmp = self.myCompare)
        textFont = QtGui.QFont("song", 16, QtGui.QFont.Normal)

        if CGConfig_max.IconFlag:
            iconLogFilePath = os.path.join(CGConfig_max.storageDir,
                                           CGConfig_max.userName + CGConfig_max.iconLogFileExt)
            logJsonData = []
            if os.path.isfile(iconLogFilePath):
                with open(iconLogFilePath, "r") as json_file:
                    logJsonData = json.load(json_file)
            bLog = False
            for task in CGConfig_max.tasks:
                if not task or not task['name']:
                    continue
                str = task['name']
                #print str
                try:
                    if task['isReturn']:
                        str = str.ljust(40, ' ') + 'X'
                    else:
                        str = str.ljust(40, ' ')
                except KeyError:
                    str = str.ljust(40, ' ')
                try:
                    iconFileID = task['IconFileID']
                except KeyError or ValueError:
                    iconFileID = ''
                iconDir = CGConfig_max.storageDir + '/' + CGConfig_max.icon_Dir
                if not os.path.exists(iconDir):
                    os.mkdir(iconDir)
                iconFile = iconDir + '/' + task['name'] + '.png'
                if iconFileID:
                    bExist, iconFile1 = judgelogData(logJsonData, iconFileID)
                    if not bExist:
                        self.service.getFile(iconFile, iconFileID, False)
                        logJsonData.append({'id': iconFileID, 'fileName': iconFile})
                        bLog = True
                else:
                    Dir = MaxPlus.PathManager.GetUserScriptsDir()
                    iconFile = Dir + '/aa.png'
                icon = QtGui.QIcon(iconFile)
                item = QtGui.QListWidgetItem(icon, '  ' + str)
                item.setFont(textFont)
                self.listWidget.addItem(item)
            if bLog:
                with open(iconLogFilePath, "w") as json_file:
                    json.dump(logJsonData, json_file)
        else:
            for task in CGConfig_max.tasks:
                if not task or not task['name']:
                    continue
                str = task['name']
                #print str
                try:
                    if task['isReturn']:
                        str = str.ljust(40, ' ') + 'X'
                    else:
                        str = str.ljust(40, ' ')
                except KeyError:
                    str = str.ljust(40, ' ')
                item = QtGui.QListWidgetItem('  ' + str)
                item.setFont(textFont)
                self.listWidget.addItem(item)

    def onSetVersion(self):
        if not self.bTaskSelected:
            return

        self.treeWidget.clear()
        self.treeWidget.show()
        headerList = []
        headerList.append(u'文件名')
        headerList.append(u' ')
        headerList.append(u'日期')
        headerList.append(u'动作')
        #headerList.append('ID')
        self.treeWidget.setHeaderLabels(headerList)
        #header = self.treeWidget.header()
        #header.setStretchLastSection(True)

        self.radiobutton3.setChecked(True)
        self.radiobutton5.setChecked(False)
        self.radiobutton6.setChecked(False)
        row = self.listWidget.currentRow()
        self.GetVersions(CGConfig_max.tasks[row])

    def GetVersions(self, task):
        self.treeWidget.clear()
        row = self.listWidget.currentRow()
        self.assetData = self.service.listMaxFile(CGConfig_max.tasks[row]['name'])
        textFont = QtGui.QFont("song", 12, QtGui.QFont.Normal)
        for arr in self.assetData:
            date = arr['uploadDate'].strftime('%b-%d-%Y %H:%M:%S')
            item = QtGui.QTreeWidgetItem(self.treeWidget, [arr['filename'], ' ', date])
            item.setFont(0, textFont)
            item.setFont(1, textFont)
            item.setFont(2, textFont)
            self.treeWidget.resizeColumnToContents(0)
            item.setText(3, '')

    def onSetReturn(self):
        if not self.bTaskSelected:
            return
        row = self.listWidget.currentRow()
        self.listWidget1.show()
        self.listWidget1.clear()
        try:
            if not CGConfig_max.tasks[row]['isReturn']:
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
        result = self.service.myWFReturnTask(CGConfig_max.tasks[row]['name'], CGConfig_max.tasks[row]['projectName'],
                                                  CGConfig_max.tasks[row]['upfolderid'])
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
        self.treeWidget.clear()
        self.treeWidget.hide()

    def onSetLoad(self):
        self.loadFlag = self.checkBox7.isChecked()
        if not self.loadFlag and CGConfig_max.currentTask and CGConfig_max.currentTask['stage'] == u'场景':
            self.modelBox.show()

    def onSetIcon(self):
        CGConfig_max.IconFlag = self.checkBox8.isChecked()
        self.GetTasks()

    def onSetSelectModel(self):
        row = self.listWidget.currentRow()
        CGConfig_max.projectName = CGConfig_max.tasks[row]['projectName']
        win = baseModelDialog(self.service, CGConfig_max.projectName, self)
        _GCProtector.widgets.append(win)
        win.show()

    def onSetSelectFile(self):
        file_dialog = QtGui.QFileDialog(
            parent=self,
            caption="Open As",
            directory='',
            filter="3dsMax (*.max)"
        )
        file_dialog.setLabelText(QtGui.QFileDialog.Accept, "Open")
        file_dialog.setLabelText(QtGui.QFileDialog.Reject, "Cancel")
        file_dialog.setOption(QtGui.QFileDialog.DontResolveSymlinks)
        file_dialog.setOption(QtGui.QFileDialog.DontUseNativeDialog)
        if not file_dialog.exec_():
            return
        self.selectFlag = 'File'
        self.baseModelText.setText(file_dialog.selectedFiles()[0])
        CGConfig_max.baseModelFile = file_dialog.selectedFiles()[0]

    def onDoubleClickItem(self, item):
        self.onOpen()

    def onClickItem(self, item):
        row = self.listWidget.currentRow()
        self.projectText.setText(CGConfig_max.tasks[row]['projectName'])
        self.stageText.setText(CGConfig_max.tasks[row]['stage'])
        self.noteText.setText(CGConfig_max.tasks[row]['note'])
        self.fileListIndex = row
        self.noteText.setText(CGConfig_max.tasks[row]['note'])
        CGConfig_max.currentTask = CGConfig_max.tasks[row]
        self.treeWidget.clear()
        CGConfig_max.assetID = ''
        result = self.service.myWFGetProjectInfo(CGConfig_max.tasks[row]['projectName'])
        project = json.loads(result)[0]
        try:
            timeUnit = project['timeUnit']
        except KeyError or ValueError:
            timeUnit = 'pal:25fps'
        if not timeUnit:
            time = timeUnit.split(':')[0]

        self.bTaskSelected = True

        if self.radiobutton3.isChecked():
            self.onSetVersion()

    def onDoubleClickItem1(self, item, column):
        row = self.treeWidget.indexOfTopLevelItem(item)
        if self.radiobutton3.isChecked():
            CGConfig_max.versionURL = self.assetData[row][19]
            CGConfig_max.assetID = self.assetData[row][0]
            self.onOpen()
            return

    def onClickItem1(self, item, column):
        row = self.treeWidget.indexOfTopLevelItem(item)
        if self.radiobutton3.isChecked():
            CGConfig_max.fileID = self.assetData[row]['id']
            if item.text(3) == 'X':
                reply = QtGui.QMessageBox.question(self, u"问题", u"是否删除?",
                                                   QtGui.QMessageBox.StandardButton.Yes | QtGui.QMessageBox.StandardButton.No)
                if reply == QtGui.QMessageBox.Yes:
                    self.service.removeasset(CGConfig_max.assetID)
                    self.GetVersions(CGConfig_max.currentTask)

    def onCancel(self):
        #self.menu.setEnable(True)
        self.close()

    def onRefresh(self):
        CGConfig_max.IconFlag = self.checkBox8.isChecked()
        self.GetTasks()

    def onOpen(self):
        currentRow = self.listWidget.currentRow()
        self.currentTask = copy.deepcopy(CGConfig_max.tasks[currentRow])
        CGConfig_max.currentTask = copy.deepcopy(self.currentTask)

        #CGConfig_max.currentTask = CGConfig_max.tasks[currentRow]
        #CGConfig_max.frameList = ''
        taskName = self.currentTask['name']
        CGConfig_max.sceneName = taskName
        projectName = self.currentTask['projectName']
        CGConfig_max.projectName = projectName
        CGConfig_max.taskIndex = self.fileListIndex

        result = self.service.myWFGetProjectInfo(projectName)
        list = json.loads(result)
        CGConfig_max.project = list[0]
        try:
            CGConfig_max.parentProjectID = CGConfig_max.project['parentProjectID']
        except KeyError:
            CGConfig_max.parentProjectID = ''

        # projectDir = os.path.join(CGConfig_max.storageDir, projectName)
        projectDir = CGConfig_max.storageDir + '/' + projectName
        if not os.path.exists(projectDir):
            os.mkdir(projectDir)

        #if not CGConfig_max.currentTask:
        #    self.close()
        #    return

        self.loadFlag = self.checkBox7.isChecked()
        if self.loadFlag:
            try:
                CGConfig_max.fileID = self.currentTask['fileID']
            except KeyError:
                CGConfig_max.fileID = None
        else:
            CGConfig_max.fileID = None

        if self.currentTask:
            MaxPlus.FileManager.Reset(True)

        if self.selectFlag == 'Model':
            CGConfig_max.baseModelFile = ''
        elif self.selectFlag == 'File':
            CGConfig_max.baseModelModel = None

        if CGConfig_max.fileID or self.currentTask['stage'] == u'场景':
            if not CGFunction_max.openTask(self.service, projectDir):
                print 'Scene File is None'
        else:
            print 'Scene File is None'
        #self.service.userActionLog(CGConfig_max.userName, CGConfig_max.projectName, CGConfig_max.sceneName, 'open')
        #self.service.userActionLog(CGConfig_max.userName, projectName, taskName, self.currentTask['_id'],
        #                           'open')

        self.close()

    def closeEvent(self, event):
        event.accept() # let the window close

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
        if CGConfig_max.lang == 'zh':
            self.projectLabel = QtGui.QLabel(u'项目', self)
        else:
            self.projectLabel = QtGui.QLabel(u'Project', self)
        self.projectText = QtGui.QLineEdit(CGConfig_max.projectName, self)
        self.projectText.setEnabled(False)

        self.layout.addWidget(self.projectLabel, 0, 0)
        self.layout.addWidget(self.projectText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)


        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.sceneLabel = QtGui.QLabel(u'任务', self)
        else:
            self.sceneLabel = QtGui.QLabel(u'Scene', self)
        self.sceneText = QtGui.QLineEdit(CGConfig_max.sceneName, self)
        self.sceneText.setEnabled(False)
        self.layout.addWidget(self.sceneLabel, 0, 0)
        self.layout.addWidget(self.sceneText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.descriptionLabel = QtGui.QLabel(u'描述', self)
            self.frameLabel = QtGui.QLabel(u'帧范围', self)
            self.assetCheckBox = QtGui.QCheckBox(u'资产', self)
        else:
            self.descriptionLabel = QtGui.QLabel(u'Description', self)
            self.frameLabel = QtGui.QLabel(u'FrameRange', self)
            self.assetCheckBox = QtGui.QCheckBox(u'资产', self)
        self.descriptionText = QtGui.QLineEdit('', self)
        self.sceneText.setEnabled(False)
        self.assetCheckBox.setChecked(True)
        start = MaxPlus.Animation.GetAnimRange().Start()
        end = MaxPlus.Animation.GetAnimRange().End()

        frameStr = str(start) + '-' + str(end)
        self.frameText = QtGui.QLineEdit(frameStr, self)
        self.layout.addWidget(self.descriptionLabel, 0, 0, 1, 1)
        self.layout.addWidget(self.descriptionText, 0, 1, 1, 5)
        self.layout.addWidget(self.frameLabel, 1, 0, 1, 1)
        self.layout.addWidget(self.frameText, 1, 1, 1, 4)
        self.layout.addWidget(self.assetCheckBox, 1, 6, 1, 1)
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
        if CGConfig_max.lang == 'zh':
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

        if CGConfig_max.lang == 'zh':
            self.setWindowTitle(u'保存任务')
        else:
            self.setWindowTitle(u'Save Task')
        self.setGeometry(400, 300, 600, 200)
        self.image = None

    def onSave(self):
        projectDir = os.path.join(CGConfig_max.storageDir, CGConfig_max.projectName)
        if not os.path.exists(projectDir):
            os.mkdir(projectDir)

        fn = os.path.join(projectDir, CGConfig_max.sceneName)

        fm = MaxPlus.FileManager
        scene_fn = fn + '.max'
        print 'scene_fn =', scene_fn
        #fm.Save(scene_fn)
        #print fm.GetFileNameAndPath()
        assetSaveFlag = self.assetCheckBox.isChecked()
        if not CGFunction_max.saveTask(self.service, scene_fn, self.frameText.text(), self.descriptionText.text(), assetSaveFlag):
            self.close()
            return
        #self.service.userActionLog(CGConfig_max.userName, CGConfig_max.projectName, CGConfig_max.sceneName, 'save')
        self.close()
        print 'save is finished'

    def onSaveSubmit(self):
        if self.fileNums == 0:
            if CGConfig_max.lang == 'zh':
                QtGui.QMessageBox.information(self, u"提示信息", u"没有选择单帧效果图!!!")
            else:
                QtGui.QMessageBox.information(self, u"Prompt", u"NO File Upload!!!")
        else:
            self.onSave()
            CGFunction_max.submitTask(self.service, CGConfig_max.projectName, CGConfig_max.sceneName,
                                      CGConfig_max.currentTask, self.fileList)

            #self.service.userActionLog(CGConfig_max.userName, CGConfig_max.projectName, CGConfig_max.sceneName, 'submit')
            self.close()

    def onCancel(self):
        self.close()

    def closeEvent(self, event):
        event.accept() # let the window close

    def onCapture(self):
        if CGConfig_max.lang == 'zh':
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
        if CGConfig_max.lang == 'zh':
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
        self.taskList = []
        self.saveAsTask = None
        self.oldTask = copy.deepcopy(CGConfig_max.currentTask)
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QtGui.QVBoxLayout()
        self.root_layout = QtGui.QVBoxLayout()

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.projectLabel = QtGui.QLabel(u'项目', self)
        else:
            self.projectLabel = QtGui.QLabel(u'Project', self)
        self.projectText = QtGui.QLineEdit(CGConfig_max.projectName, self)
        self.projectText.setEnabled(False)

        self.layout.addWidget(self.projectLabel, 0, 0)
        self.layout.addWidget(self.projectText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.sceneLabel = QtGui.QLabel(u'另存任务名', self)
        else:
            self.sceneLabel = QtGui.QLabel(u'Scene', self)
        self.sceneText = QtGui.QLineEdit('', self)
        #self.sceneText.setEnabled(False)
        self.layout.addWidget(self.sceneLabel, 0, 0)
        self.layout.addWidget(self.sceneText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.descriptionLabel = QtGui.QLabel(u'描述', self)
        else:
            self.descriptionLabel = QtGui.QLabel(u'Description', self)
        self.descriptionText = QtGui.QLineEdit('', self)
        self.sceneText.setEnabled(False)
        self.layout.addWidget(self.descriptionLabel, 0, 0)
        self.layout.addWidget(self.descriptionText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setIconSize(QtCore.QSize(60, 60))

        self.GetTasks()
        self.main_layout.addWidget(self.listWidget)
        self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemDoubleClicked (QListWidgetItem*)"),
                                self.onDoubleClickItem)
        self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemClicked (QListWidgetItem*)"), self.onClickItem)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout5 = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.button1 = QtGui.QPushButton(u'另存为', self)
            self.button2 = QtGui.QPushButton(u'取消', self)
        else:
            self.button1 = QtGui.QPushButton(u'SaveAs', self)
            self.button2 = QtGui.QPushButton(u'Cancel', self)
        self.layout5.addWidget(self.button1, 0, 1)
        self.layout5.addWidget(self.button2, 0, 0)
        self.button1.clicked.connect(self.onSaveAs)
        self.button2.clicked.connect(self.onCancel)
        self.row_Hbox.setLayout(self.layout5)
        self.main_layout.addWidget(self.row_Hbox)

        #self.setLayout(self.root_layout)
        self.setLayout(self.main_layout)

        if CGConfig_max.lang == 'zh':
            self.setWindowTitle(u'另存任务')
        else:
            self.setWindowTitle(u'Save Task')
        self.setGeometry(400, 300, 600, 600)
        self.image = None

    def myCompare(self, a, b):
        str1 = a['name'].lower()
        str2 = b['name'].lower()
        return cmp(str1, str2)

    def GetTasks(self):
        self.listWidget.clear()
        #with Timer() as t:
        print 'userName =', CGConfig_max.userName
        result = self.service.myWFGetMyTask(CGConfig_max.userName)
        #print "=> elasped : %s s" % t.secs

        if not result:
            return None
        self.taskList = json.loads(result)
        self.taskList.sort(cmp = self.myCompare)
        textFont = QtGui.QFont("song", 16, QtGui.QFont.Normal)

        for task in self.taskList:
            if not task or not task['name']:
                continue
            str = task['name']
            #print str
            try:
                if task['isReturn']:
                    str = str.ljust(40, ' ') + 'X'
                else:
                    str = str.ljust(40, ' ')
            except KeyError:
                str = str.ljust(40, ' ')
            item = QtGui.QListWidgetItem('  ' + str)
            item.setFont(textFont)
            self.listWidget.addItem(item)

    def onClickItem(self):
        row = self.listWidget.currentRow()
        self.saveAsTask = self.taskList[row]
        self.sceneText.setText(self.taskList[row]['name'])

    def onDoubleClickItem(self):
        row = self.listWidget.currentRow()
        self.saveAsTask = self.taskList[row]
        self.sceneText.setText(self.taskList[row]['name'])
        self.onSaveAs()

    def onSaveAs(self):
        projectDir = CGConfig_max.storageDir + '/' + CGConfig_max.projectName
        if not os.path.exists(projectDir):
            os.mkdir(projectDir)

        fn = self.sceneText.text() + '.max'
        scene_fn = projectDir + '/' + self.sceneText.text() + '.max'
        CGConfig_max.currentTask = self.saveAsTask

        fm = MaxPlus.FileManager
        print 'scene_fn =', scene_fn
        fm.Save(scene_fn)
        print fm.GetFileNameAndPath()
        if not CGFunction_max.saveTask(self.service, scene_fn, None, self.descriptionText.text(), True):
            self.close()
            return
        #self.service.userActionLog(CGConfig_max.userName, CGConfig_max.projectName, CGConfig_max.sceneName, 'save')
        self.close()

    def onCancel(self):
        CGConfig_max.currentTask = copy.deepcopy(self.oldTask)
        self.close()

    def closeEvent(self, event):
        CGConfig_max.currentTask = copy.deepcopy(self.oldTask)
        event.accept() # let the window close

class importModelWindow(QtGui.QDialog):
    def __init__(self, service, parent = None):
        super(importModelWindow, self).__init__(parent)
        self.service = service
        self.setup_ui()

    def setup_ui(self):
        self.super_layout = QtGui.QHBoxLayout()
        self.main_layout = QtGui.QVBoxLayout()

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.projectLabel = QtGui.QLabel(u'项目', self)
        else:
            self.projectLabel = QtGui.QLabel(u'Project', self)
        print 'projectName =', CGConfig_max.projectName
        self.projectText = QtGui.QLineEdit(CGConfig_max.projectName, self)

        self.projectText.setEnabled(False)

        self.layout.addWidget(self.projectLabel, 0, 0)
        self.layout.addWidget(self.projectText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.treeWidget = QtGui.QTreeWidget(self)
        headerList = []
        headerList.append(u'模型')
        headerList.append(u'选中')
        #headerList.append(u'路径')
        self.treeWidget.setHeaderLabels(headerList)
        self.main_layout.addWidget(self.treeWidget)
        header = self.treeWidget.header()
        header.setStretchLastSection(True)
        #header.resizeSection(4, 20)

        self.treeWidget.itemClicked.connect(self.onClickItem)
        self.treeWidget.itemDoubleClicked.connect(self.onDoubleClickItem)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.button1 = QtGui.QPushButton(u'导入', self)
            self.button2 = QtGui.QPushButton(u'取消', self)
        else:
            self.button1 = QtGui.QPushButton(u'Import', self)
            self.button2 = QtGui.QPushButton(u'Cancel', self)
        self.layout.addWidget(self.button1, 1, 1)
        self.layout.addWidget(self.button2, 1, 0)
        self.button1.clicked.connect(self.onImport)
        self.button2.clicked.connect(self.onCancel)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.setLayout(self.main_layout)
        if CGConfig_max.lang == 'zh':
            self.setWindowTitle(u'导入模型')
        else:
            self.setWindowTitle(u'Merge Model')

        self.setGeometry(400, 300, 300, 650)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)

        self.GetProjectTasks()

    def setEnabled(self, bBool):
        self.button1.setEnabled(bBool)
        self.button2.setEnabled(bBool)

    def myCompare(self, a, b):
        str1 = a['name'].lower()
        str2 = b['name'].lower()
        return cmp(str1, str2)

    def GetProjectTasks(self):
        result = self.service.myWFGetProjectTask(CGConfig_max.projectName)
        taskList1 = json.loads(result)
        print taskList1
        self.taskList = []
        textFont = QtGui.QFont("song", 10, QtGui.QFont.Normal)
        for task in taskList1:
            if task['stage'] != u'模型':
                continue
            task['count'] = 0
            task['flag'] = ''
            self.taskList.append(task)
        self.taskList.sort(cmp=self.myCompare)
        for task in self.taskList:
            item = QtGui.QTreeWidgetItem(self.treeWidget, [task['name'], task['flag']])
            item.setFont(0, textFont)
            self.treeWidget.resizeColumnToContents(0)
            item.setCheckState(1, QtCore.Qt.Unchecked)
            item.setChildIndicatorPolicy(QtGui.QTreeWidgetItem.ShowIndicator)
            task['item'] = item

        #print 'length =', len(self.taskList)

    def onSetAll(self):
        self.dispFlag = 0
        self.SetDispTask()

    def onClickItem(self, item, column):
        if column == 1:
            print 'column'
        pass

    def onDoubleClickItem(self, item, column):
        row = self.treeWidget.indexOfTopLevelItem(item)
        #print 'row =', row

    def onCancel(self):
        self.close()

    def closeEvent(self, event):
        # do stuff
        event.accept() # let the window close

    def onImport(self):
        projectDir = CGConfig_max.storageDir + '/' + CGConfig_max.projectName
        if not os.path.exists(projectDir):
            os.mkdir(projectDir)

        for task in self.taskList:
            item = task['item']
            state = item.checkState(1)
            if state == QtCore.Qt.Unchecked:
                task['importFlag'] = False
            else:
                task['importFlag'] = True
        if not CGFunction_max.importModel(self.service, projectDir, self.taskList):
            print'Scene File is None'
        #self.service.userActionLog(CGConfig_max.userName, CGConfig_max.projectName, CGConfig_max.sceneName,
        #                               CGConfig_max.currentTask['_id'], CGConfig_max.RCMaya_Action_Reference)
        self.close()

def importFile(service):
    file_dialog = QtGui.QFileDialog(
        parent=None,
        caption="Open As",
        directory='',
        filter="3dsMax (*.max)"
    )
    file_dialog.setLabelText(QtGui.QFileDialog.Accept, "Open")
    file_dialog.setLabelText(QtGui.QFileDialog.Reject, "Cancel")
    file_dialog.setOption(QtGui.QFileDialog.DontResolveSymlinks)
    file_dialog.setOption(QtGui.QFileDialog.DontUseNativeDialog)
    if not file_dialog.exec_():
        return
    file = CGConfig_max.baseModelFile = file_dialog.selectedFiles()[0]
    MaxPlus.FileManager.Merge(file)

def outputAssets():
    CGFunction_max.outputAssets()

class tarchiveWindow(QtGui.QDialog):
    def __init__(self, service, parent=None):
        super(tarchiveWindow, self).__init__(parent)
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
        self.taskList = []
        self.selectFlag = ''
        self.setup_ui()

    def setup_ui(self):
        self.super_layout = QtGui.QHBoxLayout()
        self.main_layout = QtGui.QVBoxLayout()

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.projectLabel = QtGui.QLabel(u'项目', self)
        else:
            self.projectLabel = QtGui.QLabel(u'Project', self)
        self.projectText = QtGui.QLineEdit('', self)
        self.projectText.setEnabled(False)

        self.layout.addWidget(self.projectLabel, 0, 0)
        self.layout.addWidget(self.projectText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)
        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setIconSize(QtCore.QSize(60, 60))

        self.GetProjects()
        self.main_layout.addWidget(self.listWidget)

        self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemClicked (QListWidgetItem*)"), self.onClickItem)

        self.treeWidget = QtGui.QTreeWidget(self)
        headerList = []
        headerList.append(u'任务')
        headerList.append(u'选中')
        # headerList.append(u'路径')
        self.treeWidget.setHeaderLabels(headerList)
        self.main_layout.addWidget(self.treeWidget)
        header = self.treeWidget.header()
        header.setStretchLastSection(True)
        # header.resizeSection(4, 20）

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.dirLabel = QtGui.QLabel(u'输出目录', self)
            self.dirButton = QtGui.QPushButton(u'选择', self)
        else:
            self.dirLabel = QtGui.QLabel(u'OutputDir', self)
            self.dirButton = QtGui.QPushButton(u'Select', self)
        self.dirText = QtGui.QLineEdit('', self)
        self.layout.addWidget(self.dirLabel, 0, 0)
        self.layout.addWidget(self.dirText, 0, 1)
        self.layout.addWidget(self.dirButton, 0, 2)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)
        self.dirButton.clicked.connect(self.onSelectDir)

        self.row_Hbox = QtGui.QGroupBox()
        layout1 = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.button1 = QtGui.QPushButton(u'全选', self)
            self.button2 = QtGui.QPushButton(u'全不选', self)
            self.button3 = QtGui.QPushButton(u'归档', self)
            self.button4 = QtGui.QPushButton(u'取消', self)
        else:
            self.button1 = QtGui.QPushButton(u'SelectAll', self)
            self.button2 = QtGui.QPushButton(u'UnSelectAll', self)
            self.button3 = QtGui.QPushButton(u'Tar', self)
            self.button4 = QtGui.QPushButton(u'Cancel', self)
        layout1.addWidget(self.button1, 0, 0)
        layout1.addWidget(self.button2, 0, 1)
        layout1.addWidget(self.button4, 0, 2)
        layout1.addWidget(self.button3, 0, 3)
        self.button1.clicked.connect(self.onSelectAll)
        self.button2.clicked.connect(self.onUnSelectAll)
        self.button3.clicked.connect(self.onTar)
        self.button4.clicked.connect(self.onCancel)
        self.row_Hbox.setLayout(layout1)
        self.main_layout.addWidget(self.row_Hbox)

        if CGConfig_max.lang == 'zh':
            self.setWindowTitle(u'归档')
        else:
            self.setWindowTitle(u'Tarchive')

        self.setLayout(self.main_layout)
        self.setGeometry(400, 350, 650, 650)

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def myCompare(self, a, b):
        str1 = a['name'].lower()
        str2 = b['name'].lower()
        return cmp(str1, str2)

    def GetProjects(self):
        self.listWidget.clear()
        result = self.service.myWFGetProjects(CGConfig_max.userName)
        if not result:
            return None
        self.projectList = json.loads(result)
        self.projectList.sort(cmp=self.myCompare)
        textFont = QtGui.QFont("song", 16, QtGui.QFont.Normal)

        for project in self.projectList:
            item = QtGui.QListWidgetItem(project['name'])
            item.setFont(textFont)
            self.listWidget.addItem(item)

    def GetTasks(self):
        self.treeWidget.clear()
        result = self.service.myWFGetTasksOfProject(self.projectName)
        if not result:
            return None
        self.taskList = json.loads(result)
        self.taskList.sort(cmp=self.myCompare)
        textFont = QtGui.QFont("song", 16, QtGui.QFont.Normal)
        for task in self.taskList:
            item = QtGui.QTreeWidgetItem(self.treeWidget, [task['name']])
            item.setFont(0, textFont)
            self.treeWidget.resizeColumnToContents(0)
            item.setCheckState(1, QtCore.Qt.Unchecked)
            item.setChildIndicatorPolicy(QtGui.QTreeWidgetItem.ShowIndicator)
            task['item'] = item

    def onClickItem(self, item):
        row = self.listWidget.currentRow()
        self.projectText.setText(self.projectList[row]['name'])
        self.projectName = self.projectList[row]['name']
        self.GetTasks()

    def onSelectDir(self):
        if CGConfig_max.lang == 'zh':
            dialog = QtGui.QFileDialog(self, "选择目录", ".", "*")
        else:
            dialog = QtGui.QFileDialog(self, "Select Dir", ".", "*")
        dialog.setFileMode(QtGui.QFileDialog.Directory)
        if dialog.exec_():
            dir = dialog.selectedFiles()
            self.dirText.setText(dir[0])

    def onSelectAll(self):
        for task in self.taskList:
            task['item'].setCheckState(1, QtCore.Qt.Checked)

    def onUnSelectAll(self):
        for task in self.taskList:
            task['item'].setCheckState(1, QtCore.Qt.Unchecked)

    def onCancel(self):
        # self.menu.setEnable(True)
        self.close()

    def onTar(self):
        if not self.dirText.text():
            return
        for task in self.taskList:
            state = task['item'].checkState(1)
            if state == QtCore.Qt.Checked:
                CGFunction_max.tarTask(self.service, self.dirText.text(), task)
        self.close()

    def closeEvent(self, event):
        event.accept()  # let the window close

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
        if CGConfig_max.lang == 'zh':
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
        if CGConfig_max.lang == 'zh':
            self.projectLabel = QtGui.QLabel(u'项目', self)
        else:
            self.projectLabel = QtGui.QLabel(u'Project', self)
        self.projectText = QtGui.QLineEdit(CGConfig_max.projectName, self)
        self.projectText.setEnabled(False)

        self.layout.addWidget(self.projectLabel, 0, 0)
        self.layout.addWidget(self.projectText, 0, 1)

        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
            self.sceneLabel = QtGui.QLabel(u'场景任务', self)
        else:
            self.sceneLabel = QtGui.QLabel(u'Scene', self)
        self.sceneText = QtGui.QLineEdit(CGConfig_max.sceneName, self)
        self.sceneText.setEnabled(False)

        self.layout.addWidget(self.sceneLabel, 0, 0)
        self.layout.addWidget(self.sceneText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)
        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
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
        if CGConfig_max.lang == 'zh':
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
        if CGConfig_max.lang == 'zh':
            self.setWindowTitle(u'提交渲染作业')
        else:
            self.setWindowTitle(u'Submit Render Job')
        self.setGeometry(400, 300, 450, 100)

    def setProjectName(self, projectName):
        self.projectText.setText(projectName)
        CGConfig_max.projectName = projectName

    def setSceneName(self, sceneName):
        self.sceneText.setText(sceneName)
        CGConfig_max.sceneName = sceneName

    def setSceneID(self, sceneID):
        self.sceneID = sceneID

    def onSubmit(self):
        CGConfig_max.projectName = self.projectText.text()
        CGConfig_max.sceneName = self.sceneText.text()
        """"
        RCOperation_max.renderScene(self.service, CGConfig_max.userName, self.jobText.text(), CGConfig_max.projectName,
                                 CGConfig_max.sceneName, '', self.frameText.text())

        self.service.userActionLog(CGConfig_max.userName, CGConfig_max.projectName,
                                   CGConfig_max.sceneName, 'RenderScene')
        self.menu.setEnable(True)
        self.close()
        """
    def onCancel(self):
        self.menu.setEnable(True)
        self.close()

class setupWindow(QtGui.QDialog):
    def __init__(self, service, parent = None):
        super(setupWindow, self).__init__(parent)
        # And now set up the UI
        self.service = service
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QtGui.QVBoxLayout()

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.myRootURLLabel = QtGui.QLabel(u'入口：', self)
        self.myRootURLText = SuperDuperText()
        self.myRootURLText.setText(CGConfig_max.myRootURL)
        self.layout.addWidget(self.myRootURLLabel, 1, 0)
        self.layout.addWidget(self.myRootURLText, 1, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.teamLabel = QtGui.QLabel(u'团队：', self)
        self.teamText = SuperDuperText()
        self.teamText.setText(CGConfig_max.teamName)
        self.layout.addWidget(self.teamLabel, 1, 0)
        self.layout.addWidget(self.teamText, 1, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        if self.service:
            self.row_Hbox = QtGui.QGroupBox()
            self.layout = QtGui.QGridLayout()
            self.storageLabel = QtGui.QLabel(u'缓冲区路径：', self)
            self.storageText = SuperDuperText()
            self.storageText.setText(CGConfig_max.storageDir)
            self.layout.addWidget(self.storageLabel, 1, 0)
            self.layout.addWidget(self.storageText, 1, 1)
            self.row_Hbox.setLayout(self.layout)
            self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        if CGConfig_max.lang == 'zh':
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
        if CGConfig_max.lang == 'zh':
            self.setWindowTitle(u'设置')
        else:
            self.setWindowTitle(u'Setup')
        self.setGeometry(400, 300, 450, 200)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)

    def onClickItem(self, item):
        str = self.preItem.text().split(' ')[0]
        self.preItem.setText(str.ljust(30, ' ') + ' ')

        str = item.text().split(' ')[0]
        item.setText(str.ljust(30, ' ') + 'X')
        self.preItem = item

    def onClear(self):
        CGConfig_max.storageDir = self.storageText.text()
        if os.path.exists(CGConfig_max.storageDir):
            reply = QtGui.QMessageBox.question(self, u"问题", u"是否项目缓冲区?",
                                                  QtGui.QMessageBox.StandardButton.Yes | QtGui.QMessageBox.StandardButton.No)
            if reply == QtGui.QMessageBox.Yes:
                shutil.rmtree(CGConfig_max.storageDir)
                os.rmkdir(CGConfig_max.storageDir)

        self.service.userActionLog(CGConfig_max.userName, '', '', '', CGConfig_max.RCMaya_Action_ClearBuffer)
        self.menu.setEnable(True)
        self.close()

    def onSetup(self):
        CGConfig_max.myRootURL = self.myRootURLText.text()
        CGConfig_max.teamName = self.teamText.text()
        if self.service:
            CGConfig_max.storageDir = self.storageText.text()
            if not os.path.exists(CGConfig_max.storageDir):
                os.mkdir(CGConfig_max.storageDir)
        if not self.service:
            self.service = CGService_max.DAMService()
            if not self.service.status:
                return None
        #self.service.userActionLog(CGConfig_max.userName, '', '', '', CGConfig_max.RCMaya_Action_Setu
        self.close()

    def onCancel(self):
        self.close()

    def closeEvent(self, event):
        # do stuff
        event.accept() # let the window close


