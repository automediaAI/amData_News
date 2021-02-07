import time
import datetime
now = datetime.datetime.now()
print("Current date and time: ")
print(str(now))

print("Printed immediately.")
time.sleep(60*3)
print("Printed after 3 minutes.")
now = datetime.datetime.now()
print("Current date and time: ")
print(str(now))

print("Yo!")