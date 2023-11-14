class beamlines(object):
    def __init__(self):
        # Init collection types as their names.
        self.__dict__[u'x06sa']  = u'x06sa'
        self.__dict__[u'x06da']  = u'x06da'
        self.__dict__[u'x10sa']  = u'x10sa'
        self.__dict__[u'X06SA']  = u'x06sa'
        self.__dict__[u'X06DA']  = u'x06da'
        self.__dict__[u'X10SA']  = u'x10sa'
        self.__dict__[u'PXI']    = u'x06sa'
        self.__dict__[u'PXII']   = u'x10sa'
        self.__dict__[u'PXIII']  = u'x06da'
        self.__dict__[u'pxi']    = u'x06sa'
        self.__dict__[u'pxii']   = u'x10sa'
        self.__dict__[u'pxiii']  = u'x06da'

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, item, value):
        self.__dict__[item] = value

    def beamlineNames(self):
        return self.__dict__.keys()

    def __repr__(self):
        s = ''.join(['%s, ' % k for k in self.__dict__.keys()])
        return s
