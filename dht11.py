#!/usr/bin/python
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Modified By: Andrea C. Martinez
# January 2016
# Folded in MQTT Python library from Paho and interleaved publish to topics.
# Publishing to the "toggle" topic will send a signal to the MQTT gateway turn on/off an LED
# Publishing to the "sensor" topic will send temperature and humidity readings to the MQTT gateway

#Modifications 
import sys
import netifaces as ni 
import re
import datetime
import time
import Adafruit_DHT

try:
  import paho.mqtt.publish as publish
except ImportError:
  import os
  import inspect
  cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../src")))
  if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)
  import paho.mqtt.publuish as publish


# Parse command line parameters.
sensor_args = { '11': Adafruit_DHT.DHT11,
				'22': Adafruit_DHT.DHT22,
				'2302': Adafruit_DHT.AM2302 }
if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
	sensor = sensor_args[sys.argv[1]]
	pin = sys.argv[2]
else:
	print 'usage: sudo ./Adafruit_DHT.py [11|22|2302] GPIOpin#'
	print 'example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO #4'
	sys.exit(1)

#Let's use the last octet of our ip address as a "sensor identifier"
ni.ifaddresses('wlan0')
ip = ni.ifaddresses('wlan0')[2][0]['addr']
ipRegex = re.compile(r'(.*)\.(.*)\.(.*)\.(.*)')
ipOctets = ipRegex.search(ip)
#grab the last octet, and make that the sensor id
sensor_id = ipOctets.group(4)

# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
while True:
  publish.single("toggle", "1", hostname="localhost")
  humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

  # Un-comment the line below to convert the temperature to Fahrenheit.
  #temperature = temperature * 9/5.0 + 32

  # Note that sometimes you won't get a reading and
  # the results will be null (because Linux can't
  # guarantee the timing of calls to read the sensor).  
  # If this happens try again!
  if humidity is not None and temperature is not None:
        # Un-comment the line below to convert the temperature to Fahrenheit.
        temperature = temperature * 9/5.0 + 32
	print 'Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity)
        #get the current timestamp
        timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        payload = "{\"sensor_id\": " + str(sensor_id) + ", \"timestamp\": " + str(timestamp) + ", \"temperature\": " + str(temperature) + ", \"humidity\": " + str(humidity) + " }"
        publish.single("sensor", payload, hostname="localhost")
        publish.single("toggle", "0", hostname="localhost")
        time.sleep(5)
  else:
	print 'Failed to get reading. Try again!'
	sys.exit(1)
  publish.single("toggle", "0", hostname="localhost")
