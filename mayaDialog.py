
#coding=utf-8

import sys, os
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *
import shiboken

import json
import urllib
import urllib2
import cookielib
import xml.dom.minidom
import DAMService

infoFileName = "info.conf"

storageDir = cmds.internalVar(userWorkspaceDir = True)
IconWidth = 128
IconHeight = 128

def maya_main_window():
    main_win_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(main_win_ptr), QtGui.QWidget)



class newSceneWindow(QtGui.QDialog):
    def __init__(self, service, saveAsMenuItem, parent = maya_main_window()):
        super(newSceneWindow, self).__init__(parent)
        self.service = service  
        self.saveAsMenuItem = saveAsMenuItem
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QtGui.QVBoxLayout()
        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()

        self.sceneLabel = QLabel(u'Scene Name:', self)
        self.sceneText = QLineEdit('', self)

        self.layout.addWidget(self.sceneLabel, 0, 0)
        self.layout.addWidget(self.sceneText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()

        self.button1 = QtGui.QPushButton(u'Create', self)
        self.button2 = QtGui.QPushButton(u'Cancel', self)
        self.layout.addWidget(self.button1, 1, 1)
        self.layout.addWidget(self.button2, 1, 0)

        self.button1.clicked.connect(self.onCreate)
        self.button2.clicked.connect(self.onCancel)

        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.setLayout(self.main_layout)
        self.setWindowTitle(u'Create New Scene')
        self.setGeometry(300, 300, 400, 200)

    def onCreate(self):
        sceneName = self.sceneText.text()
        result = self.service.getfolder(None, sceneName)
        data = json.loads(result)
        print 'data =', data
        isExisted = False
        if data['DATA'] != []:
            for array in data['DATA']:
                if sceneName == array[2]:
                    folder_id = array[0]
                    isExisted = True
                    break
        #scene is existed
        if isExisted:
            QtGui.QMessageBox.information( self, u"Error", u"Scene has been Existed")
            """
            mb = QtGui.QMessageBox(self)
            mb.setText(u"Prompt Message")
            mb.setInformativeText(u"Scene is Exist, it Created？")
            mb.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            mb.setDefaultButton(QtGui.QMessageBox.Yes)  
            ret = mb.exec_()
            if ret == QtGui.QMessageBox.Yes:
                folder_id = data['DATA'][0][0]
                mb.destroy()
            else:
                mb.destroy()
                return
            """
        #scene is not existed
        else:
            result = self.service.setfolder(sceneName)
            array = json.loads(result)
            print 'create_array =', array
            if array["responsecode"] ==  0:
                folder_id = array["folder_id"]
                result = self.service.setfolder('texture', folder_id)
                array = json.loads(result)
                if array["responsecode"] != 0:
                    QtGui.QMessageBox.information( self, u"Error", array["message"])
                    return
            else:
                QtGui.QMessageBox.information( self, u"Error", array["message"])
                return

        file_object = open(storageDir + infoFileName, "wb")
        string = ',' + sceneName + ',' + folder_id
        print 'string =', string
        file_object.writelines(string)
        file_object.close()

        self.saveAsMenuItem.setEnable(True) 
        self.destroy()

    def onCancel(self):
        self.destroy()




class deleteWindow(QtGui.QDialog):
    def __init__(self, service, parent = maya_main_window()):
        super(deleteWindow, self).__init__(parent)
        self.service = service
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QtGui.QVBoxLayout()
        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()

        self.sceneLabel = QLabel(u'SceneID:', self)
        self.sceneText = QLineEdit('', self)

        self.layout.addWidget(self.sceneLabel, 0, 0)
        self.layout.addWidget(self.sceneText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()

        self.button1 = QtGui.QPushButton(u'Delete', self)
        self.button2 = QtGui.QPushButton(u'Cancel', self)
        self.layout.addWidget(self.button1, 1, 1)
        self.layout.addWidget(self.button2, 1, 0)

        self.button1.clicked.connect(self.onDelete)
        self.button2.clicked.connect(self.onCancel)

        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.setLayout(self.main_layout)
        self.setWindowTitle(u'Delete Scene')
        self.setGeometry(300, 300, 400, 200)

    def onDelete(self):
        result = self.service.removefolder(self.sceneText.text())
        if result:
            self.destroy()
        else:
            QtGui.QMessageBox.information( self, u"Error", u"ID is Error!!!" )

    def onCancel(self):
        self.destroy()

class setupWindow(QtGui.QDialog):
    def __init__(self, parent = maya_main_window()):
        super(setupWindow, self).__init__(parent)
        # And now set up the UI
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QtGui.QVBoxLayout()

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.urlLabel = QLabel(u'URL：', self)
        self.urlText = QLineEdit('myURL', self)
        self.layout.addWidget(self.urlLabel, 0, 0)
        self.layout.addWidget(self.urlText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.button1 = QtGui.QPushButton(u'Setup', self)
        self.button2 = QtGui.QPushButton(u'Cancel', self)
        self.layout.addWidget(self.button1, 1, 1)
        self.layout.addWidget(self.button2, 1, 0)
        self.button1.clicked.connect(self.onSetup)
        self.button2.clicked.connect(self.onCancel)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.setLayout(self.main_layout)
        self.setWindowTitle(u'Setup')
        self.setGeometry(300, 300, 400, 200)

    def onSetup(self):
        myURL = self.urlText.text()
        self.destroy()

    def onCancel(self):
        self.destroy()
