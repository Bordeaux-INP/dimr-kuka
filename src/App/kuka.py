#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Copyright 2019:
        Laetitia Lerandy
        Alban Chauvel
        Estelle Arricau

        Projet robotique autonome 2020 DIMR KUKA
        ENSC - ENSEIRB MATMECA 3eme annee option robotique
        code de controle du robot
"""

import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import tf
from tf import TransformListener
import geometry_msgs.msg
from geometry_msgs.msg import Pose, PoseStamped
from math import pi
from std_msgs.msg import String
from moveit_commander.conversions import pose_to_list
from dimr_kuka.msg import DimrControl
from Domain.feeder import Feeder
from Domain.brick import Type



class Kuka():

    def __init__(self, feeders):
        self.is_busy = False #robot state to publish
        self.feeders = feeders

        moveit_commander.roscpp_initialize(sys.argv)
        rospy.init_node("dimr_kuka", anonymous=True)
        rospy.loginfo("Beginning with Kuka")
        self.robot = moveit_commander.RobotCommander()
        self.scene = moveit_commander.PlanningSceneInterface()
        group_name = "manipulator"
        self.move_group = moveit_commander.MoveGroupCommander(group_name)
        #self.tfb = tf.TransformBroadcaster()
        #self.tfl = tf.TransformListener()
        sub = rospy.Subscriber("kuka_bridge", DimrControl, self.callback_dimrcontrol_message)
        rospy.loginfo("topic kuka_bridge subscribed and ready to process")
        rospy.loginfo("adding objects")
        rospy.sleep(1)
        self.add_objects()

        rospy.spin()
        rospy.loginfo("Stopped manipulation")


    def callback_dimrcontrol_message(self,data):
        rospy.loginfo("Message DimrControl has been received.")
        self.move_group.set_pose_target(data.brick_pose)
        plan = self.move_group.go(wait=True)
        self.move_group.stop()
        self.move_group.clear_pose_targets()
        rospy.loginfo("finish")
        rospy.set_param("/kuka/busy", False)


    def add_objects(self):

        #Ground in base frame
        ground_pose = PoseStamped()
        ground_pose.header.frame_id = "base"
        ground_pose.pose.orientation.w = 1.0
        ground_pose.pose.position.x = 0.0
        ground_pose.pose.position.y = 0.0
        ground_pose.pose.position.z =  -0.01
        ground_name = "ground"
        self.scene.add_box(ground_name, ground_pose, size=(4, 4, 0))

        #Feeders in base frame
        for f in self.feeders:
            feeder_pose = PoseStamped()
            feeder_pose.header.frame_id = "base"
            feeder_pose.pose.orientation.w = f.pose.orientation.w
            feeder_pose.pose.position.x = f.pose.position.x
            feeder_pose.pose.position.y = f.pose.position.y
            feeder_pose.pose.position.z = f.pose.position.z + f.height/2
            feeder_name = "feeder "+str(f.id)
            self.scene.add_box(feeder_name, feeder_pose, size=(f.width, f.depth, f.height))
