#!/usr/bin/env python
"""
    Copyright 2019:
        Laetitia Lerandy
        Alban Chauvel
        Estelle Arricau

        Projet robotique autonome 2020 DIMR KUKA
        ENSC - ENSEIRB MATMECA 3eme annee option robotique
        code de l'IHM
"""

try:
    # for Python2
    import Tkinter as tk
    import tkFont as tkfont

except ImportError:
    # for Python3
    import tkinter as tk
    from tkinter import font as tkfont

import rospy
import geometry_msgs.msg
from dimr_kuka.msg import DimrControl
from PIL import Image, ImageTk
from Domain.wall import Wall

class Ihm(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        # global_feeders = feeders
        self.wall = None #created with the right values when the user click on the "start building" button on the Start_page
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        #self.kuka = None
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.column_number=4  # we can access from all frame with "self.controller.column_number"
        self.layer_number=3   # "self.controller.layer_number"

        rospy.init_node("ihm_node", anonymous=True)
        self.dimr_build_pub = rospy.Publisher("kuka_bridge", DimrControl, queue_size=10)
        self.dimr_destroy_pub = rospy.Publisher("kuka_destroy", DimrControl, queue_size=10)
        rospy.loginfo("topic kuka_bridge ready to process")
        rospy.loginfo("topic kuka_destroy ready to process")

        self.frames = {}
        for F in (Start_page, Settings,Page_joystick, Main_page): # you can ADD PAGE HERE
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")


        self.show_frame("Start_page") # the first Page to appear

    ############
    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

#=======================
class Start_page(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        img = Image.open("Images/home_img.jpg")
        labelWidth = controller.winfo_screenwidth()
        labelHeight = controller.winfo_screenheight()
        maxsize = (labelWidth, labelHeight)
        img.thumbnail(maxsize, Image.ANTIALIAS)
        img_ = ImageTk.PhotoImage(img)
        label = tk.Label(self, image=img_ )
        label.image = img_
        label.pack()

        img_param = Image.open("Images/parameter.png")
        img_param.thumbnail((50,50), Image.ANTIALIAS)
        img_p = ImageTk.PhotoImage(img_param)

        btn_start = tk.Button(self, text="START THE BUILDING",font=(None,14,'bold'),fg='black',height=3, width=30,command=self.start_building)
        btn_start.place(relx=.5, rely=.5, anchor="c")

        btn_settings = tk.Button(self,font=(None,10,'bold'),image = img_p,command=self.go_settings)
        btn_settings.image=img_p
        btn_settings.place(relx=1.,anchor="ne",bordermode="outside")

    ############
    def go_settings(self):
        self.controller.show_frame("Settings")
    ############
    def start_building(self):
        self.controller.frames["Main_page"].initialize() #draw the wall with the right number of layer and column
        self.controller.show_frame("Main_page")
        self.controller.wall = Wall(self.controller.layer_number, self.controller.column_number)

#=======================
class  Main_page(tk.Frame):

    #############
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.controller=controller
        rospy.set_param("/kuka/busy",False)
        rospy.set_param("/kuka_destroy/busy",False)
        self.column_number=self.controller.column_number
        self.layer_number=self.controller.layer_number
        self.wait=False
        self.layer_wait=0
        self.column_wait=0
        self.destroy_in_progress= False
        self.bricks = []
        self.blink=False
        self.msg = DimrControl()

    #############
    def initialize(self):
        self.column_number=self.controller.column_number
        self.layer_number=self.controller.layer_number
        self.grid()
        self.bricks = [[0 for x in xrange(self.column_number+1)] for x in xrange(self.layer_number)]
        self.arrows = [[0 for x in xrange(2)] for x in xrange(self.layer_number)]
        self.order = tk.StringVar()
        self.order.set("Click on a brick to fill the 1st layer")
        begin_row=1
        first_col_num=1
        end_col_num=1
        begin_parity=self.layer_number%2
        self.color_init="navajo white"
        self.color_current_layer="floral white"
        self.color_current_brick="green"
        self.color_brick_placed="DarkOrange2"
        self.current_layer=0

        title = tk.Label(self,text="KUKA BUILDING",font=(None,40,'bold'),anchor="n",bg=self.color_init,pady=15)
        title.grid(row=0,column=0,columnspan=self.column_number*2+first_col_num+end_col_num,sticky='NSEW')
        self.grid_rowconfigure(0,weight=2)

        for layer in range(self.layer_number-1,-1,-1):

            self.arrows[layer][0]=tk.Label(self,anchor="center",text ="",font=(None,20,'bold'),bg=self.color_init)
            self.arrows[layer][0].grid(row=begin_row+layer,column=0,sticky='NSEW')
            self.grid_columnconfigure(0,weight=2)

            if (layer%2)==begin_parity: # 2 small bricks

                self.bricks[layer][0] = tk.Button(self, bg=self.color_init,command=lambda x=abs(layer-(self.layer_number-1)), y=0: self.select_brick(x,y))
                self.bricks[layer][0].grid(column=first_col_num, row=layer+begin_row,sticky='NSEW')

                cpt=0
                for column in range(1,self.column_number,1):
                    self.bricks[layer][column] = tk.Button(self, bg=self.color_init,command=lambda x=abs(layer-(self.layer_number-1)), y=column: self.select_brick(x,y))
                    self.bricks[layer][column].grid(column=first_col_num+column+cpt, row=begin_row+layer,columnspan=2, sticky='NSEW')
                    cpt+=1

                self.bricks[layer][self.column_number] = tk.Button(self, bg=self.color_init,command=lambda x=abs(layer-(self.layer_number-1)), y=self.column_number: self.select_brick(x,y))
                self.bricks[layer][self.column_number].grid(column=first_col_num+self.column_number*2-1, row=layer+begin_row,sticky='NSEW')

            else:
                cpt=0
                for column in range(self.column_number):
                    self.bricks[layer][column] = tk.Button(self, bg=self.color_init,command=lambda x=abs(layer-(self.layer_number-1)), y=column: self.select_brick(x,y))
                    self.bricks[layer][column].grid(column=first_col_num+column+cpt, row=layer+begin_row,columnspan=2,sticky='NSEW')
                    cpt+=1

            self.arrows[layer][1]=tk.Label(self,text ="",font=(None,20,'bold'),anchor="center",bg=self.color_init)
            self.arrows[layer][1].grid(row=begin_row+layer,column=first_col_num+self.column_number*2,sticky='NSEW')
            self.grid_columnconfigure(first_col_num+self.column_number*2,weight=2)

        for layer in range(begin_row+self.layer_number-1,-1+begin_row,-1):
            self.grid_rowconfigure(layer,weight=1)
            for column in range(self.column_number*2):
                self.grid_columnconfigure(column+first_col_num,weight=1)

        self.label = tk.Label(self,textvariable=self.order,font=(None,20),fg="DarkOrange2",anchor="center",bg=self.color_init,pady=15)
        self.label.grid(row=begin_row+self.layer_number,column=0,columnspan=self.column_number*2+first_col_num+end_col_num,sticky='NSEW')
        self.grid_rowconfigure(begin_row+self.layer_number,weight=1)

        img_bin = Image.open("Images/bin2.png")
        img_bin.thumbnail((70,70), Image.ANTIALIAS)
        img_b = ImageTk.PhotoImage(img_bin)
        button_destroy = tk.Button(self,font=(None,10,'bold'),image = img_b, bg=self.color_init, command=self.destroy_wall)
        button_destroy.image=img_b
        button_destroy.place(relx=1.,anchor="ne",bordermode="outside")

        img_joystick = Image.open("Images/joystick.png")
        img_joystick.thumbnail((70,70), Image.ANTIALIAS)
        img_j= ImageTk.PhotoImage(img_joystick)
        btn_joystick= tk.Button(self,font=(None,10,'bold'),image = img_j,command=self.go_joystick,bg=self.color_init)
        btn_joystick.image=img_j
        btn_joystick.place(anchor="nw")

        self.update_arrows(self.current_layer)
        self.colorate_current_layer(0)

    ############
    def wall_in_color(self,color):
        for layer in range(self.layer_number):
            for column in range(self.column_number+1):
                if not(layer%2==0 and column==self.column_number):
                    self.bricks[abs(layer-(self.layer_number-1))][column].config(bg=color)

    ############
    def update_btn(self):
        print("salut")
        if not (rospy.get_param("/kuka/busy")):
            print("orange")
            self.wait=False
            self.bricks[self.layer_wait][self.column_wait].config(bg=self.color_brick_placed)
            self.update_white_brick()
            self.update_arrows(self.controller.wall.layer_in_progress().num)
            self.order.set("Click on a white brick to build the wall")
            self.label.config(fg="DarkOrange2")
        if self.controller.wall.is_filled_up():
            if not (rospy.get_param("/kuka/busy")):
                self.wall_in_color(self.color_current_brick)
                self.order.set("FINISHED")
                self.label.config(fg="green")
        if self.wait:
            self.blink = not self.blink
            if not self.destroy_in_progress:
                if self.blink:
                    self.bricks[self.layer_wait][self.column_wait].config(bg=self.color_brick_placed)
                else:
                    self.bricks[self.layer_wait][self.column_wait].config(bg=self.color_current_layer)
                print("repasse")
                self.parent.after(700,self.update_btn)



    #############
    def update_arrows(self,current_layer):
        for layer in range(self.layer_number):
            if layer==current_layer:
                self.arrows[abs(layer-(self.layer_number-1))][0].config(text="----->")
                self.arrows[abs(layer-(self.layer_number-1))][1].config(text="<-----")
            else:
                self.arrows[abs(layer-(self.layer_number-1))][0].config(text="")
                self.arrows[abs(layer-(self.layer_number-1))][1].config(text="")


    #############
    def colorate_current_layer(self,layer):
        for y in range(self.column_number+(layer%2)):
            self.bricks[abs(layer-(self.layer_number-1))][y].config(bg=self.color_current_layer)

    #############
    def update_white_brick(self):
        for layer in range(self.layer_number):
            for column in range(self.column_number+1):
                if not(layer%2==0 and column==self.column_number):
                    brick = self.controller.wall.at(layer,column)
                    if self.controller.wall.check_add_brick(brick):
                        self.bricks[abs(layer-(self.layer_number-1))][column].config(bg=self.color_current_layer)


    #############
    def select_brick(self, layer, column):
        if not (rospy.get_param("/kuka/busy")) and not rospy.get_param("/kuka_destroy/busy"):
            if not self.destroy_in_progress:
                current_layer=self.controller.wall.layer_in_progress().num
                brick=self.controller.wall.at(layer,column)
                if self.controller.wall.check_add_brick(brick):
                    if self.controller.wall.at(layer,column).add_to_wall():
                        rospy.set_param("/kuka/busy",True)
                        self.layer_wait=abs(layer-(self.layer_number-1))
                        self.column_wait=column
                        self.wait=True
                        self.update_empty_brick()
                        self.order.set("Pose in progress ...")
                        self.label.config(fg="DarkOrange2")
                        self.bricks[self.layer_wait][self.column_wait].config(bg=self.color_current_brick)
                        print(brick.wall_pose)
                        self.msg.brick_pose = brick.wall_pose
                        self.msg.feeder_pose = brick.feeder.pose
                        self.msg.brick_type=brick.type
                        self.msg.layer=layer
                        self.msg.column=column
                        self.msg.is_placed= False
                        self.controller.dimr_build_pub.publish(self.msg)
                        self.update_btn()

    #############
    def update_empty_brick(self):
        for layer in range(self.layer_number-1,-1,-1):
            for column in range(self.column_number,-1,-1):
                if not(layer%2==0 and column==self.column_number):
                    brick=self.controller.wall.at(layer,column)
                    if not brick.is_placed:
                        self.bricks[abs(layer-(self.layer_number-1))][column].config(bg=self.color_init)

    #############
    def go_joystick(self):
        if not rospy.get_param("/kuka/busy") and not  rospy.get_param("/kuka_destroy/busy"):
            if not self.destroy_in_progress:
                self.controller.show_frame("Page_joystick")
                # publish topic


    ############
    def destroy_wall(self):
        if not rospy.get_param("/kuka/busy"):
            print("destroy_pass")
            if not self.controller.wall.is_empty():
                self.parent.after(600,self.destroy_wall)
                if not rospy.get_param("/kuka_destroy/busy"):
                    if self.controller.wall.is_filled_up():
                        self.wall_in_color(self.color_brick_placed)
                    self.destroy_in_progress=True
                    rospy.set_param("/kuka_destroy/busy",True)
                    self.update_empty_brick()
                    self.order.set("Destruction in progress ...")
                    self.label.config(fg="DarkOrange2")
                    print("destroying the wall")
                    for layer in range(self.layer_number-1,-1,-1):
                        for column in range(self.column_number,-1,-1):
                            if not(layer%2==0 and column==self.column_number):
                                print("coucou")
                                brick=self.controller.wall.at(layer,column)
                                self.update_arrows(layer)
                                if self.controller.wall.check_remove_brick(brick):
                                    if self.controller.wall.at(layer,column).remove_from_wall():
                                        print(layer,column)
                                        self.msg.brick_pose = brick.wall_pose
                                        self.msg.feeder_pose = brick.feeder_pose
                                        self.msg.brick_type=brick.type
                                        self.msg.layer=layer
                                        self.msg.column=column
                                        self.msg.is_placed= True
                                        self.controller.dimr_destroy_pub.publish(self.msg)
                                        self.layer_wait=abs(layer-(self.layer_number-1))
                                        self.column_wait=column
                                        return True
                else:
                    self.blink = not self.blink
                    if self.destroy_in_progress:
                        if self.blink:
                            self.bricks[self.layer_wait][self.column_wait].config(bg=self.color_brick_placed)
                        else:
                            self.bricks[self.layer_wait][self.column_wait].config(bg=self.color_current_layer)
            else:
                if rospy.get_param("/kuka_destroy/busy"):
                    self.parent.after(600,self.destroy_wall)
                    self.blink = not self.blink
                    if self.destroy_in_progress:
                        if self.blink:
                            self.bricks[self.layer_wait][self.column_wait].config(bg=self.color_brick_placed)
                        else:
                            self.bricks[self.layer_wait][self.column_wait].config(bg=self.color_current_layer)
                else:
                        self.order.set("Click on a white brick to build the wall")
                        self.label.config(fg="DarkOrange2")
                        self.colorate_current_layer(0)
                        self.update_arrows(self.current_layer)
                        print("destroy done")
                        self.destroy_in_progress=False



#=======================
class Settings(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.grid()

        self.title = tk.Label(self,text="Settings",font=(None,40,'bold'),anchor="n",pady=15)
        self.title.grid(row=0,column=0,columnspan=2,sticky='NSEW')
        self.grid_rowconfigure(0,weight=2)

        self.label_layer = tk.Label(self,text="Number of layer : ",font=(None,20),anchor="n",pady=15)
        self.label_layer.grid(row=1,column=0,sticky='NSEW')
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)

        self.label_brick = tk.Label(self,text="Number of column : ",font=(None,20),anchor="n",pady=15)
        self.label_brick.grid(row=2,column=0,sticky='NSEW')
        self.grid_rowconfigure(2,weight=1)

        self.layer_slider = tk.Scale(self,from_=1, to=3,bd=3, sliderlength=100,orient="horizontal")
        self.layer_slider.grid(row=1,column=1,sticky='NSEW',padx=50)
        self.layer_slider.set(3)
        self.grid_columnconfigure(1,weight=2)

        self.brick_slider = tk.Scale(self,from_=1, to=4,bd=3,sliderlength=80,orient="horizontal")
        self.brick_slider.grid(row=2,column=1,sticky='NSEW',padx=50)
        self.brick_slider.set(4)

        self.btn_validate = tk.Button(self, text="OK",font=(None,17),bg="DarkSeaGreen1", command=self.update_values)
        self.grid_rowconfigure(3,weight=1)
        self.btn_validate.grid(row=3,column=0,columnspan=2,sticky='NSEW')

    ###########
    def update_values(self):
        self.controller.layer_number=self.layer_slider.get()
        self.controller.column_number=self.brick_slider.get()
        self.controller.show_frame("Start_page")



class Page_joystick(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        img = Image.open("Images/home_img.jpg")
        labelWidth = controller.winfo_screenwidth()
        labelHeight = controller.winfo_screenheight()
        maxsize = (labelWidth, labelHeight)
        img.thumbnail(maxsize, Image.ANTIALIAS)
        img_ = ImageTk.PhotoImage(img)
        label = tk.Label(self, image=img_ )
        label.image = img_
        label.pack()
        label = tk.Label(self, text="Teleoperation")
        label.pack(side="top", fill="x", pady=10)
        btn_back = tk.Button(self,font=(None,10,'bold'),height=3,text="Building",command=self.go_main_page)
        btn_back.place(anchor="nw")


    def go_main_page(self):
        self.controller.show_frame("Main_page")
        # mettre param ou envoyer un truc sur topic pour terminer
