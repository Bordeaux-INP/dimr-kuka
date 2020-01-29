#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
import rospy
import sys
import numpy as np
import copy
# import rospy
# import moveit_commander
# import moveit_msgs.msg
from geometry_msgs.msg import Pose, PoseStamped
import tf

from math import pi
# from std_msgs.msg import String
# from moveit_commander.conversions import pose_to_list

from brick import Small, Big, Brick
from wall import Wall

class Layer(object):
    def __init__(self,num,capacity=Wall.column_number):
        #even layer : 0, odd layer : 1
        self.num = num
        self.parity = num % 2
        self.capacity = capacity
        self.bricks = [None] * capacity
        self.fill()

    def fill(self):
        if(self.parity == 0):
            for b in range(self.capacity):
                self.bricks[b] = Brick(Big(),self.num,b)
        else:
            self.bricks[0] = Brick(Small(),self.num,0)
            for k in range(1,self.capacity-1):
                self.bricks[k] = Brick(Big(),self.num,k)
            self.bricks[self.capacity-1] = Brick(Small(),self.num,self.capacity-1)
    
    def count_placed_bricks(self):
        #count the bricks placed in the layer
        sb_number = 0
        bb_number = 0
        for brick in bricks:
            if(brick.is_placed):
                if(brick.type = Small()):
                    sb_number+=1
                else:
                    bb_number+=1
        return sb_number,bb_number
    
    def is_empty(self):
        is_empty = True
        b = 0
        while(is_empty == True and b < n):
            if(self.bricks[b] != None):
                if(self.bricks[b].is_placed == True):
                    is_empty = False
        return is_empty
    
    def is_filled_up(self):
        is_filled_up = True
        b = 0
        while(is_filled_up == True and b < n):
            if(self.bricks[b] != None):
                if(self.bricks[b].is_placed == False):
                    is_filled_up = False
        return is_filled_up
    
    def destroy(self):
        if(self.is_empty() == False):
            for b in self.bricks:
                b.remove_from_wall()
        else:
            print("Layer already empty")
    
    def build(self):
        for b in self.bricks:
            if(b.is_placed == False):
                b.move_to_wall()

    def fill_feeders(self, feeders):
        if(self.is_empty() == False):
            for b in bricks:
                b.find_right_feeder(feeders)

