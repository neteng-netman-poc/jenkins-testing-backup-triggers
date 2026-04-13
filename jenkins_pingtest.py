import sys
from helper_functions import return_info
from RunCommands import RunCommands

hostname = sys.argv[1]
device_info = return_info(hostname=hostname)

rc = RunCommands()
output = rc.single_device_single_command(device=device_info, command="ping 192.168.100.100")

print(output)
