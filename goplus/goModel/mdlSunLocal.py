from goBases import * #Windows
#from ..goBases import * #LINUX
class SunLocal(ELT):
    ''' Represent the  sun cycle for a localisation.
    '''
    
    #outer element
    locTime = eltOut('LocTime element')

    #vars
    SinSunElevation = var('sinus of the solar elevation angle')
    SinSunElevationMidday = var('sinus of the solar elevation angle at midday')
    SunAzimuth = var('Sun azimuth in degrees; south is 0') ##SM modified
    cosI = var('cosinus of the incidence angle of solar radius') ##SM modified

    SunUp = var('sun up day fraction')
    SunDown = var('sun down day fraction')
    DayTime = var('duration of day (solar above horizon)')
    
    #params
    Latitude = param('latitude of the site (deg)')
    Slope = param('slope of the stand (deg)')
    Aspect = param('aspect of the stand. 0 for north (deg)')
    Altitude=param('altitude of the site (m asl)')
    def update(self):
        
        earthInclination =  -0.40927971            #earth inclination (radian)
        sin_Latitude = sin(self.Latitude *pi/180.0)    
        cos_Latitude = cos(self.Latitude *pi/180.0)    
       
        sunDeclination = earthInclination * cos(2 * pi * (self.locTime.DOY + self.locTime.H/24.0 + 10) / self.locTime.NbDayOfYear)
        sin_Declination  = sin(sunDeclination)
        cos_Declination = cos(sunDeclination)
        
        H_angle = pi * (self.locTime.H/12.0 - 1)
        
        self.SinSunElevation = sin_Latitude * sin_Declination + cos_Latitude * cos_Declination * cos(H_angle)
        
     
        sunElevation = asin(self.SinSunElevation) * 180/pi 
        self.cosSunElevation = cos(sunElevation*pi/180)
            
        sinSunAzimuth =  cos_Declination * sin(H_angle) / self.cosSunElevation 

        if cos(H_angle) >= (tan(sunDeclination) / tan(self.Latitude *pi/180.0)): 
            self.SunAzimuth = asin(sinSunAzimuth)*180/pi
        else:
            if H_angle<0 :
                self.SunAzimuth = -180 - asin(sinSunAzimuth)*180/pi 
            else :
                self.SunAzimuth = 180 - asin(sinSunAzimuth)*180/pi

        # Angle of incidence of solar radius (I)
        self.sinSlope = sin(self.Slope * pi/180)
        self.cosSlope = cos(self.Slope * pi/180)
        self.cosDifAzi = cos((self.SunAzimuth - self.Aspect)* pi/180)
        self.cosI = self.cosSunElevation * self.sinSlope * self.cosDifAzi + self.SinSunElevation * self.cosSlope
        
        #day properties updates  et the beginning of the day
        if self.locTime .isDayBeginning:
            self.SinSunElevationMidday = sin_Latitude * sin_Declination + cos_Latitude* cos_Declination
            
            #Sun up
            _CS = -(sin_Latitude * sin_Declination) / (cos_Latitude *cos_Declination)
            
            try:
                _AT = atan((1 / _CS ** 2 - 1) ** 0.5)
            except:
                raise Exception('Solar elevation incorrect for this day')
            
            if _CS < 0 : _AT = pi - _AT
            self.SunUp = (2 * pi - _AT) * 0.5 / pi - 0.5
            
            #Sun down
            self.SunDown = 1 - self.SunUp
            
            #Day duration
            self.DayTime = 1 - 2 * self.SunUp



