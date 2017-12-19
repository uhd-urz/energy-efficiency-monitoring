#
# Copyright 2017 Heidelberg University Computing Centre
#
# Licensed under the EUPL, Version 1.2 or – as soon they
# will be approved by the European  Commission - subsequent
# versions of the EUPL (the "Licence").
# You may not use this work except in compliance with the
# Licence. 
# You may obtain a copy of the Licence at:
#
# https://joinup.ec.europa.eu/software/page/eupl
#  
# Unless required by applicable law or agreed to in 
# writing, software distributed under the Licence is 
# distributed on an "AS IS" basis, WITHOUT WARRANTIES 
# OR CONDITIONS OF ANY KIND, either express or implied. 
# See the Licence for the specific language governing 
# permissions and limitations under the Licence. 
# 


import os
from datetime import datetime
import threading
import time


class ReadTemp(object):
    """
    Temperature Readout class: includes all functions like find_connected_sensors and write data to files
    """

    def __init__(self):
        """init function"""
        self.all_temp_data = []
        self.time_interval_fits = False
        self.security_second = 1
        self.bandgap_correction_active = False

    def get_time(self):
        """returns the current time"""
        date_time = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        time_seconds = int(datetime.now().strftime('%s'))
        return date_time, time_seconds

    def find_connected_sensors(self):
        """looks up all connected sensors by checking for their individual folder.
        Returning a list of paths to the given files in which the corresponding temperatur
        is found."""
        path_to_sensors = '/sys/bus/w1/devices/'
        # for debugging and simulation purpose uncomment following line. Local virtual
        # temperature data will be used
        path_to_sensors = 'virtual_temperature_data/'
        list_of_files = os.listdir(path_to_sensors)
        list_of_dirs = []
        list_of_sensor_paths = []
        # loop through the files starting with '28-'... and append them to the list_of_dirs
        for each_file in list_of_files:
            if each_file.startswith('28-'):
                list_of_dirs.append(each_file)
        # loop through the directories and construct the whole path to the wanted files
        for each_dir in list_of_dirs:
            construct_path = os.path.join(path_to_sensors + each_dir + '/w1_slave')
            list_of_sensor_paths.append(construct_path)
        # return a list with all paths and just sensor names
        return list_of_sensor_paths, list_of_dirs

    def write_sensors_to_first_row(self, all_sensors, file_name):
        """writes the first line of the data file containing the word TIME and the sensor ids"""
        list_of_sensor_ids = sorted(all_sensors)        # will list them alphabetically by the id again
        # write first line to be like: TIME; sensor1id; sensor2id; sensor3id; ...
        with open(file_name, 'w') as data:
            data.write('TIME')
            for each_sensor in list_of_sensor_ids:
                data.write(str(';' + each_sensor))
            data.write('\n')

    def error_handler(self, sensor_id, error_type):
        """gets error type and writes error message to error.log"""
        error_log_file_name = 'error.log'
        id_position = sensor_id.find('28-')
        sensor_id = sensor_id[id_position:][:15]
        with open(error_log_file_name, 'a') as error_log:
            if error_type == '404':
                message_404 = '%s: Sensor %s got an error, type %s. Comment: This might happen due to plugging sensors' \
                              'in or out while measuring.\n' % (self.get_time()[0], sensor_id, error_type)
                error_log.write(message_404)
                print '#### ERROR 404: check error.log ####'
            elif error_type == '85':
                message_85 = '%s: Sensor %s got an error, type %s.  Comment: This might happen due ' \
                             'to mechanical stress (i.e. bending or squeezing the sensor).\n'\
                             % (self.get_time()[0], sensor_id, error_type)
                error_log.write(message_85)
                print '#### ERROR 85:  check error.log ####'

    def bandgap_correction(self, measured_temperature):
        """takes uncorrected measured temperature values as input and applies correction due to the bandgap effect.
        Returns corrected temperature values"""
        compensated_temperature = measured_temperature - 0.000133 * measured_temperature**2 + 0.005195 * measured_temperature + 0.1438
        compensated_temperature = round(compensated_temperature, 3)
        return compensated_temperature

    def read_one_sensor(self, one_sensor):
        """function to read one sensor after another, which is necessary for using threading"""
        with open(one_sensor) as f:
            content = f.readlines()
            # content looks like:
            # eb 01 4b 46 7f ff 0c 10 69 : crc=69 YES
            # eb 01 4b 46 7f ff 0c 10 69 t=30687
            if content[0].strip()[-3:] == 'YES':
                # look for temperature (t=)
                equals_pos = content[1].find('t=')
                temp_data = float(content[1][equals_pos + 2:]) / 1000
                # do error handling about 85.0 issue
                if temp_data == 85.0:
                    temp_data = '85'
                    self.error_handler(one_sensor, '85')
                else:
                    if self.bandgap_correction_active:
                        temp_data = self.bandgap_correction(temp_data)
            else:
                # no temp data found, write error message to temp data
                temp_data = '404'
                self.error_handler(one_sensor, '404')
        id_position = one_sensor.find('28-')
        sensor_id = one_sensor[id_position:][:15]
        print 'sensor %s  |  temp %s' % (sensor_id, temp_data)
        tuple_data = (one_sensor, temp_data)
        self.all_temp_data.append(tuple_data)

    def return_temp_values(self, all_sensors, seconds_per_loop):
        """loops through all sensors using the read_one_sensor function and returns the values in a list"""
        self.all_temp_data = []
        start_timer = time.time()
        raw_temp_values_list = []
        measurement_time = date_time = datetime.now().strftime('%H:%M:%S')
        raw_temp_values_list.insert(0, measurement_time)
        # now read temp value for each sensor using multithreading
        t = threading.Thread()
        for each_sensor in all_sensors:
            t = threading.Thread(target=self.read_one_sensor, args=(each_sensor,))
            t.start()
        t.join()
        # wait until all temp values are written to the list
        while len(self.all_temp_data) != len(all_sensors): # if not all data is there, wait!
            time.sleep(0.5)
        stop_timer = time.time()
        duration_time = float(stop_timer) - float(start_timer) + self.security_second
        print 'duration time: ', round(duration_time, 4)
        if float(duration_time) < float(seconds_per_loop):
            self.time_interval_fits = True
        else:
            self.time_interval_fits = False
        self.all_temp_data = sorted(self.all_temp_data)     # will list them alphabetically by the id again
        # remove first element of tuples in the list by picking just the second ones
        for i in range(len(self.all_temp_data)):
            raw_temp_values_list.append(self.all_temp_data[i][1])
        print 'save data: ', raw_temp_values_list
        return raw_temp_values_list

    def create_daily_file_name(self):
        """checks the current time and date and returns proper file name.
        Each day a new file is generated, starting at 00:00"""
        date_time = datetime.now().strftime('%Y-%m-%d')
        file_name = './firesensors_tempdata/tempdata814_' + date_time + '.csv'
        return file_name

    def write_temp_data_to_file(self, temp_data, file_name):
        """takes the temp data list and writes the values to the data file"""
        # open data file
        with open(file_name, 'a') as data:
            # write all the entries of the list to the data file
            for i, each_value in enumerate(temp_data):
                if i == 0:
                    data.write(str(each_value))
                else:
                    data.write(';' + str(each_value))
            data.write('\n')
