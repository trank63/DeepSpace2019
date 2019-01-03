import math

from ctre.pigeonimu import PigeonIMU
from wpilib import PowerDistributionPanel
from wpilib import SmartDashboard as Dash
from wpilib import analoggyro, hal

from constants import Constants
from subsystems import drive
from utils import pose, singleton, vector2d


class Odemetry(metaclass=singleton.Singleton):
    """A singleton dealing with the odemetry of the robot."""

    def __init__(self):
        """Initilize the Odemetry class."""
        super().__init__()
        self.drive = drive.Drive()
        self.timestamp = 0
        self.last_timestamp = 0
        self.dt = 0

        # Gyroscope
        if hal.isSimulation():
            self.gyro = analoggyro.AnalogGyro(0)
        else:
            self.gyro = PigeonIMU(Constants.GYRO_ID)

        self.calibrate()

        self.pose = pose.Pose()

        self.last_left_encoder_distance = 0
        self.last_right_encoder_distance = 0
        self.last_angle = 0

    def reset(self):
        if hal.isSimulation():
            self.gyro.reset()
        else:
            self.gyro.setYaw(0, 0)

    def calibrate(self):
        if hal.isSimulation():
            self.gyro.calibrate()
        else:
            # TODO how to calibrate pigeon
            pass

    def outputToSmartDashboard(self):
        Dash.putNumber(
            "Left Encoder Ticks", self.drive.getDistanceTicksLeft())
        Dash.putNumber(
            "Right Encoder Ticks", self.drive.getDistanceTicksRight())
        Dash.putNumber(
            "Left Encoder Inches", self.drive.getDistanceInchesLeft())
        Dash.putNumber(
            "Right Encoder Inches", self.drive.getDistanceInchesRight())

        Dash.putNumber("Pos X", self.pose.pos.x)
        Dash.putNumber("Pos Y", self.pose.pos.y)
        Dash.putNumber("Angle", self.getAngle())

    def getDistance(self):
        """Use encoders to return the distance driven in inches."""
        return (self.drive.getDistanceInchesLeft() + self.drive.getDistanceInchesRight()) / 2.0

    def getDistanceDelta(self):
        """Use encoders to return the distance change in inches."""
        return (((self.drive.getDistanceInchesLeft()-self.last_left_encoder_distance) + (self.drive.getDistanceInchesRight()-self.last_right_encoder_distance)) / 2.0)

    def getVelocity(self):
        """Use the distance delta to return the velocity in inches/sec."""
        if self.dt != 0:
            return self.getDistanceDelta()/self.dt
        else:
            return 0

    def getAngle(self):
        """Use the gyroscope to return the angle in radians."""
        if hal.isSimulation():
            return math.radians(self.gyro.getAngle())
        else:
            return math.radians(self.gyro.getYawPitchRoll()[0])

    def getAngleDelta(self):
        """Use the gyroscope to return the angle change in radians."""
        return self.pose.angle-self.last_angle

    def updateState(self, timestamp):
        """Use odemetry to update the robot state."""
        self.timestamp = timestamp
        self.dt = self.timestamp-self.last_timestamp
        # update angle
        self.pose.angle = self.getAngle()
        # update x and y positions
        self.pose.pos.x += self.getDistanceDelta() * math.cos(self.pose.angle)
        self.pose.pos.y += self.getDistanceDelta() * math.sin(self.pose.angle)
        # update last distances for next periodic
        self.last_left_encoder_distance = self.drive.getDistanceInchesLeft()
        self.last_right_encoder_distance = self.drive.getDistanceInchesRight()
        # update last angle and timestamp for next periodic
        self.last_angle = self.pose.angle
        self.last_timestamp = self.timestamp

    def getState(self):
        """Return the robot pose (position [inches] and orientation [radians])."""
        return self.pose
