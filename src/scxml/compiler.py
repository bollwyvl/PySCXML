'''
This file is part of pyscxml.

    pyscxml is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pyscxml is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with pyscxml.  If not, see <http://www.gnu.org/licenses/>.
    
    @author Johan Roxendal
    @contact: johan@roxendal.com
    
'''


from node import *
import sys, re
import xml.etree.ElementTree as etree
from pprint import pprint


def get_sid(node):
    if node.get('id') != '':
        return node.get('id')
    else:
        #probably not always unique, let's rewrite this at some point
        id = node.parent.get("id") + "_%s_child" % node.tag
        node.set('id',id)
        return id

    
def getLogFunction(toPrint):
    def f():
        print "Log: " + toPrint
    return f
    

def decorateWithParent(tree):
    for node in tree.getiterator():
        for child in node.getchildren():
            child.parent = node
            
# reformulate:
#def setOptionalProperties(node, obj):
#    for key in node.keys():
#        obj[key] = node.get(key)


class Compiler(object):
    def __init__(self):
        self.doc = SCXMLDocument()
        self.sendFunction = None
        self.raiseFunction = None
        self.cancelFunction = None
        self.In = None
        
        
    def registerSend(self, f):
        self.sendFunction = f
        
    def registerRaise(self, f):
        self.raiseFunction = f
        
    def registerCancel(self, f):
        self.cancelFunction = f
        
    def getExecContent(self, node):
        fList = []
        for node in node.getchildren():
            
            if node.tag == "log":
                fList.append(getLogFunction(node.get("expr")))
            elif node.tag == "raise": 
                fList.append(lambda: self.raiseFunction(node.get("event").split(".")))
            elif node.tag == "send":
                eventName = node.get("event").split(".")
                delay = int(node.get("delay")) if node.get("delay") else 0
                
                # ugly scoping hack
                def sendF(name=eventName):
                    self.sendFunction(name, {}, delay)
                    
                fList.append(sendF)
            elif node.tag == "cancel":
                fList.append(lambda: self.cancelFunction(node.get("sendid")))
            else:
                sys.exit("%s is either an invalid child of %s or it's not yet implemented" % (node.tag, node.parent.tag))
    #        elif node.tag == "script:
    #        elif node.tag == "assign:
        
        # return a function that executes all the executable content of the node.
        
        def f():
            for func in fList:
                func()
        return f
    
    def getCondFunction(self, node):
        execStr = "f = lambda dm: %s" % node.get("cond")
        exec(execStr)
        return f


    def parseXML(self, xmlStr):
        tree = etree.fromstring(xmlStr)
        decorateWithParent(tree)
        # TODO: refractor this line
        for n, node in enumerate(x for x in tree.getiterator() if x.tag not in ["log", "script", "raise", "assign", "send", "cancel"]):
            if hasattr(node, "parent"):
                parentState = self.doc.getState(node.parent.get("id"))
                
            
            if node.tag == "scxml":
                node.set("id", "__main__")
                s = State("__main__", None, n)
                if node.get("initial"):
                    s.initial = node.get("initial").split(" ")
                self.doc.rootState = s    
                
            elif node.tag == "state":
                sid = get_sid(node)
                s = State(sid, parentState, n)
                if node.get("initial"):
                    s.initial = node.get("initial").split(" ")
                self.doc.addNode(s)
                parentState.addChild(s)
                
            elif node.tag == "parallel":
                sid = get_sid(node)
                s = Parallel(sid, parentState, n)
                if node.get("initial"):
                    s.initial = node.get("initial").split(" ")
                self.doc.addNode(s)
                parentState.addChild(s)
                
            elif node.tag == "final":
                sid = get_sid(node)
                s = Final(sid, parentState, n)
                self.doc.addNode(s)
                parentState.addFinal(s)
                
            elif node.tag == "history":
                sid = get_sid(node)
                h = History(sid, parentState, node.get("type"), n)
                self.doc.addNode(h)
                parentState.addHistory(h)
                
                
            elif node.tag == "transition":
                
                t = Transition(parentState)
                if node.get("target"):
                    t.target = node.get("target").split(" ")
                if node.get("event"):
                    t.event = map(lambda x: re.sub(r"(.*)\.\*$", r"\1", x).split("."), node.get("event").split(" "))
                if node.get("cond"):
                    t.cond = self.getCondFunction(node)    
                
                
                t.exe = self.getExecContent(node)
                    
                parentState.addTransition(t)

            elif node.tag == "invoke":
                s = Invoke()
                s.id = get_sid(node)
                parentState.addInvoke(s)
                           
            elif node.tag == "onentry":
                s = Onentry()
                s.exe = self.getExecContent(node)
                parentState.addOnentry(s)
            
            elif node.tag == "onexit":
                s = Onexit()
                s.exe = self.getExecContent(node)
                parentState.addOnexit(s)
            elif node.tag == "data":
                self.doc.dm[node.get("id")] = node.get("expr")
    
        return self.doc
    
    

if __name__ == '__main__':
    
    compiler = Compiler()
    compiler.registerSend(lambda: "dummy send")
    doc = compiler.parseXML(open("../../unittest_xml/colors.xml").read())
    print doc.rootState
    