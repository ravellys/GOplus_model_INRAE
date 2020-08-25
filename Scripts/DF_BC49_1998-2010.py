# -*- coding: utf-8 -*-
# Declaration of the output variables and related statistics. Possible ootions: mean, maximum, minimum, final, sum.
# The integration step, hour, day or year,  is specified  at L159 and instanciated L203
# Alternatively, instead of declaring output variables and associated statistics as done below L7 -L37, a test file can be used with the instruction:
#from "filename" (ex: BRAY_varsToIntegrate) import varsToIntegrate

varsToIntegrate = '''
Last: mdl.locTime.Y
Last: mdl.locTime.DOY
Last: mdl.locTime.H
Sum: mdl.climate.microclim.Rain
Mean:mdl.climate.microclim.u
Mean: mdl.climate.microclim.TaC
Mean: mdl.climate.microclim.d
Mean: mdl.climate.microclim.SWDir
Mean: mdl.climate.microclim.SWDif
Mean: mdl.climate.microclim.LWDw
Last: mdl.forest.treeStand.canopy.LAI
Last: mdl.forest.treeStand.canopy.WAI
Last: mdl.forest.underStorey.canopy.LAI
Last: mdl.forest.underStorey.canopy.WAI
Last: mdl.forest.treeStand.HEIGHTmean
Last: mdl.forest.treeStand.canopy.WaterPotential
Last: mdl.forest.soil.waterCycle.RootLayerWaterPotential
Last: mdl.forest.soil.waterCycle.Stock_RootLayer
Last: mdl.forest.soil.waterCycle.Stock_AB
Last: mdl.forest.treeStand.IStress
Last: mdl.forest.soil.waterCycle.discharge
Last: mdl.forest.soil.waterCycle.Dp_B
Last: mdl.forest.soil.waterCycle.Dp_C
Last: mdl.forest.soil.waterCycle.w_A
Mean: mdl.forest.LE
Mean: mdl.forest.Rnet
Mean: mdl.forest.H
Sum: mdl.forest.GPP
Sum: mdl.forest.NEE
Sum: mdl.forest.RAuto
Sum: mdl.forest.soil.carbonCycle.Rh
Sum: mdl.forest.treeStand.canopy.Assimilation
Sum: mdl.forest.treeStand.Rm
Last: mdl.forest.treeStand.Annual_Rg
Sum : mdl.forest.treeStand.canopy.Transpiration
Sum: mdl.forest.treeStand.canopy.Evaporation
Mean: mdl.forest.treeStand.canopy.Rnet
Mean: mdl.forest.treeStand.canopy.dTsTa
Mean: mdl.forest.treeStand.canopy.DrySurfaceFraction
Mean: mdl.forest.treeStand.canopy.LE_DrySurface
Mean: mdl.forest.treeStand.canopy.LE_WetSurface
Mean: mdl.forest.treeStand.canopy.H
Sum: mdl.forest.underStorey.canopy.ETR
Sum: mdl.forest.underStorey.canopy.Assimilation
Sum: mdl.forest.underStorey.canopy.Respiration
Sum: mdl.forest.underStorey.canopy.Transpiration
Sum: mdl.forest.underStorey.canopy.Evaporation
Sum: mdl.forest.soil.surface.ETR_DrySurface
Sum: mdl.forest.soil.surface.ETR_WetSurface
Last: mdl.forest.treeStand.density
Last: mdl.forest.treeStand.Age    
Last: mdl.forest.treeStand.DBHmean 
Last: mdl.forest.treeStand.HEIGHTmean
Last: mdl.forest.treeStand.BasalArea
Last: mdl.forest.treeStand.WDeadTrees
Sum: mdl.forest.treeStand.LitterfallLeaf
Sum: mdl.forest.treeStand.LitterfallBr
Sum: mdl.forest.treeStand.LitterfallRoot
Sum: mdl.forest.treeStand.Litterfall
Last: mdl.forest.treeStand.Wr
Last: mdl.forest.treeStand.WStem
Last: mdl.forest.treeStand.WBranch
Last: mdl.forest.treeStand.WTapRoot
Last: mdl.forest.treeStand.WCoarseRoot
Last: mdl.forest.treeStand.WSmallRoot
Last: mdl.forest.treeStand.WFineRoot
Last: mdl.manager.harvest_WStem
Last: mdl.manager.harvest_WBranch
Last: mdl.forest.underStorey.foliage.W
Last: mdl.forest.underStorey.perennial.W
Last: mdl.forest.underStorey.roots.W
Last: mdl.forest.underStorey.foliage.LitterFall
Last: mdl.forest.underStorey.perennial.LitterFall
Last: mdl.forest.underStorey.roots.LitterFall
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
from goModel.ManagerElements import mdlMngt_Operations
from goModel.ManagerElements import mdlManager
from goTools.VarsIntegrater import Integrater

# Set of management practices that were applied to the tree stand ====
INTERVENTIONS = {
        1949 : ('PLANTATION', 3, 1250, 2, 0.5), 
        }


class DF49_Manager(mdlMngt_Operations.Manager):

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
            self.lastThinningYear   = 1939
            self.thinnings          = 0        
            self.seedingCutYear     = 1946
            self.FirstThinning      = False        
        
        for interventionYear, interventionParameters in INTERVENTIONS.items():
            if  self.locTime.isYearEnd and self.locTime.Y == interventionYear  : 
                
                if  interventionParameters[0] == 'PLANTATION' :         
                    self.do_Plow(areaFractionPlowed = 1,soilCarbonFractionAffected = 0.5)
                    self.do_NewTrees( interventionParameters[1], interventionParameters[2], interventionParameters[3],interventionParameters[4],)
                    

# Object Model ==============================================================            
def model(
    startYear,      
    meteoFile,      
    ):
    '''return an instance of the Model parameterized and initialized for the Bray site.
    '''

   #instanciate the model, set a specific manager and define start year
    mdl= Model()
    mdl.manager = DF49_Manager() # see above
    mdl.locTime.Y_start = startYear
   #specific parameters linked to the climate file
    mdl.climate.meteo_file_path = meteoFile
    mdl.climate.Scenario=0 # index code in mdlClimate mmodule
      
   # Set the site specific parameters from csv external file
    paraSiteFilePath = os.path.join(basePath, 'Parameters_files', 'Site', 'BC-DF49.csv')
    fileParaSite = open(paraSiteFilePath,'r')
    line=next(fileParaSite)
    for line in fileParaSite :
        L = line.split(',') 
        nam = 'mdl' + str(L[0]).lstrip(',').split(" ",1)[0].replace("'","").replace('"','')
        val = float(L[1])
        exec("%s = %s" %(nam,val))
    
    fileParaSite.close()  
    
   # Set the species parameters from csv external file
    paraSpeFilePath =os.path.join(basePath, 'Parameters_files', 'Species', 'DouglasFir.csv' )
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


    yearLastIntervention    = max([y for y in INTERVENTIONS.keys() if y < startYear])
    _initial_trees_Density  = INTERVENTIONS[yearLastIntervention][2]
    _installation           = mdl.forest.treeStand.pcs_TreeStandInstallation
    mdl.forest.treeStand.RotationYear = _installation.initialTreesAge
    _installation.initialTreesDimensionsFile =''
    return mdl

def simulate(
    mdl,              #model instance
    endYear,          #last year simulated
    fileoutName,      #name of the output file 
    outFrequency,     
    log,              #boolean to indicate if simulation information is to be printed
    header= True, 
    fileOutAppend = False, 
    ):
    ''' simulation for Douglas Fir 49 year old BC
    '''
#Specify the integration
    integrater =Integrater(mdl, varsToIntegrate) 
#open the fileOut and write header
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

    #instantiate the model

    mdl = model( 
        startYear = 1998,
        meteoFile = os.path.join(basePath, 'Met_files', 'Met_BC-DF49_1998-2010.csv')
        )
    
    endYear = 2010 
    fileoutName =os.path.join(basePath, 'Output_files', 'BC-DF49_1998-2010_d.csv')
    
    #Do simulation
    if endYear>1998:
        tstart = time()
        simulate(
            mdl             =mdl,
            endYear         =endYear,
            fileoutName     =fileoutName,
            outFrequency    =1,         #0: hour, 1: day, 2: year
            log             =True,
            header          =True,
            fileOutAppend   =False,
            )
        tend = time()
        print("\n Completed \n Output file is:", fileoutName, "\n simulate in %s mn." % str((tend-tstart)/60.))     