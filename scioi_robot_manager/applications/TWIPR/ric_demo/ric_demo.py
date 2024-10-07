import logging
import threading
import time

import numpy as np

from applications.ric_demo.robots_demo.ric_demo_manager import RIC_Demo_RobotManager
from applications.ric_demo.simulation.ric_demo_simulation import RIC_Demo_Simulation
from applications.ric_demo.consensus.ric_consensus import ConsensusTWIPR, Consensus
from applications.ric_demo.simulation.src.dummy_device import DummyDevice
from applications.ric_demo.simulation.src.twipr_data import TWIPR_Control_Mode, buildSample
from applications.ric_demo.ric_utils import generate_next_id
from robots.twipr.twipr import TWIPR
from utils.timer import Timer

logger = logging.getLogger("RIC DEMO")
logger.setLevel("DEBUG")


class RIC_Demo:
    mode: str
    ric_robot_manager: RIC_Demo_RobotManager
    simulation: RIC_Demo_Simulation
    optitrack: ...
    gui: ...
    consensus: Consensus

    _virtualRobotStreamTimer: Timer

    _thread: threading.Thread

    def __init__(self):

        self.list_of_agent_ids = ['twipr1', 'twipr2']
        self.num_of_agents = 10

        self.ric_robot_manager = RIC_Demo_RobotManager()
        self.ric_robot_manager.registerCallback('stream', self._robotManagerStream_callback)
        self.ric_robot_manager.registerCallback('new_robot', self._robotManagerNewRobot_callback)
        self.ric_robot_manager.registerCallback('robot_disconnected', self._robotManagerRobotDisconnected_callback)

        self.ric_robot_manager.gui.registerCallback('rx_message', self._guiMsg_callback)
        self.simulation = RIC_Demo_Simulation()

        self._virtualRobotStreamTimer = Timer()

        self._thread = threading.Thread(target=self._threadFunction)

    def _guiMsg_callback(self, msg, *args, **kwargs):
        print(msg)

    def init(self):
        self.ric_robot_manager.init()
        self.simulation.init()

    def start(self):
        self.ric_robot_manager.start()
        self.simulation.start()

        while not self.simulation.visualization.loaded:
            time.sleep(0.1)
        self.simulation.visualization.addObject('floor1', 'floor', {'tile_size': 0.5, 'tiles_x': 10, 'tiles_y': 10})
        self._thread.start()
        self.addVirtualAgent('vtwipr1')
        self.simulation.setVirtualAgentInput([-0.05, -0.07], 'vtwipr1')

    def _threadFunction(self):
        self._virtualRobotStreamTimer.start()

        while True:
            if self._virtualRobotStreamTimer > 0.1:
                self._virtualRobotStreamTimer.reset()

                for robot_id, agent in self.simulation.env.virtual_agents.items():
                    sample = self.buildSampleFromSimulation(robot_id)
                    if robot_id in self.ric_robot_manager.robotManager.robots.keys():
                        self.ric_robot_manager.robotManager.robots[robot_id].device.dummyStream(sample)

            time.sleep(0.01)

    def _robotManagerStream_callback(self, stream, robot, *args, **kwargs):
        if not robot.id.startswith('v'):
            x = stream.data['estimation']['state']['x']
            y = stream.data['estimation']['state']['y']
            v = stream.data['estimation']['state']['v']
            theta = stream.data['estimation']['state']['theta']
            theta_dot = stream.data['estimation']['state']['theta_dot']
            psi = stream.data['estimation']['state']['psi']
            psi_dot = stream.data['estimation']['state']['psi_dot']

            if robot.id in self.simulation.env.real_agents.keys():
                self.simulation.setRealAgentConfiguration(agent_id=robot.id, x=x, y=y, theta=theta, psi=psi)
            else:
                print("I have some error in my code")

    def _robotManagerNewRobot_callback(self, robot: TWIPR, *args, **kwargs):

        if not robot.id.startswith('v'):
            self.simulation.addRealAgent(robot.id)

    def _robotManagerRobotDisconnected_callback(self, robot, *args, **kwargs):
        self.simulation.removeRealAgent(robot.id)

    def addVirtualAgent(self, agent_id=None):
        if agent_id is not None and not agent_id.startswith('v'):
            logger.warning(f"Cannot add virtual agent with id not starting with \"v\"")
            return
        if agent_id is None:
            ids = self.simulation.env.virtual_agents.keys()
            agent_id = generate_next_id(ids)
        else:
            if agent_id in self.simulation.env.virtual_agents.keys():
                logger.warning(f"ID {agent_id} already in simulation env")
                return

        self.simulation.addVirtualAgent(agent_id)
        virtual_robot_device = DummyDevice(id=agent_id)
        self.ric_robot_manager.robotManager.deviceManager._deviceRegistered_callback(virtual_robot_device)

    def buildSampleFromSimulation(self, robot_id):
        if robot_id in self.simulation.env.virtual_agents.keys():
            virtual_agent = self.simulation.env.virtual_agents[robot_id]
            sample = buildSample()

            sample['general']['id'] = robot_id
            sample['estimation']['state']['x'] = virtual_agent.dynamics.state['x'].value
            sample['estimation']['state']['y'] = virtual_agent.dynamics.state['y'].value
            sample['estimation']['state']['v'] = virtual_agent.dynamics.state['v'].value
            sample['estimation']['state']['theta'] = virtual_agent.dynamics.state['theta'].value
            sample['estimation']['state']['theta_dot'] = virtual_agent.dynamics.state['theta_dot'].value
            sample['estimation']['state']['psi'] = virtual_agent.dynamics.state['psi'].value
            sample['estimation']['state']['psi_dot'] = virtual_agent.dynamics.state['psi_dot'].value

            return sample


def main():
    ric_demo = RIC_Demo()
    ric_demo.init()
    ric_demo.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
