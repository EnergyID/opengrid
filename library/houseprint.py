# -*- coding: utf-8 -*-
"""
opengrid

The houseprint class defines an interface to the houseprint we collect for 
each opengrid participant.


Created on Mon Dec 30 00:51:49 2013 by Roel De Coninck

"""

import os, sys
import gspread
import inspect

class Houseprint(object):
    """
    Interface to the houseprints of all opengrid participants.
    
    The houseprints are currently saved in a google drive spreadsheet.  This
    may change later.    
    
    """
    
    def __init__(self, houseprint = "Opengrid houseprint (Responses)"):
        """
        Create a connection with the google drive spreadsheet.
        Initialize a few attributes and save all the values in the spreadsheet
        to self.cellvalues (list of lists).
        """
        self.sensoramount=6
        
        # Get the path of this current file 
        self.sourcedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        
        pwdfile = file(os.path.join(self.sourcedir, 'og.txt'))
        pwd = pwdfile.read().rstrip()
        
        # open spreadsheet, store main sheet in self.sheet
        self.gc = gspread.login('opengridcc@gmail.com', pwd)
        self.sheet = self.gc.open(houseprint).sheet1
        self.cellvalues=self.sheet.get_all_values()
                
        # store {flukso_id:rownumber} in self.flukso_ids
        self._identify_fluksos()
        
        # store {sensor_x:column number} in self.sensorcols
        self.sensorcols={}
        for i in range(1,self.sensoramount+1):
            self.sensorcols[i] = self.sheet.find("Sensor "+ str(i)).col
        

        print houseprint + " successfully opened."
         
    
    def get_sensor(self, int_row, int_sensor):
        """
        Return dictionary with all sensor specifications for sensor y in row x.
        
        Parameters
        ----------
        
        int_row: row number (integer)
        int_sensor: sensor number (1-6)
        
        """
        
        # get the column of correct sensor
        col = self.sensorcols[int_sensor]
        cont = self.cellvalues[int_row-1][col-1]
        keys = ['Sensor', 'Token', 'Type', 'Function']

        try:
            res = dict(zip(keys, cont.split()))
        except:
            # there is no (complete) sensor data
            res = None
        
        if res == {}:
            res = None
        
        return res
            
    def get_all_sensors(self, int_row):
        """
        Return a nested dictionary with all sensors for a given row
        
        Parameters
        ----------
        
        int_row: row number (integer)
        
        Returns
        --------
        
        {id:{spec:value}}
        If there is no sensor data for a given id, it will contain a None object
        """
        
        res = {}
        for i in range(1,self.sensoramount+1):
            res[i] = self.get_sensor(int_row, i)
            
        return res
        
        
    def _identify_fluksos(self):
        """
        Obtain and store all flukso serial numbers as attribute self.flukso_ids
        
        Returns
        -------
        nothing, sets self.flukso_ids as a dictionary with flukso_id:row pairs.
        
        """
        
        col = self.sheet.find('Fluksometer serial number').col
        fluksos_all = self.sheet.col_values(col)
        
        # store flukso_id:rownumber
        self.flukso_ids = {}
        for i,f in enumerate(fluksos_all[1:]):
            if f is not None:
                self.flukso_ids[f] = i+2 # correct for the first row and python indexing from 0 
        
                   
    
    def get_all_fluksosensors(self):        
        """
        Return a nested dictionary with all sensors for all fluksos.
        Also add it to self as self.fluksosensors
        
        Returns
        --------
        
        {flukso:{int_sensor:{spec:value}}}
        """
        
        res = {}
        for k,v in self.flukso_ids.items():
            res[k] = self.get_all_sensors(v)
            
        self.fluksosensors = res
        return res.copy()
        

    def get_sensors_by_type(self, sensortype = None):
        """
        Return a list with sensor ids for the given sensortype.
        
        Parameters
        ----------
        
        * sensortype = 'gas', 'electricity' or 'water'
        
        Returns
        --------
        
        List with all sensor numbers of the given sensortype.
        """
        
        if not hasattr(self, 'fluksosensors'):
            self.get_all_fluksosensors()
        
        res = [] 
        for flukso, sensors in self.fluksosensors.items():
            for int_sensor,sensordic in sensors.items():
                try:
                    if sensordic['Type'] == sensortype:
                        res.append(sensordic['Sensor'])
                except TypeError:
                    pass
                
        return res
        

    def get_flukso_from_sensor(self, sensor):
        """
        Return a list with sensor ids for the given sensortype.
        
        Parameters
        ----------
        
        * sensor = sensor number (hex)
        
        Returns
        --------
        
        List with all sensor numbers of the given sensortype.
        """
        
        if not hasattr(self, 'fluksosensors'):
            self.get_all_fluksosensors()
        
        for flukso, sensors in self.fluksosensors.items():
            for int_sensor, sensordic in sensors.items():
                try:
                    if sensordic['Sensor'] == sensor:
                        return flukso
                except TypeError:
                    pass
                
        return ValueError("Flukso not found for sensor " + sensor)        

        
if __name__ == '__main__':
    
    hp = Houseprint()