#!/usr/bin/env python3
from urllib import request
import json
import time
import math
import spidev
import RPi.GPIO as GPIO
import dht11
#from dht11.__init__ import DHT11Result, DHT11 #lol

# Enable SPI
spi = spidev.SpiDev(0,0)
spi.max_speed_hz = 3600000 #3.6Mhz max speed at 5v specified in MCP3008 datasheet.

# Thanks scotty101 of raspberrypi.org forums
# https://www.raspberrypi.org/forums/viewtopic.php?t=199793#p1246000
def read_mcp3008(adc_ch):
    # MCP3008.pdf "5.0 SERIAL COMMUNICATION"
    # Table 5-2 (1000 = CH0, 1001 = CH1, 1010 = CH2, ...)
    # 8 in binary = 1000, 9 in binary = 1001, ...
    # "<<4" shifts 4 positions to the left, 1000 becomes 10000000
    adc = spi.xfer2([1,(8+adc_ch)<<4,0])
    # MCP3008 "6.1 [Usage] with Microcontroller (MCU) SPI Ports"
    # adc[1] contains 5 bits of garbage, 1 null bit, 2 bits of data
    # "&3" does a bitmask (0011), "<< 8" shifts it all 8 bits to the left
    # adc[2] contains 8 bits of more data
    data = ((adc[1]&3) << 8) + adc[2]

    return data

def calc_volt(adc, vref = 5):
    # Calculate voltage form ADC value
    return (vref * adc) / 1024

def XC4494(adc):
    #Steinhart–Hart equation for 10k resistor
    temp = math.log(((10240000/adc) - 10000)) #XC4494.pdf
    temp = 1 / (0.001129148 + (0.000234125 + (0.0000000876741 * temp * temp ))* temp ) # XC4494.pdf
    temp = temp - 273.15 # Convert Kelvin to Celcius
    return temp

def init_dht11():
    # initialize GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    return dht11.DHT11(pin = 3)

instance = init_dht11()

while True:
    datas = {}
    adc_0 = read_mcp3008(0)
    #print("Ch 0:", round(calc_volt(adc_0), 2), "V. Celsius:", XC4494(adc_0))
    datas["Celsius"] = round(calc_volt(adc_0), 2)
    adc_1 = read_mcp3008(1)
    #print("Ch 1:", round(calc_volt(adc_1), 2), "V. (Soil Moisture)")
    datas["Soil Moisture"] = round(calc_volt(adc_1), 2)
    while True:
      result = instance.read()
      if not result.is_valid():
          continue
      #print("Temperature: %-3.1f C" % result.temperature)
      #print("Humidity: %-3.1f %%" % result.humidity)
      datas["Celsius2"] = result.temperature
      datas["Humidity"] = result.humidity
      break
    print(datas)
    req = request.Request("http://192.168.1.23:8080/telegraf", data=json.dumps(datas).encode('utf8'), headers={'content-type': 'application/json'})
    print(request.urlopen(req).getcode())
    time.sleep(1)



