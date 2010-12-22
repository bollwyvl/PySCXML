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
'''

import logger
from compiler import Compiler
from interpreter import Interpreter

import time



class StateMachine(object):
    '''
    This class provides the entry point for the pyscxml library. 
    '''
    
    
    def __init__(self, xml, do_logging=True, eventProcessor=None):
        '''
        @param xml: the scxml document to parse, expressed as a string.
        @param eventProcessor: optional event processor to allow for a 
            different event processing mechanism
        '''
        logger.do_logging(do_logging)

        self.interpreter = Interpreter(eventProcessor)
        
        self.send = self.interpreter.send
        self.In = self.interpreter.In
        self.doc = Compiler().parseXML(xml, self.interpreter)
        self.datamodel = self.doc.datamodel
        
        
        
        
    def start(self, parentQueue=None, invokeId=None):
        '''Takes the statemachine to its initial state'''
        self.interpreter.interpret(self.doc, parentQueue, invokeId)
        
        
    def isFinished(self):
        '''Returns True if the statemachine has reached it top-level final state'''
        return len(self.interpreter.configuration) == 0
        


if __name__ == "__main__":
    
#    xml = open("../../unittest_xml/colors.xml").read()
#    xml = open("../../resources/tropo.xml").read()
#    xml = open("../../unittest_xml/history.xml").read()
#    xml = open("../../unittest_xml/invoke.xml").read()
    xml = open("../../unittest_xml/invoke_soap.xml").read()
#    xml = open("../../unittest_xml/factorial.xml").read()
#    xml = open("../../unittest_xml/xinclude.xml").read()
    
    
    sm = StateMachine(xml)
    sm.start()
    time.sleep(1)
#    sm.send("http.post")
    

