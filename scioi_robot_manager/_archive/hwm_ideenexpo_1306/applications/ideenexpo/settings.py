joysticks = {
    '0300509d5e040000130b000009057200': {
        'type': 'ControllerX',
        'id': 1,
        'master': True
    },
    '030082795e040000e002000000007200': {
        'type': 'ControllerX',
        'id': 2,
        'master': False
    }
}

agents = {
    'twipr1': {
        'color': [1, 0, 0],
        'optitrack_id': 1,
    },
    'twipr2': {
        'color': [1, 0, 0],
        'optitrack_id': 2,
    },
    'twipr3': {
        'color': [1, 0, 0],
        'optitrack_id': 3,
    },
    'twipr4': {
        'color': [1, 0, 0],
        'optitrack_id': 4,
    },
    'twipr5': {
        'color': [1, 0, 0],
        'optitrack_id': 5,
    },
}

optitrack = {
    'server_address': "192.168.0.100",
    'local_address': "192.168.0.100",
    'multicast_address': "192.168.0.11"
}

testbed = {
    'tile_size': 285,
    'grid': [10, 10],
}