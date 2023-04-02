#! /home/sougato97/miniconda3/envs/hri/bin/python
# -*- encoding: UTF-8 -*-
from __future__ import print_function
import random
import numpy as np
import json
import bosdyn.client
import bosdyn.client.lease
import bosdyn.client.util
import bosdyn.geometry
# import argparse
# import sys
import time
# import os
# from bosdyn.client.image import ImageClient
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient, blocking_stand
from bosdyn.client.docking import blocking_dock_robot, blocking_undock

# awake = 0, robot listens but doesnt execute till it hears the wake command 
# awake = 1, listens to all commands and executes 

class RobotInteraction():
    def __init__(self,sdk,config):
        self.command_dict = {}
        self.awake = 0 # robot/SPOT sleeping 
        self.wake_list = ['wakeup spotty','wake up spotty','hey spotty','hey scotty','spotty','scotty','wake up you be','wakeup you be','wake up','wakeup',"you'll be","you be",'u b']
        self.recognized_users = {}
        self.latest_vector = []
        self.robot = sdk.create_robot(config.hostname)
        self.set_commands()
        self.command_client = self.robot.ensure_client(RobotCommandClient.default_service_name)
        self.fwd = RobotCommandBuilder.synchro_velocity_command(v_x=1.0, v_y=0, v_rot=0)
        self.bck = RobotCommandBuilder.synchro_velocity_command(v_x=-0.5, v_y=0, v_rot=0)
        self.lft = RobotCommandBuilder.synchro_velocity_command(v_x=0, v_y=0, v_rot=0.5)
        self.rgt = RobotCommandBuilder.synchro_velocity_command(v_x=0, v_y=0, v_rot=-0.5)
        self.st_lf = RobotCommandBuilder.synchro_velocity_command(v_x=0, v_y=0.5, v_rot=0)
        self.st_rt = RobotCommandBuilder.synchro_velocity_command(v_x=0, v_y=-0.5, v_rot=0)
        self.lft_45 = RobotCommandBuilder.synchro_velocity_command(v_x=0, v_y=0, v_rot=0.785)
        self.rgt_45 = RobotCommandBuilder.synchro_velocity_command(v_x=0, v_y=0, v_rot=-0.785)
        
    def bye(self,text):
        print(f'{text}')
        self.awake = 0

    # Basically a dictionary    
    def set_commands(self):
        self.command_dict[self.say_hi] = ['hi','hello','hey there']
        self.command_dict[self.bye] = ['bye','goodbye','good bye', 'see you later', 'see you', 'see u', 'c you', 'c u', 'stop listening']
        #self.command_dict[self.move] = ['go there','go over there','come here','come over here', 'move over','come']
        # this is motors on/off
        self.command_dict[self.power_on] = ['spotty power on','scotty power on','power yourself on','power on','turn on your power','turn on power','turn on']
        self.command_dict[self.power_off] = ['power yourself down', 'power down yourself','power off','power down','turn your power off', 'turn off power','turn yourself off', 'turn off']
        self.command_dict[self.undock] = ['can you undock','get up from your station','get up','undock','un dock']
        self.command_dict[self.lap] = ['move around a bit','move around the room','take a small lap','take a small nap','taken small lap', 'tour the lab']
        self.command_dict[self.dock] = ['go back to your station','go back to station']
        # ,'go back to dock','go to your dock','dock'
        bosdyn.client.util.authenticate(self.robot)     

    def wakeup_switch(self,text):
        for s in self.wake_list:
            if s in text.lower():
                self.awake = 1
                print("I've woken up")
                return
        print("I'm asleep")
      
    def power_on(self,text):
        # Power on
        self.robot.logger.info("Powering on...")
        self.robot.power_on(timeout_sec=20)
        assert self.robot.is_powered_on(), "Power on failed."
        self.robot.logger.info("Powered on.")
        
    def execute_command(self,text):
        for key,value in self.command_dict.items(): # here the Spot functions are the keys
            for phrase in value:
                if phrase in text.lower():
                    key(phrase)
                    break
    
    def say_hi(self,text):
        phrase = random.choice(self.command_dict[self.say_hi])
        footprint_R_body = bosdyn.geometry.EulerZXY(yaw=0.0, roll=0.0, pitch=0.1)
        cmd = RobotCommandBuilder.synchro_stand_command(footprint_R_body=footprint_R_body)
        self.command_client.robot_command(cmd)
        footprint_R_body = bosdyn.geometry.EulerZXY(yaw=0.0, roll=0.0, pitch=-0.1)
        cmd = RobotCommandBuilder.synchro_stand_command(footprint_R_body=footprint_R_body)
        self.command_client.robot_command(cmd)
        cmd = RobotCommandBuilder.synchro_stand_command() 
        self.command_client.robot_command(cmd)
        self.robot.logger.info(phrase)
        # print(phrase)
        
    
    def undock(self,text):
        self.robot.logger.info("Undocking.")
        blocking_undock(self.robot)
            
    def lap(self,text):
        cmd = RobotCommandBuilder.synchro_stand_command() 
        self.command_client.robot_command(cmd)
        self.command_client.robot_command(lease=None, command = self.lft_45, end_time_secs = time.time()+1.0)
        time.sleep(2)
        self.command_client.robot_command(lease=None, command = self.fwd, end_time_secs = time.time()+2)
        time.sleep(2.5)
        self.command_client.robot_command(lease=None, command = self.lft_45, end_time_secs = time.time()+1)
        time.sleep(2)
        self.command_client.robot_command(lease=None, command = self.fwd, end_time_secs = time.time()+5)
        time.sleep(6)
        self.command_client.robot_command(lease=None, command = self.lft_45, end_time_secs = time.time()+4.0)
        time.sleep(4.1)
        self.command_client.robot_command(lease=None, command = self.fwd, end_time_secs = time.time()+4.0)
        time.sleep(5)
        self.command_client.robot_command(lease=None, command = self.rgt_45, end_time_secs = time.time()+1.1)
        time.sleep(1.5)
        blocking_stand(self.command_client)
        
    def dock(self,text):
        blocking_stand(self.command_client)
        self.robot.logger.info("Going back to my dock")
        blocking_dock_robot(self.robot, 520)
    
    def power_off(self,text):
        self.robot.power_off(cut_immediately=False, timeout_sec=20)
        assert not self.robot.is_powered_on(), "Robot power off failed."
        self.robot.logger.info("Robot safely powered off.")
        



        
