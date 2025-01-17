### $ANTLR 2.7.7 (2006-11-01): "yacc.g" -> "YaccParser.py"$
### import antlr and other modules ..
import sys
import antlr

version = sys.version.split()[0]
# if version < '2.2.1':
#     False = 0
# if version < '2.3':
#     True = not False
### header action >>> 

### header action <<< 
### preamble action>>>

### preamble action <<<

### import antlr.Token 
from antlr import Token
### >>>The Known Token Types <<<
SKIP                = antlr.SKIP
INVALID_TYPE        = antlr.INVALID_TYPE
EOF_TYPE            = antlr.EOF_TYPE
EOF                 = antlr.EOF
NULL_TREE_LOOKAHEAD = antlr.NULL_TREE_LOOKAHEAD
MIN_USER_TYPE       = antlr.MIN_USER_TYPE
ID = 4
COLON = 5
SEMICOLON = 6
CHAR = 7
STRING = 8
ERROR = 9
PREC = 10
DPREC = 11
UINT = 12
ACTION = 13
OR = 14
HYPHEN = 15
CARROT = 16
BANG = 17
LETTER = 18
DIGIT = 19
SL_COMMENT = 20
ML_COMMENT = 21
WS = 22

class Parser(antlr.LLkParser):
    ### user action >>>
    ### user action <<<
    
    def __init__(self, *args, **kwargs):
        antlr.LLkParser.__init__(self, *args, **kwargs)
        self.tokenNames = _tokenNames
        ### __init__ header action >>> 
        self.NonTerminals= set([])
        self.Terminals= set([])
        self.Rules=[]
        ### __init__ header action <<< 
        
    def grammar(self):    
        
        try:      ## for error handling
            pass
            _cnt3= 0
            while True:
                if (self.LA(1)==ID):
                    pass
                    self.rule()
                else:
                    break
                
                _cnt3 += 1
            if _cnt3 < 1:
                raise antlr.NoViableAltException(self.LT(1), self.getFilename())
            self.match(EOF_TYPE)
        
        except antlr.RecognitionException as ex:
            self.reportError(ex)
            self.consume()
            self.consumeUntil(_tokenSet_0)
        
    
    def rule(self):    
        
        id = None
        try:      ## for error handling
            pass
            pass
            id = self.LT(1)
            self.match(ID)
            self.NonTerminals.add(id.getText())
            self.match(COLON)
            self.rhs(id.getText())
            self.match(SEMICOLON)
        
        except antlr.RecognitionException as ex:
            self.reportError(ex)
            self.consume()
            self.consumeUntil(_tokenSet_1)
        
    
    def rhs(self,
        lhs
    ):    
        
        id = None
        c = None
        str = None
        pi = None
        pc = None
        dpd = None
        right=[]
        try:      ## for error handling
            pass
            while True:
                la1 = self.LA(1)
                if False:
                    pass
                elif la1 and la1 in [ID]:
                    pass
                    pass
                    id = self.LT(1)
                    self.match(ID)
                    right.append(("node",id.getText()))
                    # Heuristic: all UPPER case indicates a Terminal node 
                    
                    if id.getText() == id.getText().upper():
                       self.Terminals.add(id.getText())
                    else:
                       self.NonTerminals.add(id.getText())
                elif la1 and la1 in [CHAR]:
                    pass
                    pass
                    c = self.LT(1)
                    self.match(CHAR)
                    right.append(("node",c.getText()))
                    self.Terminals.add(c.getText())
                elif la1 and la1 in [STRING]:
                    pass
                    pass
                    str = self.LT(1)
                    self.match(STRING)
                    right.append(("node",str.getText()))
                    self.Terminals.add(str.getText())
                elif la1 and la1 in [ERROR]:
                    pass
                    self.match(ERROR)
                    right.append(("error","error"))
                elif la1 and la1 in [PREC]:
                    pass
                    self.match(PREC)
                    la1 = self.LA(1)
                    if False:
                        pass
                    elif la1 and la1 in [ID]:
                        pass
                        pass
                        pi = self.LT(1)
                        self.match(ID)
                        right.append(("%prec","%prec "+pi.getText()))
                    elif la1 and la1 in [CHAR]:
                        pass
                        pass
                        pc = self.LT(1)
                        self.match(CHAR)
                        right.append(("%prec","%prec "+pc.getText()))
                    else:
                            raise antlr.NoViableAltException(self.LT(1), self.getFilename())
                        
                elif la1 and la1 in [DPREC]:
                    pass
                    self.match(DPREC)
                    pass
                    dpd = self.LT(1)
                    self.match(UINT)
                    right.append(("%dprec","%dprec "+dpd.getText()))
                elif la1 and la1 in [ACTION]:
                    pass
                    self.match(ACTION)
                else:
                        break
                    
            self.Rules.append( (lhs,right) )
            la1 = self.LA(1)
            if False:
                pass
            elif la1 and la1 in [OR]:
                pass
                self.match(OR)
                self.rhs(lhs)
            elif la1 and la1 in [SEMICOLON]:
                pass
            else:
                    raise antlr.NoViableAltException(self.LT(1), self.getFilename())
                
        
        except antlr.RecognitionException as ex:
            self.reportError(ex)
            self.consume()
            self.consumeUntil(_tokenSet_2)
        
    
    def rulespec(self):    
        
        try:      ## for error handling
            pass
            self.match(HYPHEN)
        
        except antlr.RecognitionException as ex:
            self.reportError(ex)
            self.consume()
            self.consumeUntil(_tokenSet_0)
        
    
    def treespec(self):    
        
        try:      ## for error handling
            la1 = self.LA(1)
            if False:
                pass
            elif la1 and la1 in [CARROT]:
                pass
                self.match(CARROT)
            elif la1 and la1 in [BANG]:
                pass
                self.match(BANG)
            else:
                    raise antlr.NoViableAltException(self.LT(1), self.getFilename())
                
        
        except antlr.RecognitionException as ex:
            self.reportError(ex)
            self.consume()
            self.consumeUntil(_tokenSet_0)
        
    

_tokenNames = [
    "<0>", 
    "EOF", 
    "<2>", 
    "NULL_TREE_LOOKAHEAD", 
    "ID", 
    "COLON", 
    "SEMICOLON", 
    "CHAR", 
    "STRING", 
    "ERROR", 
    "PREC", 
    "DPREC", 
    "UINT", 
    "ACTION", 
    "OR", 
    "HYPHEN", 
    "CARROT", 
    "BANG", 
    "LETTER", 
    "DIGIT", 
    "SL_COMMENT", 
    "ML_COMMENT", 
    "WS"
]
    

### generate bit set
def mk_tokenSet_0(): 
    ### var1
    data = [ 2, 0]
    return data
_tokenSet_0 = antlr.BitSet(mk_tokenSet_0())

### generate bit set
def mk_tokenSet_1(): 
    ### var1
    data = [ 18, 0]
    return data
_tokenSet_1 = antlr.BitSet(mk_tokenSet_1())

### generate bit set
def mk_tokenSet_2(): 
    ### var1
    data = [ 64, 0]
    return data
_tokenSet_2 = antlr.BitSet(mk_tokenSet_2())
    
