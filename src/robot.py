import ctre
import wpilib as wpi
import oi
import robotstate
import constants
from subsystems import drive
from utils import submanager
from wpilib.command import Scheduler

class Robot(wpi.IterativeRobot):
    def __init__(self):
        super().__init__()
        self.robot_state = robotstate.RobotState()
        self.subsystem_manager = submanager.SubsystemManager(
            drive.Drive())

        self.timer = wpi.Timer()
        self.oi = oi.OI()

    def robotInit(self):
        """Run when the robot turns on"""
        self.subsystem_manager.zeroSensors()
        self.subsystem_manager.reset()

    def disabledInit(self):
        """Run when the robot enters disabled mode"""
        self.subsystem_manager.zeroSensors()

    def disabledPeriodic(self):
        """Run periodically during disabled mode."""
        self.robot_state.updateState(self.timer.getFPGATimestamp())
        self.subsystem_manager.outputToSmartDashboard()
        self.robot_state.outputToSmartDashboard()
        pass

    def autonomousInit(self):
        """Run when the robot enters auto mode"""
        self.subsystem_manager.zeroSensors()
        pass

    def autonomousPeriodic(self):
        """Run periodically during auto mode."""
        self.subsystem_manager.update()
        self.robot_state.updateState(self.timer.getFPGATimestamp())
        self.subsystem_manager.outputToSmartDashboard()
        self.robot_state.outputToSmartDashboard()
        pass

    def teleopInit(self):
        """Run when the robot enters teleop mode"""
        self.subsystem_manager.zeroSensors()
        self.robot_state.updateState(self.timer.getFPGATimestamp())

    def teleopPeriodic(self):
        """Run periodically during teleop mode."""
        self.robot_state.updateState(self.timer.getFPGATimestamp())
        self.robot_state.outputToSmartDashboard()
        self.subsystem_manager.update()
        self.subsystem_manager.outputToSmartDashboard()
        Scheduler.getInstance().run()


# defining main function
if __name__ == '__main__':
    wpi.run(Robot)
