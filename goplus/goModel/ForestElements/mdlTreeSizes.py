from goBases import *        # Windows
# from ...goBases import *    #LINUX


# This module calculates the individual tree characteristics: increment in diameter and height, dry matter pools of stem, branches, foliage, and roots.

import  random, math
class TreeSizes(ELT):
    
    
# Outer elements
    locTime = eltOut('LocTime element')
    treeStand = eltOut('treeStand element')

##VARIABLES====================================================================

    ## Biomass production   allocation
    
    WaProducted = var('Aerial biomass producted (Kg_DM tree-1 year-1)', 0.)
    WrProducted = var('Root biomass producted (Kg_DM tree-1 year-1)', 0.)

    ## Biomass state variables   
    
    Wa                  = var('aerial weight (Kg_DM tree-1)', 0.1)
    Wr                  = var('root weight (Kg_DM tree-1 ', 0.1)
    W                   = var('total tree weight (Kg_DM tree-1)',0.)
    WStem               = var('stem weight (kg_DM.tree-1)', 0.0)
    WStemLastYear       = var('stem weight one year before(kg_DM.tree-1)', 0.)
    WBranch             = var('branch dry mass (kg DM .tree-1)', 0.)
    WTapRoot            = var('taproot weight (Kg_DM.tree-1)', 0.)
    WCoarseRoot         = var('coarse root weight (kg_DM.tree-1)', 0.) 
    WSmallRoot          = var('small root weight (kg_DM.tree-1)', 0.) 
    WFineRoot           = var('fine root weight (kg_DM.tree-1)', 0.)     
    LeafWeight          = var('total leaf weight (kg_DM.tree-1)', 0.)
    _LeafArea           = var('total leaf area  (m2.tree-1)', 0.)
    OneYearCohortWeightMax = var('one year old cohort weight max (kg_DM.tree-1)', 0.)
    _CohortWeightMax    = var('maximal mass of needles/leaves of a cohort (kg_DM.tree-1 )',0.)
    
    ## Live fraction of tree parts
    
    _PaliveStem         = var('Fraction of living tissues in the tree stem biomass',0.)
    _PaliveBranch       = var('Fraction of living tissues in the tree branch biomass',0.)
    _PaliveTapRoot      = var('Fraction of living tissues in the tree tap root',0.)
    _PaliveCoarseRoot   = var('Fraction of living tissues in the tree coarse roots',0.)
    _PaliveSmallRoot    = var('Fraction of living tissues in the tree small roots',0.)

    ## Senescence variables

    BranchSenescence    = var('branch senescence (Kg_DM tree-1 year-1)', 0.)
    RootSenescence 	    = var('root senescence (Kg_DM tree-1 year-1)', 0.)
    LeafSenescence 	    = var('leaf senescence (Kg_DM tree-1 year-1)', 0.)

    ## Dendrometric variables

    DBH 	     = var('diameter at breast height (cm)', 0.)
    DBHOld 	= var('diameter at breast height of the previous year (cm)',0.)
    Height 	= var('tree height (m)', 0.)
    Height_old = var('tree height (m) of the previous year', 0.)
    Prod_Vol 	= var('Timber production  (m3.tree-1.y-1)',0.)
    BasalArea 	= var('basal area of a tree (m2 tree-1)',0.)
    
    ##Total tree N content
    
    N          = var('N content per tree (gN.tree-1)',0.)
    
    
# COMPUTATIONS=================================================================
    
    @pcs
    def update(self, 
               _flag = private('Flag to manage some initialisations', ELT), 
               ):
        '''update the values of individual tree biomass and size
        '''
##update total tree biomass (kg_DM. tree-1)
        self.Wa += self.WaProducted - self.BranchSenescence - self.LeafSenescence
        self.Wr += self.WrProducted - self.RootSenescence
        self.W   = self.Wa + self.Wr
        S_y_1    = self.WStem #retain the previous value of stem biomass  to calculate its net annual increment (prod_vol).
        
        #short names
        _Age_aerial = self.container.Age_aerial
        _Wa = self.Wa
        _Wr = self.Wr

## Fagus allometry from Wutzler et al. 2008, Tab 6 and Le Moguedec and Dhote (2011) 
        if self.container.Species == 'Fsylvatica' :         
            C_0         = self.container.k_DBH_1 + 2.39e-4 * 30 - 4.68e-6 * self.container.sunLocal.Altitude
            C_1         = self.container.k_DBH_2
            C_2         = self.container.k_DBH_3 + 4.06e-4 *_Age_aerial
            self.DBH    = (self.Wa /C_0 *  1/(self.Height**C_2))**(1/C_1)
            _m                          = 1.218
            _K                          = 67.3 
            _Cm                         = math.exp((1.0+_m)*(1-math.log10(1.0+_m)))
            _H0                         = _K*math.exp(-((math.log10(_K/1.3))**(-_m)+((0.4*_m*_Cm)/_K)*(_Age_aerial-5.0))**(-1.0/_m))
            _alpha                      = _H0 - 1.3 + math.pi*0.412*self.DBH
            self.Height                 = 1.3+(_alpha - (_alpha**2 - 4*math.pi*0.412*0.98764*(_H0 - 1.3)*self.DBH)**0.5)/(2*0.98764)
            self.LeafWeight             = self.container.k_Wn_1 *(self.DBH**self.container.k_Wn_2)* (self.Height**self.container.k_Wn_3) 
            self.OneYearCohortWeightMax = self.LeafWeight

            if self.DBH < 4.0 : 
                self.WCoarseRoot    = 0
            else :
                self.WCoarseRoot    =  self.Wr * max (0, self.container.k_WCoarseRoot_2 - self.container.k_WCoarseRoot_3 * math.exp(- self.container.k_WCoarseRoot_4*self.DBH))
   
            self.WFineRoot          = self.Wr * min (self.container.k_WFineRoot_1,   self.container.k_WFineRoot_2 * self.DBH**(- self.container.k_WFineRoot_3))
            self.WTapRoot           = (self.Wr - self.WCoarseRoot - self.WFineRoot)* (( self.container.k_WTapRoot_1   *self.DBH + self.container.k_WTapRoot_2)   / ((self.container.k_WTapRoot_1 * self.DBH    + self.container.k_WTapRoot_2)   + (- self.container.k_WTapRoot_3 * self.DBH  + self.container.k_WTapRoot_4)))
            self.WSmallRoot         = (self.Wr - self.WCoarseRoot - self.WFineRoot)* ((- self.container.k_WSmallRoot_3*self.DBH + self.container.k_WSmallRoot_4) / ((self.container.k_WSmallRoot_1 * self.DBH  + self.container.k_WSmallRoot_2) + (- self.container.k_WSmallRoot_3 * self.DBH + self.container.k_WSmallRoot_4)))
            Cs_0                    = self.container.k_Wstem_1 
            Cs_1                    = self.container.k_Wstem_2
            Cs_2                    = self.container.k_Wstem_3 
            self.WStem              = Cs_0 * (self.DBH**Cs_1) * (self.Height ** Cs_2)
            self.WBranch            = 0.122* self.DBH ** 3.09 * self.Height ** (-0.151- 0.0309*30- 0.000987 * self.container.sunLocal.Altitude + 0.0000306* 30* self.container.sunLocal.Altitude)
       
## Pinus Pinaster allometry (Shaiek et al. 2011) 
        elif self.container.Species == 'Ppinaster':
            self.DBH    = self.container.k_DBH_1*(_Wa**self.container.k_DBH_2)*(max(1, _Age_aerial)**self.container.k_DBH_3)
            self.Height = self.container.k_Height_1*( _Wa** self.container.k_Height_2 )*(max(1, _Age_aerial)**self.container.k_Height_3) 
            if _Age_aerial < 4.0 :
                self.LeafWeight             = self.container.k_Wn_1 *(_Wa**self.container.k_Wn_2 )*(max(1, _Age_aerial)**self.container.k_Wn_3)
                self.OneYearCohortWeightMax = self.LeafWeight/max(1, _Age_aerial)
            else:
                self.OneYearCohortWeightMax = self.container.k_Wn1_1*(_Wa**self.container.k_Wn1_2)*(_Age_aerial **self.container.k_Wn1_3)   
                self.LeafWeight             = self.container.k_Wn_1*(_Wa**self.container.k_Wn_2)*(_Age_aerial**self.container.k_Wn_3)          
                self.WTapRoot               = _Wr * min(self.container.k_WTapRoot_1, self.container.k_WTapRoot_2 * self.DBH**(- self.container.k_WTapRoot_3))
            if self.DBH > 0.0 :
                self.WCoarseRoot = _Wr *max(self.container.k_WCoarseRoot_1, self.container.k_WCoarseRoot_2 * log(self.DBH) - self.container.k_WCoarseRoot_3 )
                self.WSmallRoot  = _Wr *min(self.container.k_WSmallRoot_1,  self.container.k_WSmallRoot_2   * self.DBH ** -self.container.k_WSmallRoot_3  )
                self.WFineRoot   = _Wr - self.WTapRoot - self.WCoarseRoot- self.WSmallRoot
                self.WStem       = self.container.k_WStem_1*(_Wa**self.container.k_WStem_2)*(_Age_aerial**self.container.k_WStem_3) * self.Height ** self.container.k_WStem_4
            else:
                self.WCoarseRoot = 0.
                self.WSmallRoot  = 0.
                self.WFineRoot   = 0.
            self.WBranch = max(0, _Wa + self.BranchSenescence - self.WStem-self.LeafWeight)   

## Allometric model from Gholz et al. and Achat et al. 2019.
                      
        elif self.container.Species == 'DouglasFir':       
            self.DBH    = self.container.k_DBH_1*(_Wa**self.container.k_DBH_2)*(max(1, _Age_aerial)**self.container.k_DBH_3)
            self.Height = self.container.k_Height_1*( _Wa** self.container.k_Height_2 )*(max(1, _Age_aerial)**self.container.k_Height_3) 
            if _Age_aerial < 4:
                self.LeafWeight             = self.container.k_Wn_1 *(_Wa**self.container.k_Wn_2 )*(max(1, _Age_aerial)**self.container.k_Wn_3)
                self.OneYearCohortWeightMax = self.LeafWeight/max(1, _Age_aerial)
            else:
                self.OneYearCohortWeightMax = self.container.k_Wn1_1*(_Wa**self.container.k_Wn1_2)*(_Age_aerial **self.container.k_Wn1_3)   
                self.LeafWeight             = self.container.k_Wn_1*(_Wa**self.container.k_Wn_2)*(_Age_aerial**self.container.k_Wn_3)          
            if self.DBH > 0 :
                self.WCoarseRoot = _Wr *max(self.container.k_WCoarseRoot_1, self.container.k_WCoarseRoot_2 * log(self.DBH) - self.container.k_WCoarseRoot_3 )
                self.WFineRoot   = _Wr *min(self.container.k_WFineRoot_1, self.container.k_WFineRoot_2 * self.DBH ** (-self.container.k_WFineRoot_3))
                self.WSmallRoot  = (_Wr -self.WCoarseRoot - self.WFineRoot) * (-self.container.k_WTap_SmallRoot_3*self.DBH + self.container.k_WTap_SmallRoot_4) / \
                                  ((-self.container.k_WTap_SmallRoot_1*self.DBH +self.container.k_WTap_SmallRoot_2) + (-self.container.k_WTap_SmallRoot_3 * self.DBH +self.container.k_WTap_SmallRoot_4))

                self.WTapRoot   = (_Wr -self.WCoarseRoot - self.WFineRoot) * (-self.container.k_WTap_SmallRoot_1*self.DBH + self.container.k_WTap_SmallRoot_2) / \
                                  ((-self.container.k_WTap_SmallRoot_1*self.DBH +self.container.k_WTap_SmallRoot_2) + (-self.container.k_WTap_SmallRoot_3 * self.DBH +self.container.k_WTap_SmallRoot_4))
                self.WStem      = self.container.k_WStem_1*(_Wa**self.container.k_WStem_2)
            else:
                self.WCoarseRoot    = 0.
                self.WSmallRoot     = 0.
                self.WFineRoot      = 0.
            self.WBranch = max(0, _Wa + self.BranchSenescence - self.WStem-self.LeafWeight)   
            
## Generic parts:             
###Stem volume production, basal area
        self.Prod_vol          = (self.WStem - S_y_1) / self.container.wood_density /1000 
        self.BasalArea         = math.pi*(self.DBH*0.01/2)**2      

###Calculation of the mass of stem sapwood (alive).                 
        self._LeafArea      = self.LeafWeight * self.container.SLA 
        self._Al_As_ratio   = self.container._Al_As_ratio_slope * self.Height ** (self.container._Al_As_ratio_exp)   + self.container._Al_As_ratio_int     #AL:As ratio decreases linearly with tree height Mc Dowell 2002
        _SA                 = self._LeafArea / self._Al_As_ratio /10000                                                           #CROSS SECTIONAL AREA OF SAPWOOD m2
        if self.Height<6.0 : #Crown length fixed at 6m; To be improved, eg. see Sharma et al. PLOS ONe, 2017https://doi.org/10.1371/journal.pone.0186394
            self._PaliveStem = 1.0 
        else:
            _SV=_SA * self.container.shape_factor*self.Height
            self._PaliveStem     =min(1.0, _SV/((self.DBH/200)**2*math.pi*self.Height*self.container.shape_factor)) # THis is actually the volume ratio, assuming that heartwood denisty = sapwood density
            
        self._PaliveBranch          = max(self.container._PaliveBranch_min, self.container._PaliveBranch_max - _Age_aerial/100*(self.container._PaliveBranch_max - self.container._PaliveBranch_min))#100 is for the maximal age in yrs
        self._PaliveTap_SmallRoot   = max(self.container._PaliveTapRoot_min, self.container._PaliveTapRoot_max - self.container.Age/100*(self.container._PaliveTapRoot_max - self.container._PaliveTapRoot_min))
        self._PaliveCoarseRoot      = max(self.container._PaliveCoarseRoot_min, self.container._PaliveCoarseRoot_max - self.container.Age/100*(self.container._PaliveCoarseRoot_max - self.container._PaliveCoarseRoot_min))
        self._PaliveSmallRoot       = max(self.container._PaliveSmallRoot_min, self.container._PaliveSmallRoot_max - self.container.Age/100*(self.container._PaliveSmallRoot_max - self.container._PaliveSmallRoot_min))
      
###Calculation of the total nitrogen content of a tree, used for allocating maintenance respiration among trees.
        
        self.N              = self._PaliveStem*self.container._NStem*self.WStem + \
                              self._PaliveBranch*self.container._NBranch * self.WBranch+\
                              self.container._PaliveLeaf*self.LeafWeight * self.container._Nleaves +\
                              self._PaliveTapRoot * self.container._NTapRoot *self.WTapRoot +  \
                              self._PaliveCoarseRoot * self.container._NCoarseRoot *self.WCoarseRoot  + \
                              self._PaliveSmallRoot * self.container._NSmallRoot * self.WSmallRoot +\
                              self.container._PaliveFineRoot * self.container._NFineRoot *self.WFineRoot
                        