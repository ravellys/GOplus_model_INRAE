#Last,  Last, Max,  Min,  Last, LastWatt , LastDay

varsToIntegrate = '''
Last: mdl.locTime.Y
Last: mdl.locTime.DOY
Last: mdl.locTime.H
Last: mdl.climate.microclim.RsDif
Last: mdl.climate.microclim.RsDir
Last: mdl.climate.microclim.RsUp
Last: mdl.climate.microclim.RthDw
Last: mdl.climate.microclim.RthUp
Last: mdl.climate.microclim.TaC
Last: mdl.climate.microclim.Rain
Last: mdl.climate.microclim.d
Last: mdl.climate.microclim.u
Last: mdl.climate.microclim.CO2
Last: mdl.forest.LE
Last: mdl.forest.Rnet
Last: mdl.forest.H
Last: mdl.forest.treeStand.Age
Last: mdl.forest.treeStand.LeafFall
Last: mdl.forest.treeStand.SoilRootsWaterPotential
Last: mdl.forest.treeStand.canopy.WaterPotential
Last: mdl.forest.treeStand.Rm
Last: mdl.forest.treeStand.Rg
Last: mdl.forest.treeStand.litterfallLeaf
Last: mdl.forest.treeStand.litterfallBr
Last: mdl.forest.treeStand.litterfallRoot
Last: mdl.forest.treeStand.Litterfall
Last: mdl.forest.treeStand.IStress
Last: mdl.forest.treeStand.NbDeadTrees
Last: mdl.forest.treeStand.density
Last: mdl.forest.treeStand.DBHmean
Last: mdl.forest.treeStand.HEIGHTmean
Last: mdl.forest.treeStand.W
Last: mdl.forest.treeStand.Wa
Last: mdl.forest.treeStand.Wr
Last: mdl.forest.treeStand.Wstem
Last: mdl.forest.treeStand.WProducted
Last: mdl.forest.treeStand.canopy.LAI
Last: mdl.forest.treeStand.canopy.Rnet
Last: mdl.forest.treeStand.canopy.Rnet_star
Last: mdl.forest.treeStand.canopy.LE
Last: mdl.forest.treeStand.canopy.LE_DrySurface
Last: mdl.forest.treeStand.canopy.LE_WetSurface
Last: mdl.forest.treeStand.canopy.H
Last: mdl.forest.treeStand.canopy.Transpiration
Last: mdl.forest.treeStand.canopy.Evaporation
Last: mdl.forest.treeStand.canopy.dTsTa
Last: mdl.forest.treeStand.canopy.Assimilation
Last: mdl.forest.treeStand.canopy.Respiration
Last: mdl.forest.treeStand.canopy.Dripping
Last: mdl.forest.underStorey.Rm
Last: mdl.forest.underStorey.Rg
Last: mdl.forest.underStorey.foliage.LitterFall
Last: mdl.forest.underStorey.roots.LitterFall
Last: mdl.forest.underStorey.perennial.LitterFall
Max: mdl.forest.underStorey.canopy.LAI
Last: mdl.forest.underStorey.canopy.Rnet
Last: mdl.forest.underStorey.canopy.H
Last: mdl.forest.underStorey.canopy.Transpiration
Last: mdl.forest.underStorey.canopy.Evaporation
Last: mdl.forest.underStorey.canopy.Assimilation
Last: mdl.forest.underStorey.canopy.Respiration
Last: mdl.forest.underStorey.canopy.Dripping
Last: mdl.forest.underStorey.foliage.W
Last: mdl.forest.underStorey.perennial.W
Last: mdl.forest.underStorey.roots.W
Last: mdl.forest.underStorey.foliage.Cpool
Last: mdl.forest.underStorey.perennial.Cpool
Last: mdl.forest.underStorey.roots.Cpool
Last: mdl.forest.soil.surface.Rnet
Last: mdl.forest.soil.surface.H
Last: mdl.forest.soil.surface.ETR
Last: mdl.forest.soil.waterCycle.MoistureDeficit
Last: mdl.forest.soil.waterCycle.RootLayerWaterPotential
Last: mdl.forest.soil.carbonCycle.Ra
Last: mdl.forest.soil.carbonCycle.Rh
Last: mdl.forest.soil.carbonCycle.HUM
Last: mdl.forest.soil.carbonCycle.BIO
Last: mdl.forest.soil.carbonCycle.DPM
Last: mdl.forest.soil.carbonCycle.RPM
Last: mdl.forest.soil.waterCycle.Vidange
Last: mdl.manager.harvest_Wstem
Last: mdl.manager.harvest_Wcrown
Last: mdl.manager.harvest_Wtaproot
Last: mdl.manager.harvest_DBHmean
Last: mdl.manager.harvest_DBHsd
Last: mdl.manager.harvest_DBHquadratic
Last: mdl.manager.harvest_HEIGHTmean
Last: mdl.manager.harvest_HEIGHTsd
'''


unitsToIntegrate = '''
Y
DOY
H
W.m-2
W.m-2
W.m-2
W.m-2
W.m-2
C
mm
Pa
m.s-1
ppm
W.m-2
W.m-2
W.m-2
Y
Kg_DM .m-2_soil
MPa
g C.m-2_soil.h-1
g C.m-2_soil.h-1
g C.m-2_soil.jour-1
g C.m-2_soil.jour-1
g C.m-2_soil.jour-1
g C.m-2_soil.jour-1
Dimensionless
Dimensionless
Nb.Ha-1
cm
m
Kg_DM.m-2_soil
Kg_DM.m-2_soil
Kg_DM.m-2_soil
Kg_DM.m-2_soil
Kg_DM.m-2_soil.y-1
m2_leafAreaIndex.m-2_soil
W.m-2
W.m-2
Kg_H2O.m-2_soil.h-1
Kg_H2O.m-2_soil.h-1
degC
m.s-1
m.s-1
m.s-1
g C.m-2_soil.h-1
g C.m-2_soil.h-1
g C.m-2_soil.h-1
g C.m-2_soil.h-1
Kg_H2O.m-2_soil.h-1
g C.m-2_soil.h-1
g C.m-2_soil.h-1
Kg_DM .m-2_soil.h-1
Kg_DM .m-2_soil.h-1
Kg_DM .m-2_soil.h-1
m2_leafAreaIndex.m-2_soil
W.m-2
W.m-2
Kg_H2O.m-2_soil.h-1
Kg_H2O.m-2_soil.h-1
g C.m-2_soil.h-1
Kg_H2O.m-2_soil.h-1
Kg_DM.m-2_soil
Kg_DM.m-2_soil
Kg_DM.m-2_soil
g C.m-2_soil
g C.m-2_soil
g C.m-2_soil
W.m-2
W.m-2
Kg_H2O.m-2_soil
Kg_H2O.Kg-1_H2O
MPa
gC.m-2_soil.h-1
gC.m-2_soil.h-1
gC.m-2_soil
gC.m-2_soil
gC.m-2_soil
gC.m-2_soil
Kg_H2O.m-2_soil.h-1
Kg_DM.m-2_soil.y-1
Kg_DM.m-2_soil.y-1
Kg_DM.m-2_soil.y-1
cm
cm
cm
m
m
'''
