import json
import logging
from pyats import aetest
from rich.table import Table
from rich.console import Console
from genie.utils.diff import Diff
from pyats.log.utils import banner

# ----------------
# Get logger for script
# ----------------

log = logging.getLogger(__name__)

# ----------------
# AE Test Setup
# ----------------
class common_setup(aetest.CommonSetup):
    """Common Setup section"""
# ----------------
# Connected to devices
# ----------------
    @aetest.subsection
    def connect_to_devices(self, testbed):
        """Connect to all the devices"""
        testbed.connect()
# ----------------
# Mark the loop for Learn Interfaces
# ----------------
    @aetest.subsection
    def loop_mark(self, testbed):
        aetest.loop.mark(Test_Cisco_IOS_XE_Interfaces, device_name=testbed.devices)

# ----------------
# Test Case #1
# ----------------
class Test_Cisco_IOS_XE_Interfaces(aetest.Testcase):
    """Parse pyATS learn interface and test against thresholds"""

    @aetest.test
    def setup(self, testbed, device_name):
        """ Testcase Setup section """
        # Set current device in loop as self.device
        self.device = testbed.devices[device_name]
    
    @aetest.test
    def get_parsed_version(self):
        parsed_version = self.device.learn("interface")
        # Get the JSON payload
        self.parsed_json=parsed_version.info

    @aetest.test
    def create_file(self):
        # Create .JSON file
        with open(f'{self.device.alias}_Learn_Interface.json', 'w') as f:
            f.write(json.dumps(self.parsed_json, indent=4, sort_keys=True))
    
    @aetest.test
    def test_input_errors(self):
        # Test for version interface input errors
        input_errors_threshold = 0
        self.failed_interface = {}
        table = Table(title="pyATS Learn Interface Input Errors")
        table.add_column("Device", style="cyan")
        table.add_column("Interface", style="cyan")
        table.add_column("Input Error Threshold", style="green")
        table.add_column("Input Errors", style="red")
        table.add_column("Passed/Failed", style="green")
        for intf,value in self.parsed_json.items():
            if 'counters' in value:
                counter = value['counters']['in_errors']
                if int(counter) > input_errors_threshold:
                    table.add_row(self.device.alias,intf,str(input_errors_threshold),str(counter),'Failed',style="red")
                    self.failed_interface = int(counter)
                else:
                    table.add_row(self.device.alias,intf,str(input_errors_threshold),str(counter),'Passed',style="green")
            else:
                    table.add_row(self.device.alias,intf,input_errors_threshold,'N/A','Skipped',style="yellow")           
        # display the table
        console = Console(record=True)
        with console.capture() as capture:
            console.print(table,justify="left")
        log.info(capture.get())

        if self.failed_interface:
            self.failed()
        else:
            self.passed()

    @aetest.test
    def test_output_errors(self):
        # Test for version interface output errors
        output_errors_threshold = 0
        self.failed_interface = {}
        table = Table(title="pyATS Learn Interface Output Errors")
        table.add_column("Device", style="cyan")
        table.add_column("Interface", style="cyan")
        table.add_column("Output Error Threshold", style="green")
        table.add_column("Output Errors", style="red")
        table.add_column("Passed/Failed", style="green")
        for intf,value in self.parsed_json.items():
            if 'counters' in value:
                counter = value['counters']['out_errors']
                if int(counter) > output_errors_threshold:
                    table.add_row(self.device.alias,intf,str(output_errors_threshold),str(counter),'Failed',style="red")
                    self.failed_interface = int(counter)
                else:
                    table.add_row(self.device.alias,intf,str(output_errors_threshold),str(counter),'Passed',style="green")
            else:
                    table.add_row(self.device.alias,intf,output_errors_threshold,'N/A','Skipped',style="yellow")           
        # display the table
        console = Console(record=True)
        with console.capture() as capture:
            console.print(table,justify="left")
        log.info(capture.get())

        if self.failed_interface:
            self.failed()
        else:
            self.passed()

class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, testbed):
        testbed.disconnect()

# for running as its own executable
if __name__ == '__main__':
    aetest.main()