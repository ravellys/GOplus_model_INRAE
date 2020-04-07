from goBases import * 		#Windows
#from ...goBases import * 	#LINUX


from ForestElements.Canopy.mdlCanopy import SunShadeCanopy as Canopy


class ugCompartment(ELT):

    #Biomass
    W = var('dry biomass (Kg_DM /m2_soil)', 0.) #variable
    AboveGroundFraction = param('fraction of the compartment biomass above ground')
    BiomassCarbonContent = param('carbon weight fraction of dry biomass (Kg_C /Kg_DM)')

    #Growth
    WGrowth = var('dry biomass production (Kg_DM /m2_soil /day)',0.0) #variable
    WGrowthMax = param('Maximal annual biomass production (Kg_DM /annual_growth_cycle)')  

    #Growth pcs_Phenology
    GrowthStart  = var('day of year of growth start (DOY [1-366])',0.) #variable
    HeatSum_GrowthStart = param('Annual heat-sum to start growth (deg day)')
    GrowthLength = param('Growth length of leaf (day)')     #  CF Delzon 2001 memoire DEA, Cochard, 1988 memoire DEA et loustau et COchard ASF 1991,
                                                                 # Stahl, memoire DEA 2008; CARBOEUROPE data (Lopez memoire BTS)
                                                                                                                            
    #Mortality parameters
    LitterFall = var('dry biomass litterfall (Kg_DM /m2_soil /day)',0.) #variable
    k_MortalityTemp = param('Mortality temperature threshold (deg_C)')
    k_MortalityTempRate = param('Temperature mortality rate (Kg_DM /Kg_DM /day)')
    k_MortalitySMD = param('Mortality SMD  threshold')
    k_MortalitySMDRate = param('SMD mortality rate (Kg_DM /Kg_DM /day)')
    k_MortalityDOY = param('DOY threshold [1-365]')
    k_MortalityDOYRate = param('DOY mortality rate (Kg_DM /Kg_DM /day)')
    DPM_RPM_rate= param('rate of DPM on RPM fraction of litterfall (Kg_DM /Kg_DM)')
    LitterFallAge = param('mean litterfall age (Kg_DM /Kg_DM)')

    #Non structural carbohydrate pools
    Cpool = var('non structural carbohydrate pool (g_C /m2_soil)',0.) #variable

    #pcs_Respiration parameters
    RmQ10 = param('Q10 factor of maintenance respiration response to temperature')
    Rm15 = param('Maintenance respiration at 15degC (g_C /Kg_Dm /hour)') 
    RgCost = param('respiration cost of growth (gC /g_C)')
    kW_Rm = param('power of biomass in maintenance respiration equation -   (1: proportionnal to volume,  0.666 proportional to surface in case of sphere)')


class UnderStorey(ELT):
    '''Represents the understorey layer (typicaly  Molinea coerulea)'''

    #Outer elements
    locTime = eltOut('LocTime element')
    sunLocal =eltOut('SunLocal element')
    microclim = eltOut('Upper MicroClimate element')
    microclim_under =eltOut('Under MicroClimate element')
    soil = eltOut('Soil element')
    LitterFall = var('dry biomass litterfall (Kg_DM /m2_soil /day)', 0.) 
    
    #Inner model elements
    @eltIn
    class foliage(ugCompartment):
        W = var('dry biomass (Kg_DM /m2_soil)', 0.) 
        AboveGroundFraction = param('fraction of the compartment biomass above ground')
        WGrowthMax          = param('Maximal annual biomass production (Kg_DM /annual_growth_cycle)')
        T_Limiting_Growth   = param('Threshold of temperature limiting growth (degC)',0.)
        SMD_Limiting_Growth = param('Threshold of soil moisture deficit limiting growth',0.)
        k_MortalityTemp     = param('Mortality temperature threshold (deg_C)')
        k_MortalityTempRate = param('Temperature mortality rate (Kg_DM /Kg_DM /day)')
        k_MortalitySMD      = param('Mortality SMD  threshold')
        k_MortalitySMDRate  = param('SMD mortality rate (Kg_DM /Kg_DM /day)')
        k_MortalityDOY      = param('DOY threshold [1-365]')
        k_MortalityDOYRate  = param('DOY mortality rate (Kg_DM /Kg_DM /day)')
        Cpool               = var('non structural carbohydrate pool (g_C /m2_soil)',5.) 
    @eltIn
    class roots(ugCompartment):
        W = var('dry biomass (Kg_DM /m2_soil)', 0.1) 
        AboveGroundFraction = param('fraction of the compartment biomass above ground')
        WGrowthMax          = param('Maximal annual biomass production (Kg_DM /annual_growth_cycle)')
        T_Limiting_Growth   = param('Threshold of temperature limiting growth (degC)',0.)
        SMD_Limiting_Growth = param( 'Threshold of soil moisture deficit limiting growth',0.)
        k_MortalityTemp     = param('Mortality temperature threshold (deg_C)')
        k_MortalityTempRate = param('Temperature mortality rate (Kg_DM /Kg_DM /day)')
        k_MortalitySMD      = param('Mortality SMD  threshold')
        k_MortalitySMDRate  = param('SMD mortality rate (Kg_DM /Kg_DM /day)')
        k_MortalityDOY      = param('DOY threshold [1-365]')
        k_MortalityDOYRate  = param('DOY mortality rate (Kg_DM /Kg_DM /day)')
        Cpool               = var('non structural carbohydrate pool (g_C /m2_soil)',25.)

    @eltIn
    class perennial(ugCompartment):
        W = var('dry biomass (Kg_DM /m2_soil)', 0.05) 
        AboveGroundFraction = param('fraction of the compartment biomass above ground')
        WGrowthMax          = param('Maximal annual biomass production (Kg_DM /annual_growth_cycle)',0.)
        T_Limiting_Growth   = param('Threshold of temperature limiting growth (degC)',0.)
        SMD_Limiting_Growth = param('Threshold of soil moisture deficit limiting growth')
        k_MortalityTemp     = param('Mortality temperature threshold (deg_C)')
        k_MortalityTempRate = param('Temperature mortality rate (Kg_DM /Kg_DM /day)')
        k_MortalitySMD      = param('Mortality SMD  threshold')
        k_MortalitySMDRate  = param('SMD mortality rate (Kg_DM /Kg_DM /day)')
        k_MortalityDOY      = param('DOY threshold [1-365]')
        k_MortalityDOYRate  = param('DOY mortality rate (Kg_DM /Kg_DM /day)')
        Cpool               = var('non structural carbohydrate pool (g_C /m2_soil)',25.)

    @eltIn
    class canopy(Canopy):
        
        pcs_StomatalConductance = pcs(Canopy.pcs_StomatalConductance, 
            g_stom_Max = param('maximal stomatal conductance (m/s)'), 
            k_SWabs_P50 = param('Leaf solar radiation absorded for 50%  of stomatal conductance ponderation (W /m2_LAI)') ,  
            k_VPD_P100 = param('VPD that start to close stomata (Pa)'), 
            k_VPD_Curv = param('Curvature parameter of VPD ponderation of stomatal conductance (-)'), 
            k_Yleaf_0= param('parameter 1 of leaf water potential ponderation of stomatal conductance (MPa)'), 
            k_Yleaf_1 = param('parameter 2 of leaf water potential ponderation of stomatal conductance (-)'), 
            k_time_P50 = param('ponderation of time response to stationnary state of stomatal conductance ]0-1]'), 
            k_CO2 = param('response to a doubling of CO2 concentration from 350 to 700 ppm, Medlyn et al. 2001, New Phytol.'), 
            )
    
        pcs_ShortWaveBalance = pcs(Canopy.pcs_ShortWaveBalance, 
            rho_l = param('Leaf reflection coefficient for shortwave (_)'), 
            theta_l  = param('Leaf transmissivity for shortwave (_)'), 
            )
    
        pcs_EnergyBalance = pcs(Canopy.pcs_EnergyBalance, 
            kLAI1_LW_Int = param('parameter 1 of longwave radiation interception (-)'), 
            kLAI2_LW_Int = param('parameter 2 of longwave radiation interception (-)'), 
            Emissivity = param('emissivity'), 
            )
            
        pcs_CanopyRainInterception = pcs(Canopy.pcs_CanopyRainInterception, 
            kRainInt_LAI = param('parameter of rain interception by leaf (-)'), 
            SurfaceWaterStorageCapacity = param('water storage capacity by leaf area index(Kg_H2O /m2_leafAreaIndex)'), 
            )

        pcs_AssimilationFarquhar = pcs(Canopy.pcs_AssimilationFarquhar, 
            Vcmax_25 = param('Vcmax at TCref, expressed on a one-sided leaf area basis (mol_CO2 /m2_leaf /s))'), 
            Ea_Vcmax = param('Activation energy for Vcmax (J /mol)'),  
            Jmax_25 = param('Jmax at TCref, expressed on a one-sided leaf area basis (mol_e /m2_leaf /s'),
            Ha_Jmax = param('Activation energy for Jmax (J /mol)'),  
            Hd_Jmax = param('Deactivation energy for Jmax (J /mol)'),  
            alpha = param('Quantum yield of electron transport (mol_e /mol_photon_absorbed). \
                Litterature value obtained on SW intercepted need to be corrected for leaf absorbance'), 
            Rd_25 = param('Dark leaf respiration at 25 degC (mol_CO2 /m2_LAI /s)'),
            )

    def update(self):
        '''hourly update
        '''
        #SIMULATION INITIALISATIONS
        if self.locTime.isSimulBeginning:
            #connect the inner ELT 
            self.canopy.locTime = self.locTime
            self.canopy.sunLocal = self.sunLocal
            self.canopy.microclim = self.microclim
            self.canopy.microclim_under = self.microclim_under
            self.canopy.soil = self.soil
            for _cpt in (self.foliage, self.roots,  self.perennial):
                _cpt.Cpool = 50
            self.pcs_AllometricDimensions()
        
        if self.locTime.isYearBeginning:
            self.LitterFall = 0
            
        #Canopy processes
        self.canopy.update()
        
        #Water balance processes
        self.pcs_HydraulicStatus()
        self.pcs_Respiration()

        #plantdevelopment 
        self.pcs_Phenology()
        self.pcs_Growth()
        self.pcs_AllometricDimensions()
        self.pcs_AllocateLitterCarbonToSoil()


    #DIMENSIONS ALLOMETRICALY LINKED TO COMPARTMENT BIOMASS
    #vars
    HEIGHTmean   = var('height (m)')
    density = private('plant per hectare (plant /ha)', 3000.) #number of plants per ha.. Fixed.Used only for caculating aerodynamic parameters.
    
    @pcs    
    def pcs_AllometricDimensions(self, 
        SLA = param('specific leaf area (m2_LAI /Kg_DM)'), 
        Height_max = param('maximal height (m)'), 
        kAerialWeight_Height = param('allometric coefficient of relation between aerial weight and height'), 
        ):
        '''Evaluate dimensions  allometricaly linked to compartment biomass'''
        
        #LAI  (m2_LAI /m2_soil)
        self.canopy.LAI = SLA * self.foliage.W 

        #Height (m)
#            self.HEIGHTmean = Height_max * (1 - exp(- kAerialWeight_Height * self.perennial.W * self.perennial.AboveGroundFraction))
        self.HEIGHTmean = Height_max * (1 - exp(- kAerialWeight_Height * self.foliage.W ))

        #density used for aerodynamic dimension evaluation
        self.density= 5000  

    
    @pcs
    def pcs_HydraulicStatus(self,
        k_Rxyl_1  = param('parameter 1 in allometric relation between plant height and hydraulic resistance of the xylem', 0.), 
        k_Rxyl_2  = param('parameter 2 in allometric relation between plant height and hydraulic resistance of the xylem', 0.)):
        '''leaf water potential estimate by a simple RC model.
        C is the wter capacitance - supposed to be connected on foliage
        R is the sum of the resistance of soil and plant
        '''
        _canopy = self.canopy
        _soilWaterPotential = self.soil.waterCycle.RootLayerWaterPotential
        if _canopy.LAI>0.0001:

            #soil leaf hydraulic resistance (MPa m2_leaf s kg_H2O-1)
            Rhyd = 1000 + k_Rxyl_1*self.HEIGHTmean**k_Rxyl_2 #80000
            #Capacitance (kg_H2O m-2__leaf MPa-1)
            C=0.01#0.14

            _eRC = exp(-3600/(Rhyd*C))

            #new leaf water potentiel
            _canopy.WaterPotential = (_soilWaterPotential - _canopy.Transpiration*Rhyd/3600.0/_canopy.LAI)*(1-_eRC)+_canopy.WaterPotential *_eRC

        else:
            _canopy.WaterPotential = _soilWaterPotential

    # RESPIRATION
    Rm = var('maintenance respiration (without leaves) (g_C /m2_soil /hour)')
    Rg = var('growth respiration (g_C /m2_soil /hour)')
    R_AboveGround = var('aboveground part of respiration  (g_C /m2_soil /hour)')
    R_UnderGround = var('underground part of respiration (g_C /m2_soil /hour)')
    
    @pcs    
    def pcs_Respiration(self):
        '''Respiratory carbon fluxes.
            - the model partitions respiration between maintenance and growth components
            - calculates the two respiration components  for each compartment (foliage, roots, perennial)(g_C /m2_soil /hour)
            - distribute between aboveGround and underground repiration 
            - decrease carbon pool
        '''
        
        #initialisation
        (self.Rm, self.Rg,  self.R_AboveGround,  self.R_UnderGround) = (0, 0, 0, 0)

        #Evaluation of respiration components by compartment. Cumuls on maintenance/growth and AboveGround/UndeGround  fractions
        for _cpt in (self.foliage, self.roots, self.perennial):
            #maintenance respiration. For above and under ground parts , the temperature of air or of soil are used respectively
            _cpt_Rm_A = _cpt.AboveGroundFraction * (_cpt.W +_cpt.Cpool/(_cpt.BiomassCarbonContent))  * _cpt.Rm15 * _cpt.RmQ10 ** ((self.microclim.TaC - 15.0) / 10.0) 

            _cpt_Rm_U = (1. - _cpt.AboveGroundFraction) * (_cpt.W +_cpt.Cpool/(_cpt.BiomassCarbonContent ))  * _cpt.Rm15 * _cpt.RmQ10 ** ((self.soil.carbonCycle.Ts_resp - 15.0) / 10.0) 
            self.Rm += _cpt_Rm_A +_cpt_Rm_U

            # growth respiration
            _cpt_Rg =  (_cpt.WGrowth / 24.0) * _cpt.BiomassCarbonContent * _cpt.RgCost
            self.Rg += _cpt_Rg

            #above and under ground respiration parts
            self.R_AboveGround += _cpt_Rm_A + _cpt_Rg * _cpt.AboveGroundFraction
            self.R_UnderGround += _cpt_Rm_U + _cpt_Rg * (1-_cpt.AboveGroundFraction )

            #respiration is withdrawn from the available Cpool
            _cpt.Cpool -=  (_cpt_Rm_A  + _cpt_Rm_U  + _cpt_Rg)


    #PHENOLOGY
    @pcs    
    def pcs_Phenology(self, 
        _HeatSum = private('temperature sum from year beginning (deg day)', ELT), 
        ):
        ''' For each compartment, determine when cumulative temperature reach the  level to start growth
        '''

        #update the heat sums used for phenology outbreak
        if self.locTime.isYearBeginning:
            _HeatSum.air = 0
            _HeatSum.soil = 0
            for _cpt in (self.foliage, self.roots,  self.perennial):
                _cpt.GrowthStart = 9999
        
        _HeatSum.air  += self.microclim.TaC / 24.0
        _HeatSum.soil += self.soil.carbonCycle.Ts_resp / 24.0
        
        #daily test phenology start
        if self.locTime.isDayEnd:
            for (_cpt, _HeatSum) in ((self.foliage, _HeatSum.air), (self.roots, _HeatSum.soil), (self.perennial, _HeatSum.air)):
                if _HeatSum >= _cpt.HeatSum_GrowthStart and _cpt.GrowthStart > self.locTime.DOY :
                    _cpt.GrowthStart = self.locTime.DOY


    
    @pcs
    def pcs_Growth(self, 
        k_Alloc_P = param('Allocation rate to perennial [0-1]'), 
        k_Alloc_F = param('Allocation rate to perennial [0-1]'), 
        _Daily    = private('daily variables', ELT), 
        ):
        ''' For eah compartment, determine growth components:
            - GPP allocation to carbon pool, use of it for
            - Growth (dry biomass production)
            - Literfall production
            - new biomass
        '''

        #Each year add inconditionnality a small amount in Cpool (gC.m-2) to account for lateral advection of seeds and propagules
        if self.locTime.isYearBeginning:
            for _cpt in (self.foliage, self.roots,  self.perennial):
                _cpt.Cpool += 1
                
        #construct daily variables 
        if self.locTime.isDayBeginning:
            _Daily.GPP = 0
            _Daily.Tmin = 9999
            _Daily.TaC=0
        
        _Daily.GPP   += self.canopy.Assimilation
        _Daily.Tmin   = min(_Daily.Tmin, self.microclim.TaC)
        _Daily.TaC   += self.microclim.TaC/24.0
        
        #daily development
        if self.locTime.isDayEnd:
            _C_a = 0.0
            for _cpt in (self.foliage, self.roots, self.perennial):
                _C_a +=_cpt.Cpool
                _cpt.Cpool =0.0
            #minimul pool equals 5 days of respiration
            _CpoolMin = 5* self.Rm

            if _C_a < _CpoolMin:
                _MortalityCpool = (1-_C_a/_CpoolMin)**2
            else:
                _MortalityCpool=0

            for _cpt, _Alloc in (
                                 (self.foliage, k_Alloc_F),
                                 (self.perennial, k_Alloc_P),
                                 (self.roots, 1 - k_Alloc_F - k_Alloc_P)
                                 ):

                #plant part growth in kg dm 
                if self.soil.waterCycle.MoistureDeficit < _cpt.SMD_Limiting_Growth and _Daily.TaC > _cpt.T_Limiting_Growth  :
                    _dS = dSigmoide(self.locTime.DOY, _cpt.GrowthLength, _cpt.GrowthStart, 0.01)                                                   #derivative fo the maximal growthh
#                   _cpt.WGrowth= max(0,min(_cpt.WGrowthMax * _dS ,(_C_a - _CpoolMin) * _Alloc / _cpt.BiomassCarbonContent)/(1+_cpt.RgCost))
                    _cpt.WGrowth= max(0,min(_cpt.WGrowthMax * _dS ,(_C_a - _CpoolMin) * _Alloc / _cpt.BiomassCarbonContent)/(1+_cpt.RgCost))   #minimum of maximal growth demand and avaibale carbon 
                else :
                    _cpt.WGrowth= 0

                #mortality  (gC /m2_soil /day) : effect of low temperature, high SMD and senescence
                _cpt.LitterFall = _cpt.W * _cpt.BiomassCarbonContent * max(
                                                            _cpt.k_MortalityTempRate if (_Daily.Tmin <= _cpt.k_MortalityTemp) else 0,
                                                            _cpt.k_MortalitySMDRate if  (self.soil.waterCycle.MoistureDeficit >= _cpt.k_MortalitySMD) else 0,
                                                            _cpt.k_MortalityDOYRate if  (self.locTime.DOY >= _cpt.k_MortalityDOY) else 0,
                                                            _MortalityCpool
                                                                )
                self.LitterFall += _cpt.LitterFall
                
                #new biomass
                _cpt.W += _cpt.WGrowth - _cpt.LitterFall /_cpt.BiomassCarbonContent
                _cpt.W  = max(0, _cpt.W)
                #New carbon pool
                _cpt.Cpool +=  _Alloc *( _Daily.GPP + _C_a) - _cpt.WGrowth * _cpt.BiomassCarbonContent
                _cpt.Cpool  =  max (0.01, _cpt.Cpool) 
    
    @pcs
    def pcs_AllocateLitterCarbonToSoil(self):
        '''Add compartment litter to soil carbon incoming'''
        
        if self.locTime.isDayEnd:
            for _cpt in (self.foliage,  self.roots,  self.perennial):
                self.soil.carbonCycle.incorporateACarbonLitter(_cpt.LitterFall, _cpt.DPM_RPM, _cpt.LitterFallAge)

