#! /home/sougato97/miniconda3/envs/hri/bin/python
# -*- encoding: UTF-8 -*-
from __future__ import print_function
import time
import numpy as np
import argparse
import wave
import json


import bosdyn.client
import bosdyn.client.lease
import bosdyn.client.util
import bosdyn.geometry

import argparse
import sys
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient, blocking_stand
from bosdyn.client.docking import blocking_dock_robot, blocking_undock


from helper import RobotInteraction
import whisper
from voice import *
from utils import *
import os

# spot ip = 10.0.88.176

########################################################### Parsing ##############################################################

    
############################################################ Parsing End ##########################################################



def main(argv):
    voice_clip_path = "/home/sougato97/Human_Robot_Interaction/spot_dev/recordings/"
    pyannote_key = os.environ["PYANNOTE_API_KEY"]

    parser = argparse.ArgumentParser()
    bosdyn.client.util.add_base_arguments(parser) # getting spot parser data (i.e. ip), asks for userid & password  
    options = parser.parse_args(argv)
    bosdyn.client.util.setup_logging(options.verbose)  
    sdk = bosdyn.client.create_standard_sdk('VoiceClient') 
    robo = RobotInteraction(sdk,options) # from helper.py
    
    model = whisper.load_model("medium.en") ## exception handling
    print("Whisper model import success")

    robo.robot.time_sync.wait_for_sync()
    assert not robo.robot.is_estopped(), "Robot is estopped. Please use an external E-Stop client, " \
                                    "such as the estop SDK example, to configure E-Stop."
    lease_client = robo.robot.ensure_client(bosdyn.client.lease.LeaseClient.default_service_name)
    # for acquiring the spot connection 
    count_false = 0
    with bosdyn.client.lease.LeaseKeepAlive(lease_client, must_acquire=True, return_at_exit=True):
        # try:
        while (1):
            print("You may start with the recording")
            record_audio(voice_clip_path, "recording.mp3")
            text = transcribe(voice_clip_path + "recording.mp3",model)
            recognized = user_auth(voice_clip_path, "recording.mp3", pyannote_key)
            recognized = 1
            if recognized:
                if not robo.awake:
                    robo.wakeup_switch(text)
                elif robo.awake:
                    robo.execute_command(text)
                else:
                    print("Oops! Didn't catch that")
                count_false += 1
            elif count_false == 15:
                print("Yubee is going back to sleep")
                robo.awake = 0
            else:
                print("I don't recognize you")
                count_false += 1
        
        # except KeyboardInterrupt:
        #     print("\nDone")
        #     stream.stop_stream()
        #     stream.close()
        #     # p.terminate()
        #     #write_to_file()
        #     parser.exit(0)
        # except Exception as e:
        #     parser.exit(type(e).__name__ + ": " + str(e))



if __name__ == "__main__":
    if not main(sys.argv[1:]):
        sys.exit(1)
    main()






