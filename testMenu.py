'''
    Demonstrates the menu manager API.
'''
import MaxPlus


def outputMenuItem(item, recurse=True, indent=''):
    text = item.GetTitle()
    print indent, text if text else "----"
    if item.HasSubMenu and recurse:
        outputMenu(item.SubMenu, recurse, indent + '   ')


def outputMenu(menu, recurse=True, indent=''):
    for i in menu.Items:
        outputMenuItem(i, recurse, indent)


somethingHappened = False


def doSomething():
    global somethingHappened
    somethingHappened = True
    print 'Something happened'


action = MaxPlus.ActionFactory.Create('Do something', 'Python demos', doSomething)


def createTestMenu(name):
    if not MaxPlus.MenuManager.MenuExists(name):
        mb = MaxPlus.MenuBuilder(name)
        if action._IsValidWrapper():
            print "Created action"
        else:
            print "Failed to create action"
        mb.AddItem(action)
        mb.AddSeparator()
        menu = mb.Create(MaxPlus.MenuManager.GetMainMenu())
        print 'menu created', menu.Title
    else:
        print 'The menu ', name, ' already exists'


def getLastMenuItem(menu=MaxPlus.MenuManager.GetMainMenu()):
    return list(menu.Items)[-1]


def testLastItem(text):
    assert (getLastMenuItem().Title == text)


def main():
    print "Removing any previously left 'menu items'"
    MaxPlus.MenuManager.UnregisterMenu(u"Test")

    print "Creating a new menu"
    testLastItem(u"&Help")
    outputMenu(MaxPlus.MenuManager.GetMainMenu(), False)

    print "Creating a new menu"
    createTestMenu(u"Test")
    outputMenu(MaxPlus.MenuManager.GetMainMenu(), False)
    testLastItem(u"Test")

    assert (not somethingHappened)
    mi = getLastMenuItem()
    mi = list(mi.SubMenu.Items)[0]
    ai = mi.ActionItem
    ai.Execute()
    assert (somethingHappened)

    print "Unregistering the 'test' menu"
    MaxPlus.MenuManager.UnregisterMenu(u"Test")
    outputMenu(MaxPlus.MenuManager.GetMainMenu(), False)
    testLastItem(u"&Help")


if __name__ == '__main__':
    main()

