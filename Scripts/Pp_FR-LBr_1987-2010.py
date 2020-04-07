# -*- coding: utf-8 -*-
# Declaration of the output variables and related statistics. Possible ootions: mean, maximum, minimum, final (last), sum.
# The integration step, hour, day or year,  is specified at the end of this script.
# Alternatively, output variables and associated statistics can be declared with the instruction:: from "filename" (ex: BRAY_varsToIntegrate) import varsToIntegrate

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
Max: mdl.forest.treeStand.canopy.LAI
Max: mdl.forest.treeStand.canopy.WAI
Max: mdl.forest.underStorey.canopy.LAI
Mean: mdl.forest.soil.waterCycle.Stock_RootLayer
Mean: mdl.forest.soil.waterCycle.Dp_C
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
Sum: mdl.forest.soil.surface.ETR
Last: mdl.forest.treeStand.Age    
Last: mdl.forest.treeStand.density
Last: mdl.forest.treeStand.IStress   
Last: mdl.forest.treeStand.DBHmean 
Last: mdl.forest.treeStand.HEIGHTmean
Last: mdl.forest.treeStand.WProducted
Last: mdl.forest.treeStand.WaProducted
Last: mdl.forest.treeStand.BasalArea
Last: mdl.forest.treeStand.WDeadTrees
Last: mdl.forest.treeStand.LeafFall
Last: mdl.forest.treeStand.Wr
Last: mdl.forest.treeStand.WStem
Last: mdl.forest.treeStand.WBranch
Last: mdl.forest.treeStand.WFoliage
Last: mdl.forest.treeStand.PROD_VOL
Last: mdl.manager.harvest_WStem
Last: mdl.manager.harvest_WBranch   
Last: mdl.manager.NbCut_Trees 
Last: mdl.manager.harvest_DBHmean 
Last: mdl.manager.harvest_DBHsd   
Last: mdl.manager.harvest_basalArea   
Last: mdl.manager.thinnings
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
basePath  = os.path.dirname(os.path.realpath(__file__))+"/.."
sys.path.append(basePath+"/goplus/")
sys.path.append(basePath+"/goplus/goModel")
from goBases import *
from goModel.mdlModel import Model
from goModel.ManagerElements import mdlMngt_Operations
#from goModel.ManagerElements import mdlManager
from goTools.VarsIntegrater import Integrater


# Set of management practices that were applied to the Bray Site 1970-2010 ____________________________________________________________
INTERVENTIONS = {
        1970 : ('PLANTATION', 1250, 3 , 2, 0.5), 
        1980 : ('THINNING', 819, 2, True), 
        1991 : ('THINNING', 615, 3, True),        
        1996 : ('THINNING', 520, 2, True), 
        1999 : ('THINNING', 422,  0.4, True), 
        2001 : ('THINNING', 409,  1.0, True), 
        2002 : ('THINNING', 391,  1.5, True),
        2003 : ('THINNING', 385,  1.0, True),
        2004 : ('THINNING', 309,  1.0, True),
        2006 : ('THINNING', 301,  1.5, True),
        2008 : ('THINNING', 195,  1.5, True),
        }


class LBr_Manager(mdlMngt_Operations.Manager):


    def update(self):
        #Manage the interventions
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
            self.lastThinningYear   = 1980
            self.thinnings          = 1        
            self.seedingYear     = 1970
            self.FirstThinning      = False
 
        for interventionYear, interventionParameters in INTERVENTIONS.items():
            if  self.locTime.isYearEnd and self.locTime.Y == interventionYear  : 
                
                if  interventionParameters[0] == 'PLANTATION' :         
                    self.do_Plow(areaFractionPlowed = 1,soilCarbonFractionAffected = 0.5)
                    self.do_NewTrees( interventionParameters[2], interventionParameters[1])
                    
                if  interventionParameters[0] == 'THINNING' :
                    self.do_Plow(areaFractionPlowed = 0.75,soilCarbonFractionAffected = 0.10)
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
                self.forest.treeStand.pcs_SetSizes() 


# Object Model ================================================================               
def model(
    startYear,      #initial year
    meteoFile,      #meteo file path : str
    ):
    '''return an instance of the Model parameterized and initialized for the Bray site.
    '''

   ##instanciate the model, set a specific manager and define start year
    mdl= Model()
    mdl.manager = LBr_Manager() # see above
    mdl.locTime.Y_start = startYear
    mdl.climate.meteo_file_path = meteoFile
    mdl.climate.Scenario=0 # index code in mdlClimate mmodule; # Code 0: historical record; code 1: 500ppm, code 2: SRES A2; code 3: RCP2.6; code 4: RCP4.5; code 5: 500ppm; code 6: RCP 6.5; code 7: 500.0ppm; code 8: RCP8.5; code 9: 500ppm
      
   ## Site specific parameters from csv external file
    paraSiteFilePath = basePath + '/Parameters files/Site/FR-LBr.csv'
    fileParaSite = open(paraSiteFilePath,'r')
    line=next(fileParaSite)
    for line in fileParaSite :
        L = line.split(',') 
        nam = 'mdl' + str(L[0]).lstrip(',').split(" ",1)[0].replace("'","").replace('"','')
        val = float(L[1])
        exec("%s = %s" %(nam,val))
    
    fileParaSite.close()  
    
   ## Species parameters from csv external file
    paraSpeFilePath =basePath + '/Parameters files/Species//Ppinaster.csv' 
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
    ## Create a tree stand.
    yearLastIntervention = max([y for y in INTERVENTIONS.keys() if y < startYear])
    _initial_trees_Density = INTERVENTIONS[yearLastIntervention][1]
    _installation =mdl.forest.treeStand.pcs_TreeStandInstallation
    mdl.forest.treeStand.RotationYear = _installation.initialTreesAge
    _installation.initialTreesDimensionsFile = basePath + '/Parameters files/Tree stand/FR-LBr_dbh_1986.csv' 

    return mdl

# Launch a simulation
    
def simulate(
    mdl,              #model instance
    endYear,          # last year simulated
    fileoutName,      #name of the file to write the integrated model variables
    outFrequency,     
    log,              #boolean to indicate if simulation information is to be printed
    header= True, 
    fileOutAppend = False, 
    ):
    ''' simulation for BRAY
    '''
##Specify the integration
    integrater =Integrater(mdl, varsToIntegrate) #use the default integrable variables
    #open the fileOut and write header
    with open(fileoutName, 'w') as fileOut:
        fileOut.write('%s\n' % integrater.varNames)
        
##short reference to locTime object to accelerate conditionnal tests
        locTime = mdl.locTime     
        
##simulation loop
        while (locTime.Y is None) or (locTime.Y <endYear + 1):      
            mdl.update()
            
##made  the integrations of model variables and output the integrated values each day
            integrater.integrate() 
            if (True,  locTime.isDayEnd,  locTime.isYearEnd)[outFrequency]:
                fileOut.write('%s\n' % integrater.putStr())

##Display selected output values on a python console to monitor the simulation                
            if log and locTime.DOY==165 and locTime.H == 12 :
               print (str(locTime.Y),
                      'Age:',  str(mdl.forest.treeStand.Age), 
                      'nb: ',  str(mdl.forest.treeStand.treesCount),
                      'HEIGHT:',  str(mdl.forest.treeStand.HEIGHTmean), 
                      'DBH:', str(mdl.forest.treeStand.DBHmean),  
                      'IStress:', str(mdl.forest.treeStand.IStress), 
                      'LAI-T:', str(mdl.forest.treeStand.canopy.LAI), 
                      'Basal Area:', str(mdl.forest.treeStand.BasalArea),
                      'Thinnings', str(mdl.manager.thinnings)
                      )

if __name__ == '__main__':
    from time import  time

##instantiate the model 
    mdl = model( 
        startYear = 1986,
        meteoFile = basePath + '/Met files/Met_FR-LBr_1984-2011.csv',
        )
    endYear = 2010 #included
        
    #Do simulation
    if endYear>1987:
        tstart =time()
        simulate(
            mdl = mdl, 
            endYear = endYear, 
            fileoutName =basePath + '/output files/FR-LBr_1987-2010_d.csv', #  
            outFrequency=1,         #0: hour, 1: day, 2: year
            log =True, 
            header= True, 
            fileOutAppend = False, 
            )
        tend =time()
