class dbCollections(object):
    def __init__(self):
        # Init collection types as their names.
        self.__dict__[u"Datasets"] = u"Datasets"
        self.__dict__[u"Adp"] = u"Adp"
        self.__dict__[u"Merge"] = u"Merge"
        self.__dict__[u"Eiger"] = u"Eiger"
        self.__dict__[u"Stream"] = u"Stream"
        self.__dict__[u"MergeState"] = u"MergeState"
        self.__dict__[u"CurrentMergeId"] = u"CurrentMergeId"
        self.__dict__[u"Abort"] = u"Abort"
        self.__dict__[u"Spreadsheet"] = u"Spreadsheet"
        self.__dict__[u"Shipping"] = u"Shipping"
        self.__dict__[u"PuckInventory"] = u"PuckInventory"
        self.__dict__[u"Vdp"] = u"Vdp"

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, item, value):
        self.__dict__[item] = value

    def collectionTypes(self):
        return self.__dict__.keys()

    def collectionNames(self):
        return self.__dict__.values()

    def collectionTypeParser(self):
        return dict((k.lower(), k) for k in self.__dict__.keys())

    def __repr__(self):
        s = "".join(["%s, " % k for k in self.__dict__.keys()])
        return s
