from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import re



class RunCommands:
    def __init__(self):
        pass    
    
    def _run_command(self, net_connect, command: str):
        try:
            output = net_connect.send_command(command, delay_factor = 2, read_timeout=30)
            return str(output)
        except Exception as e:
            return str(e)
        
    def single_device_single_command(self, device, command:str):

        try:
            net_connect = ConnectHandler(**device)
            print("entering enable mode")
            net_connect.enable()
            print("enable mode entered")
            net_connect.send_command("terminal length 0")
            output = self._run_command(net_connect=net_connect, command=command)
            net_connect.disconnect()
            return str(output)
        except Exception as e:
            return e
        pass
    
    def single_device_multiple_commands(self, device, commands: list[str]):
        try:
            net_connect = ConnectHandler(**device)
            outputs = {}
            print("entering enable mode")
            net_connect.enable()
            print("enable mode entered")
            net_connect.send_command("terminal length 0")
            for command in commands:
                print(f"sending command : {command}")
                output = self._run_command(net_connect, command)
                outputs[command] = output

            net_connect.disconnect()
            return {device['ip']: outputs}
        except Exception as e:
            return {device['ip']: str(e)}
        
    def _set_config_single_device(self, device, commands):
        try:
            net_connect = ConnectHandler(**device)
            net_connect.enable()
            outputs = net_connect.send_config_set(commands)
            
            # Check for errors
            error_messages = ["Invalid input", "Ambiguous command", "Incomplete command"]
            print("checking for error messages")
            for error_message in error_messages:
                if error_message in outputs:
                    raise Exception(f"Error configuring device {device['ip']}: {outputs}")
            print("no error messages found")
            #net_connect.save_config()
            net_connect.disconnect()
            return outputs
        except Exception as e:
            print(f"Exception occurred : {e}")
            raise  # Re-raise the exception

    def get_running_config(self, device) -> list:
        try:
            net_connect = ConnectHandler(**device)
            net_connect.enable()
            net_connect.send_command("terminal length 0", expect_string=r"#")
            output = net_connect.send_command("show running-config", expect_string=r"#", delay_factor=2, read_timeout=60)
            net_connect.disconnect()

            lines = output.splitlines()
            clean_lines = []
            skip_patterns = re.compile(
                r"^(Building configuration|Current configuration|version \d|end$|!\s*$)"
            )
            for line in lines:
                if skip_patterns.match(line.strip()):
                    continue
                if line.strip() == "":
                    continue
                clean_lines.append(line)

            return clean_lines
        except Exception as e:
            return str(e)