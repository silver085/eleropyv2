import time
import ubinascii
import network
import machine

ssid = 'Ludwig LAN Beethoven'
password = '!Whoo117py'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)
station.config(dhcp_hostname='eleroradio')
print("Connecting to wifi...")
try:
    while not station.isconnected():
        time.sleep(1)
except KeyboardInterrupt:
    import machine
    pass
print('Connection successful')
print(station.ifconfig())
