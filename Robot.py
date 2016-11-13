from a_star_rpb202 import AStar
from Encoders import *
from MotionController import *
from Motors import *
from Odometer import *
from Sensors import *

class Robot:

    def __init__(self):
        self.aStar = AStar()
        self.encoders = Encoders(self.aStar)
        self.motors = Motors(self.aStar, self.encoders)
        self.odometer = Odometer(self.encoders)
        self.motionCtrl = MotionController(self.odometer, self.motors)
        self.sensors = []
        self.buttons = []
        self.analog = [0, 0, 0, 0, 0, 0]
        self.camera = []

    def addSensor(self, sensorObj):
        self.sensors.append(sensorObj)

    def readSensors(self):
        for sensor in self.sensors:
            sensor.analog = self.analog[sensor.aPin]

    def addCamera(self, camera):
        self.camera = camera

    def readAStar(self):
        self.buttons = self.aStar.read_buttons()
        self.analog = self.aStar.read_analog()
        self.readSensors()

    def forward(self, speed):
        self.motors.forward(speed)

    def turn(self, rotSpeed):
        self.motors.turn(rotSpeed)

    def move(self, speed, rotSpeed):
        self.motors.cmd(speed - rotSpeed, speed + rotSpeed) 

    def stop(self):
        self.motors.stop()
