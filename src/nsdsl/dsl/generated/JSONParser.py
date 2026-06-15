# Generated from grammar/JSON.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,12,56,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,1,0,1,0,1,1,1,
        1,1,1,1,1,5,1,17,8,1,10,1,12,1,20,9,1,1,1,1,1,1,1,1,1,3,1,26,8,1,
        1,2,1,2,1,2,1,2,1,3,1,3,1,3,1,3,5,3,36,8,3,10,3,12,3,39,9,3,1,3,
        1,3,1,3,1,3,3,3,45,8,3,1,4,1,4,1,4,1,4,1,4,1,4,1,4,3,4,54,8,4,1,
        4,0,0,5,0,2,4,6,8,0,0,60,0,10,1,0,0,0,2,25,1,0,0,0,4,27,1,0,0,0,
        6,44,1,0,0,0,8,53,1,0,0,0,10,11,3,8,4,0,11,1,1,0,0,0,12,13,5,1,0,
        0,13,18,3,4,2,0,14,15,5,2,0,0,15,17,3,4,2,0,16,14,1,0,0,0,17,20,
        1,0,0,0,18,16,1,0,0,0,18,19,1,0,0,0,19,21,1,0,0,0,20,18,1,0,0,0,
        21,22,5,3,0,0,22,26,1,0,0,0,23,24,5,1,0,0,24,26,5,3,0,0,25,12,1,
        0,0,0,25,23,1,0,0,0,26,3,1,0,0,0,27,28,5,10,0,0,28,29,5,4,0,0,29,
        30,3,8,4,0,30,5,1,0,0,0,31,32,5,5,0,0,32,37,3,8,4,0,33,34,5,2,0,
        0,34,36,3,8,4,0,35,33,1,0,0,0,36,39,1,0,0,0,37,35,1,0,0,0,37,38,
        1,0,0,0,38,40,1,0,0,0,39,37,1,0,0,0,40,41,5,6,0,0,41,45,1,0,0,0,
        42,43,5,5,0,0,43,45,5,6,0,0,44,31,1,0,0,0,44,42,1,0,0,0,45,7,1,0,
        0,0,46,54,5,10,0,0,47,54,5,11,0,0,48,54,3,2,1,0,49,54,3,6,3,0,50,
        54,5,7,0,0,51,54,5,8,0,0,52,54,5,9,0,0,53,46,1,0,0,0,53,47,1,0,0,
        0,53,48,1,0,0,0,53,49,1,0,0,0,53,50,1,0,0,0,53,51,1,0,0,0,53,52,
        1,0,0,0,54,9,1,0,0,0,5,18,25,37,44,53
    ]

class JSONParser ( Parser ):

    grammarFileName = "JSON.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'{'", "','", "'}'", "':'", "'['", "']'", 
                     "'true'", "'false'", "'null'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "STRING", "NUMBER", "WS" ]

    RULE_json = 0
    RULE_obj = 1
    RULE_pair = 2
    RULE_arr = 3
    RULE_value = 4

    ruleNames =  [ "json", "obj", "pair", "arr", "value" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    STRING=10
    NUMBER=11
    WS=12

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class JsonContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def value(self):
            return self.getTypedRuleContext(JSONParser.ValueContext,0)


        def getRuleIndex(self):
            return JSONParser.RULE_json

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterJson" ):
                listener.enterJson(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitJson" ):
                listener.exitJson(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitJson" ):
                return visitor.visitJson(self)
            else:
                return visitor.visitChildren(self)




    def json(self):

        localctx = JSONParser.JsonContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_json)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 10
            self.value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ObjContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pair(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(JSONParser.PairContext)
            else:
                return self.getTypedRuleContext(JSONParser.PairContext,i)


        def getRuleIndex(self):
            return JSONParser.RULE_obj

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterObj" ):
                listener.enterObj(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitObj" ):
                listener.exitObj(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitObj" ):
                return visitor.visitObj(self)
            else:
                return visitor.visitChildren(self)




    def obj(self):

        localctx = JSONParser.ObjContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_obj)
        self._la = 0 # Token type
        try:
            self.state = 25
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 12
                self.match(JSONParser.T__0)
                self.state = 13
                self.pair()
                self.state = 18
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==2:
                    self.state = 14
                    self.match(JSONParser.T__1)
                    self.state = 15
                    self.pair()
                    self.state = 20
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 21
                self.match(JSONParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 23
                self.match(JSONParser.T__0)
                self.state = 24
                self.match(JSONParser.T__2)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PairContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(JSONParser.STRING, 0)

        def value(self):
            return self.getTypedRuleContext(JSONParser.ValueContext,0)


        def getRuleIndex(self):
            return JSONParser.RULE_pair

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPair" ):
                listener.enterPair(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPair" ):
                listener.exitPair(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPair" ):
                return visitor.visitPair(self)
            else:
                return visitor.visitChildren(self)




    def pair(self):

        localctx = JSONParser.PairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_pair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 27
            self.match(JSONParser.STRING)
            self.state = 28
            self.match(JSONParser.T__3)
            self.state = 29
            self.value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArrContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def value(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(JSONParser.ValueContext)
            else:
                return self.getTypedRuleContext(JSONParser.ValueContext,i)


        def getRuleIndex(self):
            return JSONParser.RULE_arr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArr" ):
                listener.enterArr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArr" ):
                listener.exitArr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArr" ):
                return visitor.visitArr(self)
            else:
                return visitor.visitChildren(self)




    def arr(self):

        localctx = JSONParser.ArrContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_arr)
        self._la = 0 # Token type
        try:
            self.state = 44
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 31
                self.match(JSONParser.T__4)
                self.state = 32
                self.value()
                self.state = 37
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==2:
                    self.state = 33
                    self.match(JSONParser.T__1)
                    self.state = 34
                    self.value()
                    self.state = 39
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 40
                self.match(JSONParser.T__5)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 42
                self.match(JSONParser.T__4)
                self.state = 43
                self.match(JSONParser.T__5)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(JSONParser.STRING, 0)

        def NUMBER(self):
            return self.getToken(JSONParser.NUMBER, 0)

        def obj(self):
            return self.getTypedRuleContext(JSONParser.ObjContext,0)


        def arr(self):
            return self.getTypedRuleContext(JSONParser.ArrContext,0)


        def getRuleIndex(self):
            return JSONParser.RULE_value

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue" ):
                listener.enterValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue" ):
                listener.exitValue(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitValue" ):
                return visitor.visitValue(self)
            else:
                return visitor.visitChildren(self)




    def value(self):

        localctx = JSONParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_value)
        try:
            self.state = 53
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [10]:
                self.enterOuterAlt(localctx, 1)
                self.state = 46
                self.match(JSONParser.STRING)
                pass
            elif token in [11]:
                self.enterOuterAlt(localctx, 2)
                self.state = 47
                self.match(JSONParser.NUMBER)
                pass
            elif token in [1]:
                self.enterOuterAlt(localctx, 3)
                self.state = 48
                self.obj()
                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 4)
                self.state = 49
                self.arr()
                pass
            elif token in [7]:
                self.enterOuterAlt(localctx, 5)
                self.state = 50
                self.match(JSONParser.T__6)
                pass
            elif token in [8]:
                self.enterOuterAlt(localctx, 6)
                self.state = 51
                self.match(JSONParser.T__7)
                pass
            elif token in [9]:
                self.enterOuterAlt(localctx, 7)
                self.state = 52
                self.match(JSONParser.T__8)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





