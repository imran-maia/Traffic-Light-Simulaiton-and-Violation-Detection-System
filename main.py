import random
import time
import threading
import pygame
import sys
import os
from tkinter import Tk
from tkinter import *
from tkinter import messagebox
import pedestrians as pd


# Default values of signal timers
defaultGreen = {0:10, 1:10, 2:10, 3:10}
defaultRed = 150
defaultYellow = 5

signals = []
noOfSignals = 4
currentGreen = 0   
nextGreen = (currentGreen+1)%noOfSignals    
currentYellow = 0

# Average speeds of vehicles

speeds = {'car':0.4, 'bus':0.4, 'truck':0.4, 'bike':0.4}  

# Coordinates of vehicles' start
x = {'right':[0,0,0], 'down':[780,755,720], 'left':[1400,1400,1400], 'up':[585,620,655]}    
y = {'right':[345,380,415], 'down':[0,0,0], 'left':[550,515,480], 'up':[800,800,800]}

vehicles = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 'down': {0:[], 1:[], 2:[], 'crossed':0}, 'left': {0:[], 1:[], 2:[], 'crossed':0}, 'up': {0:[], 1:[], 2:[], 'crossed':0}}
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'bike'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(440,200),(930,200),(930,630),(440,630)]
signalTimerCoods = [(440,180),(930,180),(930,720),(440,720)]

# Coordinates of stop lines
stopLines = {'right': 480, 'down': 250, 'left': 920, 'up': 675}
defaultStop = {'right': 470, 'down': 240, 'left': 930, 'up': 685}


# Gap between vehicles
stoppingGap = 25    # stopping gap
movingGap = 25      # moving gap

# Set allowed vehicle types here
allowedVehicleTypes = {'car': True, 'bus': True, 'truck': True, 'bike': True}
allowedVehicleTypesList = []
vehiclesTurned = {'right': {1:[], 2:[]}, 'down': {1:[], 2:[]}, 'left': {1:[], 2:[]}, 'up': {1:[], 2:[]}}
vehiclesNotTurned = {'right': {1:[], 2:[]}, 'down': {1:[], 2:[]}, 'left': {1:[], 2:[]}, 'up': {1:[], 2:[]}}
rotationAngle = 3
mid = {'right': {'x':705, 'y':445}, 'down': {'x':695, 'y':450}, 'left': {'x':695, 'y':425}, 'up': {'x':695, 'y':400}}

# Set random or default green signal time here 
randomGreenSignalTimer = True
# Set random green signal time range here 
randomGreenSignalTimerRange = [10,20]

timeElapsed = 0
simulationTime = 3000
timeElapsedCoods = (1100,50)
vehicleCountTexts = ["0", "0", "0", "0"]
vehicleCountCoods = [(480,210),(880,210),(880,550),(480,550)]

pygame.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""
        
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        self.crossedIndex = 0
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.image = pygame.image.load(path)


        if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):   
            if(direction=='right'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                - vehicles[direction][lane][self.index-1].image.get_rect().width 
                - stoppingGap         
            elif(direction=='left'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                + vehicles[direction][lane][self.index-1].image.get_rect().width 
                + stoppingGap
            elif(direction=='down'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                - vehicles[direction][lane][self.index-1].image.get_rect().height 
                - stoppingGap
            elif(direction=='up'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                + vehicles[direction][lane][self.index-1].image.get_rect().height 
                + stoppingGap
        else:
            self.stop = defaultStop[direction]
            
        # Set new starting and stopping coordinate
        if(direction=='right'):
            temp = self.image.get_rect().width + stoppingGap    
            x[direction][lane] -= temp
        elif(direction=='left'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif(direction=='down'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif(direction=='up'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        if(self.direction=='right'):
            if(self.crossed==0 and self.x+self.image.get_rect().width>stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.lane == 1 or self.lane==2):
                    if(self.crossed==0 or self.x+self.image.get_rect().width<stopLines[self.direction]+40):
                        if((self.x+self.image.get_rect().width<=self.stop or (currentGreen==0 and currentYellow==0) or self.crossed==1)
                                and (self.index==0 or self.x+self.image.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):
                            self.x += self.speed
                    else:
                        if(self.turned==0):
                            if self.lane==1 :
                                self.rotateAngle += rotationAngle
                                self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                                self.x += 4.0
                                self.y -= 2.8
                                if(self.rotateAngle==90):
                                    self.turned = 1
                                    vehiclesTurned[self.direction][self.lane].append(self)
                                    self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                            else:
                                self.x+=self.speed
                        else:
                            if(self.crossedIndex==0 or (self.y>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().height + movingGap))):
                                self.y -= self.speed

            else: 
                if(self.crossed == 0):
                    if((self.x+self.image.get_rect().width<=self.stop or (currentGreen==0 and currentYellow==0)) and (self.index==0 or self.x+self.image.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - movingGap))):                
                        self.x += self.speed
                else:
                    if((self.crossedIndex==0) or (self.x+self.image.get_rect().width<(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].x - movingGap))):                 
                        self.x += self.speed
            if (signals[0].yellow==4 and signals[0].green==0
                and self.x + self.image.get_rect().width > self.stop
                and self.x + self.image.get_rect().width <= self.stop+50):
                messagebox.showinfo("Notice", f"There is a violation {self.vehicleClass}")
                self.crossed = 1
                self.x += self.speed
        elif(self.direction=='down'):
            if(self.crossed==0 and self.y+self.image.get_rect().height>stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.lane == 1 or self.lane==2):
                    if(self.crossed==0 or self.y+self.image.get_rect().height<stopLines[self.direction]+50):
                        if((self.y+self.image.get_rect().height<=self.stop or (currentGreen==1 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                            self.y += self.speed
                    else:
                        if(self.turned==0):
                            if self.lane==1 :
                                self.rotateAngle += rotationAngle
                                self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                                self.x += 1.2
                                self.y += 3.8
                                if(self.rotateAngle==90):
                                    self.turned = 1
                                    vehiclesTurned[self.direction][self.lane].append(self)
                                    self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                            else:
                                self.y+=self.speed
                        else:
                            if(self.crossedIndex==0 or ((self.x + self.image.get_rect().width) < (vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x - movingGap))):
                                self.x += self.speed

            else: 
                if(self.crossed == 0):
                    if((self.y+self.image.get_rect().height<=self.stop or (currentGreen==1 and currentYellow==0)) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap))):                
                        self.y += self.speed
                else:
                    if((self.crossedIndex==0) or (self.y+self.image.get_rect().height<(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].y - movingGap))):                
                        self.y += self.speed
            if (signals[1].yellow==4 and signals[1].green==0
                and self.y + self.image.get_rect().height > self.stop
                and self.y + self.image.get_rect().height <= self.stop+50):
                messagebox.showinfo("Notice", f"There is a violation {self.vehicleClass} ")
                self.crossed = 1
                self.x += self.speed
        elif(self.direction=='left'):
            if(self.crossed==0 and self.x<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.lane == 1 or self.lane==2):
                    if(self.crossed==0 or self.x>stopLines[self.direction]-70):
                        if((self.x>=self.stop or (currentGreen==2 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                            self.x -= self.speed
                    else: 
                        if(self.turned==0):
                            if self.lane==1 :
                                self.rotateAngle += rotationAngle
                                self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                                self.x -= 3
                                self.y += 1.2
                                if(self.rotateAngle==90):
                                    self.turned = 1
                                    vehiclesTurned[self.direction][self.lane].append(self)
                                    self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                            else :
                                self.x-=self.speed
                        else:
                            if(self.crossedIndex==0 or ((self.y + self.image.get_rect().height) <(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y  -  movingGap))):
                                self.y += self.speed

            else: 
                if(self.crossed == 0):
                    if((self.x>=self.stop or (currentGreen==2 and currentYellow==0)) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap))):                
                        self.x -= self.speed
                else:
                    if((self.crossedIndex==0) or (self.x>(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].x + vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width + movingGap))):                
                        self.x -= self.speed
            if (signals[2].yellow==4 and signals[2].green==0
                and self.x + self.image.get_rect().width > self.stop
                and self.x + self.image.get_rect().width <= self.stop+50):
                messagebox.showinfo("Notice", f"There is a violation {self.vehicleClass} ")
                self.crossed = 1
                self.x += self.speed
        elif(self.direction=='up'):
            if(self.crossed==0 and self.y<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.lane == 1):
                    if(self.crossed==0 or self.y>stopLines[self.direction]-60):
                        if((self.y>=self.stop or (currentGreen==3 and currentYellow==0) or self.crossed == 1) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height +  movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):
                            self.y -= self.speed
                    else:   
                        if(self.turned==0):
                            if self.lane==1 :
                                self.rotateAngle += rotationAngle
                                self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                                self.x -= 2
                                self.y -= 2.2
                                if(self.rotateAngle==90):
                                    self.turned = 1
                                    vehiclesTurned[self.direction][self.lane].append(self)
                                    self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                            else:
                                if(self.crossedIndex==0 or (self.x>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width + movingGap))):
                                    self.x -= self.speed
                        else :
                            self.x-=self.speed
            else: 
                if(self.crossed == 0):
                    if((self.y>=self.stop or (currentGreen==3 and currentYellow==0)) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + movingGap))):                
                        self.y -= self.speed
                else:
                    if((self.crossedIndex==0) or (self.y>(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].y + vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().height + movingGap))):                
                        self.y -= self.speed
            if (signals[3].yellow == 4 and signals[3].green == 0
                    and self.y + self.image.get_rect().height > self.stop
                    and self.y + self.image.get_rect().height <= self.stop + 50):
                messagebox.showinfo("Notice", f"There is a violation {self.vehicleClass}")
                self.crossed = 1
                self.x += self.speed

# Initialization of signals with default values
def initialize():
    minTime = randomGreenSignalTimerRange[0]
    maxTime = randomGreenSignalTimerRange[1]
    if(randomGreenSignalTimer):
        ts1 = TrafficSignal(0, defaultYellow, random.randint(minTime,maxTime))
        signals.append(ts1)
        ts2 = TrafficSignal(ts1.red+ts1.yellow+ts1.green, defaultYellow, random.randint(minTime,maxTime))
        signals.append(ts2)
        ts3 = TrafficSignal(defaultRed, defaultYellow, random.randint(minTime,maxTime))
        signals.append(ts3)
        ts4 = TrafficSignal(defaultRed, defaultYellow, random.randint(minTime,maxTime))
        signals.append(ts4)
    else:
        ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
        signals.append(ts1)
        ts2 = TrafficSignal(ts1.yellow+ts1.green, defaultYellow, defaultGreen[1])
        signals.append(ts2)
        ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
        signals.append(ts3)
        ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
        signals.append(ts4)
    repeat()


def repeat():
    global currentGreen, currentYellow, nextGreen
    while(signals[currentGreen].green>0):   
        updateValues()
        time.sleep(1)
    currentYellow = 1   # set yellow signal on
    
    # Reset stop coordinates of lanes and vehicles 
    for i in range(0,3):
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    while(signals[currentGreen].yellow>0):  # while the timer of current yellow signal is not zero
        updateValues()
        time.sleep(1)
    currentYellow = 0   # set yellow signal off
    
    # Reset all signal times of current signal to default/random times
    if(randomGreenSignalTimer):
        signals[currentGreen].green = random.randint(randomGreenSignalTimerRange[0],randomGreenSignalTimerRange[1])
    else:
        signals[currentGreen].green = defaultGreen[currentGreen]
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed
       
    currentGreen = nextGreen # set next signal as green signal
    nextGreen = (currentGreen+1)%noOfSignals    # set next green signal
    signals[nextGreen].red = signals[currentGreen].yellow+signals[currentGreen].green    
    repeat()

# Update values of the signal timers after every second
def updateValues():
    for i in range(0, noOfSignals):
        if(i==currentGreen):
            if(currentYellow==0):
                signals[i].green-=1
            else:
                signals[i].yellow-=1
        else:
            signals[i].red-=1

# Generating vehicles in the simulation
def generateVehicles():
    while(True):
        vehicle_type = random.choice(allowedVehicleTypesList)
        lane_number = random.randint(1,2)
        will_turn = 0
        if(lane_number == 1):
            temp = random.randint(0,99)
            if(temp<40):
                will_turn = 1
        elif(lane_number == 2):
            temp = random.randint(0,99)
            if(temp<40):
                will_turn = 1
        temp = random.randint(0,99)
        direction_number = 0
        dist = [25,50,75,100]
        if(temp<dist[0]):
            direction_number = 0
        elif(temp<dist[1]):
            direction_number = 1
        elif(temp<dist[2]):
            direction_number = 2
        elif(temp<dist[3]):
            direction_number = 3
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn)
        time.sleep(1)



def simTime():
    global timeElapsed, simulationTime
    while(True):
        timeElapsed += 1
        time.sleep(1)
        if(timeElapsed==simulationTime):
            os._exit(1)


## For Pedistrain Signal ##

# Default values of signal timers
defaultGreen = {0: 10, 1: 10, 2: 10, 3: 10}
defaultRed = 150
defaultYellow = 5

noOfSignals = 4
currentGreen = 0  
nextGreen = (currentGreen + 1) % noOfSignals  
currentYellow = 0  

pedSpeed = { 'pedestrian': 0.2}  # average speeds of vehicles

# Coordinates of pedestrain' start "moving"
xPed = {'right': [0, 0, 0], 'down': [560, 540, 627], 'left': [1500, 1500, 1500], 'up': [717, 840, 772]}
yPed = {'right': [278, 605, 528], 'down': [0, 0, 0], 'left': [480, 300, 448], 'up': [987, 987, 987]}

peds = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
pedVehicleTypes = {0: 'pedestrian', 1: 'pedestrian', 2: 'pedestrian', 3: 'pedestrian'}
pedDirectionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}


# Coordinates of pedestrian stop lines
pedStopLines = {'right': 480, 'down': 250, 'left': 920, 'up': 675}
pedDefaultStop = {'right': 470, 'down': 240, 'left': 930, 'up': 685}


# Gap between pedestrian 
pedStoppingGap = 15  # stopping gap
pedMovingGap = 15    # moving gap
pygame.init()
simulation = pygame.sprite.Group()


class pedMove(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = pedSpeed[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = xPed[direction][lane]
        self.y = yPed[direction][lane]
        self.crossed = 0
        peds[direction][lane].append(self)
        self.index = len(peds[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.image = pygame.image.load(path)

        if (len(peds[direction][lane]) > 1 and peds[direction][lane][
            self.index - 1].crossed == 0):  
            if (direction == 'right'):
                self.stop = peds[direction][lane][self.index - 1].stop - peds[direction][lane][
                    self.index - 1].image.get_rect().width - pedStoppingGap  
            elif (direction == 'left'):
                self.stop = peds[direction][lane][self.index - 1].stop + peds[direction][lane][
                    self.index - 1].image.get_rect().width + pedStoppingGap
            elif (direction == 'down'):
                self.stop = peds[direction][lane][self.index - 1].stop - peds[direction][lane][
                    self.index - 1].image.get_rect().height - pedStoppingGap
            elif (direction == 'up'):
                self.stop = peds[direction][lane][self.index - 1].stop + peds[direction][lane][
                    self.index - 1].image.get_rect().height + pedStoppingGap
        else:
            self.stop = pedDefaultStop[direction]

        # Set new starting and stopping coordinate
        if (direction == 'right'):
            temp = self.image.get_rect().width + pedStoppingGap
            xPed[direction][lane] -= temp
        elif (direction == 'left'):
            temp = self.image.get_rect().width + pedStoppingGap
            xPed[direction][lane] += temp
        elif (direction == 'down'):
            temp = self.image.get_rect().height + pedStoppingGap
            yPed[direction][lane] -= temp
        elif (direction == 'up'):
            temp = self.image.get_rect().height + pedStoppingGap
            yPed[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        if (self.direction == 'down'):
            if (self.crossed == 0 and self.y + self.image.get_rect().height > pedStopLines[self.direction]):
                self.crossed = 1
            if ((self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or (
                    currentGreen == 1 and currentYellow == 0)) and (
                    self.index == 0 or self.y + self.image.get_rect().height < (
                    peds[self.direction][self.lane][self.index - 1].y - pedMovingGap))):
                self.y += self.speed
            if (signals[1].yellow==4 and signals[1].green==0
                and self.y + self.image.get_rect().height > self.stop
                and self.y + self.image.get_rect().height <= self.stop+50):
                messagebox.showinfo("Notice", f"There is a violation {self.vehicleClass}") 
                self.crossed = 1
                self.x += self.speed
        elif (self.direction == 'up'):
            if (self.crossed == 0 and self.y < pedStopLines[self.direction]):
                self.crossed = 1
            if ((self.y >= self.stop or self.crossed == 1 or (currentGreen == 3 and currentYellow == 0)) and (
                    self.index == 0 or self.y > (
                    peds[self.direction][self.lane][self.index - 1].y + peds[self.direction][self.lane][
                self.index - 1].image.get_rect().height + pedMovingGap))):
                self.y -= self.speed
            if (signals[3].yellow == 4 and signals[3].green == 0
                    and self.y + self.image.get_rect().height > self.stop
                    and self.y + self.image.get_rect().height <= self.stop + 50):
                messagebox.showinfo("Notice", f" There is a violation {self.vehicleClass}")
                self.crossed = 1
                self.x += self.speed

# Generating vehicles in the simulation
def generatePed():
    while (True):
        vehicle_type = random.randint(0, 3)
        lane_number = random.randint(1, 1)
        temp = random.randint(0, 99)
        direction_number = 0
        dist = [25, 50, 75, 100]
        
        if (temp < dist[1]):
            direction_number = 1
        elif (temp < dist[3]):
            direction_number = 3
        pedMove(lane_number, pedVehicleTypes[vehicle_type], direction_number, pedDirectionNumbers[direction_number])
        time.sleep(1)

# The main function class
class Main:
    global allowedVehicleTypesList

    i = 0
    for vehicleType in allowedVehicleTypes:
        if(allowedVehicleTypes[vehicleType]):
            allowedVehicleTypesList.append(i)
        i += 1
    thread1 = threading.Thread(name="initialization",target=initialize, args=())    # initialization
    thread1.daemon = True
    thread1.start()

    # Colours
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize
    screenWidth = 1400
    screenHeight = 900
    screenSize = (screenWidth, screenHeight)

    # Setting background image 
    background = pygame.image.load('images/background.jpg')
    background = pygame.transform.flip(background, True,False)

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("Traffic System")

    # Loading  pedestrians signals
    pedestriansgreenSignal = pygame.image.load('images/pedestrians signals/green_ped.png')
    pedestriansgreenSignal = pygame.transform.rotate(pedestriansgreenSignal, -90)
    pedestriansredSignal = pygame.image.load('images/pedestrians signals/red_ped.png')
    pedestriansredSignal = pygame.transform.rotate(pedestriansredSignal, -90)

    # Loading  pedestrians signals
    pedestriansgreenSignalH = pygame.transform.rotate(pygame.image.load('images/pedestrians signals/horizantol/green_ped.png'),-90)
    pedestriansredSignalH = pygame.transform.rotate(pygame.image.load('images/pedestrians signals/horizantol/red_ped.png'),-90)

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')


    font = pygame.font.Font(None, 30)
    thread2 = threading.Thread(name="generateVehicles",target=generateVehicles, args=())    
    thread2.daemon = True
    thread2.start()

    thread21 = threading.Thread(name="generatePed", target=generatePed, args=())  
    thread21.daemon = True
    thread21.start()

    thread3 = threading.Thread(name="simTime",target=simTime, args=())
    thread3.daemon = True
    thread3.start()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                
                sys.exit()

        # Display background in simulation
        screen.blit(background,(0,0))
        
        # Display signal according to current status: green, yello, or red
        for i in range(0,noOfSignals):  
            if(i==currentGreen):
                if(currentYellow==1):
                    signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoods[i])

            else:
                if(signals[i].red<=10):
                    signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
        signalTexts = ["","","",""]


        # Display signal pedestrian
        screen.blit(pedestriansredSignalH, pd.signalCoodsHorizontal[0])
        screen.blit(pedestriansredSignal, pd.signalCoods[1])
        screen.blit(pedestriansredSignalH, pd.signalCoodsHorizontal[2])
        screen.blit(pedestriansredSignal, pd.signalCoods[3])

        for i in range(0,noOfSignals):
            if  signals[i].red==0 and signals[i].yellow==5 :
                if i==0 or i==2 :
                    screen.blit(pedestriansgreenSignalH, pd.signalCoodsHorizontal[i -2])
                else:
                    screen.blit(pedestriansgreenSignal, pd.signalCoods[i-2])
       
        # Display the vehicles

        for vehicle in simulation:
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()

        pygame.display.update()



Main()
