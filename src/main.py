#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
# import rospy
import sys
import numpy as np
import copy
# import rospy
# import moveit_commander
# import moveit_msgs.msg
from geometry_msgs.msg import Pose, PoseStamped
# import tf

from math import pi
# from std_msgs.msg import String
# from moveit_commander.conversions import pose_to_list

from Domain.feeder import Feeder
from Domain.wall import Wall
from Domain.brick import Type
from App.ihm import Ihm

def main():
     #TODO : input the taking coordinates for the b6 runner
    taking_pose_b6 = Pose()
    taking_pose_b6.position.x = 0
    taking_pose_b6.position.y = -0.5
    taking_pose_b6.position.y = 0
    taking_pose_b6.orientation.x = 0
    taking_pose_b6.orientation.y = 0
    taking_pose_b6.orientation.z = 0
    taking_pose_b6.orientation.w = 1

    f1 = Feeder(6, Type.big, taking_pose_b6)

    #TODO : input the taking coordinates for the b5 runner
    taking_pose_b5 = Pose()
    taking_pose_b5.position.x = -0.3
    taking_pose_b5.position.y = -0.5
    taking_pose_b5.position.y = 0
    taking_pose_b5.orientation.x = 0
    taking_pose_b5.orientation.y = 0
    taking_pose_b5.orientation.z = 0
    taking_pose_b5.orientation.w = 1

    f2 = Feeder(5, Type.big, taking_pose_b5)

    #TODO : input the taking coordinates for the s2 runner
    taking_pose_s2 = Pose()
    taking_pose_s2.position.x = 0.3
    taking_pose_s2.position.y = -0.5
    taking_pose_s2.position.y = 0
    taking_pose_s2.orientation.x = 0
    taking_pose_s2.orientation.y = 0
    taking_pose_s2.orientation.z = 0
    taking_pose_s2.orientation.w = 1

    f3 = Feeder(2, Type.small, taking_pose_s2)

    feeders = [f1,f2,f3]
    wall = Wall(feeders)

    app = Ihm(feeders)
    app.title("DIMR KUKA")
    app.geometry('800x500')
    app.mainloop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Killed by user')
        sys.exit(0)
