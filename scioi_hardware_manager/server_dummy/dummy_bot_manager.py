from server_dummy.twipr_dummy import TWIPR_Dummy
import random
import threading

class DummyBotManager:

    def __init__(self, n, t = 30, manager = None):
        self.bots = {}
        self.n = n
        self.time_between_robot_connections = t
        self.running = False
        self.manager = manager
    

    def _create_robots(self):
        for i in range(self.n):
            bot = TWIPR_Dummy()
            bot.information.device_id = f"twipr{i+1}"
            self.bots[bot.information.device_id] = bot
    
    def _create_random_robot_connections(self):
        random_robot_connections = [random.choice([0, 1]) for i in range(self.n)]
        while sum(random_robot_connections) < 1:
            random_robot_connections[random_robot_connections.index(0)] = 1
        return random_robot_connections

    def _robot_loop(self):
        old_robot_connections = [0]*self.n
        new_robot_connections = self._create_random_robot_connections()
        time_to_change_robots = 30
        while True:
            self._connect_disconnect_robots(old_robot_connections, new_robot_connections)
            old_robot_connections = new_robot_connections
            new_robot_connections = self._create_random_robot_connections()
            print(f"change robot connections:")
            self._print_connected_robots(new_robot_connections)
            print("--------------------")
            time.sleep(time_to_change_robots)
    
    def _print_connected_robots(self, robots_connections):
        for i,con in enumerate(robots_connections):
            if con == 1:
                print("Robot {} is connected".format(i))

    def _connect_disconnect_robots(self, old_robot_connections, new_robot_connections):
        for i in range(self.n):
            if old_robot_connections[i] == 0 and new_robot_connections[i] == 1:
                self.manager.add_new_device(self.bots[i])
            elif old_robot_connections[i] == 1 and new_robot_connections[i] == 0:
                self.manager.remove_device(self.bots[i].information.device_id)
    
    def start(self):
        if not self.running:
            self._create_robots()
            self.running = True
            # run the robot loop in a separate thread
            robot_thread = threading.Thread(target=self._robot_loop)
            robot_thread.start()
    
    def stop(self):
        self.running = False
        print("DummyBotManager stopped")
    

    
