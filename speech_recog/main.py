#! /home/sougato97/miniconda3/envs/hri/bin/python
# -*- encoding: UTF-8 -*-
from __future__ import print_function
import pyaudio
import time
import numpy as np
import argparse
import wave
import json
import noisereduce as nr



from scipy.io import wavfile
# from vosk import Model, KaldiRecognizer, SpkModel



import bosdyn.client
import bosdyn.client.lease
import bosdyn.client.util
import bosdyn.geometry
import argparse
import sys
import time
import os
# from bosdyn.client.image import ImageClient
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient, blocking_stand
from bosdyn.client.docking import blocking_dock_robot, blocking_undock


from helper import RobotInteraction
import whisper
from voice import *
from utils import *
import os

# spot ip = 10.0.88.176
noise_rate, noise_data = wavfile.read("spot_noise_ch0_recording.wav") # Noise from SPOT when its Idle (present in ~/home/vosk-api/python/example/mine)
p = pyaudio.PyAudio() # for recording audio from the microphone 



RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6 # change base on firmwares, 1_channel_firmware.bin as 1 or 6_channels_firmware.bin as 6
RESPEAKER_WIDTH = 2

CHUNK = 4000
#RECORD_SECONDS = 5
SPK_MODEL_PATH = "/home/yubie/vosk-api/models/vosk-model-spk-0.4" # Speaker recognition model path 




########################################################### Parsing ##############################################################

    
############################################################ Parsing End ##########################################################

frames_ch0 = []
frames_ch1 = []
frames_ch2 = []
frames_ch3 = []
frames_ch4 = []
frames_ch5 = []

def get_frames(data):
    global frames_ch0,frames_ch1,frames_ch2,frames_ch3,frames_ch4,frames_ch5
    a = np.frombuffer(data,dtype=np.int16)[0::6]		# Channel 0
    b = np.frombuffer(data,dtype=np.int16)[1::6]		# Channel 1
    c = np.frombuffer(data,dtype=np.int16)[2::6]		# Channel 2
    d = np.frombuffer(data,dtype=np.int16)[3::6]		# Channel 3
    e = np.frombuffer(data,dtype=np.int16)[4::6]		# Channel 4
    f = np.frombuffer(data,dtype=np.int16)[5::6]		# Channel 5
    frames_ch0.append(a.tobytes()) # processed data | like echo cancellation, etc..
    frames_ch1.append(b.tobytes()) # 1, 2, 3, 4, raw mic data | the external USB device has 4 microphones
    frames_ch2.append(c.tobytes())
    frames_ch3.append(d.tobytes())
    frames_ch4.append(e.tobytes())
    frames_ch5.append(f.tobytes()) # playback data, but not present. 
    return a # we are only using the processed channel "a" data




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
    with bosdyn.client.lease.LeaseKeepAlive(lease_client, must_acquire=True, return_at_exit=True):
        try:
            record_audio(voice_clip_path, "recording.mp3")
            text = transcribe(voice_clip_path + "recording.mp3",model)
            recognized = user_auth(voice_clip_path, "recording.mp3", pyannote_key)
            if recognized:
                if not robo.awake:
                    robo.wakeup_switch(text)
                elif robo.awake:
                    robo.execute_command(text)
                else:
                    print("Oops! Didn't catch that")
            else:
                print("I don't recognize you")

        except KeyboardInterrupt:
            print("\nDone")
            stream.stop_stream()
            stream.close()
            p.terminate()
            #write_to_file()
            parser.exit(0)
        except Exception as e:
            parser.exit(type(e).__name__ + ": " + str(e))



if __name__ == "__main__":
    if not main(sys.argv[1:]):
        sys.exit(1)
    main()






