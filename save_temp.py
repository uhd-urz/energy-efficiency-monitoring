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


from read_temp_class import ReadTemp
import time
import sys
import os


# initialize ReadTemp class and variables
ReadTemp = ReadTemp()
time_step = None
file_name = ReadTemp.create_daily_file_name()
did_just_measure = None
measurement_counter = 1


# start main program in order to measure temperature and save the data to a file
if __name__ == '__main__':
    try:
        time_step = float(sys.argv[1])
        # check if bandgap-correction-mode is activated
        if len(sys.argv) > 2:
            if sys.argv[2] == "-b":
                ReadTemp.bandgap_correction_active = True
        # if above line works, continue. if not go down to except errors
        all_connected_sensors = ReadTemp.find_connected_sensors()[0]
        print 'Found %s sensors, with the IDs:\n%s' % (len(ReadTemp.find_connected_sensors()[1]),
                                                       ReadTemp.find_connected_sensors()[1])
        measured_temp = ReadTemp.return_temp_values(all_connected_sensors, time_step)

        if ReadTemp.time_interval_fits:
            print 'provided time interval fits...'
            print 'start to print & save data with time steps of %s sec to file: %s' % \
                  (float(time_step), file_name)
            while True:     # start main loop
                file_name = ReadTemp.create_daily_file_name()
                if os.path.isfile(file_name) is False:
                    ReadTemp.write_sensors_to_first_row(ReadTemp.find_connected_sensors()[1], file_name)
                if ReadTemp.get_time()[1] % int(time_step) == 0 and did_just_measure is not True:
                    print '---------------------------------------'
                    print 'Measurement %s:' % measurement_counter
                    temp_data = ReadTemp.return_temp_values(all_connected_sensors, time_step)
                    ReadTemp.write_temp_data_to_file(temp_data, file_name)
                    did_just_measure = True
                    measurement_counter += 1
                else:
                    did_just_measure = False
                    time.sleep(1)
        else:
            print 'ERROR: provided time interval is too small, enter time interval larger than "duration time"'

    except IndexError:
        print 'ERROR: enter wanted time interval (in sec) as first argument (and optional "-b" as second argument' \
              'in order to activate the bandgap correction with python script, like: \n    ' \
              '$ python {} <time_interval> -b'.format(sys.argv[0])
    except ValueError:
        print 'ERROR: make sure to enter provided time interval with type int or float'
    except KeyboardInterrupt:
        print '\n...stopped... \n -> saved data to file: %s\n' % file_name
