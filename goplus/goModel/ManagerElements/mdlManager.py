from goBases import *
import ManagerElements.mdlMngt_Operations
import random, math



class Manager(ManagerElements.mdlMngt_Operations.Manager):
    '''Defines forest managemnt plans. 
    '''
    practicesType = param('code of the management plan to be applied')
        
    def do_management(self):
        '''Manage the sylvicultural interventions : this method must be overwrite do to something'''

        
        print (        
                'lastThinyr: ' + str(self.lastThinningYear), 
                'RDI:', str(self.forest.treeStand.RDI), 
                'seedyr:', str(self.seedingYear), 
                'germinationyr:', str(self.forest.treeStand._germinationYear),
                'H0:', str(self.forest.treeStand.Heightdom), 
                '1st Thin:', str(self.FirstThinning), 
                'practice:', str(self.practicesType)
                )
#ONF management according to 'Referentiel Sylvicole Pyrenees, Sardin, 2013)        
        if self.practicesType==0:
            
## Self Thinning.            
            
            if self.forest.treeStand.RDI > 0.95 :
                self.do_RDI_Thinning(0.80, 2.0) 
                self.do_Logging(harvestStem = False, harvestBranchWood = False, harvestTapRoot = False, harvestStump = False, harvestFoliage = False)    


## -1-  Juvenile phase
        
            if self.forest.treeStand.DBHmean < 60. :


                if self.forest.treeStand.Heightdom <= 25. and (self.locTime.Y - self.lastThinningYear) >= 6. and self.FirstThinning == False :    
                    self.FirstThinning = True
                    print ('1st thinning')
                    if self.forest.treeStand.BasalArea <= 33.:
                        self.do_BA_Thinning(ThinFactor=0.5, BAobj=(self.forest.treeStand.BasalArea * 0.67))
                    elif self.forest.treeStand.BasalArea <= 39.:
                        self.do_BA_Thinning(ThinFactor=0.5, BAobj = (self.forest.treeStand.BasalArea * 0.65)) 
                    elif self.forest.treeStand.BasalArea > 39.:
                        self.do_BA_Thinning(ThinFactor=0.5, BAobj = (self.forest.treeStand.BasalArea * 0.6)) 
                    self.do_Logging(harvestStem = True, harvestBranchWood = True, harvestTapRoot = False, harvestStump = False, harvestFoliage = False)     
                    
                elif self.forest.treeStand.Heightdom > 25. and (self.locTime.Y - self.lastThinningYear) >= 6. and self.FirstThinning == True:
                    print ('no first thinning')
                    if self.forest.treeStand.Heightdom < 30.:
                        if self.forest.treeStand.BasalArea <= 24.:
                            self.do_BA_Thinning( ThinFactor=0.5, BAobj = (self.forest.treeStand.BasalArea * 0.775)) 
                        elif self.forest.treeStand.BasalArea <= 29.:
                            self.do_BA_Thinning( ThinFactor=0.5, BAobj = (self.forest.treeStand.BasalArea * 0.75)) 
                        elif self.forest.treeStand.BasalArea > 29.:
                            self.do_BA_Thinning( ThinFactor=0.5, BAobj = (self.forest.treeStand.BasalArea * 0.7)) 
                    elif self.forest.treeStand.Heightdom >= 30.:    
                        if self.forest.treeStand.BasalArea <= 24.:
                            self.do_BA_Thinning( ThinFactor=0.5, BAobj = (self.forest.treeStand.BasalArea * 0.775)) 
                        elif self.forest.treeStand.BasalArea <= 29.:
                            self.do_BA_Thinning( ThinFactor=0.5, BAobj = (self.forest.treeStand.BasalArea * 0.75)) 
                        elif self.forest.treeStand.BasalArea > 29.:
                            self.do_BA_Thinning( ThinFactor=0.5, BAobj = (self.forest.treeStand.BasalArea * 0.775))  
                    self.do_Logging(harvestStem = True, harvestBranchWood = True, harvestTapRoot = False, harvestStump = False, harvestFoliage = False)     
                    
 ## -2- Ageing and regeneration phase

            elif self.forest.treeStand.DBHmean >= 60. :
                if self.forest.treeStand._germinationYear - self.seedingYear < 20 : 

                    ### Bottom thinning for selecting reproducive trees as the biggest
                    if (self.locTime.Y - self.lastThinningYear) >= 6. and self.forest.treeStand.BasalArea >= 30. : 
                        self.do_BA_Thinning(ThinFactor=2, BAobj=(self.forest.treeStand.BasalArea - 7.5))
                        self.do_Logging(harvestStem = True, harvestBranchWood = True, harvestTapRoot = False, harvestStump = False, harvestFoliage = False)

                    ### Spacing trees for reproduction and sowing
                    elif (self.locTime.Y - self.lastThinningYear) >= 6. and self.forest.treeStand.BasalArea < 30. : 
                        self.do_BA_Thinning( ThinFactor=2, BAobj  = (self.forest.treeStand.BasalArea * 0.67))
                        self.do_Logging(harvestStem = True, harvestBranchWood = True, harvestTapRoot = False, harvestStump = False, harvestFoliage = False)     
                    ### New seeding /masting     
                        self.seedingYear = self.locTime.Y  

                    ### last thinnings and clearcut
                elif (self.locTime.Y - self.seedingYear) == 5 or (self.locTime.Y - self.seedingYear) == 10:
                    if self.forest.treeStand.BasalArea > 16. :
                        self.do_BA_Thinning(ThinFactor=1.5, BAobj = (self.forest.treeStand.BasalArea - 8))
                        self.do_Logging(harvestStem = True, harvestBranchWood = True, harvestTapRoot = False, harvestStump = False, harvestFoliage = False)
                    elif 16 > self.forest.treeStand.BasalArea > 8. : 
                        self.do_BA_Thinning( ThinFactor=1.5, BAobj = (self.forest.treeStand.BasalArea - 6.5))
                        self.do_Logging(harvestStem = True, harvestBranchWood = True, harvestTapRoot = False, harvestStump = False, harvestFoliage = False)
                    else : #final clearcut
                        self.do_Clearcut()
                        self.do_Logging(harvestStem = True, harvestBranchWood = True, harvestTapRoot = False, harvestStump = False, harvestFoliage = False)

                    ### to avoid ageing stands when growth is nul    
                    if (self.locTime.Y - self.seedingYear) == 15:
                        self.do_Clearcut()
                        self.do_Logging(harvestStem = True, harvestBranchWood = True, harvestTapRoot = False, harvestStump = False, harvestFoliage = False)     
 
## -3- New Tree Stand. Your trees assumed to have already grown for 10 years when clearcut happened
            
            if self.forest.treeStand.density==0:
               self.do_NewTrees(10., 2000., 8.0, 2.5)
               self.FirstThinning = False
               
               
#Unmanaged stands. Self thinning rule, no harvest, no further regeneration phase for the simulation being.     
        if self.practicesType==2:            

## Thinning and mortality
        
            if self.FirstThinning and self.forest.treeStand.RDI > 0.95 : 
                self.do_RDI_Thinning( 0.8, 2.0)
                self.do_Logging(harvestStem = False, harvestBranchWood = False, harvestTapRoot = False, harvestStump = False, harvestFoliage = False)     
                self.FirstThinning = False
                
            else:
                if self.locTime.Y - self.lastThinningYear >= 5 :
                    if self.forest.treeStand.RDI > 0.95 :
                        self.do_RDI_Thinning(0.85, 2.0) 
                        self.do_Logging(harvestStem = False, harvestBranchWood = False, harvestTapRoot = False, harvestStump = False, harvestFoliage = False)                    
            
## to avoid ageing stands when growth is nul   
                        
            if (self.locTime.Y - self.seedingYear) == 15 or self.forest.treeStand.density<25:
                        self.do_Clearcut()
                        self.do_Logging(harvestStem = True, harvestBranchWood = True, harvestTapRoot = False, harvestStump = False, harvestFoliage = False)     
## New Tree Stand. The trees assumed to have already grown for 10 years when clearcut happened
            
            if self.forest.treeStand.density==0:
               self.do_NewTrees(10., 2000., 8.0, 2.5)
               self.FirstThinning = False
               

