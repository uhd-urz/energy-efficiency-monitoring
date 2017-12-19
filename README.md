# Development and implementation of a temperature monitoring system for HPC systems
The software is licensed under the [EUPL](https://joinup.ec.europa.eu/software/page/eupl).

## Introduction
This repository contains the code of the work "Development and implementation of a temperature monitoring system for HPC systems" which was published at the [27th PARS Workshop](http://fg-pars.gi.de/workshops/pars-workshop-2017/) 2017 and will be available in the PARS proceedings "PARS-Mitteilungen 2017" on the website of the special interest group [PARS](https://fg-pars.gi.de/pars-mitteilungen/).

## Abstract
In the context of high-performance computing (HPC), the removal of released heat is one challenging topic due to the continuously increasing density of computing power.
A temperature monitoring system provides insight into the heat development of an HPC cluster.
The effectiveness of this is directly related to the number of sensors, their placing and the accuracy of the temperature measurements.
Monitoring is important not only to investigate the efficiency of the cooling system for purposes of detecting defective operation of the HPC system, but also to improve the cooling of the servers and by this the achievable performance.
The main purpose of a fine-grained and unified temperature monitoring is the possibility to optimize the applications and their execution regarding the temperature spreading on HPC systems.
Based on this, we present a highly flexible and scalable -- in terms of cable length and number of sensors -- and at the same time budget-friendly monitoring infrastructure.
It is based on low-cost components such as Raspberry Pi as monitoring client and a setup using the DS18B20 digital thermometer as temperature sensor.
Focus is given on the selection of adequate temperature sensors and we explain in detail how the sensors are assembled and the quality assurance is done before these are used in the monitoring setup.


## How to use

Follow through this list to establish a monitoring system using Raspberry Pi and Dallas DS18B20 digital thermometers:
* connect sensors to Raspberry Pi (like described in the above mentioned paper)
* activate the 1-wire protocol via `raspi-config`
* clone github repository to your Raspberry Pi
* run temperature readout Python script with appropriate time interval in seconds as first argument with the script like
`python save_temp.py <time_per_loop>`


## Code explanation

One interval is considered as one loop over all connected sensors -- reading the data from the sensors, prompting it to the command line and saving it to a *.csv* file. The required time interval depends on the number of connected sensors in your network. The script will automatically calculate the minimum required time and tells you if your chosen time interval does not fit. By using multithreading the script takes about 16 seconds for one interval for a sensor network of a total of 176 sensors connected. The script is designed to run in background and also keeps track of noticeable values by logging errors to an *error.log* file. Additionally the option of activating the *bandgap-correction* is provided by passing the second argument "-b" (for *bandgap*) to the python script. See the aforementioned paper for more information.

Note the following example which will loop over all sensors reading and saving the temperature values in intervals of 10 seconds and the *bandgap-correction* activated:

`python save_temp.py 10 -b`

The code is written in Python 2.7 but we plan to migrate to Python 3 soon.
