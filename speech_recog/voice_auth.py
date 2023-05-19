#! /home/sougato97/miniconda3/envs/hri/bin/python
# -*- encoding: UTF-8 -*-

from pyannote.audio import Model
from pyannote.audio import Inference
import os
from scipy.spatial.distance import cdist
import numpy as np
import torch
import subprocess
from utils import *

def user_auth(voice_clip_path, name, pyannote_model):
  
  # Define device to be used (GPU or CPU)
  Device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
  inference = Inference(pyannote_model, window="whole", device = Device)

  flag = 0 
  # list all files in directory
  for filename in os.listdir(voice_clip_path):
    # check if the current file name contains the substring
    if 'template' in filename:
      ref = inference(voice_clip_path + filename)
      recording = inference(voice_clip_path + name)

      # Convert these 1d Numpy to 2d numpy array 
      unsqueezed_ref = np.expand_dims(ref, axis=0)
      unsqueezed_rec = np.expand_dims(recording, axis=0)

      # Compute the distance
      distance1 = cdist(unsqueezed_ref, unsqueezed_rec, metric="cosine")[0,0]

      if (distance1 < 0.60):
        flag = 1
  return flag

def register_user(pyannote_key,voice_clip_path,model):

  print("Please tell me your 1st name, but wait for the prompt")
  record_audio(voice_clip_path, "temp.mp3")
  print("Name recorded!!")
  name = transcribe(voice_clip_path + "temp.mp3", model)
  print("The name is ", name)
  os.rename(voice_clip_path + '/temp.mp3', voice_clip_path + '/' + name + '_template.mp3')
