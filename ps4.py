import rclpy

from rclpy.node import Node

from sensor_msgs.msg import Joy

from std_msgs.msg import String

from geometry_msgs.msg import Twist

from rclpy import qos

import math

class Ps4(Node):
	def __init__(self):
		super().__init__("xbox_control_node")
		self.dat = self.create_subscription(Joy, "joy", self.sub_callback, qos_profile=qos.qos_profile_sensor_data)
		self.dat

		self.sent_drive = self.create_publisher(Twist, "control_drive_topic", qos_profile=qos.qos_profile_system_default)
		self.sent_drive_timer = self.create_timer(0.05, self.sent_drive_callback)

		self.button = {}
		self.all = ["S","X","O","T","L1","R1","L2","R2","Share","Option","AL","AR","PS","Home"]
		for index, element in enumerate(self.all):
			self.button[element] = 0

		self.axes = {}
		self.all2 = ["LX", "LY", "RX", "LT", "RT", "RY"]
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
		limit = 0.1

		msg = Twist()

		x = -1*self.axes["LX"]
		y = self.axes["LY"]

		if (int(self.button["L1"]) == 0):
			if x < limit and x > -1*limit and y < limit and y >-1*limit:
				x = 0
				y = 0
			elif x < limit and x > -1*limit:
				x = 0
			elif y < limit and y > -1*limit:
				y = 0
			elif x >= 0 and y >= 0:
				x = 0.707
				y = 0.707
			elif x <= 0 and y >= 0:
				x = -0.707
				y = 0.707
			elif x <= 0 and y <= 0:
				x = -0.707
				y = -0.707
			elif x >= 0 and y <= 0:
				x = 0.707
				y = -0.707
				

		turn = -1*self.axes["RX"]
		theta = math.atan2(y, x)
		power = math.hypot(x, y)
		sin = math.sin(theta - math.pi/4)
		cos = math.cos(theta - math.pi/4)
		Max = max(abs(sin), abs(cos))
		leftFront = power * cos/Max + turn
		rightFront = power * sin/Max - turn
		leftBack = power * sin/Max + turn
		rightBack = power * cos/Max - turn

		if ((power + abs(turn)) > 1):
			leftFront /= (power + abs(turn))
			rightFront /= (power + abs(turn))
			leftBack /= (power + abs(turn))
			rightBack /= (power + abs(turn))		

		msg.linear.x = float(round(leftFront*255))
		msg.linear.y = float(round(rightFront*255))
		msg.angular.x = float(round(leftBack*255))
		msg.angular.y = float(round(rightBack*255))



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
