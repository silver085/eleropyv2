from radio.cc1101 import CC1101
import time


class Radio:
    def __init__(self, radio_config, radio_wiring):
        if radio_config:
            self.radio_config = radio_config
            self.radio_wiring = radio_wiring
            import gc
            gc.collect()
            self.radio = CC1101(spibus=self.radio_wiring["spibus"], spics=self.radio_wiring["spics"],
                                speed=self.radio_wiring["speed"], gdo0=self.radio_wiring["gdo0"],
                                gdo2=self.radio_wiring["gdo2"])

    def getData(self):
        return self.radio.checkBuffer()

    def client_loop(self, callback, svc_handler):
        print("Entering listening mode...")
        while True:

            data = self.getData()
            svc_handler()
            if data:
               print("Data received, firing callback...")
               callback(data)

            time.sleep(self.radio_config["sleep_time"])

    def raw_transmit(self, data, repeat):
        if self.radio.initialised:
            for i in range(repeat):
                self.radio.transmit(data)
        else:
            print("Message not sent, no active radio.")
