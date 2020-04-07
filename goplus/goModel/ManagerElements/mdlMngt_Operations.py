from goBases import * 
from goModel.ForestElements.mdlTrees import Trees #Windows
#from ...goBases import * #LINUX
#from ..ForestElements.mdlTrees import Trees #LINUX
import random
#from ForestElements.mdlTrees import Trees


class Manager(ELT):
    
    # Outer  elements
    locTime = eltOut('LocTime element')
    forest  = eltOut('Forest element')

    #group of inner elements
    Cut_Trees = eltIn(Trees)

    #variables  related to the trees harvested 
    harvest_W           = var('Total biomass havested kg dm ha-1 yr-1')
    harvest_WStem       = var('Stem harvested kg dm ha-1 yr-1')
    harvest_WBranch     = var('Branch harvested kg dm ha-1 yr-1')
    harvest_WTapRoots   = var('Taproot harvested kg dm ha-1 yr-1')
    NbCut_Trees         = var('Nb of trees cut  ha-1 yr-1')
    harvest_DBHmean     = var('mean DBH of harvested trees (cm)')
    harvest_DBHquadratic = var('mean DBH2 of harvested trees (cm)')
    harvest_DBHsd       = var('standard deviation of harvested trees (cm)')
    harvest_HEIGHTmean  = var('mean height of harvested trees (m)')
    harvest_HEIGHTsd    = var('Std dev of the Height of harvested trees (m)')
    harvest_basalArea   = var('Basal area of harvested trees m2 ha-1')
    seedingYear      = var('date of the seeding cut (yyyy)')    
    lastThinningYear    = var('date of the previous thinning (yyyy)') 
    FirstThinning       = var('boolean of the firest thinning event',) 
    clearcuts           = var('number of previous clearcuts')
    thinnings           = var('number of previous thinnings')
    
    
    def update(self):
        '''Manage the sylvicultural interventions'''
        
        self.harvest_W          = 0.
        self.harvest_WStem      = 0.
        self.harvest_WBranch    = 0.
        self.harvest_WTapRoot   = 0.
        self.harvest_WFoliage   = 0.
        self.NbCutTrees         = 0.
        self.harvest_DBHmean    = 0.
        self.harvest_DBHsd      = 0.
        self.harvest_DBHquadratic = 0.
        self.harvest_HEIGHTmean = 0.
        self.harvest_HEIGHTsd   = 0.
        self.harvest_basalArea  = 0.
       
        del self.Cut_Trees [:]
        
        if self.locTime.isSimulBeginning:
            self.lastThinningYear   = self.locTime.Y - 10
            self.thinnings          = 0        
            self.seedingYear     = self.locTime.Y - self.forest.treeStand.Age - 5
            self.FirstThinning      = False
        
        
        if self.locTime.isYearEnd:
            self.do_management()
            self.forest.treeStand.pcs_SetSizes() 
            
            if self.forest.treeStand.treesCount==0:
                self.forest.treeStand.update()
                
    def do_management(self):
        '''Manage the sylvicultural interventions : this method must be overwrite do to something'''
        print ('error if management implemented')
        pass
    
    def RotationYear(self) :
        '''year in the rotation. Return a value only if isYearEnd.  Suppose :
            - even-aged trees
            - 1 year of bare ground between 2 successive stands
        '''
        if self.locTime.isYearEnd:
            if len(self.forest.treeStand)>0:
                return self.forest.treeStand.RotationYear +1
            else:
                try:
                    return self.locTime.Y - self.lastThinningYear -1
                except:
                    return 0.0
        else:
            return -9999.9

            
#Operations####################################################################

    def do_Density_Thinning (self, ThinFactor, densityObjective):
        '''Select the trees to be cut. 
            All old  marks are cleared.
        '''
        
        #delete previous list of cut trees
        del self.Cut_Trees[:]
        
        #create a sorted list of the trees in function of their aerial biomass
        _sortedTrees = sorted(self.forest.treeStand,  key = (lambda tree: tree.Wa))
        
        #random generator initialisation 
        random.seed(len(_sortedTrees))     
        self.Cut_Trees=[]        
        #select tree until stopperTest ==True, add it to thinnedTrees        
        _nbtreesObjective = densityObjective*self.forest.treeStand.Area/10000.
        while len(_sortedTrees)> _nbtreesObjective :
            _tree = _sortedTrees[int((random.random() ** ThinFactor) * len(_sortedTrees))]
            self.Cut_Trees +=  [ _tree]
            _sortedTrees.remove(_tree)
            self.forest.treeStand._exclude_tree( _tree)
        
        self.thinnings += 1
        self.lastThinningYear= self.locTime.Y
        self.FirstThinning = True
        
            
    def do_RDI_Thinning(self, RDIObjective,ThinFactor):
        ''' model of thinning given in the paper Le Moguedec and Dhote 2002 An For S , Bellassen et a.  2011 Ecol Mod, Guillemot et al. (2014) Annals of botany
            rdi is the relative density index'''
        
        #delete previous list of cut trees
        del self.Cut_Trees[:]
        
        #sorted list of the trees in function of their aerial biomass
        _sortedTrees = sorted(self.forest.treeStand,  key = (lambda tree: tree.Wa))
        
        #random generator initialisation 
        random.seed(len(_sortedTrees))     

        #Select tree until stopperTest ==True, add it to thinnedTrees
        self.Cut_Trees=[]
        while self.forest.treeStand.RDI > RDIObjective and len(_sortedTrees)>1:
            _tree = _sortedTrees[int((random.random() ** ThinFactor) * len(_sortedTrees))]
            self.Cut_Trees +=  [ _tree]
            _sortedTrees.remove(_tree)
            self.forest.treeStand._exclude_tree( _tree)

        self.thinnings += 1
        self.lastThinningYear= self.locTime.Y
        self.FirstThinning = True
 
          
    def do_BA_Thinning(self, BAobj, ThinFactor):
        "thinning based on basal area"
        

        _treeStand = self.forest.treeStand        
        #create a sorted list by increasing order of the trees in function of their aerial biomass 
        _sortedTrees = sorted(_treeStand,  key = (lambda tree: tree.Wa))
        
        #choose tree until Objective reached, add it to cuttedTrees.
        self.Cut_Trees=[]
        while self.forest.treeStand.BasalArea > BAobj :         
            _tree= _sortedTrees[int((random.random() ** ThinFactor) * len(_sortedTrees))]
            self.Cut_Trees +=  [ _tree]
            _sortedTrees.remove(_tree)
            self.forest.treeStand._exclude_tree( _tree)
        
        self.thinnings += 1    
        self.lastThinningYear= self.locTime.Y
        self.FirstThinning = True
        
    def do_Clearcut(self):
        _sortedTrees = sorted(self.forest.treeStand,  key = (lambda tree: tree.Wa))
        
        self.Cut_Trees=[]
        for _tree in range(len(self.forest.treeStand.trees)):
            _trees = _sortedTrees[ _tree]
            self.Cut_Trees += [ _trees]
            self.forest.treeStand._exclude_tree( _trees)           
            
        self.lastThinningYear =  self.locTime.Y
        self.clearcuts += 1
        self.FirstThinning = True



    def do_Logging(self, harvestStem = True, harvestBranchWood = False, harvestTapRoot = False, harvestStump = False, harvestFoliage = False):
        '''Cut marked trees and harvest specified compartments.
            Residual biomass is allocate  to litter.
        '''
        
        _standArea = self.forest.treeStand.Area
        _incorporateACarbonLitter = self.forest.soil.carbonCycle.incorporateACarbonLitter
        _KgMs_by_tree_to_gC_by_m2_soil =self.forest.treeStand.BiomassCarbonContent / _standArea
        
        for _tree in self.Cut_Trees:
            
            # biomass management
            if harvestStem:
                self.harvest_WStem += _tree.WStem /_standArea
                
            else:
                _incorporateACarbonLitter ((_tree.WStem) * _KgMs_by_tree_to_gC_by_m2_soil, self.forest.treeStand.Wood_DPM_RPM,  _tree.container.Age / 2)

            if harvestFoliage:
                self.harvest_WFoliage += _tree.LeafWeight /_standArea
            else:
                _incorporateACarbonLitter ((_tree.LeafWeight) * _KgMs_by_tree_to_gC_by_m2_soil, self.forest.treeStand.Leaf_DPM_RPM, self.forest.treeStand.Leaf_Age)

            if harvestBranchWood: 
                self.harvest_WBranch += (_tree.WBranch) /_standArea
            else:
                _incorporateACarbonLitter ((_tree.WBranch) * _KgMs_by_tree_to_gC_by_m2_soil, self.forest.treeStand.Wood_DPM_RPM, self.forest.treeStand.Wood_Age) #DPm_RPM_ratio modifie le 3/03/2016 (avant 1./4)
            
            if harvestTapRoot: 
                self.harvest_WTapRoot += _tree.WTapRoot /_standArea
                _incorporateACarbonLitter( (_tree.WFineRoot + _tree.WSmallRoot+ _tree.WCoarseRoot) * _KgMs_by_tree_to_gC_by_m2_soil, self.forest.treeStand.Root_DPM_RPM, self.forest.treeStand.Root_Age)  
            else :
                _incorporateACarbonLitter( (_tree.WSmallRoot + _tree.WCoarseRoot + _tree.WFineRoot + _tree.WTapRoot)  * _KgMs_by_tree_to_gC_by_m2_soil, self.forest.treeStand.Root_DPM_RPM, self.forest.treeStand.Root_Age)  #fine roots
        
        # For updating the remaining coniferous foliage biomass
        try :
            self.forest.treeStand.Foliage_Fraction_Removed = sum(_tree.LeafWeight for _tree in self.Cut_Trees)/sum(_tree.LeafWeight for _tree in self.forest.treeStand)
        except ZeroDivisionError :
            self.forest.treeStand.Foliage_Fraction_Removed = 0
        
        self.forest.treeStand.Tree_Log = 1
   
        #Evaluate the dendrometrics dimensions of trees cut - used by models pf wood products life cyle 
        #self.Cut_Trees.update()
        self.NbCut_Trees            = len(self.Cut_Trees)
        self.harvest_DBHmean        = sum(_tree.DBH for _tree in self.Cut_Trees)/self.NbCut_Trees
        self.harvest_DBHquadratic   = (sum(_tree.DBH**2 for _tree in self.Cut_Trees)/self.NbCut_Trees)**0.5
        self.harvest_HEIGHTmean     = sum(_tree.Height for _tree in self.Cut_Trees)/self.NbCut_Trees
        self.harvest_BasalArea      = sum(_tree.BasalArea for _tree in self.Cut_Trees)/_standArea*10000
        
        _sum=0.0
        for _tree in self.Cut_Trees:
            _sum+=(_tree.DBH-self.harvest_DBHmean)**2
        self.harvest_DBHsd  = (_sum/self.NbCut_Trees)**0.5
    
        _sum=0.
        for _tree in self.Cut_Trees:
            _sum+=(_tree.Height-self.harvest_HEIGHTmean)**2
        self.harvest_HEIGHTsd = (_sum/self.NbCut_Trees)**0.5

        _sum=0.
        
        del self.Cut_Trees[:]

        
    def do_Plow(self,
                areaFractionPlowed = 0.5,
                soilCarbonFractionAffected = 0.2,) :
        '''plow() : made a plow
            areaFractionPlowed : Area fraction plowed (m2 /m2)
            soilCarbonFractionAffected : soil carbon fraction affected under plowing  (kg_C /kg_C)
        '''

        #estimate the PlowingFactor
        self.forest.soil.carbonCycle.PlowingFactor = max(self.forest.soil.carbonCycle.PlowingFactor, soilCarbonFractionAffected * areaFractionPlowed)
        self.forest.soil.carbonCycle.PlowEffect = self.k_PlowEffect 
        
        #impact on the understorey
        _UG = self.forest.underStorey
        
        _UG.foliage.LitterFall      =                              areaFractionPlowed * (_UG.foliage.W * _UG.foliage.BiomassCarbonContent + _UG.foliage.Cpool)
        _UG.roots.LitterFall        = soilCarbonFractionAffected * areaFractionPlowed * (_UG.roots.W * _UG.roots.BiomassCarbonContent +_UG.roots.Cpool)
        _UG.perennial.LitterFall    =                              areaFractionPlowed * (_UG.perennial.W * _UG.perennial.BiomassCarbonContent+_UG.perennial.Cpool)
        
        #update Cpool and biomass of each undergrowth compartments
        _UG.foliage.W   = _UG.foliage.W   * (1-areaFractionPlowed)  
        _UG.perennial.W = _UG.perennial.W * ((1-areaFractionPlowed) * _UG.perennial.AboveGroundFraction + (1-areaFractionPlowed * soilCarbonFractionAffected) * (1-_UG.perennial.AboveGroundFraction))  
        _UG.roots.W     = _UG.roots.W     * ((1-areaFractionPlowed) * _UG.roots.AboveGroundFraction     + (1-areaFractionPlowed * soilCarbonFractionAffected) * (1-_UG.roots.AboveGroundFraction))  
        # 5g of Cpool is safeguarded for regenerating the understorey layer. Can be regarded as seed bank, propagules, etc.    
        _UG.foliage.Cpool   = max (1,_UG.foliage.Cpool     *(1-areaFractionPlowed))
        _UG.perennial.Cpool = max (3,_UG.perennial.Cpool   *((1-areaFractionPlowed) * _UG.perennial.AboveGroundFraction + (1 - areaFractionPlowed * soilCarbonFractionAffected) * (1-_UG.perennial.AboveGroundFraction))  )
        _UG.roots.Cpool     = max (5,_UG.roots.Cpool       *((1-areaFractionPlowed) * _UG.roots.AboveGroundFraction     + (1 - areaFractionPlowed * soilCarbonFractionAffected) * (1-_UG.roots.AboveGroundFraction))      )
        #convert undergrowth litter in soil carbon incoming
        _UG.pcs_AllocateLitterCarbonToSoil()
        
#                                                                     ) 
    def do_NewTrees (self, tree_Age, initialTreesDensity, DBH_mean, DBH_std):
        '''Do a tree plantation at the specified density
        '''
        #Define the mean stand age and reset the management variables
        
        self.forest.treeStand.StandAge = tree_Age
        self.forest.treeStand.germinationYear =self.locTime.Y - tree_Age
        self.lastThinningYear   = self.locTime.Y - tree_Age - 10
        self.thinnings          = 0        
        self.seedingYear        = self.locTime.Y - tree_Age - 5
        self.FirstThinning      = True
        
        #initialisation of mean DBH
        
        self.forest.treeStand._install_trees_from_gauss_distribution(
                                                                     trees_Age = tree_Age,
                                                                     initialTreesDensity = initialTreesDensity,
                                                                     trees_DBH_mean = DBH_mean,
                                                                     trees_DBH_std = DBH_std,
                                                                     ) 