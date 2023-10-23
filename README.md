# HRI (Spot environment)
The source-code is related to BostonDynamics Spot. Voice controls implemented for Spot with user authentication. <br />

## Demo: Audio authentication for voice control on the Spot Robot

<br />
[![Click the picture for watching the video](https://github.com/sougato97/spot_dev/blob/v3/spot_imgs/spot_thumbnail.png)](https://youtu.be/P4jFGvzPtPE)

<!-- Audio authentication for voice control on the Spot Robot:

https://www.youtube.com/watch?v=P4jFGvzPtPE&t=1s -->

Authors: 
- Sougato Bagchi - sougato97@gmail.com/sougatob@buffalo.edu
- Geethartho Chanda - geetarth@buffalo.edu

## My setup 
- I am using windows 11 (WSL - Ubuntu 18)
- For gpu setup please install, nvidia cuda toolkit on windows 
- Your distro will be able to access the gpu drivers. 
- You need to install USBIPD on windows 
- Follow the steps from this website :
  - https://learn.microsoft.com/en-us/windows/wsl/connect-usb

## Installation
To install this project, follow these steps:
- Install Miniconda (https://docs.conda.io/en/latest/miniconda.html)
  
Create Conda env
```bash
conda create --name hri
conda activate hri
```
Install PyTorch GPU
```bash
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```
Install record audio libraries
```bash
conda install -c anaconda pyaudio
```
Install Voice Authentication module
```bash
pip install pyannote.audio
```
Install OpenAI for chatGPT integration 
```bash
conda install -c conda-forge openai
```
Install Whisper voice trascription model 
```bash
pip install -U openai-whisper
pip install git+https://github.com/openai/whisper.git 
pip install --upgrade --no-deps --force-reinstall git+https://github.com/openai/whisper.git
sudo apt update && sudo apt install ffmpeg

```
Install BostonDynamics API
```bash
python3 -m pip install --upgrade bosdyn-client bosdyn-mission bosdyn-choreography-client
python3 -m pip install bosdyn-client==3.2.2.post1 bosdyn-mission==3.2.2.post1 bosdyn-choreography-client==3.2.2.post1
```
Verify your Spot packages installation
```bash
python3 -m pip list --format=columns | grep bosdyn
```
Your output for the prev command should be:
```bash
bosdyn-api                    3.2.2.post1
bosdyn-choreography-client    3.2.2.post1
bosdyn-choreography-protos    3.2.2.post1
bosdyn-client                 3.2.2.post1
bosdyn-core                   3.2.2.post1
bosdyn-mission                3.2.2.post1
```

If you face any issues, please refer to: 
https://dev.bostondynamics.com/docs/python/quickstart

This code needs API keys from huggingface.co(for pyannote)
- I have added these keys to the .bashrc file 
- HuggingFace link - https://huggingface.co/settings/tokens
- Also you have to agree to some T&C. Preferably run it 1st time on jupyter, you will get the link there itself.
```bash
export PYANNOTE_API_KEY="you-key-please"
```

In the terminal 
- window 1 
```bash
python ./spot_dev/spot-sdk/python/examples/estop/estop_nogui.py ip_of_the_robot
```
- window 2
```bash
python ./spot_dev/speech_recog/main.py ip_of_the_robot
```

You may need to create an ssh setup for GitHub
- Follow the comands below, you may discard the prompts 
- copy and paste the id_rsa.pub contents to https://github.com/settings/keys
```bash
ssh-keygen -t rsa -b 4096 -C "email@domain.com"
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa
git config --global user.email "email@domain.com"
git config --global user.name "Jon Doe"
```
