import math
import time

import qmt

from extensions.babylon.babylon_new.babylon import BabylonVisualization
from extensions.babylon.babylon_new.scioi_pysim.scioi_py_core.utils.orientations import twiprToRotMat


def main():
    theta = 0
    psi = math.pi / 4
    rotmatrix = twiprToRotMat(theta=theta, psi = psi)
    print(rotmatrix)

    babylon = BabylonVisualization(show='chromium')
    babylon.init()
    babylon.start()

    babylon.addObject('twipr1', 'twipr', {'color': [0, 1, 0]})
    babylon.addObject('twipr2', 'twipr', {'color': [1, 0, 0]})
    babylon.addObject('twipr3', 'twipr', {'color': [0, 0, 1]})
    time.sleep(4)
    babylon.updateObject('twipr1', {'position': {'x': 1, 'y': 0}})
    babylon.updateObject('twipr2', {'position': {'x': 1, 'y': 0.5}})
    babylon.updateObject('twipr3', {'position': {'x': 1, 'y': 1, 'z': 0.25}})
    babylon.updateObject('twipr3', {'orientation': rotmatrix})




    babylon.addObject(object_id='floor1', object_class='floor',
                      object_config={'tiles_x': 10, 'tiles_y': 10, 'tile_size': 2.920 / 10})
    babylon.addObject(object_id='wall1', object_class='obstacle',
                      object_config={'size': {'x': 2.920, 'y': 0.01, 'z': 0.27},
                                     'position': {'x': 0, 'y': 2.920 / 2, 'z': 0}, 'color': [0.5, 0.5, 0.5]}, )
    babylon.addObject(object_id='wall2', object_class='obstacle',
                      object_config={'size': {'x': 2.920, 'y': 0.01, 'z': 0.27},
                                     'position': {'x': 0, 'y': -2.920 / 2, 'z': 0}, 'color': [0.5, 0.5, 0.5]}, )
    babylon.addObject(object_id='wall3', object_class='obstacle',
                      object_config={'size': {'x': 0.01, 'y': 2.92, 'z': 0.27},
                                     'position': {'x': 2.920 / 2, 'y': 0, 'z': 0}, 'color': [0.5, 0.5, 0.5]}, )
    babylon.addObject(object_id='wall4', object_class='obstacle',
                      object_config={'size': {'x': 0.01, 'y': 2.92, 'z': 0.27},
                                     'position': {'x': -2.920 / 2, 'y': 0, 'z': 0}, 'color': [0.5, 0.5, 0.5]}, )

    time.sleep(1)
    x = 0
    while True:
        x = x + 0.01
        time.sleep(0.01)


if __name__ == '__main__':
    main()
