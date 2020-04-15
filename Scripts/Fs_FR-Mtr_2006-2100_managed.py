# -*- coding: utf-8 -*-
# Declaration of the output variables and related statistics. Possible options: mean, maximum, minimum, final, sum.
# The integration step, hour, day or year,  is specified  at the end of this script
# Alternatively, instead of declaring output variables and associated statistics as done below L7 -L75, a test file can be used with the instruction:
# from "filename" (ex: BRAY_varsToIntegrate) import varsToIntegrate

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
Mean: mdl.forest.soil.waterCycle.Stock_RootLayer
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
Last: mdl.forest.treeStand.BasalArea
Last: mdl.forest.treeStand.WDeadTrees
Last: mdl.forest.treeStand.LeafFall
Last: mdl.forest.treeStand.Wr
Last: mdl.forest.treeStand.WStem
Last: mdl.forest.treeStand.WBranch
Last: mdl.manager.harvest_WStem
Last: mdl.manager.harvest_WBranch
Last: mdl.manager.harvest_W   
Last: mdl.manager.harvest_WStem   
Last: mdl.manager.harvest_WBranch 
Last: mdl.manager.harvest_WTapRoots   
Last: mdl.manager.NbCut_Trees 
Last: mdl.manager.harvest_DBHmean 
Last: mdl.manager.harvest_DBHquadratic 
Last: mdl.manager.harvest_DBHsd   
Last: mdl.manager.harvest_HEIGHTmean  
Last: mdl.manager.harvest_HEIGHTsd
Last: mdl.manager.harvest_basalArea   
Last: mdl.manager.seedingYear  
Last: mdl.manager.FirstThinning
Last: mdl.manager.lastThinningYear
Last: mdl.manager.clearcuts
Last: mdl.manager.thinnings
Last: mdl.manager.practicesType   
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
basePath  = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
sys.path.append(os.path.join(basePath, "goplus"))
sys.path.append(os.path.join(basePath, "goplus", "goModel"))
from goBases import *
from goModel.mdlModel import Model
#from goModel.ManagerElements import Mngt_Operations
from goModel.ManagerElements import mdlManager
from goTools.VarsIntegrater import Integrater



# Object Model=================================================================               
def model(
    startYear,      #initial year
    meteoFile,      #meteo file path : str
    ):
    '''return an instance of the Model parameterized and initialized f.
    '''

   #instanciate the model, set a specific manager and define start year
    mdl= Model()
    mdl.manager                 = mdlManager.Manager()
    mdl.manager.practicesType   = 0 #Select the management plan to be applied. 0 = standard; 2 = self thinning rule. 
    mdl.locTime.Y_start         = startYear
    mdl.climate.meteo_file_path = meteoFile
    mdl.climate.Scenario        = 8 # index code in mdlClimate mmodule; # Code 0: historical record; code 1: 500ppm, code 2: SRES A2; code 3: RCP2.6; code 4: RCP4.5; code 5: 500ppm; code 6: RCP 6.5; code 7: 500.0ppm; code 8: RCP8.5; code 9: 500ppm
    
   ## Set the site specific parameters from csv external file
    paraSiteFilePath            = os.path.join(basePath, 'Parameters_files', 'Site', 'FR-Mtr_140.csv')
    fileParaSite                = open(paraSiteFilePath,'r')
    line=next(fileParaSite)
    for line in fileParaSite :
        L   = line.split(',') 
        nam = 'mdl' + str(L[0]).lstrip(',').split(" ",1)[0].replace("'","").replace('"','')
        val = float(L[1])
        exec("%s = %s" %(nam,val))
    fileParaSite.close()  
    
   ## Set the species parameters from csv external file Fsylvatica 
   
    paraSpeFilePath = os.path.join(basePath, 'Parameters_files', 'Species', 'Fsylvatica.csv') 
    fileParaSpe     = open(paraSpeFilePath,'r')
    line            = next(fileParaSpe)
    for line in fileParaSpe :
        L       = line.split(',') 
        nam     = 'mdl' + str(L[0]).lstrip("'").split(',')[0].replace("'","").replace('"','')
        try :
            val = round(float(L[1]),6)
        except ValueError :
            val = str(L[1])
        exec("%s = %s" %(nam,val))

    fileParaSpe.close()

   ## intialise the tree stand.  
    _installation =mdl.forest.treeStand.pcs_TreeStandInstallation
    mdl.forest.treeStand.RotationYear = _installation.initialTreesAge
    _installation.initialTreesDimensionsFile = os.path.join(basePath, 'Parameters_files', 'Tree_stand', 'FR-Mtr_dbh_140_85.csv') 

    return mdl

def simulate(
    mdl,              #model instance
    endYear,          # last year simulated
    fileoutName,      #name of the file to write the integrated model variables
    outFrequency,     
    log,              #boolean to indicate if simulation information is to be printed
    header= True, 
    fileOutAppend = False, 
    ):
    ''' simulation Montreich (MTR) RCP85)
    '''
#integration of output variables
    integrater =Integrater(mdl, varsToIntegrate) 
    with open(fileoutName, 'w') as fileOut:
        fileOut.write('%s\n' % integrater.varNames)
 ## short reference to locTime object to accelerate conditionnal tests
        locTime = mdl.locTime     
 ## simulation loop
        while (locTime.Y is None) or (locTime.Y <endYear + 1):      
 ## update the model state
            mdl.update()
 ## daily output of the integrated values 
            integrater.integrate() 
            if (True,  locTime.isDayEnd,  locTime.isYearEnd)[outFrequency]:
                fileOut.write('%s\n' % integrater.putStr())

#Display selected output values on a python console to monitor the simulation                
            if log and locTime.DOY == 195 and locTime.H == 23:
               print (str(locTime.Y),
                      'Age:',  str(mdl.forest.treeStand.Age), 
                      ', nb: ',  str(mdl.forest.treeStand.treesCount), 
                      ', HEIGHT:',  str(mdl.forest.treeStand.Heightmean), 
                      ', DBH:', str(mdl.forest.treeStand.DBHmean),
                      ', IStress:', str(mdl.forest.treeStand.IStress), 
                      ', LAI:', str(mdl.forest.treeStand.canopy.LAI), 
                      ', Basal Area:', str(mdl.forest.treeStand.BasalArea),
                      ', Thinnings:', str(mdl.manager.thinnings)
                      )

#instantiate the model for a specific experiment. 

if __name__ == '__main__':
    from time import  time
    mdl = model( 
        startYear = 2006,
        meteoFile = os.path.join(basePath, 'Met_files', 'Met_FR-Mtr_RCP85_2006-2100.csv'),
        )
    endYear = 2100
        
#Do simulation
    if endYear>2006:
        tstart =time()
        simulate(
            mdl = mdl, 
            endYear = endYear, 
            fileoutName =os.path.join(basePath, 'Output_files', 'FR-Mtr_RCP85_age140_2006-2100_ytest.csv'), #  
            outFrequency=2,         #0: hour, 1: day, 2: year
            log =True, 
            header= True, 
            fileOutAppend = False, 
            )
        tend =time()
