import time
from applications.TWIPR.general.JoystickControl import SimpleTwiprJoystickControl

import qmt


def sampleCallback(sample, robot, *args, **kwargs):
    ...


def main():
    app = SimpleTwiprJoystickControl()
    app.init()

    app.robot_manager.registerCallback('stream', sampleCallback)
    app.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
