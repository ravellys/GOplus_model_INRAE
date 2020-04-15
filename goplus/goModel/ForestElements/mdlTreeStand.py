from __future__ import division
import os,sys
import numpy as np
from goBases import * 		#Windows
#from ...goBases import * 	#LINUX
from ForestElements.mdlTreeSizes import TreeSizes
from ForestElements.mdlTrees import Trees
from ForestElements.mdlLeavesCohort import LeavesCohort
from ForestElements.Canopy.mdlCanopy import SunShadeCanopy as Canopy
from ForestElements.SoilElements.mdlSoilCarbonCycle import SoilCarbonCycle
#from ManagerElements.mdlManager import Manager
import  random, math
basePath  = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")

class TreeStand(Trees):
    '''represent the tree stand and its main biophysical and biogeochemical processes: phenology, carbon allocation, growth, respiration, hydraulics, 
    water stress, senescence, mortality and stand installation
    '''
    # Outer elements
    locTime = eltOut('LocTime element')
    sunLocal = eltOut('SunLocal element')
    microclim = eltOut('Upper MicroClimate element')
    microclim_under = eltOut('Under MicroClimate element')
    soil = eltOut('Soil element')
    
    #Inner elements
    cohorts = eltIn(ELTS)
    canopy = eltIn(Canopy)

    #vars
    ClumpAge= var('age of last clump cut (year) (yyyy)',0.)
    Age = var('tree age (year)',0.)
    Age_aerial = var('age of the aerial part of the tree  (year)',0.)
    WLeaf   = var('total leaf weight (Kg_DM/m2_soil)',0.)
    Species     = var('Species name, ex. Ppinaster, Fsylvatica, Pmenziesii, Qrobur,...',)
    MeanTaC     = var ('daily mean temperature (degC)',0.)
    MeanSWDif   = var('daily mean diffuse SW radiation temperature (W.m-2)',0.)
    MeanSWDir   = var('daily mean direct SW radiation (W.m-2)',0.)
    Rch  = var('Chilling rate',0.)  
    Rfor = var('Forcing rate',0.)
    Sfor = var('Sum of the forcing units',0.)
    Sch  = var('Sum of the chilling units',0.)
    
    #params
    NbCohort            = param('nb of cohorts of the canopy foliage')
    k_DBH_1             = param('param allometry')
    k_DBH_2             = param('param allometry')
    k_DBH_3             = param('param allometry')
    k_Height_1          = param('param allometry')
    k_Height_2          = param('param allometry')
    k_Height_3          = param('param allometry')
    k_Wn1_1             = param('param allometry 1rst cohort')
    k_Wn1_2             = param('param allometry 1rst cohort')
    k_Wn1_3             = param('param allometry 1rst cohort')
    k_Wn_1              = param('param allometry all cohorts')
    k_Wn_2              = param('param allometry all cohorts')
    k_Wn_3              = param('param allometry all cohorts')
    k_WStem_1           = param('param allometry')
    k_WStem_2           = param('param allometry')
    k_WStem_3           = param('param allometry')
    k_WStem_4           = param('param allometry')
    k_WCoarseRoot_1     = param('param allometry')
    k_WCoarseRoot_2     = param('param allometry')
    k_WCoarseRoot_3     = param('param allometry')
    k_WSmallRoot_1      = param('param allometry')
    k_WSmallRoot_2      = param('param allometry')
    k_WSmallRoot_3      = param('param allometry')
    k_WTapRoot_1        = param('param allometry')
    k_WTapRoot_2        = param('param allometry')
    k_WTapRoot_3        = param('param allometry')
    k_WTap_SmallRoot_1  = param('param allometry')
    k_WTap_SmallRoot_2  = param('param allometry')
    k_WTap_SmallRoot_3  = param('param allometry')
    k_WTap_SmallRoot_4  = param('param allometry')
    _germinationYear    = private('year of germination (yyyy)')
    Area                = param('stand area (m2)')
    ClearCuts           = param('Clear cut id')
    ST_alpha            = param('parameter alpha of self thinning rule, 171582 oak, 198336 coniferous (trees.ha-1)')
    ST_beta             = param('parameter beta of self thinning rule, 1.701 oak, 1.6 coniferous (trees.ha-1)')
    Tree_Log            = param('Tree logging id')
    Foliage_Fraction_Removed=var('Ratio of foliage removed by thinning or respacing',0.)
    RotationYear        = var('number of years of the current rotation')
    BiomassCarbonContent = param('carbon content of dry biomass (g_C /Kg_DM)')
    SLA                 = param('specific leaf area (m2_LeafArea /Kg_DM)') # Age dependency could be introduced e.g.  (Porte et al AFS 2000)
    wood_density        = param('wood basic density (t/m3)')
    shape_factor        = param('ratio of stand stemwood volume (m3.ha-1) over basal area (m2.ha-1) times Mean Height (m), unitless')
    BBHeatSum           = param('Heat Sum for Bud Burst (deg C day)')
    k_1                 = param('cohort phenology')
    k_2                 = param('cohort phenology')
    k_3                 = param('cohort phenology')
    LifeDuration        = param('Cohort life duration, (days)') 
    DG50                = param('time since budburst to reach 50 percent of growth (days)') 
    DS50                = param('Senescence Length (days)')
    Gref                = param('Growth percentage at budburst')
    Sref                = param('Growth percentage at senescence')            
    Tmin                = param('coefficient of the chiling rate equation from Kamer 1994') 
    Tmax                = param('coefficient of the chiling rate equation from Kramer 1994') 
    Topt                = param('coefficient of the chiling rate equation from Kramer 1994')
    Tb                  = param('Base temperature of the sequential model of Kramer 1994')
    Ccrit               = param('threshold to chiling rate')
    Fcrit               = param('threshold to forcing rate')
    k_a                 = param('coefficient of the forcing rate equation from Kramer 1994') 
    k_b                 = param('coefficient of the forcing rate equation from Kramer 1994')
    k_c                 = param('coefficient of the forcing rate equation from Kramer 1994') 
    k_GSL1              = param('coefficient 1 of Growth Season Length equation')
    k_GSL2              = param('coefficient 2 of Growth Season Length equation') 
    LAI_LeafArea_ratio  = param('LAI to all sided leaf area ratio')
    _PaliveBranch_min   = param('minimum of the proportion of living mass of branches')
    _PaliveBranch_max   = param('maximum of the proportion of living mass of branches')
    _Al_As_ratio_slope  = param('slope of the leaf area to sapwood area with height (m2.cm-2)')
    _Al_As_ratio_int    = param('int of the leaf area to sapwood area regression with height (m2.cm-2)')
    _Al_As_ratio_exp    = param('int of the leaf area to sapwood area regression with height (m2.cm-2)')
    _PaliveLeaf         = param('proportion of living cells in leaf (Kg_livingCells/Kg_DM)')
    _PaliveStem         = param('proportion of living cells in Stem (Kg_livingCells/Kg_DM)')
    _PaliveTapRoot_min  = param('minimum of the proportion of living mass of branches')
    _PaliveTapRoot_max  = param('maximum of the proportion of living mass of branches')
    _PaliveCoarseRoot_min =   param('minimum of the proportion of living mass of branches')
    _PaliveCoarseRoot_max =   param('maximum of the proportion of living mass of branches')
    _PaliveSmallRoot_min = param('minimum of the proportion of living mass of branches')
    _PaliveSmallRoot_max = param('maximum of the proportion of living mass of branches')
    _PaliveFineRoot     = param('proportion of living cells in fine roots (Kg_livingCells/Kg_DM)')
    _Nleaves            = param('leaves nitrogen content (g_N/ Kg_livingCells ou mg_N/g_livingCells)')
    _NStem              = param('trunk nitrogen content (g_N/ Kg_livingCells ou mg_N/g_livingCells)')
    _NBranch            = param('Branches nitrogen content (g_N/ Kg_livingCells ou mg_N/g_livingCells)')
    _NTapRoot           = param('roots nitrogen content (g_N/ Kg_livingCells ou mg_N/g_livingCells)')
    _NCoarseRoot        = param('roots nitrogen content (g_N/ Kg_livingCells ou mg_N/g_livingCells)')        
    _NSmallRoot         = param('roots nitrogen content (g_N/ Kg_livingCells ou mg_N/g_livingCells)')
    _NFineRoot          = param('roots nitrogen content (g_N/ Kg_livingCells ou mg_N/g_livingCells)')
    
    def _simul_initialisation(self):
        '''Initialisation step'''
        
        #connect the inner ELT 
        self.canopy.locTime         = self.locTime
        self.canopy.sunLocal        = self.sunLocal
        self.canopy.microclim       = self.microclim
        self.canopy.microclim_under = self.microclim_under
        self.canopy.soil            = self.soil
        self.Sch                    = 60. #intialisation of the sum of chilling unit by 31st Dec (Soroe historical data)
        #create the trees
        self.pcs_TreeStandInstallation()
        self.Annual_Rg              = self.pcs_CarbonFluxesPartition.RgCost * (self.Wa + self.Wr) / (self.Age) * self.BiomassCarbonContent 

        #other variables initialisation
        self.microclim_d1           = 0 
        self.microclim_d2           = 0
        self.MeanTaCHiv             = 0.0
        self.Hiv                    = 0.0
        self.mortalityTrees = []  
        
    def ChillingRate(self) :
        self.Rch=0.
        if self.Species=='Fsylvatica': 
            if self.MeanTaC>self.Tmin :
                if self.MeanTaC<=self.Topt :
                    self.Rch=(self.MeanTaC-self.Tmin)/(self.Topt-self.Tmin)
                elif self.MeanTaC<self.Tmax :
                    self.Rch=(self.MeanTaC-self.Tmax)/(self.Topt-self.Tmax)
                else :
                    self.Rch=0    
                    
        elif self.Species=='DouglasFir': 
            if self.Tmin < self.microclim.TaC < self.Tmax :
                self.Rch = min (1.0, 3.13 * (((self.microclim.TaC + 4.66 ) / 10.93) ** 2.10 ) * exp(-(((self.microclim.TaC + 4.66)/10.93)**3.10)) )
            else :
                self.Rch = 0    
        return self.Rch
    
    def ForcingRate(self) :
        self.Rfor=0.
        if self.Species == 'Fsylvatica': 
            if self.MeanTaC > self.Tb :
                self.Rfor = (self.k_a/(1.+exp(self.k_b*(self.MeanTaC+self.k_c))))
            else :
                self.Rfor = 0
                
        if self.Species =='DouglasFir': 
                self.Rfor = 1 / (1 + exp(-0.47 * self.microclim.TaC+6.49))     
        return self.Rfor

    def update(self):
        '''hourly update'''
        
#Processes evaluated at the start of the simulation. 
        if self.locTime.isSimulBeginning:
            self._simul_initialisation()
        
#Processes evaluated yearly.
        if self.locTime.isYearBeginning:
            self.Age        = self.locTime.Y - self._germinationYear 
            self.Age_aerial = self.Age - self.ClumpAge
            self.SumLeafFall = 0.0
            self.Litterfall = 0.0

#Processes evaluated hourly
        ## Tree growth and senescence    
        self.pcs_LeafAreaDevelopment()
        self.pcs_SecondaryGrowth()
        self.pcs_Senescence()
        self.pcs_AllocateLitterCarbonToSoil()

        ## Canopy surface processes
        self.canopy.update()
        
        ## Water balance processes
        self.pcs_HydraulicStatus()
        self.pcs_HydricStress()

        ## Carbon balance processes
        self.pcs_Respiration()
        self.pcs_CarbonFluxesPartition()
        
        ##Computations of mean daily Temperature and radiation, used in the phenological model (mdlLeavesCohort)
        if self.Species=='Fsylvatica': 
            if self.locTime.H == 0  : 
                self.MeanTaC   = self.microclim.TaC/24.0
                self.MeanSWDif = self.microclim.SWDif/24.0
                self.MeanSWDir = self.microclim.SWDir/24.0
            else :
                self.MeanTaC   += self.microclim.TaC/24.0 
                self.MeanSWDif += self.microclim.SWDif/24.0
                self.MeanSWDir += self.microclim.SWDir/24.0    
#=============================================================================
   #LEAF AREA DEVELOPMENT
    FoliageArea = var('total Foliage area (m2_leaf /m2_soil)', 0.0 )
    LeafFall = var('Leaf Litterfall (Kg_DM /m2_soil /day)', 0.0)
    
    @pcs    
    def pcs_LeafAreaDevelopment(self):
        
        if self.Species=='Fsylvatica': 
            #Accumulates chilling unit CU from 1st nov. and forcing units when sum of CU > Ccrit
            if self.locTime.DOY == 303 :
                self.Sch  = 0.0 
                self.Rch  = 0.0
            else :
                self.Sch  +=   self.ChillingRate()/24
                if self.Sch < self.Ccrit :
                    self.Sfor = 0 
                else :
                    self.Sfor  += self.ForcingRate()/24           
                    
        if self.Species=='DouglasFir' : 
            #Accumulates chilling unit CU from 1st nov. and forcing units when sum of CU > Ccrit
            if self.locTime.DOY == 303 :
                self.Sch  = 0.0 
                self.Rch  = 0.0
            else :
                self.Sch   +=  self.ChillingRate()
                self.Sfor  +=  self.ForcingRate()
                
        if self.locTime.isYearBeginning :
            #shed dead cohorts          
            for _cohort in   [_c for _c in self.cohorts  if (_c.Retained <= 0.02) and (_c.Year != self.locTime.Y) ]:
                self.cohorts.remove(_cohort)  
            #Create a new leaf cohort
            if self.treesCount > 0:                
                _cohort           = LeavesCohort()
                _cohort.Year      = self.locTime.Y
                _cohort.treeStand = self
                _cohort.locTime   = self.locTime
                _cohort.SumSW     = 0
                _cohort.DateOfBB  = -9999
                _cohort.DateOfS   = -9999
                _cohort.Retained  = 1
                _cohort.Expansion = 0
                _cohort.HeatSum   = 0
                self.cohorts.insert(0, _cohort) 
            
            self.SumLeafFall = 0.0
            self.Litterfall  = 0.0
                
        if self.locTime.isDayBeginning:
            #Remove  cohorts when no trees or after clear cuts -
            if self.treesCount == 0:
                for _cohort in self.cohorts:self.cohorts.remove(_cohort)
                self.canopy.LAI = self.LeafFall = self.FoliageArea = 0
            else:
                for _cohort in self.cohorts:
                      _cohort.update_daily()                    
                #Leaf Area components
                self.LeafFall       = sum(_cohort.LeafFall for _cohort in self.cohorts)
                self.FoliageArea    = sum(_cohort.FoliageArea for _cohort in self.cohorts)
                self.canopy.LAI     = sum(_cohort.LAI for _cohort in self.cohorts)
                self.WLeaf          = sum(_cohort.Weight for _cohort in self.cohorts)
        
        #Update the sum of temperature used for leaf phenology
        for _cohort in self.cohorts:
            _cohort.HeatSum += self.microclim.TaC / 24.0

#______________________________________________________________________________________________________________________________________________________________
#SECONDARY GROWTH PHENOLOGY: used for allocating the growth respiration along the year.Since Rg is not depending on temperature but on growth, 
#a empirical seasonal secondary growth is simulated.
    GrowthIntensity = var('relative growth rate (annual integration = 1) (?)', 0.)
    
    @pcs    
    def pcs_SecondaryGrowth(self, 
        k_Growth_a = param('parameter a of secondary growth model (-)', 0.01),
        k_Growth_b = param('parameter b of secondary growth model (-)', 0.01), 
        k_Growth_c = param('parameter c of secondary growth model (-)', 0.01), 
        ):
        ''' Secondary growth phenology'''
        #This is to distribute the growth respiration along the year. An assymetrical function is used whose annual integral is 1. 
        #Secondary growth starts a a fixed delay before budburst. 
        #Caution : Growth respiration may be unerstimated by 1-2pct when day of budBurst is >150
        DOYBB = min(_cohort.DOYOfBB for _cohort in self.cohorts)
        if self.locTime.isDayBeginning:
            if (DOYBB-k_Growth_c) > self.locTime.DOY or DOYBB == -9999 :
                self.GrowthIntensity = 0
            else :
                _KJref = (self.locTime.DOY - (DOYBB-k_Growth_c))/ k_Growth_a
                self.GrowthIntensity = (k_Growth_b / k_Growth_a) * (_KJref ** (k_Growth_b - 1)) * exp(-(_KJref ** k_Growth_b))
    
#Senescence of tree parts =====================================================
    BranchSenescence = var('Branch biomass leave by senescence (Kg_DM /m2_soil /year)')
    RootSenescence = var('root biomass leave by senescence (Kg_DM /m2_soil /year)')

    @pcs    
    def pcs_Senescence(self, 
        k_SenBch_1 = param('coefficient 1 of allometric equation to calculate Branches senescence'), 
        k_SenBch_2 = param('coefficient 2 of allometric equation to calculate Branches senescence') , 
        k_SenBch_3 = param('coefficient 3 of allometric equation to calculate Branches senescence') , 
        k_SenRoot_1 = param('coefficient 1 of allometric equation to calculate roots senescence'), 
        k_SenRoot_2 = param('coefficient 2 of allometric equation to calculate roots senescence'), 
        k_SenRoot_3 = param('coefficient 3 of allometric equation to calculate roots senescence'),
        ):
        _Age_aerial = self.Age_aerial
        _Age = self.Age
        if self.locTime.isYearBeginning :
            #trees Branches root and foliage  senescence (Kg_DM /tree /year) and stand cumul (Kg_DM /m2_soil /year)
            _sumb =  0.
            _sumr =  0.
            _LeafSenescenceByUnitAerialBiomass = (self.LitterfallLeaf / self.BiomassCarbonContent * self.Area)/ sum(_tree.Wa for _tree in self) if len(self)>0 else 0
            for _tree in self:            
                _BranchSenescence       =  k_SenBch_1 * (_tree.WBranch **k_SenBch_2) * (max(1,_Age_aerial) **k_SenBch_3)       
                _tree.BranchSenescence  = _BranchSenescence
                _sumb                   += _tree.BranchSenescence
                _rootSenescence         = k_SenRoot_1 * (_tree.Wr /(1+_tree.Wr**(1 - k_SenRoot_2))) * (_Age **k_SenRoot_3)
                _tree.RootSenescence    = _rootSenescence
                _sumr                   += _tree.RootSenescence   
                _tree.LeafSenescence    = _tree.Wa *_LeafSenescenceByUnitAerialBiomass 
            self.BranchSenescence       = _sumb / self.Area
            self.RootSenescence         = _sumr / self.Area

#Allocate carbon to Litter and soil============================================
            
    Litterfall     = var('daily litterfall (g_C /m2_soil /day)', 0)
    LitterfallStem = var('daily Stem litterfall (g_C /m2_soil /day)', 0)
    LitterfallLeaf = var('daily leaf litterfall (g_C /m2_soil /day)', 0)
    LitterfallBr   = var('daily Branch litterfall (g_C /m2_soil /day)', 0)
    LitterfallRoot = var('daily Root litterfall (g_C /m2_soil /day)', 0)
    Wood_DPM_RPM = param('DPM RPM ratio of wood components',0.),
    Leaf_DPM_RPM = param('DPM RPM ratio of dead foliage ',0.),
    Root_DPM_RPM = param('DPM RPM ratio of roots ',0.),
    Wood_Age     = param('age of dead wood components (year)',0.),
    Leaf_Age     = param('age of dead foliage (year)',0.),
    Root_Age     = param('age of dead roots (year)',0.)
    @pcs
    def pcs_AllocateLitterCarbonToSoil(self):
        '''Add compartment litter to soil carbon incoming'''
        
        if self.locTime.isYearBeginning or self.treesCount==0:
            self.LitterfallLeaf = self.LitterfallBr = self.LitterfallRoot = self.Litterfall = 0
            
        if self.locTime.isDayBeginning:

            _Day_by_Year = 365.25
            
            #add foliage Litterfall to soil carbon as foliage die
            self.soil.carbonCycle.incorporateACarbonLitter(self.LeafFall * self.BiomassCarbonContent, self.Leaf_DPM_RPM, self.Leaf_Age) 
            
            #add dead branches to soil  carbon assuming a constant input along the year
            self.soil.carbonCycle.incorporateACarbonLitter(self.BranchSenescence * self.BiomassCarbonContent / _Day_by_Year, self.Wood_DPM_RPM, self.Wood_Age)
            
            #add dead roots to soil carbon assuming a constant input along the year
            self.soil.carbonCycle.incorporateACarbonLitter(self.RootSenescence * self.BiomassCarbonContent / _Day_by_Year,self.Root_DPM_RPM, self.Root_Age)
        
            self.LitterfallLeaf += self.LeafFall * self.BiomassCarbonContent
            self.LitterfallBr   += self.BranchSenescence * self.BiomassCarbonContent / _Day_by_Year
            self.LitterfallRoot += self.RootSenescence * self.BiomassCarbonContent / _Day_by_Year
            self.Litterfall     = self.LitterfallLeaf + self.LitterfallBr + self.LitterfallRoot
           

#HYDRAULIC STATUS==============================================================
    SoilRootsWaterPotential = var('soil- roots interface water potential (MPa)')

    @pcs    
    def pcs_HydraulicStatus(self, 
        k_Rxyl_1  = param('parameter 1 in allometric relation between tree height and hydraulic resistance of the xylem'),
        k_Rxyl_2  = param('parameter 2 in allometric relation between tree height and hydraulic resistance of the xylem'), 
        ):
        '''leaf water potential estimate by a simple RC model.
        C is the water capacitance
        R is the sum of soil-root and tree resistances
        '''        
        _canopy = self.canopy
        _soilWaterPotential = self.soil.waterCycle.RootLayerWaterPotential 
        _RhydSoil = self.soil.waterCycle.RhydSoil       

        if self.W > 0 and _canopy.LAI >0.1 :
            #hydraulic resistances in soil ansd xylem (MPa m2_LAI s kg_H2O-1)   
            RhydXyl = 5000.0 + k_Rxyl_1 * self.HEIGHTmean ** k_Rxyl_2         
            Rhyd    = RhydXyl +_RhydSoil         
            #global capacitance (kg_H2O m-2__leaf MPa-1)
            C=0.005*(self.W/15.)
            _eRC  = exp(-3600./(Rhyd*C)) 
            # Foliage water potential with the soil - root equilibrium fixed between 0 and  -0.2 MPa at field capacity
            # gravitational component is corrected for the mean height of canopy foliage, assumed at z =  mean stem height and for an intercept (-0.2 MPa) as observed
            _dLWP = _soilWaterPotential - _canopy.Transpiration*Rhyd/3600.0/_canopy.LAI \
                                    + (_canopy.WaterPotential - _soilWaterPotential + _canopy.Transpiration*Rhyd/3600/_canopy.LAI) * _eRC
                                         
            _canopy.WaterPotential =  _dLWP - self.HEIGHTmean  * 0.01
            self.SoilRootsWaterPotential = (_soilWaterPotential * RhydXyl + _canopy.WaterPotential * _RhydSoil) / Rhyd
        else:
            _canopy.WaterPotential = self.SoilRootsWaterPotential = _soilWaterPotential
 
# AutotrophicRESPIRATION=======================================================
    Rm              = var('Respiration part linked to the tissues maintenance (without leaves) (g C /m2_soil /hour)')
    Rg              = var('Respiration part linked to the tissues production (growth)  (g C /m2_soil /hour)')
    R_AboveGround   = var('Part of the respiration above soil (g C /m2_soil /hour)')
    R_BelowGround   = var('Part of the respiration under soil (g C /m2_soil /hour)')
    Annual_Rg       = var('Annual growth respiration (g_C /m2_soil /year)')
    Annual_Rm       = var('Annual maintenance respiration (g_C /m2_soil /year)')
    Annual_RmLeaf   = var('Annual foliage maintenance respiration (g_C /m2_soil /year)')
    Rg_AboveGround  = var('Part of the growth respiration above soil (g C /m2_soil /hour)')
    Rg_BelowGround  = var('Part of the growth respiration under soil (g C /m2_soil /hour)')
    Tree_N          = var('Nitrogen content of the tree stand biomass(gN/m2_soil)') 
    RmLeaf          = var('maintenance respiration at 15degC (gC.m-2.h-1) - Lloyd', 0.)
    RmStem          = var('maintenance respiration of stem (gC.m-2.h-1)', 0.)
    RmBranches      = var('maintenance respiration of branches (gC.m-2.h-1)', 0.)
    RmTapRoot       = var('maintenance respiration of tapRoot (gC.m-2.h-1)', 0.)
    RmCoarseRoots   = var('maintenance respiration of coarse roots (gC.m-2.h-1)', 0.)
    RmSmallRoots    = var('maintenance respiration of small roots (gC.m-2.h-1)', 0.)
    RmFineRoots     = var('maintenance respiration of fine roots (gC.m-2.h-1)', 0.)
    RmRoots         = var('maintenance respiration of the root system (gC.m-2.h-1)', 0.)
    Rm              = var('maintenance respiration of the entire tree (gC.m-2.h-1)', 0.)

    @pcs        
    def pcs_Respiration(self,
        _RmQ10Leaf          = param('Q10 of maintenance respiration of leaves (-)'),
        _RmQ10Stem          = param('temperature effect for trunk (dimensionless)'),
        _RmQ10Branches      = param('temperature effect for Branches (dimensionless)'),
        _RmQ10roots         = param('temperature effect for roots (dimensionless)'),
        _Photo_Inhibition   = param('fraction of mitochondrial foliage respiration inhibited by light (0-1)'),
        _RmTref             = param('Q10 of maintenance respiration of leaves (-)'),                
        ):        
        '''Respiratory carbon fluxes. 
            - the model partitions the respiration between maintenance and growth components
            - it is derived from Castanea (Dufrene et al. 2005) and includes an age dependency of Palive for the stem, roots and Branches.
            - The degree of day inhibition of maintenance respiration of foliage ranges between 17 and 66pct  depending on species (Sharp et al., 1984 Brooks and Farquhar, 1985; Kirschbaum and Farquhar,
               1987). Villar et al. (1995) give a mean rate of 51pct for evergreen tree species and 62pct for deciduous tree species.
            - Here, we apply a 50pct reduction of day foliage repiration as inhibited by SW radiation.
       '''        
    #Growth respiration for the treestand (g_C /m2_soil /hour)
        if  self.WProducted>0:
            self.Rg = self.Annual_Rg * (self.GrowthIntensity / 24.0)
            self.Rg_AboveGround = self.Rg * self.WaProducted / self.WProducted 
            self.Rg_BelowGround = self.Rg - self.Rg_AboveGround
            #self.SumRg += self.Rg
        else:
            self.SumRg = self.Rg = 0
    
   #Maintenance respiration per parts of  individual trees  (g_C /m2_soil /hour) 
        for _tree in self: 
            if _tree.WStem>0:
                _WBranch=_tree.WBranch
                _Wr=_tree.Wr
                _WStem=_tree.WStem
                _LeafWeight=_tree.LeafWeight
                _WTapRoot = _tree.WTapRoot 
                _WCoarseRoot = _tree.WCoarseRoot  
                _WSmallRoot = _tree.WSmallRoot    
                _WFineRoot = _tree.WFineRoot 
                
   # the maintenance respiration is decreased from 1.0 to 0. when Tr/Trmax drops from 0.3 to 0.0  This decrease simulates the carbohydrate deprivation of Kreps cycle         
                if self.canopy.Transpirationmax>0:                
                    Link_to_Assim = 1.0/0.1* min(0.1, self.canopy.Transpiration / self.canopy.Transpirationmax) 
                else:
                    Link_to_Assim =1.0
                    
                _tree.RmStem         =  _RmTref * self._Tissue_respiration(_WStem, _tree._PaliveStem, self._NStem, _RmQ10Stem, self.microclim.TaC) * Link_to_Assim  
                _tree.RmBranches     =  _RmTref * self._Tissue_respiration(_WBranch, _tree._PaliveBranch,  self._NBranch,_RmQ10Branches,self.microclim.TaC)*Link_to_Assim
                _tree.RmTapRoot      =  _RmTref * self._Tissue_respiration(_WTapRoot, _tree._PaliveTapRoot,    self._NTapRoot,_RmQ10roots ,self.soil.carbonCycle.Ts_resp)*Link_to_Assim
                _tree.RmCoarseRoots  =  _RmTref * self._Tissue_respiration(_WCoarseRoot, _tree._PaliveCoarseRoot, self._NCoarseRoot,_RmQ10roots ,self.soil.carbonCycle.Ts_resp)*Link_to_Assim
                _tree.RmSmallRoots   =  _RmTref * self._Tissue_respiration(_WSmallRoot, _tree._PaliveSmallRoot,  self._NSmallRoot,_RmQ10roots ,self.soil.carbonCycle.Ts_resp)*Link_to_Assim
                _tree.RmFineRoots    =  _RmTref * self._Tissue_respiration(_WFineRoot,  self._PaliveFineRoot,   self._NFineRoot,_RmQ10roots ,self.soil.carbonCycle.Ts_resp)*Link_to_Assim
                _tree.RmRoots        = _tree.RmTapRoot + _tree.RmCoarseRoots + _tree.RmSmallRoots + _tree.RmFineRoots
                _tree.RmLeaf        = (1-_Photo_Inhibition* (self.microclim.SWDif+ self.microclim.SWDir)/(50 + self.microclim.SWDif+self.microclim.SWDir))*\
                                      self.canopy.Respiration / max(0.1,self.FoliageArea)  * _tree._LeafArea
                _tree.Rm             = _tree.RmStem +_tree.RmBranches + _tree.RmRoots + _tree.RmLeaf
                _tree.Rm_AboveGround   = _tree.RmStem + _tree.RmBranches + _tree.RmLeaf
                _tree.Rm_BelowGround   = _tree.RmRoots

            else:
                 _tree.Rm = _tree.RmLeaf = _tree.Rg = self.R_AboveGround = self.R_BelowGround =0
                 
   #stand Rm (g_C /m2_soil /hour)
        self.RmRoots = sum(_tree.RmRoots for _tree in self)/self.Area
        self.RmBranches = sum(_tree.RmBranches for _tree in self)/self.Area
        self.RmStem = sum(_tree.RmStem for _tree in self)/self.Area
        self.RmLeaf = sum(_tree.RmLeaf for _tree in self)/self.Area
        self.RmTapRoot     = sum(_tree.RmTapRoot for _tree in self)/self.Area
        self.RmCoarseRoots = sum(_tree.RmCoarseRoots for _tree in self)/self.Area
        self.RmSmallRoots   = sum(_tree.RmSmallRoots for _tree in self)/self.Area
        self.RmFineRoots    = sum(_tree.RmFineRoots for _tree in self)/self.Area  
        self.Rm    = sum(_tree.Rm for _tree in self)/self.Area
        self.Tree_N=sum(_tree.N for _tree in self)/self.Area


    def _Tissue_respiration(xxx, Wi,Palivei,Ncontent,RmQ10,T) :
        '''Maintenance respiration of organs at 15C based on Castanea formulation (Dufrene et al 2005) 
            i.e: Rmi=Wi*Palivei*[Ni]*RmTref*RmQ10^(Ti-15)/10
            Wi, the organ biomass (Kg_DM/m2_soil)
            Palivei, proportion of living cells in organ (Kg_livingCells/Kg_DM)
            [Ni], organ nitrogen content (g_N/ Kg_livingCells ou mg_N/g_livingCells)
            RmTref, maintenance respiration at Tref (mol_CO2/g_N/h)
            RmQ10, Q10 of maintenance respiration (dimensionless)
        '''

        Tref=15.0
        Walive = Palivei*Wi     #Kg_LivingCells/m2_soil
        return Walive*Ncontent* RmQ10 ** ((T - Tref) / 10.0)

#Stress index==================================================================
    IStress = var('Stress index  used for root/shoot allocation ([0-1])', 0.)
    
    @pcs    
    def pcs_HydricStress(self, 
        _annual_Transpiration = private('annual cumul of transpiration with and without hydric stress control on stomata', ELT), 
        ):
            
        if self.locTime.isYearBeginning or self.treesCount ==0:
            _annual_Transpiration.effective = 0
            _annual_Transpiration.unStress  = 0

        #cumulate transpiration 
        _canopy = self.canopy
        if _canopy.Transpiration > 0 and _canopy.LAI>0 and _canopy.Transpirationmax>0 and _canopy.Gsa>0:
            _annual_Transpiration.effective +=  _canopy.Transpiration
            _annual_Transpiration.unStress  +=  _canopy.Transpirationmax
        
        if self.locTime.isYearEnd :  
            if _annual_Transpiration.unStress>0:
                self.IStress = max(0, 1 - (_annual_Transpiration.effective / _annual_Transpiration.unStress))
            else:
                self.IStress = 0
#NPP partitioning= and tree growth=============================================
    AllocRoot       = var('fraction of annual biomass increment allocated to roots [0-1] (Kg_DM /Kg_DM)')
    SumRg           = var('Annual cumulated Rg') 
    mortalityTrees  = eltIn(Trees) 
    NbDeadTrees     = var('Number of dead Trees ()')
    WDeadTrees      = var('Biomass of dead Trees (Kg_DM/m2_soil)')

    @pcs    
    def pcs_CarbonFluxesPartition(self, 
        kIstress_1  = param('coefficient 1 of stress index expression'),  
        kIstress_2  = param('coefficient 2 of stress index expression'),  
        kIstress_3  = param('coefficient 3 of stress index expression'), 
        RgCost      = param('carbon growth cost  (g_C /g_C)'), 
        _annualSum  = private('annual cumul of carbon fluxes', ELT),
        ):

        if self.locTime.isYearBeginning or self.treesCount==0:
            _annualSum.Assimilation = 0
            _annualSum.Rm           = 0
            self.SumRg              = 0 
            self.WDeadTrees         = 0
            self.mortalityTrees = [] 

        ##Annual integration of NPP components of the canopy layer
        _annualSum.Assimilation +=  self.canopy.Assimilation
        _annualSum.Rm +=  self.Rm
        self.SumRg +=  self.Rg
  
        if self.locTime.isYearEnd: 
             
            self.AllocRoot = kIstress_1 * exp(kIstress_2 * self.IStress ** kIstress_3) # # Root carbon allocation. NB To add when  coppicing: * exp ( Wr/Wa - WrWaref ) ]**-b
        ##Partitionning the carbon assimilation, maintenance respiration and growth respiration among trees 
            if len(self)>0 :
                if sum(_tree.LeafWeight for _tree in self) > 0:
                    annual_Assimilation_By_LeafWeight = _annualSum.Assimilation * self.Area  / sum(_tree.LeafWeight for _tree in self)
                    annual_Rm_By_Tree_N               = _annualSum.Rm / max(1.0,self.Tree_N)
                    annual_Rg_By_W                    = self.SumRg / self.W
                else :
                    annual_Assimilation_By_LeafWeight = 0
                    annual_Rm_By_Tree_N = 0
                    annual_Rg_By_W = 0
            else : 
                annual_Assimilation_By_LeafWeight = 0
                annual_Rm_By_Tree_N = 0
                annual_Rg_By_W = 0

            for _tree in self :
                tree_Annual_Assimilation = _tree.LeafWeight * annual_Assimilation_By_LeafWeight
                tree_Annual_Rm           = _tree.N * annual_Rm_By_Tree_N
                tree_Annual_Rg           = _tree.W * annual_Rg_By_W
                tree_Wproducted          = (tree_Annual_Assimilation - tree_Annual_Rm - tree_Annual_Rg)/self.BiomassCarbonContent 

              ## Death of a tree when its annual balance is <0
                if tree_Wproducted <= 0:
                    self.mortalityTrees += [_tree]
                    self.WDeadTrees     += _tree.W/self.Area
                       
                    # The biomass of dead tree parts is put into the soil 
                    self.soil.carbonCycle.incorporateACarbonLitter((_tree.WStem/self.Area) * self.BiomassCarbonContent, self.Wood_DPM_RPM,  self.Wood_Age )
                    self.soil.carbonCycle.incorporateACarbonLitter((_tree.LeafWeight/self.Area) * self.BiomassCarbonContent, self.Leaf_DPM_RPM, self.Leaf_Age)
                    self.soil.carbonCycle.incorporateACarbonLitter((_tree.WBranch)/self.Area * self.BiomassCarbonContent, self.Wood_DPM_RPM, self.Wood_Age)
                    self.soil.carbonCycle.incorporateACarbonLitter((_tree.WTapRoot/self.Area) * self.BiomassCarbonContent, self.Root_DPM_RPM,  self.Root_Age)
                    self.soil.carbonCycle.incorporateACarbonLitter(((_tree.WSmallRoot + _tree.WCoarseRoot )/self.Area) * self.BiomassCarbonContent, self.Root_DPM_RPM, self.Root_Age)
                    self.soil.carbonCycle.incorporateACarbonLitter((_tree.WFineRoot/self.Area) * self.BiomassCarbonContent, self.Root_DPM_RPM,  self.Root_Age)              
                     # optional: output a file of dead trees  
#                    x=str(self.locTime.Y) + str(",") +str(_tree.DBH) + str(",") + str(_tree.WaProducted) + str(",") + str(_tree.WrProducted) + str(",") + str(_tree.W) \
#                        + str(",")  +  str(_tree.LeafWeight) + str(",") + str(_tree.N) + str(",")  \
#                        + str(tree_Wproducted)  + str(",") + str (tree_Annual_Assimilation)   + str(",") + str(tree_Annual_Rm)\
#                        + str(",") + str(tree_Annual_Rg)
#                    paraDeadTreeFilePath = os.path.join(basePath, '..', '..', 'Output_files', 'DeadTrees.csv')
#                    with open(paraDeadTreeFilePath, 'a') as f:
#                        f.write('%s\n' % x)
#                    f.closed
              
                    tree_Wproducted = 0
                    self._exclude_tree(_tree)                          
                self.NbDeadTrees = len( self.mortalityTrees) #Number of dead trees
                
            ## Allocation of NPP to root and aboveground parts 
                _tree.WrProducted = tree_Wproducted * self.AllocRoot
                _tree.WaProducted = tree_Wproducted - _tree.WrProducted
               
            ##Individual tree growth 
                _tree.update()
#                #optional: output a file of live trees 
#                r = str(self.locTime.Y) + str(",") +str(_tree.DBH) +  str(",") + str(_tree.Wa) +  str(",") + str(_tree.WBranch) \
#                + str(",")  +  str(_tree.WCoarseRoot) + str(",") + str(_tree.WStem)   + str(",") +  str(_tree.LeafWeight) + str(",") + \
#                str(tree_Wproducted)  + str(",") + str (tree_Annual_Assimilation)   + str(",") + str(tree_Annual_Rm)\
#                 + str(",") + str(tree_Annual_Rg)
#                paraTreeFilePath = os.path.join(basePath, '..', '..', 'Output_files', 'LiveTrees.csv')
#                with open(paraTreeFilePath,'a') as e:
#                    e.write('%s\n' % r)
#                e.closed

            ##Individual tree Rg respiration (allocated to  the  next year). 
            self.Annual_Rg = (_annualSum.Assimilation - _annualSum.Rm ) * RgCost/(1+RgCost)
            
            ## update the tree stand statistics
            self.pcs_SetSizes() 


#BIOMASSES AND SIZES===========================================================
    density     = var('number of trees per hectare (ha-1)')
    densityMax  = var('number of trees per hectare triggering mortality (ha-1)')
    BasalArea   = var('Basal Area (m2/m2_soil)')
    W           = var('biomass (Kg_DM /m2_soil)')
    WFoliage    = var('biomass od the tree foliage (kg dm.m-2)')
    Wa          = var('aerial biomass (Kg_DM /m2_soil)')
    Wr          = var('root biomass (Kg_DM /m2_soil)')
    WStem       = var('Stem biomass (Kg_DM /m2_soil)')
    WTapRoot    = var('Taproot biomass (Kg_DM /m2_soil)')
    WCoarseRoot = var('Coarse root biomass (Kg_DM /m2_soil)')
    WSmallRoot  = var('Small root biomass (Kg_DM /m2_soil)')
    WFineRoot   = var('Fine root biomass (Kg_DM /m2_soil)')
    WProducted  = var('annual increment of biomass (Kg_DM /m2_soil /year)')
    WaProducted = var('annual increment of aerial biomass (Kg_DM /m2_soil /year)')
    WrProducted = var('annual increment of root biomass (Kg_DM /m2_soil /year)')
    DBHdom      = var('mean tree DBH of the 100 bigger trees by hectare (cm)')
    Heightdom   = var('mean tree height of the 100 bigger trees by hectare (m)')
    treesCount  = var('trees number')
    DBHmean     = var('Mean diameter at breast height (cm)')
    DBHsd       = var('Standard deviation of diameter at breast height (cm)')
    DBHquadratic = var('Quadratic mean of diameter at breast height (cm)')
    Heightmean  = var('Mean height (cm)')
    Heightsd    = var('Standard deviation of height (m)')
    PROD_VOL    = var('Iimber production (m3.ha-1.y-1)')
    RDI         = var('Relative density index ()')

    @pcs    
    def pcs_SetSizes(self):
        '''Dimensions integrated from trees list'''
        Trees.update(self)
        #Biomass and biomass increments by soil area unit (kg_DM /m2_soil)
        self.Wa             = sum(_tree.Wa for _tree in self) / self.Area 
        self.WaProducted    = sum(_tree.WaProducted for _tree in self) / self.Area 
        self.Wr             = sum(_tree.Wr for _tree in self)/ self.Area
        self.WrProducted    = sum(_tree.WrProducted for _tree in self)/ self.Area

        self.W = self.Wa + self.Wr
        self.WProducted     = self.WaProducted + self.WrProducted
        
        self.WStem          = sum(_tree.WStem for _tree in self)/ self.Area
        self.WBranch        = sum(_tree.WBranch for _tree in self)/ self.Area
        self.WFoliage       = sum(_tree.LeafWeight for _tree in self)/ self.Area
        self.WTapRoot       = sum(_tree.WTapRoot for _tree in self)/ self.Area 
        self.WCoarseRoot    = sum(_tree.WCoarseRoot for _tree in self)/ self.Area  
        self.WSmallRoot     = sum(_tree.WSmallRoot for _tree in self)/ self.Area   
        self.WFineRoot      = sum(_tree.WFineRoot for _tree in self)/ self.Area   
        self.treesCount     = len(self)
        self.DBHmean        = sum(_tree.DBH for _tree in self) / self.treesCount if self.treesCount>0 else 0
        self.DBHsd          = (sum((_tree.DBH - self.DBHmean)**2 for _tree in self) / self.treesCount)**0.5 if self.treesCount>0 else 0
        self.DBHquadratic   = (sum(_tree.DBH**2 for _tree in self)/self.treesCount)**0.5 if self.treesCount>0 else 0
        self.Heightmean     = sum(_tree.Height for _tree in self) / self.treesCount if self.treesCount>0 else 0
        self.Heightsd       = (sum((_tree.Height - self.HEIGHTmean)**2 for _tree in self) / self.treesCount)**0.5 if self.treesCount>0 else 0
        self.density        = self.treesCount*10000./self.Area
        self.BasalArea      = sum(_tree.BasalArea for _tree in self)/self.Area*10000     
        self.PROD_VOL       = sum(_tree.Prod_vol for _tree in self)/self.Area*10000  
           
        if self.treesCount>0:
#Dominant trees (100 thicker trees by hectare)
            _Ndom = round(100 * self.Area / 10000., 0) #number of dominant trees in the sample
            _biggerTrees = sorted(self,  key = (lambda tree: tree.DBH), reverse = True)[:int(_Ndom)]
#RDI Calculation                               
            self.densityMax     =self.ST_alpha/(self.DBHquadratic**self.ST_beta)
            self.RDI            = self.density/self.densityMax
            
            #Dimension of the dominant trees (100 bigger by hectare)
            if _Ndom < self.treesCount:    
                self.DBHdom     =  sum(_tree.DBH for _tree in _biggerTrees)/_Ndom
                self.Heightdom  =  sum(_tree.Height for _tree in _biggerTrees)/_Ndom
            else:
                self.DBHdom     = self.DBHmean
                self.Heightdom  = self.Heightmean     

            self.canopy.WAI     = self.shape_factor * self.density* self.HEIGHTmean * self.DBHmean/100 * math.cos(75*math.pi/180.)/self.Area \
                               + self.WBranch * 4 *math.cos(45*math.pi/180.)/ (1000*self.wood_density * math.pi*max (0.005,self.DBHmean/5/100))  


            
        else :
            self.DBHdom     = 0
            self.HEIGHTdom  = 0
            self.canopy.WAI = 0

#==============================================================================            
# Tree regeneration  - plantation. =============================================
    @pcs
    def pcs_TreeStandInstallation(self, 
        initialTreesAge             = param('Age of trees to install'), 
        initialTreesDimensionsFile  = param('file path of trees dimensions', 'E:\Data\GO+ PCS 26.14 generic\Applications\BRAY\C1983.csv'), 
        initialTreesDensity         = param('trees density (tree /ha)'), 
        initialTreesDBH_mean        = param('mean of initial trees  Wa(Kg_DM /tree)')  , 
        initialTreesDBH_std         = param('st. dev. of initial trees  Wa(Kg_DM /tree)'), 
        ):

        #create the trees
        if initialTreesDimensionsFile !=  '':
            self._install_trees_from_file_definition(initialTreesAge, initialTreesDensity, initialTreesDimensionsFile )
        else:
            if initialTreesDensity >0:
                self._install_trees_from_gauss_distribution( initialTreesAge, initialTreesDensity,  initialTreesDBH_mean,  initialTreesDBH_std)
        
        self.thinnings          = 0        
        self.seedingYear     = self.locTime.Y - initialTreesAge - 3
        self.lastThinningYear   = self.locTime.Y - initialTreesAge - 15
        self.FirstThinning      = False 
       
    def _install_trees_from_gauss_distribution(self, 
       trees_Age, 
       initialTreesDensity,  
       trees_DBH_mean, 
       trees_DBH_std, 
       ):
        '''Do a tree plantation at the specified _germinationYear  
            trees dimensions created from DBH with a Gaussian distribution, lower limit  being set at 0.1 x mean value. 
        '''

        _nbTrees = int(initialTreesDensity* self.Area*1e-4)
        random.seed(_nbTrees)
        _trees_dim = []
        for i in range(_nbTrees):
            _tree_DBH    = max(random.gauss(trees_DBH_mean, trees_DBH_std), 0.1*trees_DBH_mean)
            _trees_dim   += [(float(_tree_DBH))]
        self._include_trees(trees_Age,_trees_dim)
        
#==============================================================================
    def _install_trees_from_file_definition(self, trees_Age, nbTreesHa,
        treesFileName = '', 
        ):
        '''Initialisation step'''
        #Read trees file definition content
        _file   = open(treesFileName, 'r')
        _lines  = _file.readlines()
        _file.close()
        _trees_dim = []
        _line=[0, ]*len(_lines)
        for i in  range(len(_lines)):
            _line[i]= _lines[i].split(',')
        s=range(len(_line))
        for i in  s[1:]:
            _sDBH        =_line[i][1] 
            _trees_dim  += [( float(_sDBH))] 
        self.treesCount  = len(_trees_dim)        
        self._include_trees(trees_Age,_trees_dim)

#==============================================================================
         
    def _include_trees(self, trees_Age, trees_list =[(10, 3), ]):
        '''include trees of stand from their individual DBH value (cm) 
        ''' 
        if len(self)>0 :
            raise Exception("treeStand ELT don't support the installation of trees if not empty")
        self.Age                = trees_Age-1
        self._germinationYear   = self.locTime.Y -self.Age -1
        self.ClumpAge           = 0.
        self.Age_aerial         = self.Age
        for _t_dim in trees_list:
            _tree           = TreeSizes(self)
            _tree.locTime   = self.locTime         
            _tree.Age       = trees_Age-1
               
            if self.Species =='Fsylvatica':
                _tree.DBH       = _t_dim
                _m              = 1.218
                _K              = 67.3 
                _Cm             = math.exp((1+_m)*(1-math.log10(1+_m)))
                _H0             = _K*math.exp(-((math.log10(_K/1.3))**(-_m)+(0.4*_m*_Cm/_K)*(_tree.Age-5.0))**(-1.0/_m))
                _alpha          = _H0 - 1.3 + math.pi*0.412*_tree.DBH
                _tree.Height = 1.3+(_alpha - (_alpha**2 - 4*math.pi*0.412*0.98764*(_H0 - 1.3)*_tree.DBH)**0.5)/(2*0.98764)
                C_0             = self.k_DBH_1 + 2.39e-4 * 30 - 4.68e-6 * self.sunLocal.Altitude
                C_1             = self.k_DBH_2
                C_2             = self.k_DBH_3 + 4.06e-4 *self.Age
                _tree.Wa = C_0 * _tree.DBH**C_1 * _tree.Height**C_2
                _tree.Wr = _tree.Wa /3.0
            
            else :              #Used for coniferous      
                _tree.DBH   = _t_dim 
                _tree.Wa    = (_tree.DBH/(self.k_DBH_1*_tree.Age**self.k_DBH_3))**(1/self.k_DBH_2)
                _tree.Wr    = _tree.Wa /3.0
                
            _tree.update()
            self.append(_tree)
        self.pcs_SetSizes() 

    #Create pre existing foliage cohorts and fix their Bud Burst date 
        if self.Species=='Ppinaster':
            if trees_Age < self.NbCohort : 
                nbcohort = int(trees_Age)
            else :
                nbcohort = int(self.NbCohort)
            for _y in range(nbcohort):
                _cohort = LeavesCohort()              
                _cohort.Year =  self.locTime.Y_start - _y - 1
                _cohort.treeStand = self
                _cohort.locTime = self.locTime  
                _cohort.cohortWeightMaxOfSoil=sum(_tree.LeafWeight /nbcohort for tree in self) / self.Area * (1-_y/(trees_Age*(trees_Age-1)/2))

                if self.locTime.isSimulBeginning: 
                    _cohort.DateOfBB = 136 - int((_y+1)*365.25) 
                else:
                    _cohort.DateOfBB = self.locTime.Now + (136 - int((_y+1)*365.25))
                self.cohorts.append(_cohort)    
                
        elif self.Species=='DouglasFir':
            if trees_Age < self.NbCohort : 
                nbcohort = int(trees_Age)
            else :
                nbcohort = int(self.NbCohort) 
            for _c in range(nbcohort):
                _cohort = LeavesCohort()              
                _cohort.Year =  self.locTime.Y_start - _c - 1
                _cohort.treeStand = self
                _cohort.locTime = self.locTime   
                _cohort.cohortWeightMaxOfSoil=sum(_tree.LeafWeight /nbcohort for tree in self) / self.Area * (1-_c/(trees_Age*(trees_Age-1)/2))*7/6 # accounts for ajusting to the right LAI value at time t=0
                
                if self.locTime.isSimulBeginning: 
                    _cohort.DateOfBB = 136 - int((_c+1)*365.25) 
                else:
                    _cohort.DateOfBB = self.locTime.Now + (136 - int((_c+1)*365.25))
                self.cohorts.append(_cohort) 


    def _exclude_tree(self, tree_to_remove):
        self.remove(tree_to_remove)
        self.pcs_SetSizes() 

