import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from gui.babylon_dummy.babylon.babylon import BabylonVisualization

tick_global = 0
Ts = 0.01


def fetchFunction():
    sample = {
        'time': tick_global * Ts,
        # 'world': self.world.getVisualizationSample(),
        # 'settings': getBabylonSettings()
    }

    return sample


def main():
    babylon = BabylonVisualization(fetch_function=fetchFunction)
    babylon.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
