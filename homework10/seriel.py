import serial
ser = serial.Serial('/dev/tty.usbmodem1101') # the name of your port here
print('Opening port: ' + str(ser.name))
import pygame
WIDTH = 600
HEIGHT = 600
n1_int = 0
n2_int = 0
def update():
   n_bytes = ser.readline() # read all the letters available
   s = str(n_bytes) # turn them into a str
   result1 = s[s.find('(')+1:s.find(',')] # find everything beween ( and ,
   result2 = s[s.find(',')+1:s.find(')')] # find everything between , and )
   global n1_int
   n1_int = int(result1) # convert str to int
   global n2_int
   n2_int = int(result2)
def draw():
   screen.fill((0, 0, 0))
   screen.draw.text('a0: ' + str(n1_int)+ '\n' + 'a1: ' + str(n2_int),(0, 0))