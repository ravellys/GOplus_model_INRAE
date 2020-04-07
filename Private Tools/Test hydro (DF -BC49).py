# -*- coding: utf-8 -*-
# Declaration of the output variables and related statistics. Possible ootions: mean, maximum, minimum, final (last), sum.
# The integration step, hour, day or year,  is specified at the end of this script.
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
Last: mdl.forest.treeStand.canopy.sunLayer.LAI
Last: mdl.forest.treeStand.canopy.shadeLayer.LAI
Min: mdl.forest.treeStand.canopy.WaterPotential
Max: mdl.forest.soil.waterCycle.MoistureDeficit
Min: mdl.forest.soil.waterCycle.RootLayerWaterPotential
Last: mdl.forest.soil.waterCycle.Stock_RootLayer
Last: mdl.forest.soil.waterCycle.Stock_AB
Mean: mdl.forest.soil.waterCycle.discharge
Last: mdl.forest.soil.waterCycle.Dp_B
Last: mdl.forest.soil.waterCycle.Dp_C
Mean: mdl.forest.soil.waterCycle.w_A
Mean: mdl.forest.soil.waterCycle.w_RootLayer
Last: mdl.forest.soil.waterCycle._UA
Last: mdl.forest.soil.waterCycle._UB
Last: mdl.forest.soil.waterCycle._UC
Last: mdl.forest.soil.waterCycle._EA
Last: mdl.forest.soil.waterCycle._EC
Last: mdl.forest.soil.waterCycle.A_Ads
Last: mdl.forest.soil.waterCycle.C_Ads
Mean: mdl.forest.LE
Mean: mdl.forest.Rnet
Mean: mdl.forest.RnetLayers
Mean: mdl.forest.H
Mean: mdl.forest.treeStand.canopy.Ustar
Mean: mdl.forest.treeStand.canopy.u_surface
Sum: mdl.forest.GPP
Sum: mdl.forest.NEE
Sum: mdl.forest.RAuto
Sum: mdl.forest.soil.carbonCycle.Rh
Sum: mdl.forest.treeStand.canopy.Assimilation
Sum: mdl.forest.treeStand.canopy.Respiration
Sum: mdl.forest.treeStand.canopy.Transpiration
Sum: mdl.forest.treeStand.canopy.Transpirationmax
Mean: mdl.forest.treeStand.canopy.g_stom
Mean: mdl.forest.treeStand.canopy.g_stom_unstress
Sum: mdl.forest.treeStand.canopy.Evaporation
Mean: mdl.forest.treeStand.canopy.Rnet
Mean: mdl.forest.treeStand.canopy.Rnet_star
Min: mdl.forest.treeStand.canopy.dTsTa
Max: mdl.forest.treeStand.canopy.dTsTa
Mean: mdl.forest.treeStand.canopy.DrySurfaceFraction
Mean: mdl.forest.treeStand.canopy.LE_DrySurface
Mean: mdl.forest.treeStand.canopy.LE_WetSurface
Mean: mdl.forest.treeStand.canopy.H
Sum: mdl.forest.underStorey.canopy.ETR
Sum: mdl.forest.underStorey.canopy.Assimilation
Sum: mdl.forest.underStorey.canopy.Respiration
Sum: mdl.forest.underStorey.canopy.Transpiration
Sum: mdl.forest.underStorey.canopy.Transpirationmax
Sum: mdl.forest.underStorey.canopy.Evaporation
Last: mdl.forest.underStorey.canopy.LAI
Last: mdl.forest.underStorey.canopy.WAI
Sum: mdl.forest.soil.surface.ETR
Sum: mdl.forest.soil.surface.ETR_DrySurface
Sum: mdl.forest.soil.surface.ETR_WetSurface
Last: mdl.forest.treeStand.Age    
Last: mdl.forest.treeStand.density
Last: mdl.manager.harvest_WStem
Last: mdl.manager.harvest_WBranch
Max: mdl.forest.underStorey.foliage.W
Mean: mdl.forest.soil.carbonCycle.Ts_resp
Last: mdl.forest.soil.waterCycle.SOC
Last: mdl.forest.soil.waterCycle.VG_alpha
Last: mdl.forest.soil.waterCycle.VG_m
Last: mdl.forest.soil.waterCycle.VG_n
Last: mdl.forest.soil.waterCycle.RhydSoil
Last: mdl.forest.soil.waterCycle.w_FC
Last: mdl.forest.soil.waterCycle.w_SAT
Last: mdl.forest.soil.waterCycle.w_WP
Last: mdl.forest.soil.waterCycle.w_RES
'''

# =============================================================================
#  '''
#Sum: mdl.forest.GPP
#Sum: mdl.forest.NPP 
#Sum: mdl.forest.treeStand.Rm
#Sum: mdl.forest.treeStand.Rg
#Mean: mdl.forest.treeStand.Tree_N
#Sum: mdl.forest.treeStand.RmLeaf
#Sum: mdl.forest.NEE
#Sum: mdl.forest.soil.carbonCycle.RhLast: mdl.forest.treeStand.DBHmean 
#Last: mdl.forest.treeStand.HEIGHTmean
#Last: mdl.forest.treeStand.BasalArea
#Last: mdl.forest.treeStand.WDeadTrees
#Sum: mdl.forest.treeStand.LeafFall
#Sum: mdl.forest.treeStand.canopy.Assimilation
#Sum: mdl.forest.treeStand.canopy.Respiration
#Last: mdl.forest.treeStand.LitterfallLeaf
#Last: mdl.forest.treeStand.LitterfallBr
#Last: mdl.forest.treeStand.LitterfallRoot
#Last: mdl.forest.treeStand.Litterfall
#Last: mdl.forest.treeStand.BranchSenescence
#Last: mdl.forest.treeStand.RootSenescence
#Mean: mdl.forest.treeStand.IStress
#Last: mdl.forest.treeStand.FoliageArea
#Sum: mdl.forest.treeStand.RmStem
#Sum: mdl.forest.treeStand.RmLeaf
#Sum: mdl.forest.treeStand.RmBranches
#Sum: mdl.forest.treeStand.RmRoots
#Last: mdl.forest.treeStand.Wr
#Last: mdl.forest.treeStand.WStem
#Last: mdl.forest.treeStand.WBranch
#Last: mdl.forest.treeStand.WTapRoot
#Last: mdl.forest.treeStand.WCoarseRoot
#Last: mdl.forest.treeStand.WSmallRoot
#Last: mdl.forest.treeStand.WFineRoot
#Last: mdl.forest.treeStand.WProducted
#Last: mdl.forest.soil.waterCycle.Stock_RootLayer
#Last: mdl.forest.soil.waterCycle.Stock_AB
#Max: mdl.forest.soil.waterCycle.MoistureDeficit
#Max: mdl.forest.soil.waterCycle.RhydSoil
#Min: mdl.forest.treeStand.canopy.WaterPotential
#Max: mdl.forest.treeStand.canopy.WaterPotential
# Last: mdl.locTime.Y
# Last: mdl.locTime.DOY
# Last: mdl.locTime.H
# Last: mdl.forest.treeStand.Age
# Sum: mdl.climate.microclim.Rain
# Mean: mdl.climate.microclim.u
# Mean: mdl.climate.microclim.CO2
# Sum: mdl.forest.soil.surface.ETR
# Last: mdl.forest.soil.waterCycle.Stock_RootLayer
# Last: mdl.forest.soil.waterCycle.Stock_AB
# Max: mdl.forest.soil.waterCycle.MoistureDeficit
# Min: mdl.forest.soil.waterCycle.RootLayerWaterPotential
# Max: mdl.forest.soil.waterCycle.RootLayerWaterPotential
# Last: mdl.forest.soil.waterCycle.discharge
# Last: mdl.forest.soil.waterCycle.Dp_B
# Last: mdl.forest.soil.waterCycle.Dp_C
# Last: mdl.forest.soil.waterCycle.w_A
# Sum: mdl.forest.GPP
# Sum: mdl.forest.NPP 
# Sum: mdl.forest.treeStand.Rm
# Sum: mdl.forest.treeStand.Rg
# Sum: mdl.forest.treeStand.Tree_N
# Sum: mdl.forest.treeStand.RmLeaf
# Mean: mdl.forest.LE
# Mean: mdl.forest.Rnet
# Mean: mdl.forest.H
# Sum: mdl.forest.NEE
# Sum: mdl.forest.soil.carbonCycle.Rh
# Last: mdl.forest.treeStand.Age    
# Last: mdl.forest.treeStand.DBHmean 
# Last: mdl.forest.treeStand.HEIGHTmean
# Last: mdl.forest.treeStand.BasalArea
# Last: mdl.forest.treeStand.WDeadTrees
# Sum: mdl.forest.treeStand.LeafFall
# Sum: mdl.forest.treeStand.canopy.Assimilation
# Sum: mdl.forest.treeStand.canopy.Respiration
# Min: mdl.forest.treeStand.canopy.WaterPotential
# Max: mdl.forest.treeStand.canopy.WaterPotential
# Sum: mdl.forest.treeStand.litterfallLeaf
# Sum: mdl.forest.treeStand.litterfallBr
# Sum: mdl.forest.treeStand.litterfallRoot
# Sum: mdl.forest.treeStand.Litterfall
# Mean: mdl.forest.treeStand.IStress
# Last: mdl.forest.treeStand.NbDeadTrees
# Last: mdl.forest.treeStand.density
# Last: mdl.forest.treeStand.W
# Last: mdl.forest.treeStand.Wa
# Last: mdl.forest.treeStand.Wr
# Last: mdl.forest.treeStand.WStem
# Last: mdl.forest.treeStand.WProducted
# Last: mdl.forest.treeStand.canopy.LAI
# Sum: mdl.forest.treeStand.canopy.sunLayer.LAI
# Sum: mdl.forest.treeStand.canopy.shadeLayer.LAI
# Last: mdl.forest.treeStand.FoliageArea
# Mean: mdl.forest.treeStand.canopy.Rnet
# Mean: mdl.forest.treeStand.canopy.LE
# Mean: mdl.forest.treeStand.canopy.LE_DrySurface
# Mean: mdl.forest.treeStand.canopy.LE_WetSurface
# Mean: mdl.forest.treeStand.canopy.H
# Sum: mdl.forest.treeStand.canopy.Transpiration
# Sum: mdl.forest.treeStand.canopy.Evaporation
# Sum: mdl.forest.soil.surface.ETR
# Sum: mdl.forest.soil.surface.ETR_DrySurface
# Sum: mdl.forest.soil.surface.ETR_WetSurface
# Sum: mdl.forest.treeStand.canopy.Ga
# Mean: mdl.forest.treeStand.canopy.Ustar
# Max: mdl.forest.treeStand.canopy.dTsTa
# Max: mdl.forest.treeStand.canopy.WaterPotential
# Min: mdl.forest.treeStand.canopy.WaterPotential
# Sum: mdl.forest.treeStand.canopy.Dripping
# '''
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
from goModel.ManagerElements import mdlManager
from goTools.VarsIntegrater import Integrater



# Set of management practices that were applied to the Bray Site 1970-2010 ____________________________________________________________
INTERVENTIONS = {
        1949 : ('PLANTATION', 1250,2), 
        }


class _Manager(mdlManager.Manager):

    def update(self):
        #Manage the interventions
        for interventionYear, interventionParameters in INTERVENTIONS.items():
            if  self.locTime.isYearEnd and self.locTime.Y == interventionYear  : 
                
                if  interventionParameters[0] == 'PLANTATION' :         
                    self.do_Plow(areaFractionPlowed = 1,soilCarbonFractionAffected = 0.5)
                    self.do_NewTrees( interventionParameters[2], interventionParameters[1])
        
                self.forest.treeStand.pcs_SetSizes() #added for updating sand characteristics after management operations


# Object Model ____________________________________________________________________________________________________________________________                
def model(
    startYear,      #initial year
    meteoFile,      #meteo file path : str
#    iSoilType,     #index of the soil type : (0,1 or 2)
    ):
    '''return an instance of the Model parameterized and initialized for the Bray site.
    '''

   #instanciate the model, set a specific manager and define start year
    mdl= Model()
    mdl.manager = _Manager() # see above
    mdl.locTime.Y_start = startYear
   #specific parameters linked to the climate file
    mdl.climate.meteo_file_path = meteoFile
    mdl.climate.Scenario=0 # index code in mdlClimate mmodule; # Code 0: historical record; code 1: 500ppm, code 2: SRES A2; code 3: RCP2.6; code 4: RCP4.5; code 5: 500ppm; code 6: RCP 6.5; code 7: 500.0ppm; code 8: RCP8.5; code 9: 500ppm
      
   # Set the site specific parameters from csv external file
    paraSiteFilePath = basePath + '/Parameters files/Site/BC-DF49.csv'
    fileParaSite = open(paraSiteFilePath,'r')
    line=next(fileParaSite)
    for line in fileParaSite :
        L = line.split(',') 
        nam = 'mdl' + str(L[0]).lstrip(',').split(" ",1)[0].replace("'","").replace('"','')
        val = float(L[1])
        exec("%s = %s" %(nam,val))
    
    fileParaSite.close()  
    
   # Set the species parameters from csv external file:  Fsylvatica or Ppinaster or Pmensiezii or Quercus or any user file
   
    paraSpeFilePath =basePath + '/Parameters files/Species/DouglasFir.csv' 
    fileParaSpe = open(paraSpeFilePath,'r')
    line=next(fileParaSpe)
    for line in fileParaSpe :
        L = line.split(',') #L[0]=parameter name ; L[1]=parameter value ; L[2]=parameter comment
        nam = 'mdl' + str(L[0]).lstrip("'").split(',')[0].replace("'","").replace('"','')
        try :
            val = round(float(L[1]),6)
        except ValueError :
            val = str(L[1])

        exec("%s = %s" %(nam,val))

    fileParaSpe.close()

    yearLastPlantation = 1949
 #   _initial_trees_Age =  13
    yearLastIntervention = max([y for y in INTERVENTIONS.keys() if y < startYear])
    _initial_trees_Density = INTERVENTIONS[yearLastIntervention][1]
    _installation =mdl.forest.treeStand.pcs_TreeStandInstallation
    mdl.forest.treeStand.RotationYear = _installation.initialTreesAge
    _installation.initialTreesDimensionsFile =''

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
    ''' simulation for BRAY
    '''
#Specify the integration
    integrater =Integrater(mdl, varsToIntegrate) #use the default integrable variables
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
               print (str(locTime.Y), 'Age:',  str(mdl.forest.treeStand.Age), ', nb: ',  str(mdl.forest.treeStand.treesCount), ', HEIGHT:',  str(mdl.forest.treeStand.HEIGHTmean), ', DBH:', 
                str(mdl.forest.treeStand.DBHmean),  'IStress:', str(mdl.forest.treeStand.IStress), 'LAI-T:', str(mdl.forest.treeStand.canopy.LAI), \
               'LAI_U', str(mdl.forest.underStorey.canopy.LAI)) 

if __name__ == '__main__':
    from time import  time

#instantiate the model for a specific experiment. Here a test on the Le Bray data time series. 
#the met file is taken from the MeteoFrance Safran gridded data set.

    mdl = model( 
        startYear = 1998,
        meteoFile = basePath + '/Met files/Met_BC-DF49_1998-2010.csv'
        )
    endYear = 1999 #included
        
    #Do simulation
    if endYear>1998:
        tstart =time()
        simulate(
            mdl = mdl, 
            endYear = endYear, 
            fileoutName =basePath + '/output files/BC-DF49_1998-2010_h.csv',
            outFrequency=0,         #0: hour, 1: day, 2: year
            log =True, 
            header= True, 
            fileOutAppend = False, 
            )
        tend =time()
