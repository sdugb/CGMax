

#from PySide.QtCore import *
#from PySide.QtGui import *
from PySide import QtGui
import MaxPlus
import DAMService
#import mayaDialog

class _GCProtector(object):
    widgets = []    
       
class loginWindow(QtGui.QDialog):
    #def __init__(self, service, parent = maya_main_window()):
    def __init__(self, service, parent = None):
        super(loginWindow, self).__init__(parent)
        print "aaa"
        # And now set up the UI
        self.setup_ui()
        self.service = service

    def setup_ui(self):
        self.main_layout =QtGui.QVBoxLayout()

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.nameLabel = QLabel(u'�û�����', self)
        self.nameText = QLineEdit('gb', self)
        self.layout.addWidget(self.nameLabel, 0, 0)
        self.layout.addWidget(self.nameText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.passLabel = QLabel(u'��  �룺', self)
        self.passText = QLineEdit('gbzz01', self)
        self.passText.setEchoMode(QtGui.QLineEdit.Password)
        self.layout.addWidget(self.passLabel, 0, 0)
        self.layout.addWidget(self.passText, 0, 1)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.row_Hbox = QtGui.QGroupBox()
        self.layout = QtGui.QGridLayout()
        self.button1 = QtGui.QPushButton(u'��¼', self)
        self.button2 = QtGui.QPushButton(u'ȡ��', self)
        self.layout.addWidget(self.button1, 1, 1)
        self.layout.addWidget(self.button2, 1, 0)
        self.button1.clicked.connect(self.onLogin)
        self.button2.clicked.connect(self.onCancel)
        self.row_Hbox.setLayout(self.layout)
        self.main_layout.addWidget(self.row_Hbox)

        self.setLayout(self.main_layout)
        self.setWindowTitle(u'�û���¼')
        self.setGeometry(300, 300, 400, 200)

    def onLogin(self):
        username = self.nameText.text()
        password = self.passText.text()
        result = self.service.login(username, password)
        if result == '0':
            QtGui.QMessageBox.information( self, u"Error", u"UserName or Password is not correct!!!" )   
        elif result == '1':
            QtGui.QMessageBox.information( self, u"Prompt", u"Portal Service is not opened" )
        else:
            self.close()

    def onCancel(self):
        self.close()
    
  
def doLogin():

    service = DAMService.DAMService()
    print "doLogin"
    """
    #MaxPlus.FileManager.Reset(True)
    w = QtGui.QWidget()
    print "ff"
    w.resize(250, 100)
    w.setWindowTitle('Window')
    print "ggg"
    _GCProtector.widgets.append(w)
    print "www"
    w.show()
    print "zzz"
            
    main_layout = QtGui.QVBoxLayout()
    label = QtGui.QLabel("Click button to create a cylinder in the scene")
    main_layout.addWidget(label)
              
    cylinder_btn = QtGui.QPushButton("Cylinder")
    main_layout.addWidget(cylinder_btn)
    w.setLayout(main_layout)
    """
    win = loginWindow(service)
    print "ggg"
    #print win
    _GCProtector.widgets.append(win)
    win.show()
    
def doLogout():
    print "doLogout"
    
def doNewScene():
    print "doNewScene"
    
def doOpenScene():
    print "doOpenScene"

def doSaveasScene():
    print "doSaveasScene"

def doRenderScene():
    print "doRenderScene"
"""
app = QtGui.QApplication.instance()
if not app:
    app = QtGui.QApplication([]) 
"""
def main():
    print "aaa"
    app = QtGui.QApplication.instance()
    if not app:
        app = QtGui.QApplication([])

    login_action = MaxPlus.ActionFactory.Create('Login', 'Login', doLogin)
    login_action.Execute()
          
    logout_action = MaxPlus.ActionFactory.Create('Logout', 'Logout', doLogout)
    logout_action.Execute()    
    
    newScene_action = MaxPlus.ActionFactory.Create('New Scene', 'New Scene', doNewScene)
    newScene_action.Execute()    

    openScene_action = MaxPlus.ActionFactory.Create('Open Scene', 'Open Scene', doOpenScene)
    openScene_action.Execute()
    
    saveAsScene_action = MaxPlus.ActionFactory.Create('saveAs Scene', 'saveAs Scene', doSaveasScene)
    saveAsScene_action.Execute()  
    
    renderScene_action = MaxPlus.ActionFactory.Create('Render Scene', 'Render Scene', doRenderScene)
    renderScene_action.Execute()      
            
    print "Removing any previously left 'menu items'"
    MaxPlus.MenuManager.UnregisterMenu(u"RCMenu")

    mb = MaxPlus.MenuBuilder('RCMenu')
    mb.AddItem(login_action)
    mb.AddItem(logout_action)
    mb.AddSeparator()
    
    mb.AddItem(newScene_action)
    mb.AddItem(openScene_action)
    mb.AddItem(saveAsScene_action)
    mb.AddSeparator()
    mb.AddItem(renderScene_action)
    
    menu = mb.Create(MaxPlus.MenuManager.GetMainMenu()) 
    
if __name__ == '__main__':
    main()


