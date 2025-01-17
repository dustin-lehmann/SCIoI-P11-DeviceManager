﻿#Copyright © 2018 Naturalpoint
#
#Licensed under the Apache License, Version 2.0 (the "License")
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions andPa
#limitations under the License.


# OptiTrack NatNet direct depacketization sample for Python 3.x
#
# Uses the Python NatNetClient.py library to establish a connection (by creating a NatNetClient),
# and receive data via a NatNet connection and decode it using the NatNetClient library.

import sys
import time
from extensions.optitrack.lib_peter.NatNetClient import NatNetClient
import extensions.optitrack.lib_peter.DataDescriptions as DataDescriptions
import extensions.optitrack.lib_peter.MoCapData as MoCapData


# This is a callback function that gets connected to the NatNet client
# and called once per mocap frame.


class OptiClient(NatNetClient):
    def __init__(self, client_address="127.0.0.1", server_address="192.168.5.132", use_multicast=False, print_level=1):
        super().__init__()
        self.set_print_level(print_level)
        self.optionsDict = {
            "clientAddress": client_address,
            "serverAddress": server_address,
            "use_multicast": use_multicast
        }
        self.last_frame = None
        self.last_timestamp = None
        self.rigid_bodies = {}

        # This will create a new NatNet client
        self.optionsDict = self.my_parse_args(sys.argv, self.optionsDict)
        self.set_client_address(self.optionsDict["clientAddress"])
        self.set_server_address(self.optionsDict["serverAddress"])
        self.set_use_multicast(self.optionsDict["use_multicast"])

        # Configure the streaming client to call our rigid body handler on the emulator to send data out.
        self.new_frame_listener = self.receive_new_frame
        self.rigid_body_listener = self.receive_rigid_body_frame

    TESTER = 1
    SPOT = 2
    TESTER2 = 3
    twipr1 = 6

    def receive_new_frame(self, data_dict):
        order_list = ["frameNumber", "markerSetCount", "unlabeledMarkersCount", "rigidBodyCount", "skeletonCount",
                      "labeledMarkerCount", "timecode", "timecodeSub", "timestamp", "isRecording",
                      "trackedModelsChanged"]

        if "frameNumber" in data_dict:
            self.last_frame = data_dict["frameNumber"]
        if "timestamp" in data_dict:
            self.last_timestamp = data_dict["timestamp"]
        dump_args = False
        if dump_args == True:
            out_string = "    "
            for key in data_dict:
                out_string += key + "="
                if key in data_dict:
                    out_string += data_dict[key] + " "
                out_string += "/"
            print(out_string)

    # This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
    def receive_rigid_body_frame(self, new_id, position, rotation):
        self.rigid_bodies[new_id] = {"pos": position, "rot": rotation}
        if self.last_frame is not None:
            self.rigid_bodies[new_id]["frame"] = self.last_frame
        else:
            self.rigid_bodies[new_id]["frame"] = None
        if self.last_timestamp is not None:
            self.rigid_bodies[new_id]["timestamp"] = self.last_timestamp
        else:
            self.rigid_bodies[new_id]["timestamp"] = None
        #pass
        #print( "Received frame for rigid body", new_id )
        #print( "Received frame for rigid body", new_id," ",position," ",rotation )

    def add_lists(self, totals, totals_tmp):
        totals[0] += totals_tmp[0]
        totals[1] += totals_tmp[1]
        totals[2] += totals_tmp[2]
        return totals

    def print_configuration(self, natnet_client):
        natnet_client.refresh_configuration()
        print("Connection Configuration:")
        print("  Client:          %s" % natnet_client.local_ip_address)
        print("  Server:          %s" % natnet_client.server_ip_address)
        print("  Command Port:    %d" % natnet_client.command_port)
        print("  Data Port:       %d" % natnet_client.data_port)

        changeBitstreamString = "  Can Change Bitstream Version = "
        if natnet_client.use_multicast:
            print("  Using Multicast")
            print("  Multicast Group: %s" % natnet_client.multicast_address)
            changeBitstreamString += "false"
        else:
            print("  Using Unicast")
            changeBitstreamString += "true"

        #NatNet Server Info
        application_name = natnet_client.get_application_name()
        nat_net_requested_version = natnet_client.get_nat_net_requested_version()
        nat_net_version_server = natnet_client.get_nat_net_version_server()
        server_version = natnet_client.get_server_version()

        print("  NatNet Server Info")
        print("    Application Name %s" % (application_name))
        print("    MotiveVersion  %d %d %d %d" % (
            server_version[0], server_version[1], server_version[2], server_version[3]))
        print("    NatNetVersion  %d %d %d %d" % (
            nat_net_version_server[0], nat_net_version_server[1], nat_net_version_server[2], nat_net_version_server[3]))
        print("  NatNet Bitstream Requested")
        print("    NatNetVersion  %d %d %d %d" % (nat_net_requested_version[0], nat_net_requested_version[1], \
                                                  nat_net_requested_version[2], nat_net_requested_version[3]))

        print(changeBitstreamString)
        #print("command_socket = %s"%(str(natnet_client.command_socket)))
        #print("data_socket    = %s"%(str(natnet_client.data_socket)))
        print("  PythonVersion    %s" % (sys.version))

    def print_commands(self, can_change_bitstream):
        outstring = "Commands:\n"
        outstring += "Return Data from Motive\n"
        outstring += "  s  send data descriptions\n"
        outstring += "  r  resume/start frame playback\n"
        outstring += "  p  pause frame playback\n"
        outstring += "     pause may require several seconds\n"
        outstring += "     depending on the frame data size\n"
        outstring += "Change Working Range\n"
        outstring += "  o  reset Working Range to: start/current/end frame 0/0/end of take\n"
        outstring += "  w  set Working Range to: start/current/end frame 1/100/1500\n"
        outstring += "Return Data Display Modes\n"
        outstring += "  j  print_level = 0 supress data description and mocap frame data\n"
        outstring += "  k  print_level = 1 show data description and mocap frame data\n"
        outstring += "  l  print_level = 20 show data description and every 20th mocap frame data\n"
        outstring += "Change NatNet data stream version (Unicast only)\n"
        outstring += "  3  Request NatNet 3.1 data stream (Unicast only)\n"
        outstring += "  4  Request NatNet 4.1 data stream (Unicast only)\n"
        outstring += "General\n"
        outstring += "  t  data structures self test (no motive/server interaction)\n"
        outstring += "  c  print configuration\n"
        outstring += "  h  print commands\n"
        outstring += "  q  quit\n"
        outstring += "\n"
        outstring += "NOTE: Motive frame playback will respond differently in\n"
        outstring += "       Endpoint, Loop, and Bounce playback modes.\n"
        outstring += "\n"
        outstring += "EXAMPLE: PacketClient [serverIP [ clientIP [ Multicast/Unicast]]]\n"
        outstring += "         PacketClient \"192.168.10.14\" \"192.168.10.14\" Multicast\n"
        outstring += "         PacketClient \"127.0.0.1\" \"127.0.0.1\" u\n"
        outstring += "\n"
        print(outstring)

    def request_data_descriptions(self, s_client):
        # Request the model definitions
        s_client.send_request(s_client.command_socket, s_client.NAT_REQUEST_MODELDEF, "",
                              (s_client.server_ip_address, s_client.command_port))

    def test_classes(self):
        totals = [0, 0, 0]
        print("Test Data Description Classes")
        totals_tmp = DataDescriptions.test_all()
        totals = self.add_lists(totals, totals_tmp)
        print("")
        print("Test MoCap Frame Classes")
        totals_tmp = MoCapData.test_all()
        totals = self.add_lists(totals, totals_tmp)
        print("")
        print("All Tests totals")
        print("--------------------")
        print("[PASS] Count = %3.1d" % totals[0])
        print("[FAIL] Count = %3.1d" % totals[1])
        print("[SKIP] Count = %3.1d" % totals[2])

    def my_parse_args(self, arg_list, args_dict):
        # set up base values
        arg_list_len = len(arg_list)
        if arg_list_len > 1:
            args_dict["serverAddress"] = arg_list[1]
            if arg_list_len > 2:
                args_dict["clientAddress"] = arg_list[2]
            if arg_list_len > 3:
                if len(arg_list[3]):
                    args_dict["use_multicast"] = True
                    if arg_list[3][0].upper() == "U":
                        args_dict["use_multicast"] = False

        return args_dict


if __name__ == "__main__":

    opti = OptiClient("127.0.0.1", "127.0.0.1", True, 0)
    opti.run()
    tracked_asset = 7
    while True:
        if tracked_asset in opti.rigid_bodies:
            print(opti.rigid_bodies[tracked_asset]['pos'], "\t", opti.rigid_bodies[tracked_asset]["rot"])
            pass
        time.sleep(.02)
