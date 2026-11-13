import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
print( "BASE_DIR", BASE_DIR )

LIB_DIR = BASE_DIR / "libs"
print( "LIB_DIR", LIB_DIR )

sys.path.insert( 0, str( LIB_DIR ) )

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = os.environ.get("INFLUXDB_TOKEN")
org = "ptjoker95"
url = "http://192.168.0.27:8086"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

bucket="MPU-6050"

write_api = write_client.write_api(write_options=SYNCHRONOUS)

for value in range(5):
  point = (
    Point("measurement1")
    .tag("tagname1", "tagvalue1")
    .field("field1", value)
  )
  write_api.write(bucket=bucket, org="ptjoker95", record=point)
  time.sleep(1) # separate points by 1 second
