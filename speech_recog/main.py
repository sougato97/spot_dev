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
from pyannote.audio import Model
from voice_auth import *
from utils import *
import os

# spot ip = 10.0.88.176

def main(argv):
    voice_clip_path = "/home/sougato97/Human_Robot_Interaction/spot_dev/recordings/"
    pyannote_key = os.environ["PYANNOTE_API_KEY"]


    model = whisper.load_model("medium.en") ## exception handling
    pyannote_model = Model.from_pretrained("pyannote/embedding", use_auth_token = pyannote_key)
    print("Models import success")

    parser = argparse.ArgumentParser()
    # print("The value of parser is:", parser)
    bosdyn.client.util.add_base_arguments(parser) # getting spot parser data (i.e. ip), asks for userid & password  
    options = parser.parse_args(argv)
    # print("The debug value is:", options)
    bosdyn.client.util.setup_logging(options.verbose)  
    sdk = bosdyn.client.create_standard_sdk('VoiceClient') 
    # print("check 1")
    robo = RobotInteraction(sdk,options) # from helper.py
    # print("check 2")

    robo.robot.time_sync.wait_for_sync()
    assert not robo.robot.is_estopped(), "Robot is estopped. Please use an external E-Stop client, " \
                                    "such as the estop SDK example, to configure E-Stop."
    lease_client = robo.robot.ensure_client(bosdyn.client.lease.LeaseClient.default_service_name)
    # for acquiring the spot connection 
    with bosdyn.client.lease.LeaseKeepAlive(lease_client, must_acquire=True, return_at_exit=True):

        # will have to change the logic later, but for now, I will change the wake_up to always 1 
        robo.awake = 1
        while (1):
            flag = input("Please give the input according to the provided options : \nUser Registration - 1 \nAuthorized mode - 2 \nBypass Auth & use as guest - 3\nExit -4")
            # Reg mode
            if (flag == '1'):
                register_user(pyannote_key,voice_clip_path,model)
                continue    
            # Auth Mode
            elif (flag == '2'):
                while(1):
                    flag = input("You may start with the recording. But press 1 to stop the conversation, any other key for continuation.")
                    if (flag == '1'):
                        break
                    record_audio(voice_clip_path, "recording.mp3")
                    text = transcribe(voice_clip_path + "recording.mp3",model)
                    recognized = user_auth(voice_clip_path, "recording.mp3", pyannote_model)
                    # recognized = 1
                    if recognized:
                        try:
                            robo.execute_command(text)
                        except:
                            print("Wrong command")
                    else:
                        print("You are not an authorized user")
            # Guest Mode
            elif (flag == '3'):
                while(1):
                    flag = input("You may start with the recording. But press 1 to stop the conversation, any other key for continuation.")
                    if (flag == '1'):
                        break
                    print("You may start with the recording")
                    record_audio(voice_clip_path, "recording.mp3")
                    text = transcribe(voice_clip_path + "recording.mp3",model)
                    try:
                        robo.execute_command(text)
                    except:
                        print("Wrong command")
            # Return/exit
            elif (flag == '4'):
                return 
            else:
                continue
        



if __name__ == "__main__":
    if not main(sys.argv[1:]):
        sys.exit(1)
    main()






