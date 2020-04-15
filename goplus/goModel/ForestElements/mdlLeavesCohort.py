from goBases import * 		# Windows
# from ...goBases import *	# Linux 
import os,sys
basePath  = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")

class LeavesCohort(ELT):

    #Outer elements
    locTime = eltOut('LocTime element')
    treeStand = eltOut('treeStand element')

    #variables
    Year = var('year of the cohort emergency')
    HeatSum = var('cumulated degree day (degC day)', 0.0)
    DateOfBB = var('date of emergency since start of simul (date)', -9999)
    DOYOfBB = var('DOY of emergency (budburst stade) (day of year)', -9999)
    Expansion = var('foliage expansion level [0-1] (m2_leaf /m2_leaf)', 0)
    Retained = var('Foliage retention level [0-1] (m2_leaf /m2_leaf)', 1)
    Weight = var('biomass (kg_DM /m2_soil)', 0)
    LeafFall = var('leaf biomass fall (kg_DM /m2_soil /day)',)
    FoliageArea = var('area (m2_leaf /m2_soil)',)
    LAI = var('leaf area index (m2_projected_leaf /m2_soil)')
    SLA = param('specific leaf area (m2_LeafArea /Kg_DM)')
    SumSW=var('accumulated SW radiation from bud burst until DOY 258 (W.m-2)')
    DateOfS = var('date of senesence (date)',0.)
    _GSL=var('life duration of broadleaved cohort of leaves (days)',0)
    cohortWeightMaxOfSoil = var('CohortWeightMax by soil area. now defined and fixed for a cohort(kg d.m. m-2)', 0.0)
  
   
    def update_daily(self, 
        LAI_LeafArea_ratio = param('LAI on LeafArea ratio Chen et al. Can J for Res 1991 (m2_LAI /m2_LeafArea)', 0.), 
        _CohortWeightMax   = private('CohortWeightMax by tree and soil area ', ELT),
        ):
        
#==============================================================================
#New cohort
        if self.DateOfBB== -9999:
            
      #Each cohort has a fixed biomass value 
            _CohortWeightMax.ofTree = {tree: tree.OneYearCohortWeightMax for tree in self.treeStand} #store the CohortWeightMax of all trees 
            if self.treeStand.treesCount > 0:
                self.cohortWeightMaxOfSoil = sum(_CohortWeightMax.ofTree[_tree] for _tree in self.treeStand) / self.treeStand.Area
            else :
                    #trick  to allow a treeStand functionning without trees (clear-cutting period)
               self.cohortWeightMaxOfSoil = 0.001
               
      # accumulate forcing unit or heatsum
            if self.treeStand.Species=='Fsylvatica': #(from Kramer 1994)
                if self.treeStand.Sfor   >= self.treeStand.Fcrit :
                    self.DateOfBB = self.locTime.Now-1
                    self.DOYOfBB  = self.locTime.DOY-1
            if self.treeStand.Species == 'Ppinaster': #(from Desprez loustau and Dupuis, ASF, 1994)
                if  self.HeatSum  > self.treeStand.BBHeatSum:
                    self.DateOfBB = self.locTime.Now-1
                    self.DOYOfBB  = self.locTime.DOY-1 
            if self.treeStand.Species == 'DouglasFir': #(from Harrington et al. FEM 2004)
                if  self.treeStand.Sfor >= 357 + 5123 * exp(-0.0016*self.treeStand.Sch) :
                    self.DateOfBB = self.locTime.Now-1
                    self.DOYOfBB  = self.locTime.DOY-1
            self.Expansion = 0.0
            self.LeafFall  = 0.0
            self.Retained  = 1.0
            self.Weight    = 0.0
            self.FoliageArea = 0.0001
            self.LAI       = 0.00001
#==============================================================================
# Cohort lifecycle                    
        else :
            
    #Pinus and Douglas fir        
            #correction of the cohort leafweight when thetree stand is thinned (evergreen species only)
            if self.treeStand.Species=='Ppinaster' or self.treeStand.Species == 'DouglasFir':
                if self.treeStand.Tree_Log == 1  and self.locTime.DOY == 1 :
                    self.cohortWeightMaxOfSoil  *= 1 / (1 + self.treeStand.Foliage_Fraction_Removed)
                else :
                    self.treeStand.Tree_Log = 0
                    self.treeStand.Foliage_Fraction_Removed = 0
                _Jref = self.locTime.Now - self.DateOfBB      #Number of days since emergency
            #update the proportion of needles retained 
                if _Jref < (self.treeStand.k_1*self.treeStand.LifeDuration) :
                    self.Retained = 1
                elif _Jref < (self.treeStand.k_2*self.treeStand.LifeDuration) :
                    self.Retained = 1 - 0.2 * (_Jref - self.treeStand.k_1*self.treeStand.LifeDuration) / ((self.treeStand.k_2-self.treeStand.k_1)*self.treeStand.LifeDuration)
                elif _Jref < (self.treeStand.k_3*self.treeStand.LifeDuration) :
                    self.Retained = 0.8
                elif _Jref < self.treeStand.LifeDuration :
                    self.Retained = 0.8 * (1 - (_Jref - self.treeStand.k_3*self.treeStand.LifeDuration) / ((1-self.treeStand.k_3)*self.treeStand.LifeDuration))
                else :
                    self.Retained = 0   
            #update the needle expansion rate
                if _Jref < 0 :
                    self.Expansion = 0
                elif _Jref < 92 :
                    self.Expansion = _Jref / 92
                else :
                    self.Expansion = 1.0
    
    #Fagus
            elif self.treeStand.Species=='Fsylvatica':       
                #increment the amount of SW received since bud burst date and zero this amount after DOY 258.        
                self.SumSW += self.treeStand.MeanSWDir+self.treeStand.MeanSWDir
                # life duration as a function of accumulated SW radiation (Picart Deshors, unpublished)
                if self.locTime.DOY==258:
                    self._GSL= self.treeStand.k_GSL1*self.SumSW + self.treeStand.k_GSL2
                    self.DateOfS= self._GSL+self.DOYOfBB
                if self.locTime.DOY>258:
                    self.SumSW=0
                ##################################################
                #update the natural expansion rate 
                ################################################## 
                _Sumref = self.DOYOfBB
                _Growth50 = _Sumref + self.treeStand.DG50
                _GrowthNatural = 1./(1.+((1./self.treeStand.Gref)-1)**((self.locTime.DOY - _Growth50)/(_Sumref - _Growth50)))
                _GrowthMax = 1.
                _Growth =_GrowthNatural
                self.Expansion = self.Expansion + _Growth*(_GrowthMax - self.Expansion)
                
                ##################################################
                #Leaf shedding
                ##################################################           
                if self.DateOfS>0:
                    _Lref = self.DateOfS
                    _L50 =_Lref+self.treeStand.DS50
                    _LostNatural = 1./(1.+((1./self.treeStand.Sref)-1.)**((self.locTime.DOY-_L50)/(_Lref-_L50)))
                    self.Retained = self.Retained*(1.0 - _LostNatural)
                    
        if  self.Retained<0.025:
            self.Weight 	  = 0.0
            self.Area	  = 0.00001 
            self.LAI       = 0.00001
            self.LeafFall  = 0.        

#==============================================================================                
        #update cohort leaf  biomass and area
        self.LeafFall       = max(0., self.Weight -self.Retained * self.Expansion *  self.cohortWeightMaxOfSoil)       
        self.Weight         = self.Retained * self.Expansion * self.cohortWeightMaxOfSoil
        self.FoliageArea    = self.treeStand.SLA * self.Weight
        self.LAI            = self.FoliageArea * self.treeStand.LAI_LeafArea_ratio
        
        #To check cohort life cycles. Create a csv file including each cohort
#        z = str(self.locTime.Y) + str(",") +str(self.locTime.DOY) + str(",") + str(self.FoliageArea ) + str(",") + str(self.LAI) +  str(",") + str(self.DOYOfBB) + str(",") + str(self.DateOfBB) \
#        + str(",") + str(self.cohortWeightMaxOfSoil) + str(",") + str (self.Retained) + str(",") + str(self.SumSW)+ str(",") + str (self.treeStand.Sfor)  + str(",") + str (self.treeStand.Sch) + str(",") + str (self.treeStand.Tree_Log)  + str(",") + str (self.treeStand.Foliage_Fraction_Removed)
#        paraCohortFilePath = os.path.join(basePath, '..', '..', 'Output_files', 'Foliage_Cohorts.csv')
#        with open(paraCohortFilePath,'a') as c:
#            c.write('%s\n' % z)
#        c.closed

#==============================================================================
