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
    voice_clip_path = "/home/sougato97/Human_Robot_Interaction/nao_dev/recordings/"
    
    global frames_ch0,frames_ch1,frames_ch2,frames_ch3,frames_ch4,frames_ch5

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
            # speech recognition model 
            model = Model("/home/yubie/vosk-api/models/vosk-model-en-in-0.5")
            spk_model = SpkModel(SPK_MODEL_PATH)
            stream = p.open(
                rate=RESPEAKER_RATE,
                format=p.get_format_from_width(RESPEAKER_WIDTH),
                channels=RESPEAKER_CHANNELS,
                input=True,
                frames_per_buffer=CHUNK,)

            print("#" * 80)
            print("Press Ctrl+C to stop the recording")
            print("#" * 80)
            stream.start_stream()
            rec = KaldiRecognizer(model, RESPEAKER_RATE) # model is the voice vector of the person speaking
            rec.SetSpkModel(spk_model)
            timeout = time.time() + 25 # if no comand given for 25s or more spot goes to sleep 
            while stream.is_active():
                if time.time() > timeout:
                    print("I'm going back to sleep")
                    robo.awake = 0
                data = stream.read(CHUNK)
                a = get_frames(data)
                # y = a is the processed audio channel 
                # sr = sample rate of the speaker, like 16khz
                # stationary = whether the noise is tsationary or not
                # y = idle SPOT noise we imported 
                reduced_noise = nr.reduce_noise(y=a, sr=RESPEAKER_RATE, stationary=False, n_jobs=-1,y_noise=noise_data) 
                # reduced_noise only needed when we are using it on a noisy environment, otherwise use "a.tostring()" instead of "reduced_noise.tostring()" in the next line 
                if rec.AcceptWaveform(reduced_noise.tostring()):
                    # "res" is a dictionary with 2 keys i.e., 
                    # "text" -> associated with recognized text from the person's phrase.
                    # "spk - > associated with person's voice vector. 
                    # whenever you speak you get this dictionary
                    res = json.loads(rec.Result())  
                    text = res["text"] # recognized phrase(text) from the person's voice 
                    if "spk" in res:
                        print("You said:", text)
                        vector = res["spk"]
                        #print("X-vector:", vector)
                        recognized = robo.recognize(vector)
                        if recognized:
                            if not robo.awake:
                                robo.wakeup_switch(text)
                            else:
                                robo.execute_command(text)
                        else:
                            print("I don't recognize you")
                    else:
                        print("Oops! Didn't catch that")

                    timeout = time.time() + 25

                else:
                    pass
                #print(rec.PartialResult())
                

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






