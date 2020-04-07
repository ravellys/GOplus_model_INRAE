from goBases import *
#from ForestElements.SoilElements.mdlSoilCarbonCycle import *
import math
class SoilWaterCycle(ELT):
    ''' Soil water contents cycle
       Update 23/02/2017 -Version pcs26.14 generic
    '''

    # Outer elements
    locTime = eltOut('LocTime element')
    treeStand = eltOut('TreesStand element')
    underStorey = eltOut('UnderStorey element')
    surface = eltOut('SoilSurface element')


    #Soil properties parameters
    Dp_Soil  = param("total soil depth (m)", 0.)
    Dp_Roots = param("Root layer depth (m). Must be smaller than Dp_Soil", 0.)
    Clay     = param ("percentage of clay in the soil, average over the root zone, (0-100)",)  
    Silt     = param ("percentage of silt in the soil, average over the root zone,(0-100)", )  
    Sand     = param ("percentage of sand in the soil, average over the root zone,(0-100)", )  
    BD       = param ("soil basic density (t m-3)", ) 
    SOC      = var('Soil organic carbon content gC 1OOg soil-1 or pct', 0.)
    
    #water table file path
    WaterTable_file_path = param('complete path-name to water table file', 'defaultWaterTableData.csv' )
    AltitudeRef = param('Altitude of reference (m)',  0.0 )

    @pcs
    def update(self):
        #simulation initialisation
        if self.locTime.isSimulBeginning:
            self.pcs_VG_Parameters()
            self.pcs_Hydro_parameters
            self.pcs_WaterStatusInRootsLayer()

    #        else: pass

        #Reevalution of soil water components when depth of the groundwater table is prescribed
    #    if self.WaterTable_file_path != 0: 
    #        if self.locTime.isDayEnd :
    #            if self.DOY==366: self.DOY=365
    #            else: pass  
    #            if (self.Year== self.locTime.Y and self.DOY == self.locTime.DOY) :
    #                self.Dp_C = - (self.DpC_forced - self.AltitudeRef )
    #                self.WaterTableFromDataFile()
    #           else: pass     
       

        self.pcs_Discharge()
        self.pcs_LayersDepthUpdate()
        self.pcs_WaterStatusInRootsLayer()
    
    
#Values of Van Genuchten parameters as proposed by GHANBARIAN-ALAVIJEH1 et al. Pedosphere 2010, depending on the soil clay content (pct)  and based also on Huang and Zhang 2005.       
    VG_alpha = var('alpha parameter of van Genuchten expression of soil water potential (kPa-1)',), 
    VG_m  = var('m parameter of van Genuchten expression of soil water potential',)
    VG_n  = var('n parameter of van Genuchten expression of soil water potential',)
    w_SAT = var('Saturation (Kg_H2O /m3_soil)', 0.)
    w_FC  = var('Field capacity (Kg_H2O /m3_soil)', 0.)
    w_WP  = var('Wilt point (Kg_H2O /m3_soil)',0.)
    w_RES = var('Residual point (Kg_H2O /m3_soil)',0.) #minimum soil water content under direct atmopsheric evaporation 
    Correction = var('coorection factor forcing the root water potential =-1.8 MPa when available water = 0',) #- used only for correcting root water potential 
    @pcs    
    def pcs_VG_Parameters(self,  
        a_0     = param('coefficient a0 in D equation',2.35), 
        a_1     = param('coefficient a1 in D equation',0.0822), 
        a_2     = param('coefficient a2 in D equation',-0.497), 
        a_3     = param('coefficient a3 in D equation',1.238),  
        Dfrac   = param('fractal dimension of the SWRC model by Tyler and Wheatcraft (1990) ',),) : 
        
        Dfrac           = a_0 + (1-math.exp(a_1 * self.Clay))/( a_2 * (1 + math.exp(a_1 * self.Clay)) + a_3 * (1 - math.exp(a_1*self.Clay))) #proposed by Huang and Zhang (2005)
        self.VG_m       = (3-Dfrac) / (4-Dfrac)
        self.VG_n       = 1 / (1-self.VG_m)
        _Sx             = 0.72-0.35*math.exp(-(self.VG_n**4))
        _lambda         =   self.VG_m * self.VG_n
        self.VG_alpha   = _Sx**(1/_lambda) / 1.365 * (_Sx**(-1/self.VG_m)-1)**(1-self.VG_m)#the air entry point hmin=1365 Pa is fixed at the average of 2 samples analysed in GHANBARIAN-ALAVIJEH1 et al - table II
        self.Correction = -0.000639*self.Clay**2 - 0.018346 * self.Clay + 0.995324
#     Pedotransfer functions from: Wosten et al. 1999 Geoderma, and Roman-Dobarco et al. 2019 Geoderma, units in kg H2O m-3 soil.
#     SAT is adapted (* 0.75)for fitting with Landes podzolic soil.
    @pcs    
    def pcs_Hydro_parameters(self, ):
        self.w_SAT = ( 0.7919+ 0.001691*self.Clay  - 0.29619  * self.BD    -0.000001491 * self.Silt**2 + 0.0000821*(self.SOC*2)**2+ 0.02427 / self.Clay+ 0.01113 / self.Silt + 0.01472*math.log(self.Silt)-0.0000733*(self.SOC*2)*self.Clay\
                     -0.000619*self.BD*self.Clay  - 0.001183 * self.BD   *(self.SOC*2)-0.0001664*self.Silt)*1000  *0.75             
        self.w_FC  = (0.245 + 0.00224 *self.Clay  - 0.00114  * self.Sand   + 0.0334 * min(5.0, self.SOC))*1000
        self.w_WP  = (0.047 + 0.00431 *self.Clay  - 0.0000139* self.Sand + 0.0108 * min(5.0,self.SOC))*1000
        self.w_RES = 0.99 * self.w_WP

#Discharge of the aquifer by deep or lateral runoff.
    discharge = var('water loss by discharge by the soil (Kg_H2O /m2_soil /day)', 0.)
    @pcs    
    def pcs_Discharge(self, 
        kdischarge_0 = param('coefficient kDr0 in groundwater discharge expression - V0',0.), 
        kdischarge_1 = param('coefficient kDr1 in groundwater discharge expression- Pmax',0.01), 
        kdischarge_2 = param('coefficient kDr2 in groundwater discharge expression-puissance',0.0), ) : 
        '''Process depth water table discharge  : empiric relationship with one of the state variables of soil water content'''

        
        if self.locTime.isDayEnd : 
            self.discharge = kdischarge_0 * max(0, ((kdischarge_1 - self.Dp_C) / kdischarge_1)) ** kdischarge_2  # empirical discharge function
            if self.Dp_C<0:
                self.discharge *= 5.0 #discharge is increased 5 fold when the soil is flooded . (To do: link with slope).


#Dynamic depth of LAYERS C(aquifer) and B (field capacity)
    w_A     = var('water content of layer A (Kg_H2O /m3_soil)', )
    Dp_B    = var('depth of the limit between layer B and A (m)', )
    Dp_C    = var('depth of the limit between layer C and B (m)', )
    _UA     = var('water uptaken by roots from layer A (Kg_H2O m-2_soil day-1)',)
    _UB     = var('water uptaken by roots from layer B (Kg_H2O m-2_soil day-1)',)
    _UC     = var('water uptaken by roots from layer C (Kg_H2O m-2_soil day-1)',)
    _EA     = var('evaporation from layer A (Kg_H2O m-2.day-1_soil)',)   
    _EB     = var('evaporation from layer B (Kg_H2O m-2.day-1_soil)',)            
    _EC     = var('evaporation from layer C (Kg_H2O m-2_soil.day-1)',)
    _dA     = var('water balance of layer A (Kg_H2O m-2_soil.day-1)',)
    _dB     = var('water balance of layer B (Kg_H2O m-2_soil.day-1)',)                 
    _dC     = var('water balance of layer C (Kg_H2O m-2_soil.day-1)',)    
    A_Ads   = var('Input of rainfall water into layer A (Kg_H2O m-2_soil day-1)',)
    B_Ads   = var('Input of rainfall water into layer B (Kg_H2O m-2_soil day-1)',)
    C_Ads   = var('Direct percolation into layer C (Kg_H2O m-2_soil day-1)',)  
    fast_C  = param('coefficient for fast transfer to C under unsaturated conditions,[0-1] unitless',)
       
    @pcs    
    def pcs_LayersDepthUpdate(self, 
        _dailySum =private('use to sum daily fluxes', ELT)
        ):
        '''Evaluate the layers limit depth (B,  C) and water content (A) at the day end (h=23)'''

        #daily initialisation 
        if self.locTime.isDayBeginning : 
            self.pcs_Hydro_parameters()
            _dailySum.ETR_DrySurface = 0
            _dailySum.ETR_RootsAbsorption = 0
            _dailySum.Input = 0
            self._UA = 0.
            self._UB = 0.                 
            self._UC = 0.
            self._EA = 0.          
            self._EB = 0.
            self._EA = 0. 
            self._EC = 0.
            self._dA = 0.
            self._dB = 0.                 
            self._dC = 0.
            self.Discharge =0.
            self.A_Ads   = 0.
            self.B_Ads   = 0.
            self.C_Ads   = 0.
            self.StockAB = 0. 
        # Calculation of daily sums of evaporation, transpiration and net throughflow  of water from the surface of the soil
        _dailySum.ETR_DrySurface += self.surface.ETR_DrySurface
        _dailySum.ETR_RootsAbsorption  += self.treeStand.canopy.Transpiration + self.underStorey.canopy.Transpiration
        _dailySum.Input +=  self.surface.Input
        
        if self.locTime.isDayEnd :   
        # Remove layer A when at Field Capacity    
        # Exception: minimal layer A thickness allows one day evapotranspiration (4kg H20 m-2 day-1)             
            self._UC    = max(0, min(_dailySum.ETR_RootsAbsorption,                    (self.Dp_Roots-self.Dp_C)*(self.w_SAT-self.w_FC)))
            self._UB    = max(0, min(_dailySum.ETR_RootsAbsorption-self._UC,           max(0,(self.Dp_Roots-self.Dp_B)*(self.w_FC-self.w_A))))
            self._UA    = max(0, min(_dailySum.ETR_RootsAbsorption-self._UB-self._UC,  (self.Dp_Roots)*(self.w_A-self.w_WP)))
            if self.w_A >= 0.99 * self.w_FC:
                self.Dp_B= 4/(self.w_FC-self.w_WP)
        # Uptake in soil layers by plant transpiration ordered according to water availability (C>B>A)
            
        # The residual uptake is taken from B Layer (assuming a capillary rise from layer B into the root layer).    
            if _dailySum.ETR_RootsAbsorption-(self._UC + self._UB + self._UA) > 0 :
                self._UB    += _dailySum.ETR_RootsAbsorption-(self._UC + self._UB + self._UA)
        # Flooded soil: the only C layer is present                
            if self.Dp_C<=0.:   
                self._UC   = _dailySum.ETR_RootsAbsorption
                self._EC   = _dailySum.ETR_DrySurface
                self.C_Ads = _dailySum.Input
        # Unsaturated soil 
            else:
                # 1. Layer A absent 
                if self.Dp_B  <= 4/(self.w_FC-self.w_WP):
                    self._EC   =  _dailySum.ETR_DrySurface 
                    self.A_Ads = 0
                    self.C_Ads = _dailySum.Input
                # 2. Layer A present
                else:
                    self._EA  = max(0., min(_dailySum.ETR_DrySurface, (self.w_A-self.w_RES)*self.Dp_B))
                    self._EB  = max(0, _dailySum.ETR_DrySurface - self._EA)
                #3. Soil input 
                    self.A_Ads = max(0, min((1-self.fast_C)*_dailySum.Input, self.Dp_Roots*(0.99*self.w_FC-self.w_A)))
                #There is no input in layer B (at FC)               
                    self.B_Ads = max(0., min(_dailySum.Input  - self.A_Ads, (self.Dp_B-4/(self.w_FC - self.w_WP)) * (self.w_SAT -self.w_FC) ))
                    self.C_Ads = max(0.,_dailySum.Input  - self.A_Ads - self.B_Ads)

    MoistureDeficit         = var('soil moisture deficit in the soil layer prospected by roots  [0-1] (Kg_H2O /Kg_H2O)', 0.)
    RootLayerWaterPotential = var('water potential in the soil layer prospected by roots (MPa)', 0.)
    RootLayerPressureHead   = var('water potential in the soil layer prospected by roots (cm)', 0.)
    w_RootLayer             = var('water content in the soil layer prospected by roots (Kg_H2O /m3_soil)', 0.)
    RhydSoil                = var('Soil Hydraulic resistance from Van Genuchten',0.1) 
    Stock_RootLayer         = var('Water stock in the root zone',0.)
    Stock_AB                = var('Water stock in the layers A and B',0.)
        
    @pcs    
    def pcs_WaterStatusInRootsLayer(self, 
        ):

        if self.locTime.isDayEnd : 
             
            self._dB    = self.B_Ads - (self._EB + self._UB) 
            self._dA    = self.A_Ads - (self._EA + self._UA) 
            self.w_A   += self._dA /  max(10/(self.w_FC-self.w_WP),self.Dp_Roots)   
            self.Dp_B  -= self._dB / max (2.5,(self.w_SAT- self.w_A))
            self._dC    = self.C_Ads - (self.discharge + self._EC + self._UC) 
            if self.Dp_B < 4 / (self.w_FC-self.w_WP) :
                self._dC   += (4 / (self.w_FC-self.w_WP) - self.Dp_B) *(self.w_SAT - self.w_FC)
                self.Dp_B =  4 / (self.w_FC-self.w_WP)
                 
            self.Dp_C  -= self._dC / (self.w_SAT - self.w_FC)
            self.w_RootLayer            = (\
                                        self.w_A * min (self.Dp_Roots, self.Dp_B)\
                                        + min(max(0,self.Dp_Roots -self.Dp_B) , self.Dp_C -self.Dp_B) * self.w_FC\
                                        + max(0,self.Dp_Roots-self.Dp_C)*self.w_SAT \
                                        )/ self.Dp_Roots 
            self.Stock_RootLayer         = self.w_RootLayer*self.Dp_Roots
            self.Stock_AB                = self.w_A * self.Dp_B + self.w_FC*(self.Dp_C-self.Dp_B)               
            self.MoistureDeficit         = max(0, min((self.w_FC - self.w_RootLayer ) / (self.w_FC - self.w_WP), 1)) 
            self.RootLayerWaterPotential = max (-1.8, (-1.0/self.VG_alpha)*((min(1.0,(max(self.w_RootLayer,self.w_RES) - self.w_RES*self.Correction)/(self.w_FC-self.w_RES)))**(-1.0/self.VG_m)-1.0)**(1.0-self.VG_m)/ 1000)                                           
            self.RhydSoil                = 2447 * (1.0+(self.VG_alpha * (-self.RootLayerWaterPotential) )**self.VG_n)**(self.VG_m/2.0) \
                                           / ((1.0-(self.VG_alpha   * (-self.RootLayerWaterPotential) )**(self.VG_n-1.0)*(1.0+(self.VG_alpha * (-self.RootLayerWaterPotential))**self.VG_n)**-self.VG_m)**2)
                                           # 2447is for conversion to  m2 h Mpa kgH2O-1