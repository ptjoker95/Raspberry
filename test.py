import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="localhost", help="브로커 주소")
print( parser.parse_args().host )

args = parser.parse_args()
print(args)
print(args.host)