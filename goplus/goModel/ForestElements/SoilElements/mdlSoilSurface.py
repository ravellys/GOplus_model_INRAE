from goBases import * #Windows OS
# from ....goBases import* #linux OS
#TODO : separate the sub process as BigLeafCanopySurface

class SoilSurface(ELT):
    ''' Soil water contents cycle 
    '''

    # Outer elements
    microclim = eltOut('MicroClimate upper soil')
    
    def update(self):
        #canopy water balance, part 1: evaluation of the dry fraction
        self.DrySurfaceFraction = 1 - self.WaterSurfaceContent / (1 * self.pcs_waterBalance.SurfaceWaterStorageCapacity)
        
        self.pcs_energyBalance()
        self.pcs_waterBalance()        

    #ENERGY BALANCE
   # Conductances composantes
    Gsa  = var('surface - aerodynamic conductance (m /s)')
    Gtot = var('total soil to air conductance (m /s)')

    # RadiativeFlux
    SWDir_Int = var('direct shortwave radiation intercepted (W /m2_soil)')
    SWDif_Int = var('diffuse shortwave radiation intercepted (W /m2_soil)')
    SW_Int    = var('total shortwave radiation intercepted (W /m2_soil)')
    SW_Sct    = var('shortwave radiation reflected (W /m2_soil)')
    SW_Abs    = var('shortwave radiation absorbed (W /m2_soil)')

    LWDw_Int = var('downward longwave radiation intercepted (W /m2_soil)')
    LW_Sct   = var('longwave radiation scattered (W /m2_soil)')
    LW_Abs   = var('longwave radiation absorbed (W /m2_soil)')
    LW_Emi   = var('longwave radiation emitted (W /m2_soil)')

    Rnet_star = var('radiative balance of isothermal air-soil (W /m2_soil)')
    Rnet      = var('radiative balance of soil (W /m2_soil)')

    #Sensible Heat Flux
    dTsTa = var('soil surface-air temperature gradient (degK)')
    H     = var('heat flux (W /m2_soil')

    # Latent Heat Flux
    LE_DrySurface = var('latent flux of dry leaf area part  (W /m2_soil)')
    LE_WetSurface = var('latent flux of wet leaf area part  (W /m2_soil)')
    LE            = var('latent flux (W /m2_soil)')

    @pcs    
    def pcs_energyBalance(self, 
        
        Albedo     = param('albedo (?)',), 
        Emissivity = param('emissivity',) , 
        ):

        _microclim = self.microclim

        #Diffuse and beam shortwave interception
        self.SWDif_Int = _microclim.SWDif 
        self.SWDir_Int = _microclim.SWDir 

        #total shortwave interception, reflection and absorption
        self.SW_Int = self.SWDir_Int + self.SWDif_Int 
        self.SW_Sct = self.SW_Int * Albedo
        self.SW_Abs = self.SW_Int - self.SW_Sct

        #exchange coefficients for long wave independant of surface temperature
        _K_IntLW = 1.
        _Sigma   = 0.000000056703 # Stefan-Boltzmann constant (W /m2 /K^4)
        _K_EchLW = 4. * _K_IntLW * Emissivity * _Sigma * _microclim.TaK ** 3 
        
        #longwave fluxes components absorbed and reflected
        self.LWDw_Int = _K_IntLW * _microclim.LWDw
        self.LW_Abs   = self.LWDw_Int * Emissivity
        self.LW_Sct   = self.LWDw_Int  - self.LW_Abs
        
        
        #Aerodynamic conductance
        k = 0.41    			#von Karman
        height_surface = 0.15 		
        z0 = 0.01 			     #roughness length for momentum
        d  = 0.9*(height_surface-z0)
        ustar = self.microclim.u*k/log((max(0.2,self.microclim.z_ref) - d)/z0)

      
        #aerodynamic  resistance for momentum
        raM = self.microclim.u /ustar**2
        _Ga = 1/raM
        
        
        _waterCycle = self.container.waterCycle
        if _waterCycle.w_A -_waterCycle.w_RES <= 0:
            raS = 1e8
        else:
            raS = 100.*((_waterCycle.w_SAT - _waterCycle.w_RES)/(_waterCycle.w_A -_waterCycle.w_RES) - 1) 
        
        #Equivalent conductance
        self.Gsa = 1/(raM+raS)
        
        #radiative balance of the isothermal air-surface 
        self.Rnet_star = (self.SW_Abs + self.LW_Abs) -  _K_IntLW * Emissivity * _Sigma * _microclim.TaK ** 4

        #test of condensation 
        if ((_K_EchLW + _Ga * _microclim.Rho_Cp) * _microclim.d + _microclim.s * self.Rnet_star) < 0 :
            self.Gtot = _Ga
        else :
            self.Gtot = self.DrySurfaceFraction * self.Gsa + (1 - self.DrySurfaceFraction) * _Ga

        #air-surface temperature difference
        self.dTsTa = (self.Rnet_star - self.Gtot * (_microclim.Rho_Cp /_microclim.Gamma) * _microclim.d) / (_K_EchLW + _microclim.Rho_Cp * (_Ga + self.Gtot * _microclim.s  / _microclim.Gamma)) 
        self.dTsTa=max(-15, min(self.dTsTa, 15)) 

        #longwave flux emitted
        self.LW_Emi =  _K_IntLW * Emissivity * _Sigma * (_microclim.TaK + self.dTsTa) ** 4
        
        #sensible heat flux 
        self.H = _Ga * _microclim.Rho_Cp * self.dTsTa

        #net radiation

        self.Rnet = (self.SW_Abs + self.LW_Abs) -self.LW_Emi 

        #Evaporation of wet and dry layer part
        _LEgradient = _microclim.Rho_Cp / _microclim.Gamma * (_microclim.d + _microclim.s * self.dTsTa )

        if _LEgradient > 0 :
            self.LE_WetSurface = _Ga * _LEgradient * (1 - self.DrySurfaceFraction)
            self.LE_DrySurface = self.Gsa * _LEgradient * self.DrySurfaceFraction
        else :
            self.LE_WetSurface = _Ga * _LEgradient
            self.LE_DrySurface = 0

        self.LE = self.LE_DrySurface + self.LE_WetSurface


    #vars
    WaterSurfaceContent = var('water storage content on surface (Kg_H2O /m2_soil)', 0)
    DrySurfaceFraction  = var('dry surface fraction ([0-1])')
    InterceptedRain     = var('rain intercepted by surface (Kg_H2O /m2_soil /hour)')
    Input               = var('rain flowing through the surface into the soil (Kg_H2O /m2_soil /hour)')
    ETR_DrySurface      = var('Evaporation from below surface  (Kg_H2O /m2_soil /hour)')
    ETR_WetSurface      = var('Evaporation from the wet fraction of the soil surface (Kg_H2O /m2_soil /hour)')
    ETR                 = var('Evaporation (Kg_H2O /m2_soil /hour)')

    @pcs    
    def pcs_waterBalance(self, 
        SurfaceWaterStorageCapacity = param('water storage capacity by surface area (Kg_H2O /m2_soil)', 0.5), 
        ):
        '''Process hydric balance'''
        
        #convert the latent heat flux (W/ m2) in Evapotranspiration (Kg_H2O/ m2 /hour)
        self.ETR_DrySurface = self.LE_DrySurface / self.microclim.Lambda * 3600
        self.ETR_WetSurface = self.LE_WetSurface / self.microclim.Lambda * 3600
        self.ETR = self.ETR_DrySurface + self.ETR_WetSurface
 
        #part of rain intercepted (mm/h),  Input  (mm/h) and new water content retained on the  surface
        #Loustau et al. 1992 J of Hydrol
        self.InterceptedRain = self.microclim.Rain
        self.Input = max(0, (self.WaterSurfaceContent + self.InterceptedRain - self.ETR_WetSurface) - SurfaceWaterStorageCapacity)

        #surface water surface content
        self.WaterSurfaceContent = max(0, self.WaterSurfaceContent + (self.InterceptedRain - self.ETR_WetSurface - self.Input))
        self.DrySurfaceFraction = 1 - self.WaterSurfaceContent / SurfaceWaterStorageCapacity
