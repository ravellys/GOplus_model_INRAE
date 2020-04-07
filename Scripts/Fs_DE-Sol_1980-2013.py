# -*- coding: utf-8 -*-
# Declaration of the output variables and related statistics. Possible options: mean, maximum, minimum, final, sum.
# The integration step, hour, day or year,  is specified  at the end of this script


varsToIntegrate = '''
Last: mdl.locTime.Y
Last: mdl.locTime.DOY
Last: mdl.locTime.H
Sum:  mdl.climate.microclim.Rain
Mean: mdl.climate.microclim.u
Mean: mdl.climate.microclim.TaC
Mean: mdl.climate.microclim.d
Mean: mdl.climate.microclim.SWDir
Mean: mdl.climate.microclim.SWDif
Mean: mdl.climate.microclim.LWDw
Last: mdl.forest.treeStand.canopy.LAI
Last: mdl.forest.treeStand.canopy.WAI
Last: mdl.forest.underStorey.canopy.LAI
Last: mdl.forest.underStorey.canopy.WAI
Last: mdl.forest.treeStand.canopy.sunLayer.LAI
Last: mdl.forest.treeStand.canopy.shadeLayer.LAI
Min: mdl.forest.treeStand.canopy.WaterPotential
Min: mdl.forest.soil.waterCycle.RootLayerWaterPotential
Last: mdl.forest.soil.waterCycle.Stock_RootLayer
Last: mdl.forest.soil.waterCycle.w_A
Last: mdl.forest.soil.waterCycle.w_RootLayer
Mean: mdl.forest.LE
Mean: mdl.forest.Rnet
Mean: mdl.forest.H
Sum: mdl.forest.GPP
Sum: mdl.forest.NEE
Sum: mdl.forest.RAuto
Sum: mdl.forest.soil.carbonCycle.Rh
Sum: mdl.forest.treeStand.canopy.Assimilation
Sum: mdl.forest.treeStand.canopy.Respiration
Sum: mdl.forest.treeStand.canopy.Transpiration
Sum: mdl.forest.treeStand.canopy.Evaporation
Sum: mdl.forest.underStorey.canopy.ETR
Sum: mdl.forest.underStorey.canopy.Assimilation
Sum: mdl.forest.underStorey.canopy.Respiration
Sum: mdl.forest.underStorey.canopy.Transpiration
Sum: mdl.forest.underStorey.canopy.Evaporation
Sum: mdl.forest.soil.surface.ETR
Sum: mdl.forest.soil.surface.ETR_DrySurface
Sum: mdl.forest.soil.surface.ETR_WetSurface
Last: mdl.forest.treeStand.Age    
Last: mdl.forest.treeStand.density
Last: mdl.forest.treeStand.IStress   
Last: mdl.forest.treeStand.DBHmean 
Last: mdl.forest.treeStand.HEIGHTmean
Last: mdl.forest.treeStand.BasalArea
Last: mdl.forest.treeStand.PROD_VOL
Last: mdl.forest.treeStand.WDeadTrees
Last: mdl.forest.treeStand.LeafFall
Last: mdl.forest.treeStand.Wr
Last: mdl.forest.treeStand.WStem
Last: mdl.forest.treeStand.WBranch
Last: mdl.forest.treeStand.WFoliage
Last: mdl.forest.treeStand.WTapRoot
Last: mdl.forest.treeStand.WCoarseRoot
Last: mdl.forest.treeStand.WSmallRoot
Last: mdl.forest.treeStand.WFineRoot
Last: mdl.manager.harvest_WStem
Last: mdl.manager.harvest_WBranch
Last: mdl.forest.underStorey.foliage.W
Last: mdl.forest.underStorey.perennial.W
Last: mdl.forest.underStorey.roots.W
Last: mdl.forest.soil.carbonCycle.HUM
Last: mdl.forest.soil.carbonCycle.BIO
Last: mdl.forest.soil.carbonCycle.DPM
Last: mdl.forest.soil.carbonCycle.RPM
Last: mdl.forest.soil.waterCycle.SOC
'''
# =============================================================================

import csv
import math
from sys import path
import os,sys
basePath  = os.path.dirname(os.path.realpath(__file__)) + "/.."
sys.path.append(basePath+"/goplus/")
sys.path.append(basePath+"/goplus/goModel")
from goBases import *
from goModel.mdlModel import Model
from goModel.ManagerElements import mdlMngt_Operations
from goTools.VarsIntegrater import Integrater

#Site Historical Solling management
#The dates of thinning are prescribed according to the ISIMIP scenario ========

INTERVENTIONS = {
        1848 : ('PLANTATION',5000, 2),
        1970 : ('THINNING', 226, 1, True),
        1985 : ('THINNING', 223, 2.0, True),
        1990 : ('THINNING', 217, 2.0, True),
        1996 : ('THINNING', 212, 2.0, True),
        2000 : ('THINNING', 199, 2.0, True),
        2005 : ('THINNING', 164, 2.0, True),
        2009 : ('THINNING', 140, 0.5, True),
        2014 : ('THINNING', 130, 1, True),
        }

class Solling_Manager(mdlMngt_Operations.Manager):

    def update(self):
        
        #Management variables initialisation
        
        self.harvest_WStem      = 0.
        self.harvest_WBranch    = 0.
        self.harvest_WTapRoot   = 0.
        self.harvest_WFoliage   = 0.
        self.NbCutTrees         = 0.
        self.harvest_DBHmean    = 0.
        self.harvest_DBHsd      = 0.
        self.harvest_DBHquadratic = 0.
        self.harvest_HEIGHTmean = 0.
        self.harvest_HEIGHTsd   = 0.
        self.harvest_basalArea  = 0.
       
        del self.Cut_Trees [:]
        
        if self.locTime.isSimulBeginning:
            self.lastThinningYear   = self.locTime.Y - 10
            self.thinnings          = 0        
            self.seedingYear     = self.locTime.Y - self.forest.treeStand.Age - 5
            self.FirstThinning      = False
        
        # Specifications of the Plantation and thinnings operations
        for interventionYear, interventionParameters in INTERVENTIONS.items():
            if  self.locTime.isYearEnd and self.locTime.Y == interventionYear  : 

                    
                if  interventionParameters[0] == 'THINNING' :
                    self.do_Density_Thinning(
                            ThinFactor=interventionParameters[2], 
                            densityObjective = interventionParameters[1], 
                            )
                    self.do_Logging(
                            harvestStem = interventionParameters[3], 
                            harvestBranchWood = False, 
                            harvestTapRoot = False, 
                            harvestStump=False,
                            harvestFoliage = False, 
                            )
                    self.lastThinningYear= self.locTime.Y

                self.forest.treeStand.pcs_SetSizes() #added for updating sand characteristics after management operations


# Object Model ____________________________________________________________________________________________________________________________                
def model(
    startYear,      #initial year
    meteoFile,      #meteo file path : str
    ):
    '''return an instance of the Model parameterized and initialized f.
    '''

   #instanciate the model, set a specific manager and define start year
    mdl= Model()
    mdl.manager = Solling_Manager() # Additional manager scheme can be used:examples at \goModel\ManagerElements
    mdl.locTime.Y_start = startYear
    mdl.climate.meteo_file_path = meteoFile
    mdl.climate.Scenario=0 # index code in mdlClimate mmodule; # Code 0: historical record; code 1: 500ppm, code 2: SRES A2; code 3: RCP2.6; code 4: RCP4.5; code 5: 500ppm; code 6: RCP 6.5; code 7: 500.0ppm; code 8: RCP8.5; code 9: 500ppm
      
   # Set the site specific parameters from csv external file
    paraSiteFilePath =basePath +'/Parameters files/Site/DE-Sol.csv'
    fileParaSite = open(paraSiteFilePath,'r')
    line=next(fileParaSite)
    for line in fileParaSite :
        L = line.split(',') 
        nam = 'mdl' + str(L[0]).lstrip(',').split(" ",1)[0].replace("'","").replace('"','')
        val = float(L[1])
        exec("%s = %s" %(nam,val))
    
    fileParaSite.close()  
    
   # Set the species parameters from csv external file Fsylvatica 
   
    paraSpeFilePath =basePath +'/Parameters files/Species/Fsylvatica.csv' 
    fileParaSpe = open(paraSpeFilePath,'r')
    line=next(fileParaSpe)
    for line in fileParaSpe :
        L = line.split(',') 
        nam = 'mdl' + str(L[0]).lstrip("'").split(',')[0].replace("'","").replace('"','')
        try :
            val = round(float(L[1]),6)
        except ValueError :
            val = str(L[1])
        exec("%s = %s" %(nam,val))

    fileParaSpe.close()

    yearLastIntervention = max([y for y in INTERVENTIONS.keys() if y < startYear])
    _initial_trees_Density = INTERVENTIONS[yearLastIntervention][1]
    _installation =mdl.forest.treeStand.pcs_TreeStandInstallation
    mdl.forest.treeStand.RotationYear = _installation.initialTreesAge
    _installation.initialTreesDimensionsFile =basePath +'/Parameters files/Tree stand/DE-Sol_dbh_1980.csv' 

    return mdl

def simulate(
    mdl,              #model instance
    endYear,          
    fileoutName,      
    outFrequency,     
    log,              #boolean to indicate if simulation information is to be printed
    header= True, 
    fileOutAppend = False, 
    ):
    ''' simulation 
    '''
#Specify the integration
    integrater =Integrater(mdl, varsToIntegrate) #use the default integrable variables
    with open(fileoutName, 'w') as fileOut:
        fileOut.write('%s\n' % integrater.varNames)
#short reference to locTime object to accelerate conditionnal tests
        locTime = mdl.locTime     
#simulation loop
        while (locTime.Y is None) or (locTime.Y <endYear + 1):      
#update the model state
            mdl.update()
#made  the integrations of model variables and output the integrated values each day
            integrater.integrate() 
            if (True,  locTime.isDayEnd,  locTime.isYearEnd)[outFrequency]:
                fileOut.write('%s\n' % integrater.putStr())

#Display selected output values on a python console to monitor the simulation                
            if log and locTime.DOY == 195 and locTime.H == 23:
                print (str(locTime.Y),
                      'Age:',  str(mdl.forest.treeStand.Age), 
                      'nb: ',  str(mdl.forest.treeStand.treesCount),
                      'HEIGHT:',  str(mdl.forest.treeStand.HEIGHTmean), 
                      'DBH:', str(mdl.forest.treeStand.DBHmean),  
                      'LAI:', str(mdl.forest.treeStand.canopy.LAI), 
                      'IStress:', str(mdl.forest.treeStand.IStress), 
                      'LAI-T:', str(mdl.forest.treeStand.canopy.LAI), 
                      'Basal Area:', str(mdl.forest.treeStand.BasalArea),
                      'Thinnings', str(mdl.manager.thinnings)
                      )

if __name__ == '__main__':
    from time import  time

#instantiate the model for a specific experiment. Here a test on the hisotrical Time series of FR-HEs site

    mdl = model( 
        startYear = 1980,
        meteoFile = basePath +'/Met files/Met_DE-Sol_1980-2012.csv',
        )
    endYear = 2013 #included
        
    #Do simulation
    if endYear>1980:
        tstart =time()
        simulate(
            mdl = mdl, 
            endYear = endYear, 
            fileoutName =basePath +'/output files/DE-Sol_1980-2012_d.csv', #  
            outFrequency=1,         #0: hour, 1: day, 2: year
            log =True, 
            header= True, 
            fileOutAppend = False, 
            )
        tend =time()
