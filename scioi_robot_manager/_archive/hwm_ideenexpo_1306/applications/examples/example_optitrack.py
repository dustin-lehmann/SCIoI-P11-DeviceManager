import time

from applications.robot_manager import RobotManager


def main():
    manager = RobotManager(optitrack=True)

    manager.init()
    manager.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
