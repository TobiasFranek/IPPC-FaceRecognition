import RPi.GPIO as GPIO
import time

buzzer = 23

GPIO.setmode(GPIO.BCM)

GPIO.setup(buzzer,GPIO.OUT)

GPIO.output(buzzer,GPIO.HIGH)
time.sleep(1.5)

GPIO.output(buzzer,GPIO.LOW)
time.sleep(0.3)

GPIO.output(buzzer,GPIO.HIGH)
time.sleep(0.5)

GPIO.output(buzzer,GPIO.LOW)
time.sleep(0.3)

GPIO.output(buzzer,GPIO.HIGH)
time.sleep(0.2)


GPIO.output(buzzer,GPIO.LOW)