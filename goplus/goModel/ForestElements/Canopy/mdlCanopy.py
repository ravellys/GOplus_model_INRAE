# -*- coding: utf-8 -*-

from goBases import * 		# Windows
#from ....goBases import * 	# Linux

class SunShadeLeafLayer(ELT):
    SW_Abs = var('shortwave radiation absorbed (W /m2_soil)')
    LAI    = var('Part of the canopy LAI associated with this fraction (m2_LAI /m2_soil)')
    Anet   = var('Assimilation net (g_C /m2_soil /hour)')
    WAI    = var('Wood Area Index (m2 Stem and Branch area /m2 soil)') 	

class SunShadeCanopy(ELT):
    '''Canopy surface exchanges according to Sun /Shade model approach (DePury and Farquhar 1997)'''

    # Outer elements
    locTime         = eltOut('LoctTime element')
    sunLocal        = eltOut('SunLocal element')
    microclim       = eltOut('Upper MicroClimate element')
    microclim_under = eltOut('Under MicroClimate element')
    soil            = eltOut('Soil element')

    #Inner elements
    sunLayer = eltIn(SunShadeLeafLayer)
    shadeLayer = eltIn(SunShadeLeafLayer)

    #state variables define outer
    LAI             = var('Leaf area Index (m2_leafAreaIndex / m2_soil)',0.)
    WaterPotential  = var('leaf water potential (MPa)',0.)
    WAI	          = var('Wood Area Index (m2 Stem and Branch area /m2 soil)',0.) 
    def update(self):
        #Energy balance processes
        self.pcs_AerodynamicConductance()
        self.pcs_StomatalConductance()
        self.pcs_ShortWaveBalance()
        self.pcs_EnergyBalance()
        
        #Water balance processes
        self.pcs_EvapoTranspiration()
        self.pcs_CanopyRainInterception()

        #Carbon balance processes
        self.pcs_AssimilationFarquhar()

#___________________________________________________________________________________________________________
    # AERODYNAMIC CONDUCTANCE
    # NEutral conditions.  Assumed to be identical for H and LE  
    Ga              = var('aerodynamic conductance (m /s)')
    u_surface       = var('wind speed at canopy surface (m /s)')
    height_surface  = var('heigth of the surface (m)')
    Ustar           = var('friction velocity (m/s)')
    @pcs
    def pcs_AerodynamicConductance(self):
             
        if self.container.density >0:
            
            k           = 0.41    	#von Karman 
            alpha       = 0.000724  	#Nakai et al. 2008
            beta        = 0.273     	#Nakai et al. 2008
            self.height_surface = max(0.20, self.container.HEIGHTmean) 
            d           = self.height_surface*(1-(1-exp(-alpha*self.container.density))/(alpha*self.container.density) * (1-exp(-beta*(self.LAI+self.WAI)))/(beta*(self.LAI+self.WAI)+0.0001))  #displacement height (m)
            z0          = 0.264*(self.height_surface-d) 

            if z0 > 0 and (self.LAI+self.WAI) > 1.5 :
                if self.microclim.z_ref == 2 :
                    ustar = self.microclim.u*k/log(((6.5138*self.height_surface**0.5078) - d)/z0)   
                elif self.microclim.z_ref == 10 :
                    ustar = self.microclim.u*k/log(((20.475*self.height_surface**0.2886) - d)/z0)
                else :
                    ustar = self.microclim.u*k/log((self.microclim.z_ref - d)/z0)      
                # The polynome in height surface, 6.5138 *self.height_surface**0.5078 or 20.475*self.height_surface**0.2886, are for extrapolating Zref when needed. 
                # Meteorological input data mostly used are from ARPEGE/ALADIN on SAFRAN grid. U is for z=10m above a short grass.
                # 20.475*self.height_surface**0.2886 (m) corresponds to the altitude above a forest where  U = Uref(SAFRAN) at z=10m.
                # 6.5138*self.height_surface**0.5078 (m) corresponds to the altitude above a forest where  U = Uref(SAFRAN) at z= 2m.
                #in all other cases, u is assumed to be measured on site at z=zref.
                self.Ustar      = ustar
                self.u_surface  = ustar/k*log((self.height_surface-d)/z0) 
                
                if self.u_surface < 0:
                    raise Exception('u negative')
                
                #aerodynamic resistance for momentum
                raM     = self.microclim.u / ustar**2
                self.Ga = 1./ raM 
            else:
                self.height_surface = self.microclim.z_ref 
                self.u_surface      = self.microclim.u
                self.Ga             = 0.0001
            
        else:
            self.height_surface = self.microclim.z_ref 
            self.u_surface  = self.microclim.u
            self.Ga         = 0.0001

#___________________________________________________________________________________________________________
    # STOMATAL CONDUCTANCE
    g_stom          = var('stomatal conductance (m3_vapour /m2_leafAreaIndex /s = m/s)',0.)
    g_stom_unstress = var('stomatal conductance without hydric stress (m3_vapour /m2_leafAreaIndex /s = m/s)',0.)

    @pcs
    def pcs_StomatalConductance(self, 
        g_stom_Max = param('maximal stomatal conductance (m/s)'), 
        k_SWabs_P50= param('Leaf solar radiation absorded for 50%  of stomatal conductance ponderation (W /m2_LAI)',), 
        k_VPD_P100 = param('VPD threshold to close stomata (Pa)'), 
        k_VPD_Curv = param('Curvature parameter of VPD ponderation of stomatal conductance (-)'), 
        k_Yleaf_0  = param('Leaf water potential at 50 pct stomata closure (MPa)'), 
        k_Yleaf_1  = param('Curvature parameter of leaf water potential ponderation of stomatal conductance (-)'), 
        k_Yleaf_2  = param('Leaf water potential offset(Mpa)',0.), 
        k_time_P50 = param('time for 50% response of stomatal conductance to stationnary state (min)'), 
	    k_CO2     = param('response to a doubling of CO2 concentration from 350 to 700 ppm, Medlyn et al. 2001, New Phytol'),    
        ):

        if self.LAI > 0.01:
            #radiation control of stomata
            self.pond_SW =  self.SW_Abs /(self.SW_Abs+k_SWabs_P50)
            
            # Vapour pressure saturation deficit (Pa)  control    
            _pond_VPD =  1 / (max(1, self.microclim.d /k_VPD_P100) ** k_VPD_Curv)    

            # leaf water potential (MPa)  control
            if self.WaterPotential>-3.0 :
                _pond_Yleaf = max(0.0 ,1 / (1+(min(-0.01,self.WaterPotential)/ k_Yleaf_0)** k_Yleaf_1))
            else :
                _pond_Yleaf = 0.0001
            
            # CO2 control (ppm1
            _pond_YCO2 =(1-(1-k_CO2)*(self.microclim.CO2/350-1))
            
            # steady state conductance
            _g_Stat =  g_stom_Max * self.pond_SW * _pond_VPD * _pond_Yleaf *_pond_YCO2
            
            #stomatal conductance - unstress used to calculate the stress index
            _g_Stat_unstress =  g_stom_Max * self.pond_SW *_pond_YCO2
            
            # Dynamic stomatal conductance
            self.g_stom =  _g_Stat  +(self.g_stom -_g_Stat)* exp(-60./k_time_P50)
            self.g_stom_unstress  =  _g_Stat_unstress 

        else:
            self.g_stom = 0.0001
            self.g_stom_unstress =0.0001
#___________________________________________________________________________________________________________
    # SHORT WAVE BALANCE
    SWDir_Int_f = var('direct shortwave radiation intercepted (W /m2_soil)')
    SWDif_Int_f = var('diffuse shortwave radiation intercepted (W /m2_soil)')
    SWUp_Int    = var('upward shortwave radiation intercepted (W /m2_soil)')
    SW_Sct_Up   = var('shortwave radiation reflected up(W /m2_soil)')
    SW_Sct_Dw   = var('shortwave radiation reflected down(W /m2_soil)')
    SW_Abs_f    = var('shortwave radiation absorbed by foliage (W /m2_soil)')
    WAIDir      = var('wood area index for direct solar radiation (m2_leaf /m2_soil), Breda 2003')
    SW_Int_w    = var('shortwave radiation intercepted  by woody parts(W /m2_soil)')
    SWUp_Int_w  = var('Upward shortwave radiation intercepted  by woody parts(W /m2_soil)')
    SWDif_Int_w = var('Downward diffuse shortwave radiation intercepted  by woody parts(W /m2_soil)')
    SWDir_Int_w = var('Downward direct shortwave radiation intercepted  by woody parts(W /m2_soil)')
    SW_Abs_w    = var('shortwave radiation absorbed by woody parts (W /m2_soil)')
    SW_Abs      = var('shortwave radiation absorbed by foliage + woody parts (W /m2_soil)',0.)
    @pcs
    def pcs_ShortWaveBalance(self, 
        k_Beam_f    = param('Extinction coefficient of canopy for perpendicular beam radiation taking into account of aggregation factor '),  
        k_d_f       = param('diffuse shortwave extinction coefficient taking into account of aggregation factor'),
        k_Beam_w    = param('direct shortwave extinction coefficient by woody parts'),      
        k_d_w       = param('diffuse shortwave extinction coefficient by woody parts'),
        rho_l       = param('Leaf reflection coefficient for shortwave (_)'),
        theta_l     = param('Leaf transmissivity for shortwave (_)'),
        rho_cd      = param('Canopy reflection coefficient for diffuse shortwave (_)'), 
        Albedo_w    = param('Wood reflectance (?)'), 
        WAIDirmax   = param('WAIDir coefficient, Breda 2003',0.),
        WAIDirmin   = param('WAIDir coefficient, Breda 2003',0.),
        SLA         = param('SLA'),
        ):
        '''Shortwave absorption is partionned between a Sun and a Shade layer (DePury and Farquhar 1997)
            We add the source of beam and diffuse from under 'layer'
        '''

        sinB            = self.sunLocal.SinSunElevation
        microclim       = self.microclim
        microclim_under = self.microclim_under
        L_c             = self.LAI
        absorbance      = 1- rho_l - theta_l #Leaf absorbance : (1-sigma) of DePury
        _alpha          = WAIDirmax*(1.0-sinB)+ WAIDirmin
        self.WAIDir     = _alpha*L_c  / (1.0 -_alpha)

        if L_c > 0 :
           
            if sinB >0:

                #Radiation extinction coefficient accounting for the solar angle and scattering [eq: S2, S4]
                k_b = k_Beam_f / sinB
                kp_b = k_b * absorbance**0.5 
                kp_d = k_d_f * absorbance**0.5

                #canopy reflection coefficient for beam shortwave 
                rho_h = (1-absorbance**0.5)/(1+absorbance**0.5)
                rho_cb= 1- exp(-2*rho_h * k_b/(1+k_b)) 

                # __CANOPY _____________________________________________
                #canopy shortwave components interception (W /m2_soil) .
                self.SWDir_Int_f = microclim.SWDir * (1 - exp(-kp_b*L_c)) 
                self.SWDif_Int_f = microclim.SWDif * (1 - exp(-kp_d*L_c)) 
                self.SWUp_Int = microclim_under.SWUp * (1 - exp(-kp_d*L_c))

                #canopy shortwave components reflection (W /m2_soil)
                self.SW_Sct_Up  = rho_cb * self.SWDir_Int_f + rho_cd * self.SWDif_Int_f 
                self.SW_Sct_Dw = rho_cd * self.SWUp_Int

                # __SUN LAYER __________________________________________
                #Sunlit leaf area index of the canopy (m2_LAI /m2_soil))
                self.sunLayer.LAI =(1 - exp(-k_b * L_c  )) / k_b

                #Fractions of beam , scaterred beam  and diffuse  shortwave absorbed by the sunLayer 
                fracSunDir_abs = absorbance * (1 - exp(-k_b*L_c  )) #[eq: 20b]
                fracSunDirScat_abs = (1 - rho_cb)*(1-exp(-(kp_b + k_b)*L_c))*kp_b/(kp_b + k_b) - absorbance*(1 - exp(-2*k_b*L_c))/2 
                fracSunDif_abs = (1 - rho_cd) * (1-exp(-(kp_d + k_b)*L_c)) * kp_d /(kp_d + k_b) 
                self.sunLayer.SW_Abs = microclim.SWDir * ( fracSunDir_abs + fracSunDirScat_abs) + (microclim.SWDif  + microclim_under.SWUp) * fracSunDif_abs#
                
            else:
                kp_d = k_d_f * absorbance**0.5
                k_b = k_Beam_f
                fracSunDif_abs = (1 - rho_cd) * (1-exp(-(kp_d + k_b)*L_c)) * kp_d /(kp_d + k_b)
                self.SWDir_Int_f = 0
                self.SWDif_Int_f = microclim.SWDif *  (1 - exp(-k_d_w*self.WAI)*(1-fracSunDif_abs))
                self.SWUp_Int    = microclim_under.SWUp *  (1 - exp(-k_d_w*self.WAI)*(1-fracSunDif_abs))
                self.SW_Sct_Up  = rho_cd * self.SWDif_Int_f
                self.SW_Sct_Dw = rho_cd * microclim_under.SWUp * fracSunDif_abs

                self.sunLayer.LAI = 0.
                self.sunLayer.SW_Abs = 0.

        else:
            self.SWDir_Int_f = 0.
            self.SWDif_Int_f = 0.
            self.SWUp_Int = 0.
            self.SW_Sct_Up  = 0.
            self.SW_Sct_Dw = 0.

            self.sunLayer.LAI = 0.
            self.sunLayer.SW_Abs = 0.            
        
        #Shortwave absorbed  by canopy foliage (W /m2_soil) 
        self.SW_Abs_f = (self.SWDir_Int_f + self.SWDif_Int_f + self.SWUp_Int) - (self.SW_Sct_Up + self.SW_Sct_Dw)

        #Shortwave absorbed by the shaded foliage
        self.shadeLayer.SW_Abs = max(0., self.SW_Abs_f - self.sunLayer.SW_Abs)
        self.shadeLayer.LAI = self.LAI - self.sunLayer.LAI
        
        #Shortwave absorbed by the woody parts
        #Diffuse from above:
        self.SWDif_Int_w = (self.microclim.SWDif - self.SWDif_Int_f ) * (1. - exp(-k_d_w * self.WAI)) 
        if (sinB > 0):
             self.SWDir_Int_w = (self.microclim.SWDir -  self.SWDir_Int_f )* (1. - exp(-k_Beam_w*self.WAIDir))
        else :
            self.SWDir_Int_w = 0
        
        #Upward radiation intercepted by woody part.
        self.SWUp_Int_w = self.microclim_under.SWUp * (1. - exp(-k_d_w * self.WAI))      
        
        #total intercepted radiation by woody parts 
        self.SW_Int_w = self.SWDif_Int_w  + self.SWDir_Int_w + self.SWUp_Int_w
        self.SW_Abs_w = self.SW_Int_w * (1.0 - Albedo_w)
        self.SW_Abs   = self.SW_Abs_f + self.SW_Abs_w
        
        
#==============================================================================      
    #ENERGY BALANCE
   # Conductances 
    Gsa = var('stomatal + aerodynamique conductance (m /s)')
    Gsamax = var('stomatal + aerodynamique conductance (m /s)')
    Gtot = var('total canopy to air conductance (m /s)')
    R_R = var('resistance to radiative heat transfer (s/m)')
    R_HR = var('total thermal resistance (s.m-1)')
    R_H =  var('resistance to convective heat transfer (s/m)')
    Rsa = var('resistance - total leaf to air resistance s/m')
    Rsamax = var('resistance - total leaf to air resistance s/m')
    
    # Longwave fluxes
    LWDw_Int = var('downward longwave radiation intercepted (W /m2_soil)')
    LWUp_Int = var('upward longwave radiation intercepted (W /m2_soil)')
    LW_Sct_Up = var('longwave radiation reflected (W /m2_soil)')
    LW_Sct_Dw = var('longwave radiation reflected (W /m2_soil)')
    LW_Abs = var('longwave radiation absorbed (W /m2_soil)')
    LW_Emi = var('longwave radiation emitted (W /m2_soil)')

    #Radiative balance
    Rnet_star = var('radiative balance in the case of a leaf area temperature equal to that of air  (W /m2_soil)')
    Rnet = var('radiative balance (W /m2_soil)')

    # Sensible Heat Flux
    dTsTa = var('leaf-air temperature gradient (degK)')
    H = var('heat flux (W /m2_soil')

    # Latent heat Flux
    LE_DrySurface = var('latent flux of dry leaf area part  (W /m2_soil)')
    LE_DrySurfacemax = var('latent flux of dry leaf area part  (W /m2_soil)')
    LE_WetSurface = var('latent flux of wet leaf area part  (W /m2_soil)')
    LE = var('latent flux (W /m2_soil)')
    DrySurfaceFraction = var('rate of leaf surface dry ([0-1])',1.0)


    @pcs    
    def pcs_EnergyBalance(self, 
        kLAI1_LW_Int = param('parameter 1 of longwave radiation interception (-)',  0.0), 
        kLAI2_LW_Int = param('parameter 2 of longwave radiation interception (-)',  0.0), 
        Emissivity = param('emissivity', 0.0) , 
        ):

        if self.LAI >0.001:
            _microclim = self.microclim
            _microclim_under = self.microclim_under

            #fraction of LW absorbed by the foliage and the woody parts  
            _LWInt_f = exp(kLAI1_LW_Int*self.LAI  + kLAI2_LW_Int * self.LAI **2.) 
            _LWInt_w = exp(-1.0 *self.WAI)
          
            _Sigma = 0.000000056703 # Stefan-Boltzmann constant (W /m2 /K^4)
            _R_R  = self.R_R
            _R_HR = self.R_HR
            _R_R = _microclim.Rho_Cp /( 2. * 4.* (1-_LWInt_f*_LWInt_w) *_Sigma * Emissivity * _microclim.TaK ** 3.) 
            _R_H = self.R_H
            _R_H = 1./(self.Ga)  
            _R_HR = 1. / ((1./_R_R)+ (1./_R_H))
   
            #longwave fluxes intercepted
            self.LWDw_Int = (1-_LWInt_f*_LWInt_w) * _microclim.LWDw
            self.LWUp_Int = (1-_LWInt_f*_LWInt_w) * _microclim_under.LWUp

            #longwave fluxes reflected
            self.LW_Sct_Up = (1-Emissivity)* (self.LWDw_Int  * 0.75 + self.LWUp_Int * 0.25)
            self.LW_Sct_Dw = (1-Emissivity)* (self.LWDw_Int  * 0.25 + self.LWUp_Int * 0.75)

            #longwave fluxes absorbed
            self.LW_Abs = (self.LWDw_Int + self.LWUp_Int) - (self.LW_Sct_Up + self.LW_Sct_Dw)

            #Conductances
            _Ga = self.Ga
            _Rsa = self.Rsa

        
            try:
                self.Gsa = 1. / (1. / _Ga + 1. / (self.LAI*self.g_stom))
                self.Gsamax = 1. / (1. / _Ga + 1. / (self.LAI*self.g_stom_unstress))
            except:
                self.Gsa = 0.0001
                self.Gsamax = 0.0001
                
            self.Rsa = 1 / (self.Gsa + 0.0001)
            self.Rsamax = 1 /(self.Gsamax + 0.0001)
            #isothermal radiative balance (Ts =Tair)
            self.Rnet_star = (self.SW_Abs + self.LW_Abs) - 2. * (1-_LWInt_f*_LWInt_w) * Emissivity * _Sigma * _microclim.TaK ** 4.

            #Condensation: all canopy surface area is assumed to be wet
            if ((_microclim.Rho_Cp) * _microclim.d / _R_HR + _microclim.s * self.Rnet_star) < 0. :  # Storage term is missing (neglected).
                self.Gtot = _Ga
            else :
                self.Gtot = self.DrySurfaceFraction * self.Gsa + (1 - self.DrySurfaceFraction) * _Ga + 0.00001

            #air-surface temperature difference (Ts - Tair)
            self.dTsTa = self.Rnet_star * _microclim.Gamma * (self.Gtot**-1) * _R_HR / (_microclim.Rho_Cp * (_microclim.Gamma * (self.Gtot**-1) \
            + _microclim.s * _R_HR))- _R_HR * _microclim.d /(_microclim.Gamma*(self.Gtot**-1) + _microclim.s * _R_HR ) #Jones p187 eq.9.6
            self.dTsTa = max(-1.0, min(self.dTsTa, 15.)) # cut below -1 because erroneous value due to stable conditions

            #longwave flux emitted
            self.LW_Emi = 2. * (1-_LWInt_f*_LWInt_w) * Emissivity * _Sigma * (_microclim.TaK + self.dTsTa) ** 4.

            #sensible heat flux 
            self.H = _Ga * _microclim.Rho_Cp * self.dTsTa

            #net radiation
            self.Rnet = self.SW_Abs + self.LW_Abs -self.LW_Emi
            _LEgradient = _microclim.Rho_Cp / _microclim.Gamma * (_microclim.d + _microclim.s * self.dTsTa)

            if _LEgradient > 0 :
                self.LE_DrySurface      = (self.DrySurfaceFraction) *  (_microclim.Rho_Cp*(_microclim.d + _microclim.s * self.dTsTa))  / (_microclim.Gamma * self.Rsa)                  
                self.LE_DrySurfacemax   = (self.DrySurfaceFraction) *  (_microclim.Rho_Cp*(_microclim.d + _microclim.s * self.dTsTa))  / (_microclim.Gamma * self.Rsamax)
                self.LE_WetSurface      = (1. - self.DrySurfaceFraction) *   min (self.WaterSurfaceContent*self.microclim.Lambda/3600, (_microclim.Rho_Cp*(_microclim.d + _microclim.s * self.dTsTa) ) / (1./(self.Ga) * _microclim.Gamma))
            else :

                self.microclim.Rain += -_microclim.Rho_Cp*(_microclim.d + _microclim.s * self.dTsTa)  / (1./(self.Ga) * _microclim.Gamma)/ _microclim.Lambda *3600
                self.LE_DrySurface = 0.0
                self.LE_DrySurfacemax = 0.0
                self.LE_WetSurface =  min (self.WaterSurfaceContent*self.microclim.Lambda/3600, (_microclim.Rho_Cp*(_microclim.d + _microclim.s * self.dTsTa) ) / (1./(self.Ga) * _microclim.Gamma))
           
                
            self.LE = self.LE_DrySurface + self.LE_WetSurface
            self.R_H =_R_H
            self.R_HR = _R_HR
        else:
            self.Gtot = 0
            self.Gsa = 0
            self.LWDw_Int = 0
            self.LWUp_Int = 0
            self.LW_Sct_Up = 0
            self.LW_Sct_Dw = 0
            self.LW_Abs = 0
            self.Rnet_star = 0
            self.dTsTa = 0
            self.LW_Emi = 0
            self.H = 0
            self.Rnet = 0
            self.LE_WetSurface = 0
            self.LE_DrySurface = 0
            self.LE_DrySurfacemax = 0
            self.LE = 0


    
#Water vapour flux ============================================================
    Transpiration = var('transpiration (Kg_H2O /m2_soil /hour)')
    Transpirationmax = var('transpiration (Kg_H2O /m2_soil /hour)')
    Evaporation = var('evaporation of water retained on leaf surface (Kg_H2O /m2_soil /hour)')
    ETR = var('evapotranspiration (Kg_H2O /m2_soil /hour)')

    

    @pcs
    def pcs_EvapoTranspiration(self):
        '''canopy evapotranspiration
        '''

        #convert the latent heat flux (W/ m2) in Evapotranspiration (Kg_H2O/ m2 /hour)
        _factor = 3600./self.microclim.Lambda
        self.Transpiration = _factor * self.LE_DrySurface
        self.Transpirationmax = _factor * self.LE_DrySurfacemax
        self.Evaporation   = _factor * self.LE_WetSurface
        self.ETR = self.Transpiration + self.Evaporation 
        
    
    # Canopy Water Balance
    InterceptedRain = var('rain intercepted by leaf (Kg_H2O /m2_soil /hour)')
    Dripping = var('rain intercepted by leaf and subsequently lost by dripping (Kg_H2O /m2_soil /hour)')
    WaterSurfaceContent = var('water storage content on leaf + Stem + Branch surface (Kg_H2O /m2_soil)',0.)
    TK_leaf = var ('Temperature of the foliage in Kelvin')

    @pcs
    def pcs_CanopyRainInterception(self, 
        kRainInt_LAI = param('parameter of rain interception by leaf (-)'),
        kRainInt_WAI = param('parameter of rain interception by leaf (-)'), 
        SurfaceWaterStorageCapacity = param('water storage capacity by foliage+wood area (Kg_H2O /m2_plant area )'), 
        ):
        '''Process interception of rain by the canopy  '''

        _waterSurfaceCapacity = max(0.01,(self.LAI + self.WAI) * SurfaceWaterStorageCapacity)

        #Rain intercepted (mm/h) and dripping  (mm/h) 
        self.InterceptedRain = self.microclim.Rain * (1 - exp(-kRainInt_LAI * self.LAI - kRainInt_WAI*self.WAI))
        self.Dripping = max(0., (self.WaterSurfaceContent + self.InterceptedRain - self.Evaporation) - _waterSurfaceCapacity)
        #canopy water surface content
        self.WaterSurfaceContent += (self.InterceptedRain - self.Evaporation - self.Dripping)
        self.WaterSurfaceContent  = max(0,self.WaterSurfaceContent)
        self.DrySurfaceFraction   = 1 - self.WaterSurfaceContent / _waterSurfaceCapacity

    
#ASSIMILATION   and foliage respiration =======================================
    Assimilation = var('Raw assimilation (g C /m2_soil /hour)')
    Respiration = var('Dark respiration (g C /m2_soil /hour)')

    @pcs
    def pcs_AssimilationFarquhar(self, 
        #Biochemistry photosynthetic parameters at the reference temperature and activation energies
        #from Bernacchi et al. 2001 in Medlyn et al. 2002    
        Kc_25= param('Michaelis-Menten constant of rubisco for CO2 at 25 degC (mol_CO2 /mol)'),
        Ea_Kc = param('Activation energy for Kc (J /mol)'),#Medlyn et al. 2002 [eq 5]
        Ko_25 = param('Michaelis-Menten constant of rubisco for O2 at 25 degC (mol_O2 /mol)'),
        Ea_Ko =   param('Activation energy for Kc (J /mol)'),
        GammaStar_25 = param('CO2 compensation point of photosynthesis in the absence of mitochondrial respiration (mol_CO2 /mol_air : ppm)'),
        Ea_GammaStar = param('Activation energy for GammaStar (J /mol)'),#Medlyn et al. 2002 [eq 12]

        #Medlyn et al. 2002 
        Vcmax_25 = param('Vcmax at 25 degC, expressed on a one-sided leaf area basis (mol_CO2 /m2_LAI /s))'),
        Ea_Vcmax = param('Activation energy for Vcmax (J /mol)'),

        Jmax_25 = param('Jmax at 25 degC, expressed on a one-sided leaf area basis (mol_e /m2_LAI /s'),
        Ha_Jmax = param('Activation energy for Jmax (J /mol)'),
        Hd_Jmax = param('Desactivation energy for Jmax (J /mol)'),
        TCopt_Jmax = param('temperature of Jmax optimum (deg_C)'),
        alpha = param('Quantum yield of electron transport (mol_e /mol_photon_absorbed). \
                Litterature value obtained on SW intercepted need to be corrected for leaf absorbance'),
        Rd_25 = param('Dark leaf respiration at 25 degC (mol_CO2 /m2_LAI /s)'),  
        Ea_Rd= param('Activation energy for Rd (J /mol)'), 

        ):
        ''' Process photosynthesys along Farquhar's model for each sun and shade layers
            Resolution of Anet from the syStem of equation of :
             - Farquhar et al. model :  Anet =min(Ac,Aj) - Rd
             - Diffusivity of CO2 through stomata :  Anet = gc(Ca - Ci)
        '''

        if self.LAI > 0.001 :
            #calculated parameters
            R = 8.3145 #J /mol /K
            TKref = 25. + 273.15 #K
            TKopt_Jmax = TCopt_Jmax +273.15
            KHa_Jmax = Ha_Jmax/(R* TKopt_Jmax)
            KHd_Jmax = Hd_Jmax/(R* TKopt_Jmax)
            K_Jmax_25 = Jmax_25*(KHd_Jmax  -KHa_Jmax*(1-exp(KHd_Jmax*(1 - TKopt_Jmax/TKref))))

            self.TK_leaf = self.microclim.TaK + self.dTsTa           
            T_factor = (self.TK_leaf-TKref)/(R*self.TK_leaf*TKref)    

            #Biochemistry photosynthetic parameters dependence to temperature
            Rd = Rd_25 * exp(Ea_Rd*T_factor)      

            Kc = Kc_25 * exp(Ea_Kc*T_factor)
            Ko = Ko_25 * exp(Ea_Ko*T_factor)
            Oi = 0.2095 #mol_O2 /mol_air
            Km = Kc*(1. + Oi/Ko)                             #effective Michaelis-Menten coefficient for CO2 (mol_CO2 /mol_air)
            GammaStar = GammaStar_25 * exp(Ea_GammaStar*T_factor)

            Vcmax = Vcmax_25 * exp(Ea_Vcmax*T_factor)# Medlyn et al. Arrhenius  function               
            Jmax = K_Jmax_25 * exp(Ha_Jmax*T_factor )/ (KHd_Jmax - KHa_Jmax * (1 - exp(KHd_Jmax*(1 - TKopt_Jmax/self.TK_leaf)))) #  Medlyn et al. Peak function

            #stomatal conductance for CO2
       
            gsCO2= (2 * (self.microclim.P)/(R*self.TK_leaf) /1.6) * max(0.0001, self.g_stom) # convert  m/s (m3_vapour /m2_LAI /s) to mol_CO2/m2_Leaf area developed / s
            gm = -0.04/1000000 + 1.34 * gsCO2 # internal conductance to CO2 Ellsworth et al. 2015
            gCO2= 1 / (1/gm + 1/gsCO2)#  parameterisation questionable. internal conductance to CO2 Ellsworth et al. 2015
            Ca = self.microclim.CO2 * 1.0e-6      #mol_CO2 /mol_air

            #Assimilation in case of a limitation by the carboxylation rate (mol_CO2 /m2_LAI/s)
            #as the smallest root of 2nd order equation (-x2 + bx + c = 0) 
            b = gCO2*(Ca+Km) + Vcmax - Rd
            c = gCO2*((Ca+Km)*Rd - (Ca-GammaStar)*Vcmax)            
            Anet_c = (b - sqrt(b*b +4.*c))/2.
            

            #Resolution of minimum of Assimilation limitation for each layer
            for layer in (self.sunLayer, self.shadeLayer):
                if (layer.LAI >0 ) and (self.TK_leaf > 276.15) : #condition on leaf temperature 
                    #Electron transport rate 
                    #as the smallest root of 2nd order equation (-x2 + bx + c = 0) 
                    theta = 0.9
                    Q = layer.SW_Abs/ layer.LAI*4.6e-6 #W /m2_soil to mol_photon /m2_LAI/s
                    b = (alpha*Q +Jmax )/theta
                    c = -alpha*Q * Jmax /theta
                    J = (b - sqrt(b*b +4.*c))/2.

                    #Assimilation in case of a limitation by the electron transfert rate (mol_CO2 /m2_LAI /s)
                    #as the smallest root of 2nd order equation (-x2 + bx + c = 0) 
                    b = gCO2*(Ca+2.*GammaStar) + J/4. - Rd
                    c = gCO2*((Ca+2.*GammaStar)*Rd - (Ca-GammaStar)*J/4.)
                    Anet_j = (b - sqrt(b*b +4.*c))/2.

                    #net assimilation is the minimum of the  assimilation limited by J and Vc. Conversion of mol_CO2 /m2_LAI /s into g_C /m2_soil /hour
                    layer.Anet = min(Anet_j, Anet_c) * (12. * layer.LAI* 3600.)

                else:
                    layer.Anet = 0
                
            #Assimilation and respiration of the canopy (g_C /m2_soil /hour)
            self.Respiration = Rd * (12. * self.LAI* 3600.) # Conversion from mol_CO2 /m2_LAI /s to g_C /m2_soil /hour
            self.Assimilation = self.sunLayer.Anet + self.shadeLayer.Anet + self.Respiration 

        else: 
           self.Respiration = self.Assimilation = self.sunLayer.Anet = self.shadeLayer.Anet = 0
