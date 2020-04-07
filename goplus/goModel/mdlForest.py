from goBases import * 		#Windows
#from ...goBases import * 	#LINUX

from mdlMicroClimate import MicroClimate
from ForestElements.mdlTreeStand import TreeStand
from ForestElements.mdlUnderStorey import UnderStorey
from ForestElements.mdlSoil import Soil
from ForestElements.mdlLeavesCohort import LeavesCohort

class Forest(ELT):
    '''Forest is an integrative ELT grouping the two vegetation layers ,
      soil layer, and  microclimates associated to each layers.
    It manages :
        - the order of processes evaluations for each of these components.
        - some flux between these components.
        - the ecosystem global fluxes
    '''
    
    #Outer elements
    locTime = eltOut('LocTime element')
    sunLocal = eltOut('SunLocal element')
    microclim  = eltOut('Upper forest MicroClimate')

    #Inner elements
    treeStand = eltIn(TreeStand)
    microclim_UnderStorey = eltIn(MicroClimate)
    underStorey = eltIn(UnderStorey)
    microclim_Soil = eltIn(MicroClimate)
    soil = eltIn(Soil)
    cohort=eltIn(LeavesCohort)
    
    def update(self):
        ''' triggers the update over the Forest inner ELT in function of the moment caracteristics'''
        
        #connect the inner ELT of the Forest
        if self.locTime.isSimulBeginning : 
            self.treeStand.locTime = self.locTime
            self.treeStand.sunLocal = self.sunLocal       
            self.treeStand.microclim = self.microclim       
            self.treeStand.microclim_under = self.microclim_UnderStorey
            self.treeStand.soil = self.soil
            self.treeStand.cohort = self.cohort
            
            self.underStorey.locTime = self.locTime
            self.underStorey.sunLocal = self.sunLocal
            self.underStorey.microclim = self.microclim_UnderStorey
            self.underStorey.microclim_under = self.microclim_Soil
            self.underStorey.soil = self.soil

            self.soil.locTime = self.locTime
            self.soil.microclim = self.microclim_Soil
            self.soil.treeStand = self.treeStand
            self.soil.underStorey = self.underStorey
            self.soil.forest = self

        #update the Trees layer
        self.treeStand.update()
        
        #update the microclimate properties impacted by treeStand canopy surface
        self.pcs_updateMicroclimatesImpactedByACanopy(
                                                    canopy = self.treeStand.canopy, 
                                                    upperMicroclim = self.microclim, 
                                                    underMicroclim = self.microclim_UnderStorey)

        #update the underStorey layer
        self.underStorey.update()
        
        #update the microclimates properties impacted by underStorey layer
        self.pcs_updateMicroclimatesImpactedByACanopy(
                                                    canopy = self.underStorey.canopy, 
                                                    upperMicroclim = self.microclim_UnderStorey, 
                                                    underMicroclim = self.microclim_Soil)
            
        #update the soil layer
        self.soil.update()
        
        #update the microclimates properties impacted by soil layer
        _soil_CS = self.soil.surface
        
        self.microclim_Soil.SWUp = _soil_CS.SW_Sct
        self.microclim_Soil.LWUp = _soil_CS.LW_Emi + _soil_CS.LW_Sct
    
        #Integratives Forest fluxes
        self.pcs_integrateForestFluxes()


    #FOREST FLUXES
    ETR = var('evapotranspiratioon (Kg_H2O /m2_soil /hour)')
    NEE = var('carbon net ecosystem exchange (g_C /m2_soil /hour)')
    Rnet = var('net radiation calculate as the ecosystem radiative balance (W /m2_soil)')
    RnetLayers = var('net radiation calculated as the sum of Rnet of each layer (W /m2_soil)') 
    H = var('sensible heat (W /m2_soil)')
    LE = var('latent heat (W /m2_soil)')
    INTER= var('Intercepted Rain (Kg_H2O /m2_soil /hour)') 
    T = var('Global Transpiration (Kg_H2O /m2_soil /hour)') 
    NPP= var('NPP (g_C /m2_soil /hour)') 
    GPP= var('GPP (g_C /m2_soil /hour)') 
    Reco= var('ecosystem respiration (g_C /m2_soil /hour)')    
    RAuto = var('Auttorophic Ecosystem Respiration  (g_C /m2_soil /hour)')

    
    #Carbon calculations
    SoilCarbon = var('Soil organic carbon as a sum of DPM, RPM, HUM and BIO (gC m-2_soil)')
    BiomCarbon = var('Biomass Carbon stock (trees + understorey (gC m-2_soil)')

    def pcs_integrateForestFluxes(self):
        _treeStand_CS = self.treeStand.canopy
        _underStorey_CS = self.underStorey.canopy
        _soil_CS = self.soil.surface
        _microclim = self.microclim
        
        self.ETR = self.soil.surface.ETR + _underStorey_CS.ETR + _treeStand_CS.ETR
        self.NEE = (self.treeStand.Rm +self.treeStand.Rg - _treeStand_CS.Assimilation )  \
                    + (self.underStorey.Rm + self.underStorey.Rg - _underStorey_CS.Assimilation ) \
                    + self.soil.carbonCycle.Rh
        self.Rnet = _microclim.SWDif + _microclim.SWDir - _microclim.SWUp + _microclim.LWDw - _microclim.LWUp 
        self.RnetLayers = _soil_CS.Rnet + _underStorey_CS.Rnet + _treeStand_CS.Rnet
        self.H = _soil_CS.H + _underStorey_CS.H + _treeStand_CS.H
        self.LE = _soil_CS.LE + _underStorey_CS.LE + _treeStand_CS.LE
        self.Reco = self.treeStand.Rm +self.treeStand.Rg + self.soil.carbonCycle.Rh + self.underStorey.Rg + self.underStorey.Rm # SM : added
        self.GPP = self.treeStand.canopy.Assimilation + self.underStorey.canopy.Assimilation    
        self.T = self.underStorey.canopy.Transpiration + self.treeStand.canopy.Transpiration
        self.INTER = self.ETR - self.T - self.soil.surface.ETR
        self.RAuto = self.treeStand.Rm + self.treeStand.Rg + self.underStorey.Rm + self.underStorey.Rg
        self.NPP = self.treeStand.canopy.Assimilation + self.underStorey.canopy.Assimilation - self.RAuto
        self.SoilCarbon = self.soil.carbonCycle.DPM + self.soil.carbonCycle.RPM + self.soil.carbonCycle.HUM + self.soil.carbonCycle.BIO + self.soil.carbonCycle.IOM
        self.BiomCarbon = (self.treeStand.Wa + self.treeStand.Wr) * self.treeStand.BiomassCarbonContent \
			   + self.underStorey.perennial.W * self.underStorey.perennial.BiomassCarbonContent \
			   + self.underStorey.foliage.W   * self.underStorey.foliage.BiomassCarbonContent \
        		   + self.underStorey.roots.W * self.underStorey.roots.BiomassCarbonContent \
			   + self.underStorey.roots.Cpool + self.underStorey.foliage.Cpool + self.underStorey.perennial.Cpool   

    def pcs_updateMicroclimatesImpactedByACanopy(self, canopy, upperMicroclim, underMicroclim):
        '''update the microclimates  properties impacted by underStorey layer'''
        
        upperMicroclim.SWUp = underMicroclim.SWUp - canopy.SWUp_Int + canopy.SW_Sct_Up

        upperMicroclim.LWUp = underMicroclim.LWUp - canopy.LWUp_Int + 0.5 * canopy.LW_Emi + canopy.LW_Sct_Up

        underMicroclim.SWDif = upperMicroclim.SWDif - canopy.SWDif_Int_f -canopy.SWDif_Int_w + canopy.SW_Sct_Dw
        underMicroclim.SWDir = upperMicroclim.SWDir - canopy.SWDir_Int_f -canopy.SWDir_Int_w
        underMicroclim.LWDw = upperMicroclim.LWDw - canopy.LWDw_Int + 0.5 * canopy.LW_Emi + canopy.LW_Sct_Dw
        
        underMicroclim.z_ref = canopy.height_surface
        underMicroclim.CO2 = upperMicroclim.CO2
        underMicroclim.u = canopy.u_surface
        underMicroclim.TaC = upperMicroclim.TaC
        underMicroclim.P = upperMicroclim.P
        underMicroclim.e = upperMicroclim.e
        underMicroclim.Rain = (upperMicroclim.Rain - canopy.InterceptedRain) + canopy.Dripping
        
        underMicroclim.update()
