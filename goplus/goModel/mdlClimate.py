from goBases import * 		#Windows
#from ...goBases import * 	#LINUX

from mdlMicroClimate import MicroClimate
import  math

def CO2_mdl(YearFrac = 1990.5, Scenario = 0):
    '''model of CO2 evolution as a function of time (year and fraction as float)'''
    _SAFRAN = 0.013*(YearFrac-1950)**2 + 0.518*(YearFrac-1950) + 310.44 # formulae based on Mauna Loa obs since 1950
    _CO2_A2 =  0.0000000297892*(YearFrac-2000)**4 + 0.0000786964*(YearFrac-2000)**3 + 0.0202866*(YearFrac-2000)**2 + 1.99387*(YearFrac-2000) + 369.645
    _CO2_26 = -2018.523 + 1.2060584*YearFrac - 0.0363264*(YearFrac-2033.5)**2 - 0.0001755*(YearFrac-2033.5)**3 + 9.6064e-6*(YearFrac-2033.5)**4 + 1.6606e-8*(YearFrac-2033.5)**5 - 1.0814e-9*(YearFrac-2033.5)**6
    _CO2_45 = -4888.404 + 2.6223372*YearFrac + 0.0054081*(YearFrac-2033.5)**2 - 0.0003754*(YearFrac-2033.5)**3 - 4.9167e-6*(YearFrac-2033.5)**4 + 3.428e-8*(YearFrac-2033.5)**5 + 6.867e-10*(YearFrac-2033.5)**6
    _CO2_6  =  -4042.426 + 2.2024856*YearFrac + 0.0134218*(YearFrac-2033.5)**2 + 0.0003215*(YearFrac-2033.5)**3 + 2.4632e-6*(YearFrac-2033.5)**4 - 5.3655e-8*(YearFrac-2033.5)**5 - 5.892e-10*(YearFrac-2033.5)**6
    _CO2_85 = -7682.627 + 4.0049942*YearFrac + 0.0468563*(YearFrac-2033.5)**2 + 0.000237*(YearFrac-2033.5)**3 - 2.0803e-6*(YearFrac-2033.5)**4 - 2.2891e-8*(YearFrac-2033.5)**5 - 6.848e-12*(YearFrac-2033.5)**6

    # Codification of the CO2 scenario
    # Code 0: historical record; code 1: 500ppm, code 2: SRES A2; code 3: RCP2.6; code 4: RCP4.5; code 5: 500ppm; code 6: RCP 6.5; code 7: 500.0ppm; code 8: RCP8.5; code 9: 500ppm
    _CO2 = (_SAFRAN, 500.0, _CO2_A2, _CO2_26,  _CO2_45, 500.0,  _CO2_6,  500.0,  _CO2_85, 500.0) [int(Scenario)]
    
    return _CO2


def atmP(Altitude):    
    '''international formulae of barometric nivelment for atm pressure (Pa)'''
    return 100. * 1013.25 * (1-0.0065*Altitude/288.15)**5.255
    
    
def SWDifFrac_mdl(sinB,DOY,SW):
    '''Evaluate the diffuse part of solar radiation (Boland et al. 2008)
        - sinB sine of solar elevation
        - DOY: day of the year 
        - SW : incident solar radiation (W /m2_soil)
    '''

    #Incident Radiation S0 (W.m-2)
    SCS=1370.0  # solar constant 
    S0=SCS*(1+0.033*cos(360*DOY/365.0*pi/180.0))*max(0,sinB)

    #atmosphere transmissivity (or sky clearness)
    ATMTRANS = min (1,(SW/S0 if S0>0 else 0))
    #Boland et al. 2008. Generic model - coefficient fitted to Bordeaux Data.    
    DD = 1/(1+math.exp(-4.70+7.80*ATMTRANS))
    return DD    


class Climate(ELT):

    #outer elements
    locTime = eltOut('LocTime element')
    sunLocal = eltOut('SunLocal element')
    
    #inner element
    microclim = eltIn(MicroClimate)
    
    #meteo file path
    meteo_file_path = param('complete path-name to meteo file', 'defaultMeteoData.csv' )
    Scenario = param("index of CO2 scenario")

    
    def update(self):
        self.pcs_climateConditionsFromDataFile()
    
    @pcs
    def pcs_climateConditionsFromDataFile(self, 
        _ = private('use to store file object of meteorological data', ELT), 
        ):
    
        #initialize private vars
        if self.locTime.isSimulBeginning:
            _.meteo_file = open(self.meteo_file_path, 'r')

        try :
            #read a record string and skip comments,reload file if end of file reached
            _strRecord = "#"      
            # New version from CM 29/08/2017
            while _strRecord=='' or _strRecord.strip()[0]=='#':
                _strRecord=_.meteo_file.readline()
                if _strRecord=='':
                    _.meteo_file=open(self.meteo_file_path, 'r')
            while ( (len(_strRecord.split(',')) > 1 ) and int(_strRecord.split(',')[0]) < self.locTime.Y_start) : #start meteofile after 1st year
                _strRecord=_.meteo_file.readline()
                if _strRecord=='':
                    _.meteo_file=open(self.meteo_file_path, 'r')

            
            #split record into data list
            _data =  _strRecord.strip().split(',')
            
            # Check that climate forcing dates corresponds to simulation date 
            if (int(_data[0]) != self.locTime.Y or int(_data[1]) != self.locTime.DOY or int(_data[2]) != self.locTime.H) \
            and (self.locTime.H != 0) : # Exception for 1st hour after end of simulation which is often missing in meteo data
                print ('Year:' + str(self.locTime.Y) + ', DOY : ' + str(self.locTime.DOY) + ', Hour : ' +  str(self.locTime.H))
                raise NameError ( 'Meteo file dates are not fitting with simulation dates')
        
            _microclim = self.microclim
            
            #when pressure not present use default value
            if  _data[3].strip()!='':
                _microclim.P = float(_data[3])
            elif self.sunLocal.Altitude != '':
                _microclim.P = atmP(self.sunLocal.Altitude) 
            else:
                 _microclim.P = 101600
            
            _microclim.TaC  = float( _data[4])
            _microclim.e    = float(_data[5])
            _microclim.Rain = float(_data[6])
            _microclim.u    = float(_data[7])
            
            _SVF = 1 #Sky view fraction : value for an horizontal plan . To determine Diffuse / Direct ratio. Can be extracted from some GIS soft.           
            
            #SWDir and SWDif from SW and SWDifFrac if present, else use model partition
            if  _data[9].strip()!='':
                _SWDifFrac = float(_data[9]) 
            else:
                if _microclim.Rain >0 :
                    _SWDifFrac = 1 
                else:
                    _SWDifFrac = SWDifFrac_mdl(self.sunLocal.SinSunElevation, self.locTime.DOY,  float(_data[8]))
            
            _microclim.SWDir = float(_data[8])*(1-_SWDifFrac)
            _microclim.SWDif = float(_data[8])*_SWDifFrac *_SVF           
            _microclim.LWDw  = float(_data[10])
            
            #CO2 from file or model
            if self.Scenario is not None :
                _microclim.CO2 = CO2_mdl(self.locTime.Y+self.locTime.DOY/365.0,  self.Scenario)
            else :
                _microclim.CO2 = CO2_mdl(self.locTime.Y+self.locTime.DOY/365.0) #default scenario=A2
                print ("CO2 scenario is not defined")
            
        except :
            print('Error during conversion of climatic data file,  on position %i' % _.meteo_file.tell())
            raise
                        
        self.microclim.update()


