import dataclasses
import threading
import time

from extensions.cli.cli import CommandSet, Command, CommandArgument
from extensions.joystick.joystick_manager import JoystickManager, Joystick
from robots.twipr.twipr import TWIPR
from robots.twipr.twipr_manager import TWIPR_Manager
from robots.twipr.utils.twipr_data import TWIPR_Control_Mode
from utils.logging import Logger

LIMIT_TORQUE_FORWARD_DEFAULT = 0.02
LIMIT_TORQUE_TURN_DEFAULT = 0.055
#
# LIMIT_TORQUE_FORWARD_DEFAULT = 0.08
# LIMIT_TORQUE_TURN_DEFAULT = 0.1
LIMIT_SPEED_FORWARD_DEFAULT = 1
LIMIT_SPEED_TURN_DEFAULT = 0.5

logger = Logger('joystickcontrol')


@dataclasses.dataclass
class JoystickAssignment:
    joystick: Joystick
    robot: TWIPR


class TWIPR_JoystickControl:
    from core.utils.callbacks import registerCallback

    twipr_manager: TWIPR_Manager
    joystick_manager: JoystickManager
    limits: dict
    assignments: dict[str, JoystickAssignment]

    callbacks: dict

    _run_in_thread: bool
    _thread: threading.Thread
    _exit: bool

    # ==================================================================================================================
    def __init__(self, twipr_manager: TWIPR_Manager, thread=False):
        self.twipr_manager = twipr_manager

        self.joystick_manager = JoystickManager()
        self._run_in_thread = thread

        self.twipr_manager.registerCallback('robot_disconnected', self._robotDisconnected_callback)
        self.joystick_manager.registerCallback('new_joystick', self._newJoystick_callback)
        self.joystick_manager.registerCallback('joystick_disconnected', self._joystickDisconnected_callback)

        self.limits = {
            'torque': {
                'forward': 0,
                'turn': 0,
            },
            'speed': {
                'forward': 0,
                'turn': 0,
            }
        }

        self.assignments = {}

        self.callbacks = {
            'new_assignment': [],
            'assignment_removed': [],
            'new_joystick': [],
            'joystick_disconnected': []
        }

        self._exit = False

        if self._run_in_thread:
            self._thread = threading.Thread(target=self._threadFunction)
        else:
            self._thread = None

    # ==================================================================================================================
    def init(self):
        self.joystick_manager.init()
        self.resetLimits()

    # ------------------------------------------------------------------------------------------------------------------
    def start(self):
        self.joystick_manager.start()
        if self._run_in_thread:
            self._thread.start()

    # ------------------------------------------------------------------------------------------------------------------
    def close(self):
        self._exit = True
        if self._run_in_thread:
            self._thread.join()

    # ------------------------------------------------------------------------------------------------------------------
    def assignJoystick(self, joystick, twipr):
        if isinstance(joystick, str):
            joystick = self.joystick_manager.getJoystickById(joystick)
            if joystick is None:
                return
        if isinstance(twipr, str):
            twipr = self.twipr_manager.getRobotById(twipr)
            if twipr is None:
                return

        self.assignments[joystick.id] = JoystickAssignment(joystick, twipr)
        joystick.setButtonCallback(button=1, event='down', function=twipr.setControlMode, parameters={'mode': 2})
        joystick.setButtonCallback(button=0, event='down', function=twipr.setControlMode, parameters={'mode': 0})
        logger.info(f"Assign Joystick: {joystick.id} -> Robot: {twipr.id}")

        for callback in self.callbacks['new_assignment']:
            callback(joystick, twipr)

    # ------------------------------------------------------------------------------------------------------------------
    def unassignJoystick(self, joystick):
        if isinstance(joystick, str):
            joystick = self.joystick_manager.getJoystickById(joystick)
            if joystick is None:
                return

        for key, assignment in self.assignments.items():
            if assignment.joystick == joystick:
                self.assignments.pop(key)
                logger.info(f"Unassign Joystick: {joystick.id} -> Robot: {assignment.robot.id}")
                joystick.clearAllButtonCallbacks()

                for callback in self.callbacks['assignment_removed']:
                    callback(joystick, assignment.robot)
                return

    # ------------------------------------------------------------------------------------------------------------------
    def resetLimits(self):
        self.limits['torque']['forward'] = LIMIT_TORQUE_FORWARD_DEFAULT
        self.limits['torque']['turn'] = LIMIT_TORQUE_TURN_DEFAULT
        self.limits['speed']['forward'] = LIMIT_SPEED_FORWARD_DEFAULT
        self.limits['speed']['turn'] = LIMIT_SPEED_TURN_DEFAULT

    # ------------------------------------------------------------------------------------------------------------------
    def update(self):
        for assignment in self.assignments.values():
            # Check which mode the robot is in
            if assignment.robot.data.control.mode == TWIPR_Control_Mode.TWIPR_CONTROL_MODE_BALANCING:
                torques = self._calculateTorques(assignment)
                assignment.robot.setTorque(torques)
            elif assignment.robot.data.control.mode == TWIPR_Control_Mode.TWIPR_CONTROL_MODE_VELOCITY:
                speeds = self._calculateSpeeds(assignment)
                assignment.robot.setSpeed(v=speeds[0], psi_dot=speeds[1])

    # ------------------------------------------------------------------------------------------------------------------
    def _calculateTorques(self, assignment: JoystickAssignment) -> list:
        # Read the Joystick axes
        forward_joystick = -assignment.joystick.axis[1]
        turn_joystick = -assignment.joystick.axis[2]

        boost = (assignment.joystick.axis[5] + 1) * 0.25

        # torque_forward_max_cmd = self._manual_torque_limits['forward'] + master_boost * (
        #         ideenexpo_settings.manual_control_settings['forward']['max'] - self._manual_torque_limits['forward'])

        # Calculate the commands
        forward_cmd = forward_joystick * self.limits['torque']['forward'] + boost * (0.08 - self.limits['torque']['forward'])
        turn_cmd = turn_joystick * self.limits['torque']['turn']

        # Calculate the torques (negative values: forward)
        torque_left = -(forward_cmd + turn_cmd)
        torque_right = -(forward_cmd - turn_cmd)

        return [torque_left, torque_right]

    # ------------------------------------------------------------------------------------------------------------------
    def _calculateSpeeds(self, assignment: JoystickAssignment) -> list:
        return [0, 0]

    # ------------------------------------------------------------------------------------------------------------------
    def _threadFunction(self):
        while not self._exit:
            self.update()
            time.sleep(0.1)

    # ------------------------------------------------------------------------------------------------------------------
    def _robotDisconnected_callback(self, robot, *args, **kwargs):
        for assignment in self.assignments.values():
            if assignment.robot == robot:
                self.unassignJoystick(assignment.joystick)
                return

    # ------------------------------------------------------------------------------------------------------------------
    def _newJoystick_callback(self, joystick, *args, **kwargs):
        for callback in self.callbacks['new_joystick']:
            callback(joystick)

    # ------------------------------------------------------------------------------------------------------------------
    def _joystickDisconnected_callback(self, joystick, *args, **kwargs):
        for assignment in self.assignments.values():
            if assignment.joystick == joystick:
                self.unassignJoystick(assignment.joystick)

        for callback in self.callbacks['joystick_disconnected']:
            callback(joystick)


# ======================================================================================================================
class TWIPR_JoystickControl_CommandSet(CommandSet):
    name = 'joysticks'
    description = 'Joystick Control of TWIPR robots'

    def __init__(self, joystick_control: TWIPR_JoystickControl):
        super().__init__(name=self.name)

        self.joystick_control = joystick_control

        # self.manager.registerCallback('new_robot', self._newRobot_callback)
        # self.manager.registerCallback('robot_disconnected', self._robotDisconnected_callback)

        self.addCommand(TWIPR_JoystickControl_Command_List(self.joystick_control))
        self.addCommand(TWIPR_JoystickControl_Command_Assign(self.joystick_control))
        self.addCommand(TWIPR_JoystickControl_Command_Unassign(self.joystick_control))
        # self.addCommand(TWIPR_Manager_Command_List(self.manager))
        # self.addCommand(TWIPR_Manager_Command_Stop(self.manager))
        # self.addCommand(TWIPR_Manager_Command_Mode(self.manager))

    def _newRobot_callback(self, robot, *args, **kwargs):
        ...

    def _robotDisconnected_callback(self, robot, *args, **kwargs):
        ...


# ======================================================================================================================
class TWIPR_JoystickControl_Command_List(Command):
    description = 'Lists all connected Joysticks'
    name = 'list'
    joystick_control: TWIPR_JoystickControl
    arguments = {
    }

    def __init__(self, joystick_control: TWIPR_JoystickControl):
        super().__init__(name=self.name, callback=None, description=self.description)
        self.joystick_control = joystick_control

    def function(self, *args, **kwargs):
        ...


class TWIPR_JoystickControl_Command_Assign(Command):
    description = 'Assigns a Joystick to a TWIPR'
    name = 'assign'
    joystick_control: TWIPR_JoystickControl
    arguments = {
        'joystick': CommandArgument(
            name='joystick',
            type=str,
            short_name='j',
            description='ID of the Joystick to assign',
            is_flag=False,
        ),
        'robot': CommandArgument(
            name='robot',
            type=str,
            short_name='r',
            description='ID of the robot to assign',
            is_flag=False,
        )
    }

    def __init__(self, joystick_control: TWIPR_JoystickControl):
        super().__init__(name=self.name, callback=None, description=self.description)
        self.joystick_control = joystick_control

    def function(self, *args, **kwargs):
        ...


class TWIPR_JoystickControl_Command_Unassign(Command):
    description = 'Unassigns a joystick from a robot. If not arguments are given, it unassigns all.'
    name = 'unassign'
    joystick_control: TWIPR_JoystickControl
    arguments = {
        'joystick': CommandArgument(
            name='joystick',
            type=str,
            short_name='j',
            description='ID of the Joystick to unassign',
            optional=True,
            default=None,
        ),
        'robot': CommandArgument(
            name='robot',
            type=str,
            short_name='r',
            description='ID of the robot to unassign',
            optional=True,
            default=None
        )
    }

    def __init__(self, joystick_control: TWIPR_JoystickControl):
        super().__init__(name=self.name, callback=None, description=self.description)
        self.joystick_control = joystick_control

    def function(self, *args, **kwargs):
        ...
