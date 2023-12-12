import json
import os


class Config:

    def __init__(self):
        print("Current path is: " + os.getcwd())
        self.config_path = os.getcwd() + "config.json"
        try:
            with open(self.config_path) as config_file:
                self.config_data = json.load(config_file)
            import gc
            gc.collect()
            gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        except Exception as err:
            print("Error: ", err)
            print("Couldn't load configuration, exiting.")
            exit(-255)
        except KeyboardInterrupt:
            print("Detected keyboard interrupt!")


    def save_config(self):
        try:
            with open(self.config_path, "w") as config_file:
                json.dump(self.get_config(), config_file)
            print("Configuration saved.")
        except Exception as err:
            print(f"Unable to save configuration file {self.config_path}, error is: {err}")
            print("Unable to save config file:" + self.config_path + " error is: " + err)

    def get_config(self):
        if self.config_data:
            return self.config_data
        else:
            print("No config in memory.")
            exit(-255)

    def add_address(self, remote_address, blind_addresses, channel):
        import time
        self.config_data["addresses"].append({
            "id": str(time.ticks_ms()),
            "remote_address": remote_address,
            "blind_addresses": blind_addresses,
            "channel": channel
        })
        self.save_config()
