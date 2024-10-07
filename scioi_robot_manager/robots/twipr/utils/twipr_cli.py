from robots.twipr.twipr_manager import TWIPR_Manager
from robots.twipr.twipr import TWIPR
from extensions.cli.cli import *


# TWIPR Command Set
# General Commands:
# info --detail
# stop
# controlmode -m
# controlconfig --config
# statefeedback --gain
# input -l -r
# speed -f -t
# sensors --detail
# state --detail
# stream --values
# led --front --back --all --color
# restart


class TWIPR_CommandSet(CommandSet):
    robot: TWIPR

    def __init__(self, robot: TWIPR):
        super().__init__(name=robot.id)
        self.robot = robot


# TWIPR Manager Command Set

# stop
# info
# list --detail
# controlmode -a -m --all
# stream

class TWIPR_Manager_CommandSet(CommandSet):
    name = 'robots'
    description = 'Functions related to connected TWIPR'

    def __init__(self, manager: TWIPR_Manager):
        super().__init__(name=self.name)

        self.manager = manager

        self.manager.registerCallback('new_robot', self._newRobot_callback)
        self.manager.registerCallback('robot_disconnected', self._robotDisconnected_callback)

        self.addCommand(TWIPR_Manager_Command_List(self.manager))
        self.addCommand(TWIPR_Manager_Command_Stop(self.manager))
        self.addCommand(TWIPR_Manager_Command_Mode(self.manager))

    def _newRobot_callback(self, robot, *args, **kwargs):
        ...

    def _robotDisconnected_callback(self, robot, *args, **kwargs):
        ...


# ======================================================================================================================
class TWIPR_Manager_Command_List(Command):
    description = 'Lists all connected TWIPR robots'
    name = 'list'
    manager: TWIPR_Manager
    arguments = {
        'detail': CommandArgument(
            name='detail',
            type=bool,
            short_name='d',
            description='Shows detailed information for each robot',
            is_flag=True,
            default=False
        )
    }

    def __init__(self, manager: TWIPR_Manager):
        super().__init__(name=self.name, callback=None, description=self.description)
        self.manager = manager

    def function(self, *args, **kwargs):
        if self.manager.connected_robots == 0:
            print("No robots connected")
            return

        for id, robot in self.manager.robots.items():
            print(f"ID: \"{id}\" \t Rev: {robot.device.information.revision}")


# ======================================================================================================================
class TWIPR_Manager_Command_Stop(Command):
    description = 'Deactivates the control on selected (or all) TWIPR robots'
    name = 'stop'
    manager: TWIPR_Manager
    arguments = {
        'robot': CommandArgument(
            name='robot',
            type=str,
            short_name='r',
            description='ID of the robot',
            is_flag=False,
            optional=True,
            default=None
        )
    }

    def __init__(self, manager: TWIPR_Manager):
        super().__init__(name=self.name, callback=None, description=self.description, arguments=None)
        self.manager = manager

    def function(self, robot=None, *args, **kwargs):

        if robot is None:
            for id, robot in self.manager.robots.items():
                robot.stop()
            return

        if robot is not None:
            if robot in self.manager.robots:
                self.manager.robots[robot].stop()
            else:
                logger.warning(f"Robot \"{robot}\" not found.")


# ======================================================================================================================
class TWIPR_Manager_Command_Mode(Command):
    description = 'Sets the control mode of selected (or all) TWIPR robots'
    name = 'mode'
    manager: TWIPR_Manager
    arguments = {
        'mode': CommandArgument(
            name='mode',
            type=int,
            short_name='m',
            description='Mode of control (0:off, 1:direct, 2:torque)',
            is_flag=False,
            optional=False,
            default=None
        ),
        'robot': CommandArgument(
            name='robot',
            type=str,
            short_name='r',
            description='ID of the robot',
            is_flag=False,
            optional=True,
            default=None
        ),

    }

    def __init__(self, manager: TWIPR_Manager):
        super().__init__(name=self.name, callback=None, description=self.description, arguments=None)
        self.manager = manager

    def function(self, mode: int, robot=None, *args, **kwargs):

        if robot is None:
            for id, robot in self.manager.robots.items():
                robot.setControlMode(mode)
            return

        if robot is not None:
            if robot in self.manager.robots:
                self.manager.robots[robot].setControlMode(mode)
            else:
                logger.warning(f"Robot \"{robot}\" not found.")

# ======================================================================================================================
