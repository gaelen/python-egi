import fwhelper as fwh

FWH = fwh.FunctionWrappingHelper     

class Klass:

    def method1(self, a,b,c):
       pass

    @staticmethod
    def method2(a,b,c,d): pass     


FWH(Klass.method1).dump()     
FWH(Klass.method2).dump()     

klass = Klass()
FWH(klass.method1).dump()     
FWH(klass.method2).dump()     
