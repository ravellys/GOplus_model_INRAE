from goBases import * #Windows OS
#from ....goBases import * #Linux OS
#from ForestElements.SoilElements.mdlSoilWaterCycle import  SoilWaterCycle
class SoilCarbonCycle(ELT):
    ''' Soil carbon decomposition adapted from the RothC model:
        - time step --> daily
        - a plowing factor is added to simulating the effect of soil operations
        - see Moreaux V. - 2012
        - one soil compartment is considered
    '''

    # Outer elements
    locTime     = eltOut('LocTime element')
    microclim   = eltOut('MicroClimate upper soil')
    treeStand   = eltOut('TreesStand element')
    underStorey = eltOut('UnderStorey element')
    Ts_resp     = var('soil temperature at depth of maximal respiration activity (degC)',)
    Ts_prof     = var('soil temperature at depth(degC)',)
    Ra          = var('autotrophic respiration of soil (gC /m2_soil /hour)')
    
    @pcs
    def update(self, 
        kTresp_Ta = param('coeffient in restore force of Ts_resp to Ta (-)'), 
        kTresp_Tp = param('coeffient in restore force of Ts_resp to Ts_prof (-)'), 
        ):
        
        #estimation of the soil temperature at 10 cm depth (2 restoring forces : Ta and Ts_prof)
        self.Ts_resp += kTresp_Ta * (self.microclim.TaC - self.Ts_resp) + kTresp_Tp * (self.Ts_prof - self.Ts_resp)
        self.Ts_prof = (self.Ts_prof * 500000.0 + self.Ts_resp) / (500000.0 + 1)

        #heterotrophic respiration from Roth 
        self.pcs_decomposition_RothC()

        #autotrophic respiration
#        self.Ra = self.treeStand.R_UnderGround + self.underStorey.R_UnderGround


    #vars
    HUM     = var('humified organic matter (gC /m2_soil)',0. )
    BIO     = var('microbial biomass (gC /m2_soil)',0.)
    DPM     = var('decomposable plant material (gC /m2_soil)',0.)
    RPM     = var('resistant plant material (gC /m2_soil)',0.)
    IOM     = var('resistant to decomposition carbon (gC /m2_soil)',0.)
    Rh      = var('CO2 product (gC /m2_soil /hour)',0.)#TODO : change time step evaluation to avoid init need
    HUM_age  = var('humified organic matter age (y)',0.)
    BIO_age  = var('microbial biomass age (y)',0.)
    DPM_age  = var('decomposable plant material age (y)',0.)
    RPM_age  = var('resistant plant material age (y)', 0.)
    IOM_age  = var('resistant to decomposition carbon age (y)',0.)
    Rh_age   = var('CO2 product age (y)',0.)#TODO : change time step evaluation to avoid init need
    PlowingFactor = var('soil carbon fraction affected by the plowing  [0-1] ',0.)
    PlowEffect    = var('amplification factor sof soil decomposition and mineralisation by plowing',0.)
 
    @pcs    
    def pcs_decomposition_RothC(self, 
        k_HUM = param('decomposition rate of HUM (/y)', 0.0), 
        k_BIO = param('decomposition rate of BIO (/y)',  0.0), 
        k_DPM = param('decomposition rate of DPM (/y)',  0.0), 
        k_RPM = param('decomposition rate of RPM (/y)',  0.0), 
        PlowEffect_HalfTime = param('half time of plowing effect (day)', 0.0), 
        ):
       
        #Daily evaluation of soil carbon 
        if self.locTime.isDayEnd : 
            
            _dage = 1.0 / 365.25
            _x= 1.67 * (1.85 + 1.6 * exp(-0.0786 * self.waterCycle.Clay))
            _RothC_xClay = _x/(1.0+_x) #clay constant effect on CO2 rate
            
            #evaluate empirical a,b,c factors 
            _a = 47.9 / (1 + exp(106 / (self.Ts_resp + 18.3)))
            _b = 0.2 + (1 - 0.2) * (1 - self.waterCycle.MoistureDeficit)
            _c = 0.6
            _d = (1.0 - self.PlowingFactor + self.PlowEffect * self.PlowingFactor )
            _abcd = _a * _b * _c * _d * _dage
            
            #Decomposition 
            _DPM_dec = self.DPM * (1 - exp(-k_DPM * _abcd))
            _RPM_dec = self.RPM * (1 - exp(-k_RPM * _abcd))
            _BIO_dec = self.BIO * (1 - exp(-k_BIO * _abcd))
            _HUM_dec = self.HUM * (1 - exp(-k_HUM * _abcd))
            _dec = _DPM_dec + _RPM_dec + _BIO_dec + _HUM_dec
            _dec_age = (_DPM_dec * (self.DPM_age + _dage) + _RPM_dec * (self.RPM_age + _dage) + _BIO_dec * (self.BIO_age + _dage) + _HUM_dec * (self.HUM_age + _dage)) / _dec
            
            #Decomposition allocation
            _to_CO2_rate = min(1, _RothC_xClay * ( (1 - self.PlowingFactor) +  self.PlowingFactor * self.PlowEffect))
            _to_BIO_rate = 0.46 * (1 - _to_CO2_rate)
            _to_HUM_rate = 0.54 * (1 - _to_CO2_rate)
            
            #New pool content
            self.DPM    = self.DPM - _DPM_dec 
            self.RPM    = self.RPM - _RPM_dec 
            self.BIO    = (self.BIO - _BIO_dec) + _dec * _to_BIO_rate
            self.HUM    = (self.HUM - _HUM_dec) + _dec * _to_HUM_rate
            _BIO        = self.BIO
            _HUM        = self.HUM
            self.waterCycle.SOC = (self.HUM + self.DPM + self.RPM) / (self.waterCycle.Dp_Roots * self.waterCycle.BD)* 100 / 1000000 #unit is pct of soil mass. Organic carbon is supposed to be located within the root layer
            
            #New pool age
            self.DPM_age = self.DPM_age + _dage 
            self.RPM_age = self.RPM_age + _dage
            self.BIO_age = ((_BIO - _BIO_dec) * (self.BIO_age + _dage) + _dec * _to_BIO_rate * _dec_age) / self.BIO
            self.HUM_age = ((_HUM -_HUM_dec) * (self.HUM_age + _dage) + _dec * _to_HUM_rate * _dec_age) / self.HUM
          
            #Heterotrophic respiration 
            self.Rh     = _dec * _to_CO2_rate / 24.
            self.Rh_age = _dec_age

            #Plowing effect attenuation
            self.PlowEffect = max(1, self.PlowEffect * 0.4 ** (1.0 / (PlowEffect_HalfTime- 1)))
    
    def incorporateACarbonLitter(self, 
        carbonLitter,                   #litter carbon  mass (gC /m2_soil)
        carbonLitter_DPM_RPM_ratio,     #ratio of decomposable over resistant parts of carbon litter (-)
        carbonLitter_age,               #carbon age of carbonLitter (year)
        ):
        '''to be called by other model element to specify their contribution to soil carbon input
        '''
        
        if carbonLitter > 0. :
            _IDPM = carbonLitter * carbonLitter_DPM_RPM_ratio / (1 + carbonLitter_DPM_RPM_ratio)
            self.DPM_age =  (self.DPM * self.DPM_age + _IDPM * carbonLitter_age) / (self.DPM + _IDPM)            
            self.DPM += _IDPM

            _IRPM = carbonLitter * 1.0 / (1 + carbonLitter_DPM_RPM_ratio)
            self.RPM_age = (self.RPM  * self.RPM_age + _IRPM * carbonLitter_age) / (self.RPM +  _IRPM)
            self.RPM += _IRPM


