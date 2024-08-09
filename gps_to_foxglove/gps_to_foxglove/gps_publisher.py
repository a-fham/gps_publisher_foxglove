import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
import serial
import json
import os

class GpsPublisher(Node):
    def __init__(self):
        super().__init__('gps_publisher')
        self.publisher = self.create_publisher(String, 'gps_data', 10)
        self.logging_control_subscriber = self.create_subscription(
            Bool, 'gps_logging_control', self.logging_control_callback, 10
        )
        self.serial_port = '/dev/ttyUSB0'  # Update with your serial port
        self.baud_rate = 9600  # Update with your baud rate
        self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
        self.timer = self.create_timer(1.0, self.timer_callback)  # Adjust the timer period as needed
        self.current_data = {"Latitude": None, "Longitude": None, "Altitude": None}
        self.get_logger().info(f'Initialized GPS Publisher with serial port {self.serial_port} and baud rate {self.baud_rate}')

        # Initialize logging
        self.logging = False
        self.log_file = os.path.join(os.path.expanduser("~"), "gps_data.log")

    def timer_callback(self):
        try:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8').strip()
                self.get_logger().info(f'Received raw data: {line}')

                # Process the data
                self.process_data(line)

                # Publish data if all required values are present
                if all(self.current_data.values()):
                    json_msg = String()
                    json_msg.data = json.dumps({
                        "Latitude": self.current_data["Latitude"],
                        "Longitude": self.current_data["Longitude"],
                        "Altitude": self.current_data["Altitude"].split()[0]
                    })
                    self.publisher.publish(json_msg)
                    self.get_logger().info(f'Publishing: {json_msg.data}')

                    # Store latest data for logging
                    self.latest_data = json.dumps({
                        "Latitude": self.current_data["Latitude"],
                        "Longitude": self.current_data["Longitude"],
                        "Altitude": self.current_data["Altitude"].split()[0]
                    })

                    # Reset current_data after publishing
                    self.current_data = {"Latitude": None, "Longitude": None, "Altitude": None}
        except Exception as e:
            self.get_logger().error(f'Error in timer_callback: {e}')

    def process_data(self, raw_data):
        try:
            parts = raw_data.split(':')
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()

                if key in self.current_data:
                    self.current_data[key] = value
                else:
                    self.get_logger().warn(f'Unexpected data key: {key}')
            else:
                self.get_logger().warn(f'Unexpected data format: {raw_data}')
        except Exception as e:
            self.get_logger().error(f'Error in process_data: {e}')

    def logging_control_callback(self, msg):
        if msg.data:  # If the message is True
            if hasattr(self, 'latest_data'):
                try:
                    with open(self.log_file, 'a') as f:
                        f.write(f'{self.latest_data}\n')
                        self.get_logger().info(f'Logged latest data to file: {self.latest_data}')
                except IOError as e:
                    self.get_logger().error(f'Error writing to file: {e}')
            else:
                self.get_logger().info('No data available to log.')
            # Toggle logging state off after logging
            self.logging = False
        else:
            self.get_logger().info('Logging control disabled.')

def main(args=None):
    rclpy.init(args=args)
    gps_publisher = GpsPublisher()
    rclpy.spin(gps_publisher)

    gps_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
