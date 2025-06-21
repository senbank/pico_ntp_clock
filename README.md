# pico_ntp_clock
Basic bedside alarm clock with ntp functionality
You need 6 male to female dupont cable to connecting the display and buzzer, 7-segment display tm1637, buzzer and a raspberry pi pico w or pico 2w or maybe an esp32
Edit code for gpio pins to connection for your liking you may use https://picow.pinout.xyz/ site for layout
Download the micropython for your device https://micropython.org/download/ and flash it on your device (using thonny simplifies the process)
Transfer the 3 files on to microcontroller (main.py, passwd.py, tm1637.py)
microcontroller pulls wifi credentials from passwd.py so edit it accordingly
adjust the main.py for your gpio pins and your timezone for displaying time correctly
connect it to a 5v 0.5a or higher amp usb wall plug and find out its ip via your wifi interface, you can access it via your browser but be careful to connect with http not https
