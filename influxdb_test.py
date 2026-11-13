import local_library

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

client = InfluxDBClient(
        url="http://192.168.0.27:8086",
        token="4lkcXNhkRiX-xOJfFxx5ol9CWETRHaMNJw5b8nPhuc_RNjQOVrGiSjEBY7gTKEYxq9Ve1x7Yy_XaMvW5z3AnFg==",
        org="ptjoker95",)

write_api = client.write_api( write_options=SYNCHRONOUS )

point = (
        Point("mpu6050")
        .field("ax", 0.12)
        .field("ay", -0.03)
        .field("az", 9.81)
        )

write_api.write( bucket="MPU-6050", record=point )

write_api.close()
client.close()
