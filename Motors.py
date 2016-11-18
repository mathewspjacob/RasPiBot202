from PID import PID
from Encoders import Encoders

class Motors:

    def __init__(self, aStar, encoders, timeStep = .05):
        self.aStar = aStar
        self.encoders = encoders
        self.trimL = 1
        self.trimR = .95
        self.dirL = 1 * self.trimL
        self.dirR = 1 * self.trimR
        self.maxFwdCmd = 400
        self.maxRotCmd = 300
        self.prevCmdL = 0
        self.prevCmdR = 0
        self.accelStep = .07 # Max increase in command between time steps for .cmd method

        self.pidL = PID(.7, 6)
        self.pidR = PID(.7, 6)
        self.timeStep = timeStep
        self.tickDist = .32938 # Dist travelled per tick (in mm)
        self.speedCst = 742. # Approximate speed (in mm/s) for unit command
        self.lastCountL = 0
        self.lastCountR = 0
        self.speedL = 0
        self.speedR = 0

        
    # In-loop; This method is designed to be called within a loop with a short time step
    # Odometer.update() needs to be called in the loop to read the encoders counts. To
    # use this method independent from the odometer, change self.encoder.getCounts()
    # for self.encoders.readCounts() on the first line of the method.
    # speedTarget arguments are in mm/s.
    def speed(self, speedTargetL, speedTargetR):

        self.countL, self.countR = self.encoders.getCounts()

        deltaCountL = self.countL - self.lastCountL
        deltaCountR = self.countR - self.lastCountR

        self.speedL = deltaCountL * self.tickDist / self.timeStep
        self.speedR = deltaCountR * self.tickDist / self.timeStep
        cmdL = self.pidL.getOutput(speedTargetL, self.speedL, self.timeStep) / self.speedCst
        cmdR = self.pidR.getOutput(speedTargetR, self.speedR, self.timeStep) / self.speedCst

        # Limit motor command
        if cmdL < -1:
            cmdL = -1
        elif cmdL > 1:
            cmdL = 1
        if cmdR < -1:
            cmdR = -1
        elif cmdR > 1:
            cmdR = 1
        
        # Temporary fix to bypass defective pin B on left encoder
        self.setEncodersDir(cmdL, cmdR)
        
        self.aStar.motors(cmdL * self.dirL * self.maxFwdCmd, cmdR * self.dirR * self.maxFwdCmd)

        self.lastCountL += deltaCountL
        self.lastCountR += deltaCountR

    # In-loop; This method is to be called from within a loop.
    # cmd arguments are the motor speed commands ranging from -1 to 1 (-max to max speed)
    def cmd(self, cmdL, cmdR):
        # Limit motor acceleration
        if cmdL - self.prevCmdL > self.accelStep:
            cmdL = self.prevCmdL + self.accelStep
        if cmdR - self.prevCmdR > self.accelStep:
            cmdR = self.prevCmdR + self.accelStep
        # Limit motor command
        if cmdL < -1:
            cmdL = -1
        elif cmdL > 1:
            cmdL = 1
        if cmdR < -1:
            cmdR = -1
        elif cmdR > 1:
            cmdR = 1
        # Temporary fix to bypass defective pin B on left encoder
        self.setEncodersDir(cmdL, cmdR)
        # Command motors
        self.aStar.motors(cmdL * self.dirL * self.maxFwdCmd, cmdR * self.dirR * self.maxFwdCmd)
        self.prevCmdL, self.prevCmdR = cmdL, cmdR

    def forward(self, cmd):
        self.aStar.motors(cmd * self.dirL * self.maxFwdCmd, cmd * self.dirR * self.maxFwdCmd)
        # Temporary fix to bypass defective pin B on left encoder
        self.setEncodersDir(cmd, cmd)
        
    def turn(self, rotCmd):
        self.aStar.motors(-rotCmd * self.dirL * self.maxRotCmd, rotCmd * self.dirR * self.maxRotCmd)

    def reset(self):
        self.pidL.reset()
        self.pidR.reset()
        self.lastCountL = 0
        self.lastCountR = 0
        self.speedL = 0
        self.speedR = 0

    def stop(self):
        self.aStar.motors(0, 0)
        self.prevCmdL = 0
        self.prevCmdR = 0
        self.reset()

    # Temporary fix to bypass defective pin B on left encoder
    def setEncodersDir(self, cmdL, cmdR):
        if cmdL >= 0:
            self.encoders.countSignLeft = 1
        else:
            self.encoders.countSignLeft = -1
        if cmdR >= 0:
            self.encoders.countSignRight = 1
        else:
            self.encoders.countSignRight = -1
        
        
