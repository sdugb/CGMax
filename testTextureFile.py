import MaxPlus

assets = MaxPlus.AssetManager.GetAssets()
print "There are ", len(assets), " assets"
for i in range(len(assets)):
    print "fileName =", assets[i].ResolvedFileName