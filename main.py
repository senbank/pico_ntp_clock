from machine import Pin, PWM, SPI
from passwd import passwd
import network, usocket, utime, ntptime, tm1637

# user data
ssid = passwd['ssid']
pw = passwd['password']

tm = tm1637.TM1637(clk=Pin(0), dio=Pin(1))
tm.brightness (val=0)

web_query_delay = 600000
timezone_hour = 3 # timezone offset (hours)
alarm = [7, 30, 0] # alarm[hour, minute, enabled(1=True)]

# connect to wifi
print("Connecting to WiFi...")
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

wifi.connect(ssid, pw)
while not wifi.isconnected():
    pass
print("Connected.")

#wifi.config(dhcp_hostname="esp32clock")
#print(wifi.config('dhcp_hostname'))

# setup web server
s = usocket.socket()
s.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
s.bind(("", 80)) # listen port 80
s.setblocking(False) # set to non-blocking mode
s.settimeout(1)
s.listen(1) # allow 1 client
print("Web server is now online at", ssid, "IP:", wifi.ifconfig()[0])

# webpage to be sent to user
def webpage(data):
    html = "<!DOCTYPE html>"
    html += "<html>"
    html += "<head>"
    html += "<title>MicroPython Alarm Clock</title>"
    html += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
    html += "<link rel=\"icon\" href=\"#\">"
    html += "<style>body {background-color: Black;} h1 {color: Red;} h2 {color: Darkred;} p1 {color: Yellow;} p2 {color:Yellow;}</style>"
    html += "</head>"
    html += "<body><center>"
    html += "<h1>MicroPython Alarm Clock</h1>"
    html += "<h2>When would you like to wake up?</h2>"
    html += "<form methon=\"GET\" action=\"\">"
    html += "<p1>Set at (hour/minute) "
    html += "<input type=\"text\" name=\"hour\" size=\"2\" maxlength=\"2\" max=\"23\" min=\"0\" value=\"" + str(data[0]) + "\">"
    html += " : <input type=\"text\" name=\"minute\" size=\"2\" maxlength=\"2\" max=\"59\" min=\"0\" value=\"" + str(data[1]) + "\">"
    html += "</p><p2>Enable: <select name=\"enable\">"
    if data[2] == 1:
        html += "<option value=\"0\">No</option>"
        html += "<option value=\"1\" selected>Yes</option>"
    else:
        html += "<option value=\"0\" selected>No</option>"
        html += "<option value=\"1\">Yes</option>"
    html += "</select></p>"
    html += "<p><input type=\"submit\" value=\"Update\"></p>"
    html += "</form>"
    html += "<p><input type=\"button\" value=\"Refresh\" onclick=\"window.location.href=''\"></p>"
    html += "</center></body>"
    html += "</html>"
    return html


update_time = utime.ticks_ms() - web_query_delay
clients = []

#p0 = Pin(2, Pin.OUT)



while True:
            
    utime.sleep(0.5)
    
    try:
        # listen to new clients
        client, addr = s.accept()
        print("New client connected, IP:", addr)
        clients.append(client)

    except:
    
        pass # no clients to connect now
        
    # if there are clients connected:
    for client in clients:
        
        try:
            # get HTTP response
            request = client.recv(1024)
            request_text = str(request.decode("utf-8"))
            para_pos = request_text.find("/?")
            
            # extract GET parameters and set the alarm
            if para_pos > 0:
                para_str = request_text[para_pos + 2:(request_text.find("HTTP/") - 1)]
                para_array = para_str.split('&')
                
                for i in range(len(para_array)):
                    para_array[i] = (para_array[i])[para_array[i].find('=') + 1:]
                
                for i in range(3):
                    if para_array[i].isdigit():
                        alarm[i] = int(para_array[i])
                    else:
                        print("!!! Alarm time set error !!!")
                
                print("Alarm has been set to", str(alarm[0]) + ":" + str(alarm[1]))
                utime.sleep(0.5)
                
                if alarm[2] == 1:
                    print("Alarm enabled")
                else:
                    print("Alarm disabled")
            
            # send web page to user
            response = webpage(alarm)
            print("Sending web page...")
            client.send("HTTP/1.1 200 OK\n")
            client.send("Content-Type: text/html; charset=utf-8\n")
            client.send("Connection: close\n\n")
            client.send(response)
            client.close()
            clients.remove(client)
            print("Client connection ended.")
            
        except:
            pass

    # update web clock time
    if utime.ticks_ms() - update_time >= web_query_delay:
        
        try:
            # update system time from NTP server
            ntptime.settime()
            print("NTP server query successful.")
            print("System time updated:", utime.localtime())
            update_time = utime.ticks_ms()
            
        except:
            print("NTP server query failed.")
    
    # display time and alarm status
    local_time_sec = utime.time() + timezone_hour * 3600
    local_time = utime.localtime(local_time_sec)
    time_str = "{3:02d}:{4:02d}:{5:02d}".format(*local_time)
    hour = "{3:n}".format(*local_time)
    minute = "{4:n}".format(*local_time)
    tm.numbers(int(hour), int(minute))
    
    #trigger alarm
    if alarm[2] == 1 and alarm[0] == local_time[3] and alarm[1] == local_time[4] and 2 >= local_time[5]:
        
        tones = {
        "B0": 31,
        "C1": 33,
        "CS1": 35,
        "D1": 37,
        "DS1": 39,
        "E1": 41,
        "F1": 44,
        "FS1": 46,
        "G1": 49,
        "GS1": 52,
        "A1": 55,
        "AS1": 58,
        "B1": 62,
        "C2": 65,
        "CS2": 69,
        "D2": 73,
        "DS2": 78,
        "E2": 82,
        "F2": 87,
        "FS2": 93,
        "G2": 98,
        "GS2": 104,
        "A2": 110,
        "AS2": 117,
        "B2": 123,
        "C3": 131,
        "CS3": 139,
        "D3": 147,
        "DS3": 156,
        "E3": 165,
        "F3": 175,
        "FS3": 185,
        "G3": 196,
        "GS3": 208,
        "A3": 220,
        "AS3": 233,
        "B3": 247,
        "C4": 262,
        "CS4": 277,
        "D4": 294,
        "DS4": 311,
        "E4": 330,
        "F4": 349,
        "FS4": 370,
        "G4": 392,
        "GS4": 415,
        "A4": 440,
        "AS4": 466,
        "B4": 494,
        "C5": 523,
        "CS5": 554,
        "D5": 587,
        "DS5": 622,
        "E5": 659,
        "F5": 698,
        "FS5": 740,
        "G5": 784,
        "GS5": 831,
        "A5": 880,
        "AS5": 932,
        "B5": 988,
        "C6": 1047,
        "CS6": 1109,
        "D6": 1175,
        "DS6": 1245,
        "E6": 1319,
        "F6": 1397,
        "FS6": 1480,
        "G6": 1568,
        "GS6": 1661,
        "A6": 1760,
        "AS6": 1865,
        "B6": 1976,
        "C7": 2093,
        "CS7": 2217,
        "D7": 2349,
        "DS7": 2489,
        "E7": 2637,
        "F7": 2794,
        "FS7": 2960,
        "G7": 3136,
        "GS7": 3322,
        "A7": 3520,
        "AS7": 3729,
        "B7": 3951,
        "C8": 4186,
        "CS8": 4435,
        "D8": 4699,
        "DS8": 4978
        }

        song = ["E5","G5","A5","P","E5","G5","B5","A5","P","E5","G5","A5","P","G5","E5"]
            
        print("!!! Alarm triggered !!")
        #buzzer = PWM(Pin(3, Pin.OUT), freq=440, duty=512)
        buzzer = PWM(Pin(3), freq=440)
        
        def playtone(frequency):
            buzzer.duty_u16(1000)
            buzzer.freq(frequency)

        def bequiet():
            buzzer.duty_u16(0)
    
        def playsong(mysong):
            for i in range(len(mysong)):
                if (mysong[i] == "P"):
                    bequiet()
                else:
                    playtone(tones[mysong[i]])
                utime.sleep(0.4)
            bequiet()
    
        playsong(song)
        
        """a = 515
        b = 698
        for i in range(2):
        
            buzzer.freq(a)
            utime.sleep(1)
            buzzer.freq(b)
            utime.sleep(1)"""
    
        buzzer.deinit()
        
        print("Alarm turned off.")
        #alarm[2] == 0
        
    elif 30 == local_time[4] and 58 <= local_time[5]:
        
        try:
            # update system time from NTP server
            ntptime.settime()
            print("NTP server query successful.")
            print("System time updated:", utime.localtime())
            
        except:
            
            print("NTP server query failed.")
    
    #p0.value(0)



