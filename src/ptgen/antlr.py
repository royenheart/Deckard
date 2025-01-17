## This file is part of PyANTLR. See LICENSE.txt for license
## details..........Copyright (C) Wolfgang Haefelinger, 2004.

## get sys module
from io import TextIOWrapper
import sys
import os

version = sys.version.split()[0]
# if version < '2.2.1':
#     False = 0
# if version < '2.3':
#     True = not False

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                     global symbols                             ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

### ANTLR Standard Tokens
SKIP                = -1
INVALID_TYPE        = 0
EOF_TYPE            = 1
EOF                 = 1
NULL_TREE_LOOKAHEAD = 3
MIN_USER_TYPE       = 4

### ANTLR's EOF Symbol
EOF_CHAR            = ''

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                    general functions                           ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

## Version should be automatically derived from configure.in. For now,
## we need to bump it ourselfs. Don't remove the <version> tags.
## <version>
def version():
    r = {
        'major'  : '2',
        'minor'  : '7',
        'micro'  : '5',
        'patch'  : '' ,
        'version': '2.7.5'
        }
    return r
## </version>

def error(fmt,*args):
    if fmt:
        print("error: ", fmt % tuple(args))

def ifelse(cond,_then,_else):
    if cond :
        r = _then
    else:
        r = _else
    return r

def is_string_type(x):
    return  (isinstance(x,str) or isinstance(x,str))

def assert_string_type(x):
    assert is_string_type(x)
    pass

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                     ANTLR Exceptions                           ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class ANTLRException(Exception):

    def __init__(self, *args):
        Exception.__init__(self, *args)


class RecognitionException(ANTLRException):

    def __init__(self, *args):
        ANTLRException.__init__(self, *args)
        self.fileName = None
        self.line = -1
        self.column = -1
        if len(args) >= 2:
            self.fileName = args[1]
        if len(args) >= 3:
            self.line = args[2]
        if len(args) >= 4:
            self.column = args[3]

    def __str__(self):
        buf = ['']
        if self.fileName:
            buf.append(self.fileName + ":")
        if self.line != -1:
            if not self.fileName:
                buf.append("line ")
            buf.append(str(self.line))
            if self.column != -1:
                buf.append(":" + str(self.column))
            buf.append(":")
        buf.append(" ")
        return str('').join(buf)

    __repr__ = __str__


class NoViableAltException(RecognitionException):

    def __init__(self, *args):
        RecognitionException.__init__(self, *args)
        self.token = None
        self.node  = None
        if isinstance(args[0],AST):
            self.node = args[0]
        elif isinstance(args[0],Token):
            self.token = args[0]
        else:
            raise TypeError("NoViableAltException requires Token or AST argument")

    def __str__(self):
        if self.token:
            line = self.token.getLine()
            col  = self.token.getColumn()
            text = self.token.getText()
            return "unexpected symbol at line %s (column %s): \"%s\"" % (line,col,text)
        if self.node == ASTNULL:
            return "unexpected end of subtree"
        assert self.node
        ### hackish, we assume that an AST contains method getText
        return "unexpected node: %s" % (self.node.getText())

    __repr__ = __str__


class NoViableAltForCharException(RecognitionException):

    def __init__(self, *args):
        self.foundChar = None
        if len(args) == 2:
            self.foundChar = args[0]
            scanner = args[1]
            RecognitionException.__init__(self, "NoViableAlt",
                                          scanner.getFilename(),
                                          scanner.getLine(),
                                          scanner.getColumn())
        elif len(args) == 4:
            self.foundChar = args[0]
            fileName = args[1]
            line = args[2]
            column = args[3]
            RecognitionException.__init__(self, "NoViableAlt",
                                          fileName, line, column)
        else:
            RecognitionException.__init__(self, "NoViableAlt",
                                          '', -1, -1)

    def __str__(self):
        mesg = "unexpected char: "
        if self.foundChar >= ' ' and self.foundChar <= '~':
            mesg += "'" + self.foundChar + "'"
        elif self.foundChar:
            mesg += "0x" + hex(ord(self.foundChar)).upper()[2:]
        else:
            mesg += "<None>"
        return mesg

    __repr__ = __str__


class SemanticException(RecognitionException):

    def __init__(self, *args):
        RecognitionException.__init__(self, *args)


class MismatchedCharException(RecognitionException):

    NONE = 0
    CHAR = 1
    NOT_CHAR = 2
    RANGE = 3
    NOT_RANGE = 4
    SET = 5
    NOT_SET = 6

    def __init__(self, *args):
        self.args = args
        if len(args) == 5:
            # Expected range / not range
            if args[3]:
                self.mismatchType = MismatchedCharException.NOT_RANGE
            else:
                self.mismatchType = MismatchedCharException.RANGE
            self.foundChar = args[0]
            self.expecting = args[1]
            self.upper = args[2]
            self.scanner = args[4]
            RecognitionException.__init__(self, "Mismatched char range",
                                          self.scanner.getFilename(),
                                          self.scanner.getLine(),
                                          self.scanner.getColumn())
        elif len(args) == 4 and is_string_type(args[1]):
            # Expected char / not char
            if args[2]:
                self.mismatchType = MismatchedCharException.NOT_CHAR
            else:
                self.mismatchType = MismatchedCharException.CHAR
            self.foundChar = args[0]
            self.expecting = args[1]
            self.scanner = args[3]
            RecognitionException.__init__(self, "Mismatched char",
                                          self.scanner.getFilename(),
                                          self.scanner.getLine(),
                                          self.scanner.getColumn())
        elif len(args) == 4 and isinstance(args[1], BitSet):
            # Expected BitSet / not BitSet
            if args[2]:
                self.mismatchType = MismatchedCharException.NOT_SET
            else:
                self.mismatchType = MismatchedCharException.SET
            self.foundChar = args[0]
            self.set = args[1]
            self.scanner = args[3]
            RecognitionException.__init__(self, "Mismatched char set",
                                          self.scanner.getFilename(),
                                          self.scanner.getLine(),
                                          self.scanner.getColumn())
        else:
            self.mismatchType = MismatchedCharException.NONE
            RecognitionException.__init__(self, "Mismatched char")

    ## Append a char to the msg buffer.  If special,
    #  then show escaped version
    #
    def appendCharName(self, sb, c):
        if not c or c == 65535:
            # 65535 = (char) -1 = EOF
            sb.append("'<EOF>'")
        elif c == '\n':
            sb.append("'\\n'")
        elif c == '\r':
            sb.append("'\\r'");
        elif c == '\t':
            sb.append("'\\t'")
        else:
            sb.append('\'' + c + '\'')

    ##
    # Returns an error message with line number/column information
    #
    def __str__(self):
        sb = ['']
        sb.append(RecognitionException.__str__(self))

        if self.mismatchType == MismatchedCharException.CHAR:
            sb.append("expecting ")
            self.appendCharName(sb, self.expecting)
            sb.append(", found ")
            self.appendCharName(sb, self.foundChar)
        elif self.mismatchType == MismatchedCharException.NOT_CHAR:
            sb.append("expecting anything but '")
            self.appendCharName(sb, self.expecting)
            sb.append("'; got it anyway")
        elif self.mismatchType in [MismatchedCharException.RANGE, MismatchedCharException.NOT_RANGE]:
            sb.append("expecting char ")
            if self.mismatchType == MismatchedCharException.NOT_RANGE:
                sb.append("NOT ")
            sb.append("in range: ")
            appendCharName(sb, self.expecting)
            sb.append("..")
            appendCharName(sb, self.upper)
            sb.append(", found ")
            appendCharName(sb, self.foundChar)
        elif self.mismatchType in [MismatchedCharException.SET, MismatchedCharException.NOT_SET]:
            sb.append("expecting ")
            if self.mismatchType == MismatchedCharException.NOT_SET:
                sb.append("NOT ")
            sb.append("one of (")
            for i in range(len(self.set)):
                self.appendCharName(sb, self.set[i])
            sb.append("), found ")
            self.appendCharName(sb, self.foundChar)

        return str().join(sb).strip()

    __repr__ = __str__


class MismatchedTokenException(RecognitionException):

    NONE = 0
    TOKEN = 1
    NOT_TOKEN = 2
    RANGE = 3
    NOT_RANGE = 4
    SET = 5
    NOT_SET = 6

    def __init__(self, *args):
        self.args =  args
        self.tokenNames = []
        self.token = None
        self.tokenText = ''
        self.node =  None
        if len(args) == 6:
            # Expected range / not range
            if args[3]:
                self.mismatchType = MismatchedTokenException.NOT_RANGE
            else:
                self.mismatchType = MismatchedTokenException.RANGE
            self.tokenNames = args[0]
            self.expecting = args[2]
            self.upper = args[3]
            self.fileName = args[5]

        elif len(args) == 4 and isinstance(args[2], int):
            # Expected token / not token
            if args[3]:
                self.mismatchType = MismatchedTokenException.NOT_TOKEN
            else:
                self.mismatchType = MismatchedTokenException.TOKEN
            self.tokenNames = args[0]
            self.expecting = args[2]

        elif len(args) == 4 and isinstance(args[2], BitSet):
            # Expected BitSet / not BitSet
            if args[3]:
                self.mismatchType = MismatchedTokenException.NOT_SET
            else:
                self.mismatchType = MismatchedTokenException.SET
            self.tokenNames = args[0]
            self.set = args[2]

        else:
            self.mismatchType = MismatchedTokenException.NONE
            RecognitionException.__init__(self, "Mismatched Token: expecting any AST node", "<AST>", -1, -1)

        if len(args) >= 2:
            if isinstance(args[1],Token):
                self.token = args[1]
                self.tokenText = self.token.getText()
                RecognitionException.__init__(self, "Mismatched Token",
                                              self.fileName,
                                              self.token.getLine(),
                                              self.token.getColumn())
            elif isinstance(args[1],AST):
                self.node = args[1]
                self.tokenText = str(self.node)
                RecognitionException.__init__(self, "Mismatched Token",
                                              "<AST>",
                                              self.node.getLine(),
                                              self.node.getColumn())
            else:
                self.tokenText = "<empty tree>"
                RecognitionException.__init__(self, "Mismatched Token",
                                              "<AST>", -1, -1)

    def appendTokenName(self, sb, tokenType):
        if tokenType == INVALID_TYPE:
            sb.append("<Set of tokens>")
        elif tokenType < 0 or tokenType >= len(self.tokenNames):
            sb.append("<" + str(tokenType) + ">")
        else:
            sb.append(self.tokenNames[tokenType])

    ##
    # Returns an error message with line number/column information
    #
    def __str__(self):
        sb = ['']
        sb.append(RecognitionException.__str__(self))

        if self.mismatchType == MismatchedTokenException.TOKEN:
            sb.append("expecting ")
            self.appendTokenName(sb, self.expecting)
            sb.append(", found " + self.tokenText)
        elif self.mismatchType == MismatchedTokenException.NOT_TOKEN:
            sb.append("expecting anything but '")
            self.appendTokenName(sb, self.expecting)
            sb.append("'; got it anyway")
        elif self.mismatchType in [MismatchedTokenException.RANGE, MismatchedTokenException.NOT_RANGE]:
            sb.append("expecting token ")
            if self.mismatchType == MismatchedTokenException.NOT_RANGE:
                sb.append("NOT ")
            sb.append("in range: ")
            appendTokenName(sb, self.expecting)
            sb.append("..")
            appendTokenName(sb, self.upper)
            sb.append(", found " + self.tokenText)
        elif self.mismatchType in [MismatchedTokenException.SET, MismatchedTokenException.NOT_SET]:
            sb.append("expecting ")
            if self.mismatchType == MismatchedTokenException.NOT_SET:
                sb.append("NOT ")
            sb.append("one of (")
            for i in range(len(self.set)):
                self.appendTokenName(sb, self.set[i])
            sb.append("), found " + self.tokenText)

        return str().join(sb).strip()

    __repr__ = __str__


class TokenStreamException(ANTLRException):

    def __init__(self, *args):
        ANTLRException.__init__(self, *args)


# Wraps an Exception in a TokenStreamException
class TokenStreamIOException(TokenStreamException):

    def __init__(self, *args):
        if args and isinstance(args[0], Exception):
            io = args[0]
            TokenStreamException.__init__(self, str(io))
            self.io = io
        else:
            TokenStreamException.__init__(self, *args)
            self.io = self


# Wraps a RecognitionException in a TokenStreamException
class TokenStreamRecognitionException(TokenStreamException):

    def __init__(self, *args):
        if args and isinstance(args[0], RecognitionException):
            recog = args[0]
            TokenStreamException.__init__(self, str(recog))
            self.recog = recog
        else:
            raise TypeError("TokenStreamRecognitionException requires RecognitionException argument")

    def __str__(self):
        return str(self.recog)

    __repr__ = __str__


class TokenStreamRetryException(TokenStreamException):

    def __init__(self, *args):
        TokenStreamException.__init__(self, *args)


class CharStreamException(ANTLRException):

    def __init__(self, *args):
        ANTLRException.__init__(self, *args)


# Wraps an Exception in a CharStreamException
class CharStreamIOException(CharStreamException):

    def __init__(self, *args):
        if args and isinstance(args[0], Exception):
            io = args[0]
            CharStreamException.__init__(self, str(io))
            self.io = io
        else:
            CharStreamException.__init__(self, *args)
            self.io = self


class TryAgain(Exception):
    pass


###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       Token                                    ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class Token(object):
    SKIP                = -1
    INVALID_TYPE        = 0
    EOF_TYPE            = 1
    EOF                 = 1
    NULL_TREE_LOOKAHEAD = 3
    MIN_USER_TYPE       = 4

    def __init__(self,**argv):
        try:
            self.type = argv['type']
        except:
            self.type = INVALID_TYPE
        try:
            self.text = argv['text']
        except:
            self.text = "<no text>"

    def isEOF(self):
        return (self.type == EOF_TYPE)

    def getColumn(self):
        return 0

    def getLine(self):
        return 0

    def getFilename(self):
        return None

    def setFilename(self,name):
        return self

    def getText(self):
        return "<no text>"

    def setText(self,text):
        if is_string_type(text):
            pass
        else:
            raise TypeError("Token.setText requires string argument")
        return self

    def setColumn(self,column):
        return self

    def setLine(self,line):
        return self

    def getType(self):
        return self.type

    def setType(self,type):
        if isinstance(type,int):
            self.type = type
        else:
            raise TypeError("Token.setType requires integer argument")
        return self

    def toString(self):
        ## not optimal
        type_ = self.type
        if type_ == 3:
            tval = 'NULL_TREE_LOOKAHEAD'
        elif type_ == 1:
            tval = 'EOF_TYPE'
        elif type_ == 0:
            tval = 'INVALID_TYPE'
        elif type_ == -1:
            tval = 'SKIP'
        else:
            tval = type_
        return '["%s",<%s>]' % (self.getText(),tval)

    __str__ = toString
    __repr__ = toString

### static attribute ..
Token.badToken = Token( type=INVALID_TYPE, text="<no text>")

if __name__ == "__main__":
    print("testing ..")
    T = Token.badToken
    print(T)

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       CommonToken                              ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class CommonToken(Token):

    def __init__(self,**argv):
        Token.__init__(self,**argv)
        self.line = 0
        self.col  = 0
        try:
            self.line = argv['line']
        except:
            pass
        try:
            self.col = argv['col']
        except:
            pass

    def getLine(self):
        return self.line

    def getText(self):
        return self.text

    def getColumn(self):
        return self.col

    def setLine(self,line):
        self.line = line
        return self

    def setText(self,text):
        self.text = text
        return self

    def setColumn(self,col):
        self.col = col
        return self

    def toString(self):
        ## not optimal
        type_ = self.type
        if type_ == 3:
            tval = 'NULL_TREE_LOOKAHEAD'
        elif type_ == 1:
            tval = 'EOF_TYPE'
        elif type_ == 0:
            tval = 'INVALID_TYPE'
        elif type_ == -1:
            tval = 'SKIP'
        else:
            tval = type_
        d = {
           'text' : self.text,
           'type' : tval,
           'line' : self.line,
           'colm' : self.col
           }

        fmt = '["%(text)s",<%(type)s>,line=%(line)s,col=%(colm)s]'
        return fmt % d

    __str__ = toString
    __repr__ = toString


if __name__ == '__main__' :
    T = CommonToken()
    print(T)
    T = CommonToken(col=15,line=1,text="some text", type=5)
    print(T)
    T = CommonToken()
    T.setLine(1).setColumn(15).setText("some text").setType(5)
    print(T)
    print(T.getLine())
    print(T.getColumn())
    print(T.getText())
    print(T.getType())

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                    CommonHiddenStreamToken                     ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class CommonHiddenStreamToken(CommonToken):
    def __init__(self,*args):
        CommonToken.__init__(self,*args)
        self.hiddenBefore = None
        self.hiddenAfter  = None

    def getHiddenAfter(self):
        return self.hiddenAfter

    def getHiddenBefore(self):
        return self.hiddenBefore

    def setHiddenAfter(self,t):
        self.hiddenAfter = t

    def setHiddenBefore(self, t):
        self.hiddenBefore = t

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       Queue                                    ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

## Shall be a circular buffer on tokens ..
class Queue(object):

    def __init__(self):
        self.buffer = [] # empty list

    def append(self,item):
        self.buffer.append(item)

    def elementAt(self,index):
        return self.buffer[index]

    def reset(self):
        self.buffer = []

    def removeFirst(self):
        self.buffer.pop(0)

    def length(self):
        return len(self.buffer)

    def __str__(self):
        return str(self.buffer)

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       InputBuffer                              ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class InputBuffer(object):
    def __init__(self):
        self.nMarkers = 0
        self.markerOffset = 0
        self.numToConsume = 0
        self.queue = Queue()

    def __str__(self):
        return "(%s,%s,%s,%s)" % (
           self.nMarkers,
           self.markerOffset,
           self.numToConsume,
           self.queue)

    def __repr__(self):
        return str(self)

    def commit(self):
        self.nMarkers -= 1

    def consume(self) :
        self.numToConsume += 1

    ## probably better to return a list of items
    ## because of unicode. Or return a unicode
    ## string ..
    def getLAChars(self) :
        i = self.markerOffset
        n = self.queue.length()
        s = ''
        while i<n:
            s += self.queue.elementAt(i)
        return s

    ## probably better to return a list of items
    ## because of unicode chars
    def getMarkedChars(self) :
        s = ''
        i = 0
        n = self.markerOffset
        while i<n:
            s += self.queue.elementAt(i)
        return s

    def isMarked(self) :
        return self.nMarkers != 0

    def fill(self,k):
        ### abstract method
        raise NotImplementedError()

    def LA(self,k) :
        self.fill(k)
        return self.queue.elementAt(self.markerOffset + k - 1)

    def mark(self) :
        self.syncConsume()
        self.nMarkers += 1
        return self.markerOffset

    def rewind(self,mark) :
        self.syncConsume()
        self.markerOffset = mark
        self.nMarkers -= 1

    def reset(self) :
        self.nMarkers = 0
        self.markerOffset = 0
        self.numToConsume = 0
        self.queue.reset()

    def syncConsume(self) :
        while self.numToConsume > 0:
            if self.nMarkers > 0:
                # guess mode -- leave leading characters and bump offset.
                self.markerOffset += 1
            else:
                # normal mode -- remove first character
                self.queue.removeFirst()
            self.numToConsume -= 1

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       CharBuffer                               ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class CharBuffer(InputBuffer):
    def __init__(self,reader):
        ##assert isinstance(reader,file)
        super(CharBuffer,self).__init__()
        ## a reader is supposed to be anything that has
        ## a method 'read(int)'.
        self.input = reader

    def __str__(self):
        base = super(CharBuffer,self).__str__()
        return "CharBuffer{%s,%s" % (base,str(input))

    def fill(self,amount):
        try:
            self.syncConsume()
            while self.queue.length() < (amount + self.markerOffset) :
                ## retrieve just one char - what happend at end
                ## of input?
                c = self.input.read(1)
                ### python's behaviour is to return the empty string  on
                ### EOF, ie. no exception whatsoever is thrown. An empty
                ### python  string  has  the  nice feature that it is of
                ### type 'str' and  "not ''" would return true. Contrary,
                ### one can't  do  this: '' in 'abc'. This should return
                ### false,  but all we  get  is  then  a TypeError as an
                ### empty string is not a character.

                ### Let's assure then that we have either seen a
                ### character or an empty string (EOF).
                assert len(c) == 0 or len(c) == 1

                ### And it shall be of type string (ASCII or UNICODE).
                assert is_string_type(c)

                ### Just append EOF char to buffer. Note that buffer may
                ### contain then just more than one EOF char ..

                ### use unicode chars instead of ASCII ..
                self.queue.append(c)
        except Exception as e:
            raise CharStreamIOException(e)
        ##except: # (mk) Cannot happen ...
            ##error ("unexpected exception caught ..")
            ##assert 0

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       LexerSharedInputState                    ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class LexerSharedInputState(object):
    def __init__(self,ibuf):
        assert isinstance(ibuf,InputBuffer)
        self.input = ibuf
        self.column = 1
        self.line = 1
        self.tokenStartColumn = 1
        self.tokenStartLine = 1
        self.guessing = 0
        self.filename = None

    def reset(self):
        self.column = 1
        self.line = 1
        self.tokenStartColumn = 1
        self.tokenStartLine = 1
        self.guessing = 0
        self.filename = None
        self.input.reset()

    def LA(self,k):
        return self.input.LA(k)

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                    TokenStream                                 ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class TokenStream(object):
    def nextToken(self):
        pass

    def __iter__(self):
        return TokenStreamIterator(self)

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                    TokenStreamIterator                                 ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class TokenStreamIterator(object):
    def __init__(self,inst):
        if isinstance(inst,TokenStream):
            self.inst = inst
            return
        raise TypeError("TokenStreamIterator requires TokenStream object")

    def __next__(self):
        assert self.inst
        item = self.inst.nextToken()
        if not item or item.isEOF():
            raise StopIteration()
        return item

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                    TokenStreamSelector                        ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class TokenStreamSelector(TokenStream):

    def __init__(self):
        self._input = None
        self._stmap = {}
        self._stack = []

    def addInputStream(self,stream,key):
        self._stmap[key] = stream

    def getCurrentStream(self):
        return self._input

    def getStream(self,sname):
        try:
            stream = self._stmap[sname]
        except:
            raise ValueError("TokenStream " + sname + " not found");
        return stream;

    def nextToken(self):
        while 1:
            try:
                return self._input.nextToken()
            except TokenStreamRetryException as r:
                ### just retry "forever"
                pass

    def pop(self):
        stream = self._stack.pop();
        self.select(stream);
        return stream;

    def push(self,arg):
        self._stack.append(self._input);
        self.select(arg)

    def retry(self):
        raise TokenStreamRetryException()

    def select(self,arg):
        if isinstance(arg,TokenStream):
            self._input = arg
            return
        if is_string_type(arg):
            self._input = self.getStream(arg)
            return
        raise TypeError("TokenStreamSelector.select requires " +
                        "TokenStream or string argument")

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                      TokenStreamBasicFilter                    ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class TokenStreamBasicFilter(TokenStream):

    def __init__(self,input):

        self.input = input;
        self.discardMask = BitSet()

    def discard(self,arg):
        if isinstance(arg,int):
            self.discardMask.add(arg)
            return
        if isinstance(arg,BitSet):
            self.discardMark = arg
            return
        raise TypeError("TokenStreamBasicFilter.discard requires" +
                        "integer or BitSet argument")

    def nextToken(self):
        tok = self.input.nextToken()
        while tok and self.discardMask.member(tok.getType()):
            tok = self.input.nextToken()
        return tok

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                      TokenStreamHiddenTokenFilter              ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class TokenStreamHiddenTokenFilter(TokenStreamBasicFilter):

    def __init__(self,input):
        TokenStreamBasicFilter.__init__(self,input)
        self.hideMask = BitSet()
        self.nextMonitoredToken = None
        self.lastHiddenToken = None
        self.firstHidden = None

    def consume(self):
        self.nextMonitoredToken = self.input.nextToken()

    def consumeFirst(self):
        self.consume()

        p = None;
        while self.hideMask.member(self.LA(1).getType()) or \
              self.discardMask.member(self.LA(1).getType()):
            if self.hideMask.member(self.LA(1).getType()):
                if not p:
                    p = self.LA(1)
                else:
                    p.setHiddenAfter(self.LA(1))
                    self.LA(1).setHiddenBefore(p)
                    p = self.LA(1)
                self.lastHiddenToken = p
                if not self.firstHidden:
                    self.firstHidden = p
            self.consume()

    def getDiscardMask(self):
        return self.discardMask

    def getHiddenAfter(self,t):
        return t.getHiddenAfter()

    def getHiddenBefore(self,t):
        return t.getHiddenBefore()

    def getHideMask(self):
        return self.hideMask

    def getInitialHiddenToken(self):
        return self.firstHidden

    def hide(self,m):
        if isinstance(m,int):
            self.hideMask.add(m)
            return
        if isinstance(m.BitMask):
            self.hideMask = m
            return

    def LA(self,i):
        return self.nextMonitoredToken

    def nextToken(self):
        if not self.LA(1):
            self.consumeFirst()

        monitored = self.LA(1)

        monitored.setHiddenBefore(self.lastHiddenToken)
        self.lastHiddenToken = None

        self.consume()
        p = monitored

        while self.hideMask.member(self.LA(1).getType()) or \
              self.discardMask.member(self.LA(1).getType()):
            if self.hideMask.member(self.LA(1).getType()):
                p.setHiddenAfter(self.LA(1))
                if p != monitored:
                    self.LA(1).setHiddenBefore(p)
                p = self.lastHiddenToken = self.LA(1)
            self.consume()
        return monitored

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       StringBuffer                             ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class StringBuffer:
    def __init__(self,string=None):
        if string:
            self.text = list(string)
        else:
            self.text = []

    def setLength(self,sz):
        if not sz :
            self.text = []
            return
        assert sz>0
        if sz >= self.length():
            return
        ### just reset to empty buffer
        self.text = self.text[0:sz]

    def length(self):
        return len(self.text)

    def append(self,c):
        self.text.append(c)

    ### return buffer as string. Arg 'a' is  used  as index
    ## into the buffer and 2nd argument shall be the length.
    ## If 2nd args is absent, we return chars till end of
    ## buffer starting with 'a'.
    def getString(self,a=None,length=None):
        if not a :
            a = 0
        assert a>=0
        if a>= len(self.text) :
            return ""

        if not length:
            ## no second argument
            L = self.text[a:]
        else:
            assert (a+length) <= len(self.text)
            b = a + length
            L = self.text[a:b]
        s = ""
        for x in L : s += x
        return s

    toString = getString ## alias

    def __str__(self):
        return str(self.text)

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       Reader                                   ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

## When reading Japanese chars, it happens that a stream returns a
## 'char' of length 2. This looks like  a  bug  in the appropriate
## codecs - but I'm  rather  unsure about this. Anyway, if this is
## the case, I'm going to  split  this string into a list of chars
## and put them  on  hold, ie. on a  buffer. Next time when called
## we read from buffer until buffer is empty.
## wh: nov, 25th -> problem does not appear in Python 2.4.0.c1.

class Reader(object):
    def __init__(self,stream):
        self.cin = stream
        self.buf = []

    def read(self,num):
        assert num==1

        if len(self.buf):
            return self.buf.pop()

        ## Read a char - this may return a string.
        ## Is this a bug in codecs/Python?
        c = self.cin.read(1)

        if not c or len(c)==1:
            return c

        L = list(c)
        L.reverse()
        for x in L:
            self.buf.append(x)

        ## read one char ..
        return self.read(1)

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       CharScanner                              ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class CharScanner(TokenStream):
    ## class members
    NO_CHAR = 0
    EOF_CHAR = ''  ### EOF shall be the empty string.

    def __init__(self, *argv, **kwargs):
        super(CharScanner, self).__init__()
        self.saveConsumedInput = True
        self.tokenClass = None
        self.caseSensitive = True
        self.caseSensitiveLiterals = True
        self.literals = None
        self.tabsize = 8
        self._returnToken = None
        self.commitToPath = False
        self.traceDepth = 0
        self.text = StringBuffer()
        self.hashString = hash(self)
        self.setTokenObjectClass(CommonToken)
        self.setInput(*argv)

    def __iter__(self):
        return CharScannerIterator(self)

    def setInput(self,*argv):
        ## case 1:
        ## if there's no arg we default to read from
        ## standard input
        if not argv:
            import sys
            self.setInput(sys.stdin)
            return

        ## get 1st argument
        arg1 = argv[0]

        ## case 2:
        ## if arg1 is a string,  we assume it's a file name
        ## and  open  a  stream  using 2nd argument as open
        ## mode. If there's no 2nd argument we fall back to
        ## mode '+rb'.
        if is_string_type(arg1):
            f = open(arg1,"rb")
            self.setInput(f)
            self.setFilename(arg1)
            return

        ## case 3:
        ## if arg1 is a file we wrap it by a char buffer (
        ## some additional checks?? No, can't do this in
        ## general).
        if isinstance(arg1, TextIOWrapper):
            self.setInput(CharBuffer(arg1))
            return

        ## case 4:
        ## if arg1 is of type SharedLexerInputState we use
        ## argument as is.
        if isinstance(arg1,LexerSharedInputState):
            self.inputState = arg1
            return

        ## case 5:
        ## check whether argument type is of type input
        ## buffer. If so create a SharedLexerInputState and
        ## go ahead.
        if isinstance(arg1,InputBuffer):
            self.setInput(LexerSharedInputState(arg1))
            return

        ## case 6:
        ## check whether argument type has a method read(int)
        ## If so create CharBuffer ...
        try:
            if arg1.read:
                rd = Reader(arg1)
                cb = CharBuffer(rd)
                ss = LexerSharedInputState(cb)
                self.inputState = ss
            return
        except:
            pass

        ## case 7:
        ## raise wrong argument exception
        raise TypeError(argv)

    def setTabSize(self,size) :
        self.tabsize = size

    def getTabSize(self) :
        return self.tabsize

    def setCaseSensitive(self,t) :
        self.caseSensitive = t

    def setCommitToPath(self,commit) :
        self.commitToPath = commit

    def setFilename(self,f) :
        self.inputState.filename = f

    def setLine(self,line) :
        self.inputState.line = line

    def setText(self,s) :
        self.resetText()
        self.text.append(s)

    def getCaseSensitive(self) :
        return self.caseSensitive

    def getCaseSensitiveLiterals(self) :
        return self.caseSensitiveLiterals

    def getColumn(self) :
        return self.inputState.column

    def setColumn(self,c) :
        self.inputState.column = c

    def getCommitToPath(self) :
        return self.commitToPath

    def getFilename(self) :
        return self.inputState.filename

    def getInputBuffer(self) :
        return self.inputState.input

    def getInputState(self) :
        return self.inputState

    def setInputState(self,state) :
        assert isinstance(state,LexerSharedInputState)
        self.inputState = state

    def getLine(self) :
        return self.inputState.line

    def getText(self) :
        return str(self.text)

    def getTokenObject(self) :
        return self._returnToken

    def LA(self,i) :
        c = self.inputState.input.LA(i)
        if not self.caseSensitive:
            ### E0006
            c = c.__class__.lower(c)
        return c

    def makeToken(self,type) :
        try:
            ## dynamically load a class
            assert self.tokenClass
            tok = self.tokenClass()
            tok.setType(type)
            tok.setColumn(self.inputState.tokenStartColumn)
            tok.setLine(self.inputState.tokenStartLine)
            return tok
        except:
            self.panic("unable to create new token")
        return Token.badToken

    def mark(self) :
        return self.inputState.input.mark()

    def _match_bitset(self,b) :
        if b.member(self.LA(1)):
            self.consume()
        else:
            raise MismatchedCharException(self.LA(1), b, False, self)

    def _match_string(self,s) :
        for c in s:
            if self.LA(1) == c:
                self.consume()
            else:
                raise MismatchedCharException(self.LA(1), c, False, self)

    def match(self,item):
        if is_string_type(item):
            return self._match_string(item)
        else:
            return self._match_bitset(item)

    def matchNot(self,c) :
        if self.LA(1) != c:
            self.consume()
        else:
            raise MismatchedCharException(self.LA(1), c, True, self)

    def matchRange(self,c1,c2) :
        if self.LA(1) < c1 or self.LA(1) > c2 :
            raise MismatchedCharException(self.LA(1), c1, c2, False, self)
        else:
            self.consume()

    def newline(self) :
        self.inputState.line += 1
        self.inputState.column = 1

    def tab(self) :
        c = self.getColumn()
        nc = ( ((c-1)/self.tabsize) + 1) * self.tabsize + 1
        self.setColumn(nc)

    def panic(self,s='') :
        print("CharScanner: panic: " + s)
        sys.exit(1)

    def reportError(self,ex) :
        print(ex)

    def reportError(self,s) :
        if not self.getFilename():
            print("error: " + str(s))
        else:
            print(self.getFilename() + ": error: " + str(s))

    def reportWarning(self,s) :
        if not self.getFilename():
            print("warning: " + str(s))
        else:
            print(self.getFilename() + ": warning: " + str(s))

    def resetText(self) :
        self.text.setLength(0)
        self.inputState.tokenStartColumn = self.inputState.column
        self.inputState.tokenStartLine = self.inputState.line

    def rewind(self,pos) :
        self.inputState.input.rewind(pos)

    def setTokenObjectClass(self,cl):
        self.tokenClass = cl

    def testForLiteral(self,token):
        if not token:
            return
        assert isinstance(token,Token)

        _type = token.getType()

        ## special tokens can't be literals
        if _type in [SKIP,INVALID_TYPE,EOF_TYPE,NULL_TREE_LOOKAHEAD] :
            return

        _text = token.getText()
        if not _text:
            return

        assert is_string_type(_text)
        _type = self.testLiteralsTable(_text,_type)
        token.setType(_type)
        return _type

    def testLiteralsTable(self,*args):
        if is_string_type(args[0]):
            s = args[0]
            i = args[1]
        else:
            s = self.text.getString()
            i = args[0]

        ## check whether integer has been given
        if not isinstance(i,int):
            assert isinstance(i,int)

        ## check whether we have a dict
        assert isinstance(self.literals,dict)
        try:
            ## E0010
            if not self.caseSensitiveLiterals:
                s = s.__class__.lower(s)
            i = self.literals[s]
        except:
            pass
        return i

    def toLower(self,c):
        return c.__class__.lower()

    def traceIndent(self):
        print(' ' * self.traceDepth)

    def traceIn(self,rname):
        self.traceDepth += 1
        self.traceIndent()
        print("> lexer %s c== %s" % (rname,self.LA(1)))

    def traceOut(self,rname):
        self.traceIndent()
        print("< lexer %s c== %s" % (rname,self.LA(1)))
        self.traceDepth -= 1

    def uponEOF(self):
        pass

    def append(self,c):
        if self.saveConsumedInput :
            self.text.append(c)

    def commit(self):
        self.inputState.input.commit()

    def consume(self):
        if not self.inputState.guessing:
            c = self.LA(1)
            if self.caseSensitive:
                self.append(c)
            else:
                # use input.LA(), not LA(), to get original case
                # CharScanner.LA() would toLower it.
                c =  self.inputState.input.LA(1)
                self.append(c)

            if c and c in "\t":
                self.tab()
            else:
                self.inputState.column += 1
        self.inputState.input.consume()

    ## Consume chars until one matches the given char
    def consumeUntil_char(self,c):
        while self.LA(1) != EOF_CHAR and self.LA(1) != c:
            self.consume()

    ## Consume chars until one matches the given set
    def consumeUntil_bitset(self,bitset):
        while self.LA(1) != EOF_CHAR and not self.set.member(self.LA(1)):
            self.consume()

    ### If symbol seen is EOF then generate and set token, otherwise
    ### throw exception.
    def default(self,la1):
        if not la1 :
            self.uponEOF()
            self._returnToken = self.makeToken(EOF_TYPE)
        else:
            self.raise_NoViableAlt(la1)

    def filterdefault(self,la1,*args):
        if not la1:
            self.uponEOF()
            self._returnToken = self.makeToken(EOF_TYPE)
            return

        if not args:
            self.consume()
            raise TryAgain()
        else:
            ### apply filter object
            self.commit();
            try:
                func=args[0]
                args=args[1:]
                func(*args)
            except RecognitionException as e:
                ## catastrophic failure
                self.reportError(e);
                self.consume();
            raise TryAgain()

    def raise_NoViableAlt(self,la1=None):
        if not la1: la1 = self.LA(1)
        fname = self.getFilename()
        line  = self.getLine()
        col   = self.getColumn()
        raise NoViableAltForCharException(la1,fname,line,col)

    def set_return_token(self,_create,_token,_ttype,_offset):
        if _create and not _token and (not _ttype == SKIP):
            string = self.text.getString(_offset)
            _token = self.makeToken(_ttype)
            _token.setText(string)
        self._returnToken = _token
        return _token

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                   CharScannerIterator                          ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class CharScannerIterator:

    def __init__(self,inst):
        if isinstance(inst,CharScanner):
            self.inst = inst
            return
        raise TypeError("CharScannerIterator requires CharScanner object")

    def __next__(self):
        assert self.inst
        item = self.inst.nextToken()
        if not item or item.isEOF():
            raise StopIteration()
        return item

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       BitSet                                   ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

### I'm assuming here that a long is 64bits. It appears however, that
### a long is of any size. That means we can use a single long as the
### bitset (!), ie. Python would do almost all the work (TBD).

class BitSet(object):
    BITS     = 64
    NIBBLE   = 4
    LOG_BITS = 6
    MOD_MASK = BITS -1

    def __init__(self,data=None):
        if not data:
            BitSet.__init__(self,[int(0)])
            return
        if isinstance(data,int):
            BitSet.__init__(self,[int(data)])
            return
        if isinstance(data,int):
            BitSet.__init__(self,[data])
            return
        if not isinstance(data,list):
            raise TypeError("BitSet requires integer, long, or " +
                            "list argument")
        for x in data:
            if not isinstance(x,int):
                raise TypeError(self,"List argument item is " +
                                "not a long: %s" % (x))
        self.data = data

    def __str__(self):
        bits = len(self.data) * BitSet.BITS
        s = ""
        for i in range(0,bits):
            if self.at(i):
                s += "1"
            else:
                s += "o"
            if not ((i+1) % 10):
                s += '|%s|' % (i+1)
        return s

    def __repr__(self):
        return str(self)

    def member(self,item):
        if not item:
            return False

        if isinstance(item,int):
            return self.at(item)

        if not is_string_type(item):
            raise TypeError(self,"char or unichar expected: %s" % (item))

        ## char is a (unicode) string with at most lenght 1, ie.
        ## a char.

        if len(item) != 1:
            raise TypeError(self,"char expected: %s" % (item))

        ### handle ASCII/UNICODE char
        num = ord(item)

        ### check whether position num is in bitset
        return self.at(num)

    def wordNumber(self,bit):
        return bit >> BitSet.LOG_BITS

    def bitMask(self,bit):
        pos = bit & BitSet.MOD_MASK  ## bit mod BITS
        return (1 << pos)

    def set(self,bit,on=True):
        # grow bitset as required (use with care!)
        i = self.wordNumber(bit)
        mask = self.bitMask(bit)
        if i>=len(self.data):
            d = i - len(self.data) + 1
            for x in range(0,d):
                self.data.append(0)
            assert len(self.data) == i+1
        if on:
            self.data[i] |=  mask
        else:
            self.data[i] &= (~mask)

    ### make add an alias for set
    add = set

    def off(self,bit,off=True):
        self.set(bit,not off)

    def at(self,bit):
        i = self.wordNumber(bit)
        v = self.data[i]
        m = self.bitMask(bit)
        return v & m


###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                      some further funcs                        ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

def illegalarg_ex(func):
    raise ValueError(
       "%s is only valid if parser is built for debugging" %
       (func.__name__))

def runtime_ex(func):
    raise RuntimeException(
       "%s is only valid if parser is built for debugging" %
       (func.__name__))

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       TokenBuffer                              ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class TokenBuffer(object):
    def __init__(self,stream):
        self.input = stream
        self.nMarkers = 0
        self.markerOffset = 0
        self.numToConsume = 0
        self.queue = Queue()

    def reset(self) :
        self.nMarkers = 0
        self.markerOffset = 0
        self.numToConsume = 0
        self.queue.reset()

    def consume(self) :
        self.numToConsume += 1

    def fill(self, amount):
        self.syncConsume()
        while self.queue.length() < (amount + self.markerOffset):
            self.queue.append(self.input.nextToken())

    def getInput(self):
        return self.input

    def LA(self,k) :
        self.fill(k)
        return self.queue.elementAt(self.markerOffset + k - 1).type

    def LT(self,k) :
        self.fill(k)
        return self.queue.elementAt(self.markerOffset + k - 1)

    def mark(self) :
        self.syncConsume()
        self.nMarkers += 1
        return self.markerOffset

    def rewind(self,mark) :
        self.syncConsume()
        self.markerOffset = mark
        self.nMarkers -= 1

    def syncConsume(self) :
        while self.numToConsume > 0:
            if self.nMarkers > 0:
                # guess mode -- leave leading characters and bump offset.
                self.markerOffset += 1
            else:
                # normal mode -- remove first character
                self.queue.removeFirst()
            self.numToConsume -= 1

    def __str__(self):
        return "(%s,%s,%s,%s,%s)" % (
           self.input,
           self.nMarkers,
           self.markerOffset,
           self.numToConsume,
           self.queue)

    def __repr__(self):
        return str(self)

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       ParserSharedInputState                   ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class ParserSharedInputState(object):

    def __init__(self):
        self.input = None
        self.reset()

    def reset(self):
        self.guessing = 0
        self.filename = None
        if self.input:
            self.input.reset()

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       Parser                                   ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class Parser(object):

    def __init__(self, *args, **kwargs):
        self.tokenNames = None
        self.returnAST  = None
        self.astFactory = None
        self.tokenTypeToASTClassMap = {}
        self.ignoreInvalidDebugCalls = False
        self.traceDepth = 0
        if not args:
            self.inputState = ParserSharedInputState()
            return
        arg0 = args[0]
        assert isinstance(arg0,ParserSharedInputState)
        self.inputState = arg0
        return

    def getTokenTypeToASTClassMap(self):
        return self.tokenTypeToASTClassMap


    def addMessageListener(self, l):
        if not self.ignoreInvalidDebugCalls:
            illegalarg_ex(addMessageListener)

    def addParserListener(self,l) :
        if (not self.ignoreInvalidDebugCalls) :
            illegalarg_ex(addParserListener)

    def addParserMatchListener(self, l) :
        if (not self.ignoreInvalidDebugCalls) :
            illegalarg_ex(addParserMatchListener)

    def addParserTokenListener(self, l) :
        if (not self.ignoreInvalidDebugCalls):
            illegalarg_ex(addParserTokenListener)

    def addSemanticPredicateListener(self, l) :
        if (not self.ignoreInvalidDebugCalls):
            illegalarg_ex(addSemanticPredicateListener)

    def addSyntacticPredicateListener(self, l) :
        if (not self.ignoreInvalidDebugCalls):
            illegalarg_ex(addSyntacticPredicateListener)

    def addTraceListener(self, l) :
        if (not self.ignoreInvalidDebugCalls):
            illegalarg_ex(addTraceListener)

    def consume(self):
        raise NotImplementedError()

    def _consumeUntil_type(self,tokenType):
        while self.LA(1) != EOF_TYPE and self.LA(1) != tokenType:
            self.consume()

    def _consumeUntil_bitset(self, set):
        while self.LA(1) != EOF_TYPE and not set.member(self.LA(1)):
            self.consume()

    def consumeUntil(self,arg):
        if isinstance(arg,int):
            self._consumeUntil_type(arg)
        else:
            self._consumeUntil_bitset(arg)

    def defaultDebuggingSetup(self):
        pass

    def getAST(self) :
        return self.returnAST

    def getASTFactory(self) :
        return self.astFactory

    def getFilename(self) :
        return self.inputState.filename

    def getInputState(self) :
        return self.inputState

    def setInputState(self, state) :
        self.inputState = state

    def getTokenName(self,num) :
        return self.tokenNames[num]

    def getTokenNames(self) :
        return self.tokenNames

    def isDebugMode(self) :
        return self.false

    def LA(self, i):
        raise NotImplementedError()

    def LT(self, i):
        raise NotImplementedError()

    def mark(self):
        return self.inputState.input.mark()

    def _match_int(self,t):
        if (self.LA(1) != t):
            raise MismatchedTokenException(
               self.tokenNames, self.LT(1), t, False, self.getFilename())
        else:
            self.consume()

    def _match_set(self, b):
        if (not b.member(self.LA(1))):
            raise MismatchedTokenException(
               self.tokenNames,self.LT(1), b, False, self.getFilename())
        else:
            self.consume()

    def match(self,set) :
        if isinstance(set,int):
            self._match_int(set)
            return
        if isinstance(set,BitSet):
            self._match_set(set)
            return
        raise TypeError("Parser.match requires integer ot BitSet argument")

    def matchNot(self,t):
        if self.LA(1) == t:
            raise MismatchedTokenException(
               tokenNames, self.LT(1), t, True, self.getFilename())
        else:
            self.consume()

    def removeMessageListener(self, l) :
        if (not self.ignoreInvalidDebugCalls):
            runtime_ex(removeMessageListener)

    def removeParserListener(self, l) :
        if (not self.ignoreInvalidDebugCalls):
            runtime_ex(removeParserListener)

    def removeParserMatchListener(self, l) :
        if (not self.ignoreInvalidDebugCalls):
            runtime_ex(removeParserMatchListener)

    def removeParserTokenListener(self, l) :
        if (not self.ignoreInvalidDebugCalls):
            runtime_ex(removeParserTokenListener)

    def removeSemanticPredicateListener(self, l) :
        if (not self.ignoreInvalidDebugCalls):
            runtime_ex(removeSemanticPredicateListener)

    def removeSyntacticPredicateListener(self, l) :
        if (not self.ignoreInvalidDebugCalls):
            runtime_ex(removeSyntacticPredicateListener)

    def removeTraceListener(self, l) :
        if (not self.ignoreInvalidDebugCalls):
            runtime_ex(removeTraceListener)

    def reportError(self,x) :
        fmt = "syntax error:"
        f = self.getFilename()
        if f:
            fmt = ("%s:" % f) + fmt
        if isinstance(x,Token):
            line = x.getColumn()
            col  = x.getLine()
            text = x.getText()
            fmt  = fmt + 'unexpected symbol at line %s (column %s) : "%s"'
            print(fmt % (line,col,text), file=sys.stderr)
        else:
            print(fmt,str(x), file=sys.stderr)

    def reportWarning(self,s):
        f = self.getFilename()
        if f:
            print("%s:warning: %s" % (f,str(x)))
        else:
            print("warning: %s" % (str(x)))

    def rewind(self, pos) :
        self.inputState.input.rewind(pos)

    def setASTFactory(self, f) :
        self.astFactory = f

    def setASTNodeClass(self, cl) :
        self.astFactory.setASTNodeType(cl)

    def setASTNodeType(self, nodeType) :
        self.setASTNodeClass(nodeType)

    def setDebugMode(self, debugMode) :
        if (not self.ignoreInvalidDebugCalls):
            runtime_ex(setDebugMode)

    def setFilename(self, f) :
        self.inputState.filename = f

    def setIgnoreInvalidDebugCalls(self, value) :
        self.ignoreInvalidDebugCalls = value

    def setTokenBuffer(self, t) :
        self.inputState.input = t

    def traceIndent(self):
        print(" " * self.traceDepth)

    def traceIn(self,rname):
        self.traceDepth += 1
        self.trace("> ", rname)

    def traceOut(self,rname):
        self.trace("< ", rname)
        self.traceDepth -= 1

    ### wh: moved from ASTFactory to Parser
    def addASTChild(self,currentAST, child):
        if not child:
            return
        if not currentAST.root:
            currentAST.root = child
        elif not currentAST.child:
            currentAST.root.setFirstChild(child)
        else:
            currentAST.child.setNextSibling(child)
        currentAST.child = child
        currentAST.advanceChildToEnd()

    ### wh: moved from ASTFactory to Parser
    def makeASTRoot(self,currentAST,root) :
        if root:
            ### Add the current root as a child of new root
            root.addChild(currentAST.root)
            ### The new current child is the last sibling of the old root
            currentAST.child = currentAST.root
            currentAST.advanceChildToEnd()
            ### Set the new root
            currentAST.root = root

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       LLkParser                                ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class LLkParser(Parser):

    def __init__(self, *args, **kwargs):
        try:
            arg1 = args[0]
        except:
            arg1 = 1

        if isinstance(arg1,int):
            super(LLkParser,self).__init__()
            self.k = arg1
            return

        if isinstance(arg1,ParserSharedInputState):
            super(LLkParser,self).__init__(arg1)
            self.set_k(1,*args)
            return

        if isinstance(arg1,TokenBuffer):
            super(LLkParser,self).__init__()
            self.setTokenBuffer(arg1)
            self.set_k(1,*args)
            return

        if isinstance(arg1,TokenStream):
            super(LLkParser,self).__init__()
            tokenBuf = TokenBuffer(arg1)
            self.setTokenBuffer(tokenBuf)
            self.set_k(1,*args)
            return

        ### unknown argument
        raise TypeError("LLkParser requires integer, " +
                        "ParserSharedInputStream or TokenStream argument")

    def consume(self):
        self.inputState.input.consume()

    def LA(self,i):
        return self.inputState.input.LA(i)

    def LT(self,i):
        return self.inputState.input.LT(i)

    def set_k(self,index,*args):
        try:
            self.k = args[index]
        except:
            self.k = 1

    def trace(self,ee,rname):
        print(type(self))
        self.traceIndent()
        guess = ""
        if self.inputState.guessing > 0:
            guess = " [guessing]"
        print((ee + rname + guess))
        for i in range(1,self.k+1):
            if i != 1:
                print(", ")
            if self.LT(i) :
                v = self.LT(i).getText()
            else:
                v = "null"
            print("LA(%s) == %s" % (i,v))
        print("\n")

    def traceIn(self,rname):
        self.traceDepth += 1;
        self.trace("> ", rname);

    def traceOut(self,rname):
        self.trace("< ", rname);
        self.traceDepth -= 1;

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                    TreeParserSharedInputState                  ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class TreeParserSharedInputState(object):
    def __init__(self):
        self.guessing = 0

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       TreeParser                               ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class TreeParser(object):

    def __init__(self, *args, **kwargs):
        self.inputState = TreeParserSharedInputState()
        self._retTree   = None
        self.tokenNames = []
        self.returnAST  = None
        self.astFactory = ASTFactory()
        self.traceDepth = 0

    def getAST(self):
        return self.returnAST

    def getASTFactory(self):
        return self.astFactory

    def getTokenName(self,num) :
        return self.tokenNames[num]

    def getTokenNames(self):
        return self.tokenNames

    def match(self,t,set) :
        assert isinstance(set,int) or isinstance(set,BitSet)
        if not t or t == ASTNULL:
            raise MismatchedTokenException(self.getTokenNames(), t,set, False)

        if isinstance(set,int) and t.getType() != set:
            raise MismatchedTokenException(self.getTokenNames(), t,set, False)

        if isinstance(set,BitSet) and not set.member(t.getType):
            raise MismatchedTokenException(self.getTokenNames(), t,set, False)

    def matchNot(self,t, ttype) :
        if not t or (t == ASTNULL) or (t.getType() == ttype):
            raise MismatchedTokenException(getTokenNames(), t, ttype, True)

    def reportError(self,ex):
        print("error:",ex, file=sys.stderr)

    def  reportWarning(self, s):
        print("warning:",s)

    def setASTFactory(self,f):
        self.astFactory = f

    def setASTNodeType(self,nodeType):
        self.setASTNodeClass(nodeType)

    def setASTNodeClass(self,nodeType):
        self.astFactory.setASTNodeType(nodeType)

    def traceIndent(self):
        print(" " * self.traceDepth)

    def traceIn(self,rname,t):
        self.traceDepth += 1
        self.traceIndent()
        print(("> " + rname + "(" +
              ifelse(t,str(t),"null") + ")" +
              ifelse(self.inputState.guessing>0,"[guessing]","")))

    def traceOut(self,rname,t):
        self.traceIndent()
        print(("< " + rname + "(" +
              ifelse(t,str(t),"null") + ")" +
              ifelse(self.inputState.guessing>0,"[guessing]","")))
        self.traceDepth -= 1

    ### wh: moved from ASTFactory to TreeParser
    def addASTChild(self,currentAST, child):
        if not child:
            return
        if not currentAST.root:
            currentAST.root = child
        elif not currentAST.child:
            currentAST.root.setFirstChild(child)
        else:
            currentAST.child.setNextSibling(child)
        currentAST.child = child
        currentAST.advanceChildToEnd()

    ### wh: moved from ASTFactory to TreeParser
    def makeASTRoot(self,currentAST,root):
        if root:
            ### Add the current root as a child of new root
            root.addChild(currentAST.root)
            ### The new current child is the last sibling of the old root
            currentAST.child = currentAST.root
            currentAST.advanceChildToEnd()
            ### Set the new root
            currentAST.root = root

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###               funcs to work on trees                           ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

def rightmost(ast):
    if ast:
        while(ast.right):
            ast = ast.right
    return ast

def cmptree(s,t,partial):
    while(s and t):
        ### as a quick optimization, check roots first.
        if not s.equals(t):
            return False

        ### if roots match, do full list match test on children.
        if not cmptree(s.getFirstChild(),t.getFirstChild(),partial):
            return False

        s = s.getNextSibling()
        t = t.getNextSibling()

    r = ifelse(partial,not t,not s and not t)
    return r

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                          AST                                   ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class AST(object):
    def __init__(self):
        pass

    def addChild(self, c):
        pass

    def equals(self, t):
        return False

    def equalsList(self, t):
        return False

    def equalsListPartial(self, t):
        return False

    def equalsTree(self, t):
        return False

    def equalsTreePartial(self, t):
        return False

    def findAll(self, tree):
        return None

    def findAllPartial(self, subtree):
        return None

    def getFirstChild(self):
        return self

    def getNextSibling(self):
        return self

    def getText(self):
        return ""

    def getType(self):
        return INVALID_TYPE

    def getLine(self):
        return 0

    def getColumn(self):
        return 0

    def getNumberOfChildren(self):
        return 0

    def initialize(self, t, txt):
        pass

    def initialize(self, t):
        pass

    def setFirstChild(self, c):
        pass

    def setNextSibling(self, n):
        pass

    def setText(self, text):
        pass

    def setType(self, ttype):
        pass

    def toString(self):
        self.getText()

    __str__ = toString

    def toStringList(self):
        return self.getText()

    def toStringTree(self):
        return self.getText()

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       ASTNULLType                              ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

### There is only one instance of this class **/
class ASTNULLType(AST):
    def __init__(self):
        AST.__init__(self)
        pass

    def getText(self):
        return "<ASTNULL>"

    def getType(self):
        return NULL_TREE_LOOKAHEAD


###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       BaseAST                                  ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class BaseAST(AST):

    verboseStringConversion = False
    tokenNames = None

    def __init__(self):
        self.down  = None ## kid
        self.right = None ## sibling

    def addChild(self,node):
        if node:
            t = rightmost(self.down)
            if t:
                t.right = node
            else:
                assert not self.down
                self.down = node

    def getNumberOfChildren(self):
        t = self.down
        n = 0
        while t:
            n += 1
            t = t.right
        return n

    def doWorkForFindAll(self,v,target,partialMatch):
        sibling = self

        while sibling:
            c1 = partialMatch and sibling.equalsTreePartial(target)
            if c1:
                v.append(sibling)
            else:
                c2 = not partialMatch and sibling.equalsTree(target)
                if c2:
                    v.append(sibling)

            ### regardless of match or not, check any children for matches
            if sibling.getFirstChild():
                sibling.getFirstChild().doWorkForFindAll(v,target,partialMatch)

            sibling = sibling.getNextSibling()

    ### Is node t equal to 'self' in terms of token type and text?
    def equals(self,t):
        if not t:
            return False
        return self.getText() == t.getText() and self.getType() == t.getType()

    ### Is t an exact structural and equals() match of this tree.  The
    ### 'self' reference is considered the start of a sibling list.
    ###
    def equalsList(self, t):
        return cmptree(self, t, partial=False)

    ### Is 't' a subtree of this list?
    ### The siblings of the root are NOT ignored.
    ###
    def equalsListPartial(self,t):
        return cmptree(self,t,partial=True)

    ### Is tree rooted at 'self' equal to 't'?  The siblings
    ### of 'self' are ignored.
    ###
    def equalsTree(self, t):
        return self.equals(t) and \
               cmptree(self.getFirstChild(), t.getFirstChild(), partial=False)

    ### Is 't' a subtree of the tree rooted at 'self'?  The siblings
    ### of 'self' are ignored.
    ###
    def equalsTreePartial(self, t):
        if not t:
            return True
        return self.equals(t) and cmptree(
           self.getFirstChild(), t.getFirstChild(), partial=True)

    ### Walk the tree looking for all exact subtree matches.  Return
    ### an ASTEnumerator that lets the caller walk the list
    ### of subtree roots found herein.
    def findAll(self,target):
        roots = []

        ### the empty tree cannot result in an enumeration
        if not target:
            return None
        # find all matches recursively
        self.doWorkForFindAll(roots, target, False)
        return roots

    ### Walk the tree looking for all subtrees.  Return
    ###  an ASTEnumerator that lets the caller walk the list
    ###  of subtree roots found herein.
    def findAllPartial(self,sub):
        roots = []

        ### the empty tree cannot result in an enumeration
        if not sub:
            return None

        self.doWorkForFindAll(roots, sub, True)  ### find all matches recursively
        return roots

    ### Get the first child of this node None if not children
    def getFirstChild(self):
        return self.down

    ### Get the next sibling in line after this one
    def getNextSibling(self):
        return self.right

    ### Get the token text for this node
    def getText(self):
        return ""

    ### Get the token type for this node
    def getType(self):
        return 0

    def getLine(self):
        return 0

    def getColumn(self):
        return 0

    ### Remove all children */
    def removeChildren(self):
        self.down = None

    def setFirstChild(self,c):
        self.down = c

    def setNextSibling(self, n):
        self.right = n

    ### Set the token text for this node
    def setText(self, text):
        pass

    ### Set the token type for this node
    def setType(self, ttype):
        pass

    ### static
    def setVerboseStringConversion(verbose,names):
        verboseStringConversion = verbose
        tokenNames = names
    setVerboseStringConversion = staticmethod(setVerboseStringConversion)

    ### Return an array of strings that maps token ID to it's text.
    ##  @since 2.7.3
    def getTokenNames():
        return tokenNames

    def toString(self):
        return self.getText()

    ### return tree as lisp string - sibling included
    def toStringList(self):
        ts = self.toStringTree()
        sib = self.getNextSibling()
        if sib:
            ts += sib.toStringList()
        return ts

    __str__ = toStringList

    ### return tree as string - siblings ignored
    def toStringTree(self):
        ts = ""
        kid = self.getFirstChild()
        if kid:
            ts += " ("
        ts += " " + self.toString()
        if kid:
            ts += kid.toStringList()
            ts += " )"
        return ts

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       CommonAST                                ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

### Common AST node implementation
class CommonAST(BaseAST):
    def __init__(self,token=None):
        super(CommonAST,self).__init__()
        self.ttype = INVALID_TYPE
        self.text  = "<no text>"
        self.line  = 0
        self.column= 0
        self.initialize(token)
        #assert self.text

    ### Get the token text for this node
    def getText(self):
        return self.text

    ### Get the token type for this node
    def getType(self):
        return self.ttype
    
    ### Get the line for this node
    def getLine(self):
        return self.line

    ### Get the column for this node
    def getColumn(self):
        return self.column
    
    def initialize(self,*args):
        if not args:
            return

        arg0 = args[0]

        if isinstance(arg0,int):
            arg1 = args[1]
            self.setType(arg0)
            self.setText(arg1)
            return

        if isinstance(arg0,AST) or isinstance(arg0,Token):
            self.setText(arg0.getText())
            self.setType(arg0.getType())
            self.line = arg0.getLine()
            self.column = arg0.getColumn()
            return

    ### Set the token text for this node
    def setText(self,text_):
        assert is_string_type(text_)
        self.text = text_

    ### Set the token type for this node
    def setType(self,ttype_):
        assert isinstance(ttype_,int)
        self.ttype = ttype_

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                     CommonASTWithHiddenTokens                  ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class CommonASTWithHiddenTokens(CommonAST):

    def __init__(self,*args):
        CommonAST.__init__(self,*args)
        self.hiddenBefore = None
        self.hiddenAfter  = None

    def getHiddenAfter(self):
        return self.hiddenAfter

    def getHiddenBefore(self):
        return self.hiddenBefore

    def initialize(self,*args):
        CommonAST.initialize(self,*args)
        if args and isinstance(args[0],Token):
            assert isinstance(args[0],CommonHiddenStreamToken)
            self.hideenBefore = args[0].getHiddenBefore()
            self.hiddenAfter  = args[0].getHiddenAfter()

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       ASTPair                                  ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class ASTPair(object):
    def __init__(self):
        self.root = None          ### current root of tree
        self.child = None         ### current child to which siblings are added

    ### Make sure that child is the last sibling */
    def advanceChildToEnd(self):
        if self.child:
            while self.child.getNextSibling():
                self.child = self.child.getNextSibling()

    ### Copy an ASTPair.  Don't call it clone() because we want type-safety */
    def copy(self):
        tmp = ASTPair()
        tmp.root = self.root
        tmp.child = self.child
        return tmp

    def toString(self):
        r = ifelse(not root,"null",self.root.getText())
        c = ifelse(not child,"null",self.child.getText())
        return "[%s,%s]" % (r,c)

    __str__ = toString
    __repr__ = toString


###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       ASTFactory                               ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class ASTFactory(object):
    def __init__(self,table=None):
        self._class = None
        self._classmap = ifelse(table,table,None)

    def create(self,*args):
        if not args:
            return self.create(INVALID_TYPE)

        arg0 = args[0]
        arg1 = None
        arg2 = None

        try:
            arg1 = args[1]
            arg2 = args[2]
        except:
            pass

        # ctor(int)
        if isinstance(arg0,int) and not arg2:
            ### get class for 'self' type
            c = self.getASTNodeType(arg0)
            t = self.create(c)
            if t:
                t.initialize(arg0, ifelse(arg1,arg1,""))
            return t

        # ctor(int,something)
        if isinstance(arg0,int) and arg2:
            t = self.create(arg2)
            if t:
                t.initialize(arg0,arg1)
            return t

        # ctor(AST)
        if isinstance(arg0,AST):
            t = self.create(arg0.getType())
            if t:
                t.initialize(arg0)
            return t

        # ctor(token)
        if isinstance(arg0,Token) and not arg1:
            ttype = arg0.getType()
            assert isinstance(ttype,int)
            t = self.create(ttype)
            if t:
                t.initialize(arg0)
            return t

        # ctor(token,class)
        if isinstance(arg0,Token) and arg1:
            assert isinstance(arg1,type)
            assert issubclass(arg1,AST)
            # this creates instance of 'arg1' using 'arg0' as
            # argument. Wow, that's magic!
            t = arg1(arg0)
            assert t and isinstance(t,AST)
            return t

        # ctor(class)
        if isinstance(arg0,type):
            ### next statement creates instance of type (!)
            t = arg0()
            assert isinstance(t,AST)
            return t


    def setASTNodeClass(self,className=None):
        if not className:
            return
        assert isinstance(className,type)
        assert issubclass(className,AST)
        self._class = className

    ### kind of misnomer - use setASTNodeClass instead.
    setASTNodeType = setASTNodeClass

    def getASTNodeClass(self):
        return self._class



    def getTokenTypeToASTClassMap(self):
        return self._classmap

    def setTokenTypeToASTClassMap(self,amap):
        self._classmap = amap

    def error(self, e):
        import sys
        print(e, file=sys.stderr)

    def setTokenTypeASTNodeType(self, tokenType, className):
        """
        Specify a mapping between a token type and a (AST) class.
        """
        if not self._classmap:
            self._classmap = {}

        if not className:
            try:
                del self._classmap[tokenType]
            except:
                pass
        else:
            ### here we should also perform actions to ensure that
            ### a. class can be loaded
            ### b. class is a subclass of AST
            ###
            assert isinstance(className,type)
            assert issubclass(className,AST)  ## a & b
            ### enter the class
            self._classmap[tokenType] = className

    def getASTNodeType(self,tokenType):
        """
        For a given token type return the AST node type. First we
        lookup a mapping table, second we try _class
        and finally we resolve to "antlr.CommonAST".
        """

        # first
        if self._classmap:
            try:
                c = self._classmap[tokenType]
                if c:
                    return c
            except:
                pass
        # second
        if self._class:
            return self._class

        # default
        return CommonAST

    ### methods that have been moved to file scope - just listed
    ### here to be somewhat consistent with original API
    def dup(self,t):
        return antlr.dup(t,self)

    def dupList(self,t):
        return antlr.dupList(t,self)

    def dupTree(self,t):
        return antlr.dupTree(t,self)

    ### methods moved to other classes
    ### 1. makeASTRoot  -> Parser
    ### 2. addASTChild  -> Parser

    ### non-standard: create alias for longish method name
    maptype = setTokenTypeASTNodeType

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###                       ASTVisitor                               ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

class ASTVisitor(object):
    def __init__(self,*args):
        pass

    def visit(self,ast):
        pass

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###
###               static methods and variables                     ###
###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx###

ASTNULL = ASTNULLType()

### wh: moved from ASTFactory as there's nothing ASTFactory-specific
### in this method.
def make(*nodes):
    if not nodes:
        return None

    for i in range(0,len(nodes)):
        node = nodes[i]
        if node:
            assert isinstance(node,AST)

    root = nodes[0]
    tail = None
    if root:
        root.setFirstChild(None)

    for i in range(1,len(nodes)):
        if not nodes[i]:
            continue
        if not root:
            root = tail = nodes[i]
        elif not tail:
            root.setFirstChild(nodes[i])
            tail = root.getFirstChild()
        else:
            tail.setNextSibling(nodes[i])
            tail = tail.getNextSibling()

        ### Chase tail to last sibling
        while tail.getNextSibling():
            tail = tail.getNextSibling()
    return root

def dup(t,factory):
    if not t:
        return None

    if factory:
        dup_t = factory.create(t.__class__)
    else:
        raise TypeError("dup function requires ASTFactory argument")
    dup_t.initialize(t)
    return dup_t

def dupList(t,factory):
    result = dupTree(t,factory)
    nt = result
    while t:
        ## for each sibling of the root
        t = t.getNextSibling()
        nt.setNextSibling(dupTree(t,factory))
        nt = nt.getNextSibling()
    return result

def dupTree(t,factory):
    result = dup(t,factory)
    if t:
        result.setFirstChild(dupList(t.getFirstChild(),factory))
    return result

###xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
### $Id: antlr.py,v 1.1.1.1 2005/02/02 10:24:36 geronimo Exp $

# Local Variables:    ***
# mode: python        ***
# py-indent-offset: 4 ***
# End:                ***
