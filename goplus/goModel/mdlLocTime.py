from goBases import * #Windows
from sys import path

#from ..goBases import * #LINUX
from goBases.goELT import *

class LocTime(ELT):
    ''' LocTime represent the time in the model 
    '''

    Y = var('year')
    DOY =  var('Day Of Year')
    H = var('hour')
    Now = var('number of days since the beginning of simulation')
    NbDayOfYear = var('number of days in current year')
    
    isSimulBeginning =var('True if it is the first time step', 2)
    isDayBeginning =var('True at the start of the day')
    isYearBeginning =var('True at the start of the year')
    isDayEnd =var('True at the end of day')
    isYearEnd =var('True at the start of year')

    #params
    #○Y_start = param('initial year',  1980)
    leapYear = param('0: if only 365 days/year, 1: if allow leap year')

    def update(self):
        '''update the time states
        '''
        #simulation beginning state modification
        if self.isSimulBeginning: 
            self.isSimulBeginning -= 1
        
        #initialisations
        if self.isSimulBeginning: 
            self.Y = self.Y_start-1
            self.NbDayOfYear = 365 + (self.leapYear and (self.Y % 4) == 0)
            self.Now=0
            self.DOY =self.NbDayOfYear     
            self.H = 23 

        #time states progression
        self.isDayBeginning = self.isYearBeginning =  self.isDayEnd =  self.isYearEnd = False
        
        self.H =  (self.H + 1) % 24
        if self.H == 0:
            self.isDayBeginning = True
            self.Now +=1
            self.DOY = (self.DOY % self.NbDayOfYear) +1
            
            if self.DOY == 1:
                self.isYearBeginning=True
                self.Y += 1
                self.NbDayOfYear = 365 + (self.leapYear and (self.Y % 4) == 0)
        if self.H == 23:
            self.isDayEnd = True
            if self.DOY == self.NbDayOfYear:
                self.isYearEnd=True


