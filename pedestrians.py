
signals = []
noOfSignals = 4


speeds = 1   # average speeds of vehicles

# Coordinates of pedestrians start
x = {'right':0, 'down':697, 'left':1400, 'up':657}
y = {'right':398, 'down':0, 'left':436, 'up':800}

vehicles = {'right':[], 'crossed':0, 'down':[],'crossed':0,'left':[],'crossed':0, 'up': [], 'crossed':0}

directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(530,200),(968,255),(830,630),(365,638)] #2 snf 4 y direction

# Coordinates of Horizontal signal image, timer, and vehicle count
signalCoodsHorizontal = [(365,255),(975,200),(968,638),(350,635)] #1 and 3 x dirction




# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

# Gap between vehicles
stoppingGap = 25    # stopping gap
movingGap = 25   # moving gap



class TrafficSignal:
    def __init__(self, red, green):
        self.red = red
        self.green = green
