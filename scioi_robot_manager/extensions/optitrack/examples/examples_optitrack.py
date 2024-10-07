import time

from extensions.optitrack.optitrack import OptiTrack


def example_optitrack():
    optitrack = OptiTrack(server_address="127.0.0.1", local_address="127.0.0.1", multicast_address="239.255.42.99")
    optitrack.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    example_optitrack()
