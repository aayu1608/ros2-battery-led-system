#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from my_robot_interfaces.srv import SetLed

class BatteryNode(Node): 

    def __init__(self): 

        super().__init__('battery_node')
        self.battery_state = "full"
        self.last_time_battery_changed = self.get_current_time_seconds()
        self.battery_timer = self.create_timer(0.1, self.check_battery_status)
        self.set_led_client = self.create_client(SetLed, "set_led")
        self.get_logger().info("Battery node has been started")

    def get_current_time_seconds(self):
        seconds, nanoseconds = self.get_clock().now().seconds_nanoseconds()
        return seconds + nanoseconds / 1000000000.00
    
    def check_battery_status(self):
        time_now = self.get_current_time_seconds()
        if self.battery_state == "full":
            if time_now - self.last_time_battery_changed > 4.0:
                self.battery_state = "empty"
                self.get_logger().info("Battery is now empty, charging...")
                self.call_set_led_srv(2, 1)
                self.last_time_battery_changed = time_now
        elif self.battery_state == "empty":
            if time_now - self.last_time_battery_changed > 6.0:
                self.battery_state = "full"
                self.get_logger().info("Battery is now full")
                self.call_set_led_srv(2, 0)
                self.last_time_battery_changed = time_now

    def call_set_led_srv(self, led_number, state):
        while not self.set_led_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for set_led service to be available...")
        request = SetLed.Request()
        request.led_number = led_number
        request.state = state
        future = self.set_led_client.call_async(request)
        future.add_done_callback(self.set_led_response_callback)
    
    def set_led_response_callback(self, future):
        response: SetLed.Response = future.result()
        if response.success:
            self.get_logger().info("Led state changed")
        else:
            self.get_logger().error("Led state change failed")

def main(args=None):
    rclpy.init(args=args)
    node = BatteryNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
 