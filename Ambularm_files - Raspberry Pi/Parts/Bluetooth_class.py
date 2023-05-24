import time
import bluetooth
import sys

class Bluetooth_manager:
    def __init__(self, phone_mac_address, uuid):
        self.phone_mac_address = phone_mac_address
        self.uuid = uuid
        self.channel = self.find_port()
        self.is_sock_connection_open = False

    def find_port(self):
        for connect_tries in range(1, 6):
            service_matches = bluetooth.find_service(uuid=self.uuid, address=self.phone_mac_address)

            if len(service_matches) == 0:
                print("Couldn't find the service, still looking...")
                time.sleep(1)
                if connect_tries == 5:
                    print("Couldn't find the service, exiting...")
                    sys.exit(0)
            else:
                break

        first_match = service_matches[0]
        port = first_match["port"]  # RFCOMM port
        name = first_match["name"]
        host = first_match["host"]

        print(f"Connecting to '{name}' on {host} on port (channel): {port}")
        return port

    def send_message_to_phone(self, message):
        # Create the client socket
        if not self.is_sock_connection_open:
            self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            try:
                self.sock.connect((self.phone_mac_address, self.channel))
                self.is_sock_connection_open = True
            except bluetooth.btcommon.BluetoothError as err:
                # Error handling
                print("An error occurred: ", err)
                self.sock.close()
                self.is_sock_connection_open = False

        if self.is_sock_connection_open:
            try:
                message = message + "\n"
                self.sock.send(message)
                print(f"Message sent: {message}")
            except bluetooth.btcommon.BluetoothError as err:
                print("An error occurred: ", err)
                self.sock.close()
                self.is_sock_connection_open = False
    
    def close_connection(self):
        self.sock.close()
            

# How to use:
# phone_mac_address = "A8:34:6A:ED:83:EB"  # Phone's Bluetooth (MAC) Address
# uuid = "691e69ed-9e3c-48ff-ab87-851d1ef80f47"  # Same UUID as on Android Application
# message = "Hello from Raspberry Pi!"

# bluetooth_manager = Bluetooth_manager(phone_mac_address, uuid)
# bluetooth_manager.send_message_to_phone(message)
