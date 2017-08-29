from PySide import QtGui
import MaxPlus

class _GCProtector(object):
    widgets = []

def make_cylinder():
    obj = MaxPlus.Factory.CreateGeomObject(MaxPlus.ClassIds.Cylinder)
    obj.ParameterBlock.Radius.Value = 10.0
    obj.ParameterBlock.Height.Value = 30.0
    node = MaxPlus.Factory.CreateNode(obj)
    time = MaxPlus.Core.GetCurrentTime()
    MaxPlus.ViewportManager.RedrawViews(time)

    return

app = QtGui.QApplication.instance()
if not app:
    app = QtGui.QApplication([])
    

def main(): 
    def doLogin():
        print "aaa"
        #MaxPlus.FileManager.Reset(True)
        w = QtGui.QWidget()
        print "ff"
        w.resize(250, 100)
        w.setWindowTitle('Window')
        _GCProtector.widgets.append(w)
        w.show()
        
        main_layout = QtGui.QVBoxLayout()
        label = QtGui.QLabel("Click button to create a cylinder in the scene")
        main_layout.addWidget(label)
        
        cylinder_btn = QtGui.QPushButton("Cylinder")
        main_layout.addWidget(cylinder_btn)
        w.setLayout(main_layout)
        
        cylinder_btn.clicked.connect(make_cylinder)    
    
    print "aaaa"
    
    login_action = MaxPlus.ActionFactory.Create('Login', 'Login', doLogin)
    login_action.Execute()
            
    #logout_action = MaxPlus.ActionFactory.Create('Logout', 'Logout', doLogout)
    #logout_action.Execute()    
        
    #newScene_action = MaxPlus.ActionFactory.Create('New Scene', 'New Scene', doNewScene)
    #newScene_action.Execute()    
    
    #openScene_action = MaxPlus.ActionFactory.Create('Open Scene', 'Open Scene', doOpenScene)
    #openScene_action.Execute()
        
    #saveAsScene_action = MaxPlus.ActionFactory.Create('saveAs Scene', 'saveAs Scene', doSaveasScene)
    #saveAsScene_action.Execute()  
        
    #renderScene_action = MaxPlus.ActionFactory.Create('Render Scene', 'Render Scene', doRenderScene)
    #renderScene_action.Execute()      
           
    print "Removing any previously left 'menu items'"
    MaxPlus.MenuManager.UnregisterMenu(u"RCMenu")
    
    mb = MaxPlus.MenuBuilder('RCMenu')
    mb.AddItem(login_action)
    #mb.AddItem(logout_action)
    mb.AddSeparator()
        
    #mb.AddItem(newScene_action)
    #mb.AddItem(openScene_action)
    #mb.AddItem(saveAsScene_action)
    #mb.AddSeparator()
    #mb.AddItem(renderScene_action)
        
    menu = mb.Create(MaxPlus.MenuManager.GetMainMenu())  
    
    MaxPlus.FileManager.Reset(True)
    w = QtGui.QWidget()
    print "ff"
    w.resize(300, 300)
    w.setWindowTitle('title')
    _GCProtector.widgets.append(w)
    w.show()
        
    main_layout = QtGui.QVBoxLayout()
    label = QtGui.QLabel("Click button to create a cylinder in the scene")
    main_layout.addWidget(label)
        
    cylinder_btn = QtGui.QPushButton("Cylinder")
    main_layout.addWidget(cylinder_btn)
    w.setLayout(main_layout)
    
    cylinder_btn.clicked.connect(make_cylinder)      
    

if __name__ == '__main__':
    main()
