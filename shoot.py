import rclpy

from rclpy.node import Node

from sensor_msgs.msg import Joy

from std_msgs.msg import String

from geometry_msgs.msg import Twist

from rclpy import qos

import math

class Ps4(Node):
	def __init__(self):
		super().__init__("shoot_node")
		self.pwm_shoot = 0
		self.dat = self.create_subscription(Joy, "joy", self.sub_callback, qos_profile=qos.qos_profile_sensor_data)
		self.dat

		self.sent_drive = self.create_publisher(Twist, "control_shoot_topic", qos_profile=qos.qos_profile_system_default)
		self.sent_drive_timer = self.create_timer(0.05, self.sent_drive_callback)

		self.button = {}
		self.all = ["S","X","O","T","L1","R1","L2","R2","Share","Option","AL","AR","PS","Home"]
		for index, element in enumerate(self.all):
			self.button[element] = 0

		self.axes = {}
		self.all2 = ["LX", "LY", "RX", "LT", "RT", "RY", "BX", "BY"]
		for index, element in enumerate(self.all2):
			self.axes[element] = 0


	def sub_callback(self, msg_in):	#subscription topic
		for index, element in enumerate(self.all):
			self.button[element] = msg_in.buttons[index]
#			print(f"{self.all[index]}  :  {self.button[element]}")

		for index, element in enumerate(self.all2):
			if msg_in.axes[index] <= 0.2 and msg_in.axes[index] >= -0.2:
				self.axes[element] = 0
			else:
				self.axes[element] = msg_in.axes[index]
#			print(f"{self.all2[index]} : {self.axes[element]}")

	def sent_drive_callback(self): #publisher drive topic
		msg = Twist()

		if self.axes["BX"] == 1:
			self.pwm_shoot = 0
		elif self.axes["BY"] == 1:
			self.pwm_shoot = 51
		elif self.axes["BX"] == -1:
			self.pwm_shoot = 102
		elif self.axes["BY"] == -1:
			self.pwm_shoot = 153
		elif self.button["Share"] == 1:
			self.pwm_shoot = 204
		elif self.button["Option"] == 1:
			self.pwm_shoot = 255
        
		msg.angular.x = float(round(self.pwm_shoot))
		self.sent_drive.publish(msg)

	def check_bouncing(self, com, arr):
		for i in arr:
			if i == com:
				return False
		return True

def main():
	rclpy.init()

	sub = Ps4()
	rclpy.spin(sub)

	rclpy.shutdown()

if __name__=="__main__":
	main()
