"""Base class for serial devices. Includes some convenience methods to open
ports and check for the expected device
"""
# Part of the PsychoPy library
# Copyright (C) 2014 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

import time
from psychopy import logging
from psychopy.hardware import serialdevice

class BlackBoxToolkit(serialdevice.SerialDevice):
    """A base class for serial devices, to be sub-classed by specific devices
    """
    name='BlackBoxToolkit'
    longName ="BlackBoxToolkit 2"
    driverFor = ["BlackBoxToolkit 2"] #list of supported devices (if more than one supports same protocol)

    def __init__(self, port=None, sendBreak=False):
        #if we're trying to send the break signal then presumably the device is sleeping
        if sendBreak:
            checkAwake = False
        else:
            checkAwake = True
        #run initialisation
        super(BlackBoxToolkit, self).__init__(port,
            baudrate=460800, eol="\n",
            parity='N',    # enable parity checking
            autoPause = 0.1,
            checkAwake=checkAwake,
            )
        if sendBreak:
            self.sendBreak()

    def isAwake(self):
        """Checks that the black box returns "BBTK;\n" when probed with "CONN"
        """
        self.sendMessage('CONN')
        reply = self.getResponse(timeout=1.0)
        return reply=='BBTK;\n'
    def showAbout(self):
        """Will show the 'about' screen on the LCD panel for 2 seconds
        """
        time.sleep(self.autoPause)
        self.sendMessage('ABOU')
    def getFirmware(self):
        """Returns the firmware version in YYYYMMDD format
        """
        self.sendMessage("FIRM")
        time.sleep(0.1)
        return self.getResponse(timeout=0.5).replace(";","")
    def setEventThresholds(self, threshList=[]):
        self.sendMessage('SEPV')
        time.sleep(5) #it takes quite a while to switch to this mode
        for threshVal in threshList:
            time.sleep(0.5)
            self.sendMessage(str(threshVal))
    def getEventThresholds(self):
        self.sendMessage("GEPV")
        time.sleep(self.autoPause)
        reply = self.getResponse(timeout=5.0)
        if reply == '':
            return []
        else:
            reply = reply.replace(';\n','') #remove final ';'
            reply = reply.split(',')
        return reply
    def clearMemory(self):
        """
        """
        self.sendMessage('SPIE')
        time.sleep(self.autoPause)
        reply = self.getResponse(timeout=5)
        #should return either FRMT or ESEC to indicate it started
        if reply.startswith('FRMT'):
            logging.info("BBTK.clearMemory(): Starting full format of BBTK memory")
        elif reply.startswith('ESEC'):
            logging.info("BBTK.clearMemory(): Starting quick erase of BBTK memory")
        else:
            logging.error("BBTK.clearMemory(): didn't get a reply from %s" %(str(self.com)))
            return False
        #now wait until we get told 'DONE'
        self.com.setTimeout(20)
        retVal = self.com.readline()
        if retVal.startswith("DONE"):
            logging.info("BBTK.clearMemory(): completed")
            return True
        else:
            logging.error("BBTK.clearMemory(): Stalled waiting for %s" %(str(self.com)))
            return False

    def recordStimulusData(self, duration):
        """Record data for a given duration (seconds) and return a list of
        events that occured in that period.
        """
        self.sendMessage("DSCM")
        time.sleep(self.autoPause)
        self.sendMessage("TIML")
        time.sleep(self.autoPause)
        self.sendMessage("%i" %(int(duration*1000000))) #BBTK expects this in microsecs
        time.sleep(self.autoPause)
        self.sendMessage("RUDS")
    def getEvents(self, timeout=10):
        """Look for a string that matches SDAT;\n.........EDAT;\n
        and process it as events
        """
        foundDataStart=False
        t0=time.time()
        while not foundDataStart and (time.time()-t0)<timeout:
            if self.com.readline().startswith('SDAT'):
                foundDataStart=True
                logging.warning("BBTK.getEvents() found data. Processing...")
                break
        #ceck if we're processing data
        if not foundDataStart:
            logging.warning("BBTK.getEvents() found no data (SDAT was not found on serial port inputs")
            return []
        events=[]
        self.com.setTimeout(2.0)
        while True:
            line = self.com.readline()
            if line.startswith('EDAT'): #end of data stream
                break
            events.append(line)
        return events
    def sendBreak(self):
        self.com.sendBreak()

if __name__=="__main__":

    logging.console.setLevel(logging.DEBUG)

    BBTK = BlackBoxToolkit('/dev/ttyACM0')
    print BBTK.com #info about the com port that's open

    time.sleep(0.2)
    BBTK.showAbout()

    time.sleep(0.1)
    BBTK.setEventThresholds(range(8))
    time.sleep(2)
    print 'thresholds:', BBTK.getEventThresholds()

    BBTK.clearRAM()
    time.sleep(2)
    print 'leftovers:', BBTK.com.read(BBTK.com.inWaiting())
