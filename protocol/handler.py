from protocol.eleroProtocol import EleroProtocol
from protocol.protocolUtils import map_byte_to_address, map_to_byte_address, map_to_byte_address_wchannel, map_from_str


class Handler:
    def __init__(self, addresses, autodiscovery_callback, debug=False):
        self.addresses = addresses
        self.elero = EleroProtocol()
        self.debug = debug

    def get_blind_state(self, payload):
        if self.elero:
            return self.elero.eleroState[payload[6]]

    def on_receive_data(self, data):
        try:
            (length, cnt, typ, chl, src, bwd, fwd, dests, payload, rssi, lqi, crc) = self.elero.interpretMsg(data)
            if self.debug:
                print("\n\n")
                print("len= {:d}, cnt= {:d}, typ={:02X}, chl={:d}".format(length, cnt, typ, chl), end=',')
                print(f"\nSource: {map_byte_to_address(src)}")
                print(f"BWD: {map_byte_to_address(bwd)}")
                print(f"FWD: {map_byte_to_address(fwd)}")
                print(f"Length of Destinations {len(dests)}")
                des_list = []
                for dest in dests:
                    if len(dest) > 1:
                        print(map_byte_to_address(dest))
                        print(f"----> {map_byte_to_address(dest)}")
                    else:
                        print(':[{:d}]'.format(dest[0]), end=',')
                print("rssi={:.1f},lqi={:d},crc={:d}".format(rssi, lqi, crc), end=', ')
                print("payload=" + ''.join('{:02X}:'.format(a) for a in payload))
            blind_pos = None
            if typ == 0x6A:
                print("Autolerning due to stop button ->")
                return {"remote": map_byte_to_address(src), "blind_id": map_byte_to_address(dests[0]), "channel": chl,
                        "action": "stop", "rssi": rssi}
            elif typ == 0xCA:
                print("Autolerning due to status message ->")
                print("Blind id:" + map_byte_to_address(src))
                print("----> Remote: " + map_byte_to_address(dests[0]))
                print("status is: " + self.get_blind_state(payload=payload))
                blind_pos = self.get_blind_state(payload=payload)
                print(
                #    f"Blind id: {map_byte_to_address(src)} ----> Remote {map_byte_to_address(dests[0])} Status is: {self.get_blind_state(payload=payload)}")

                return {"remote": map_byte_to_address(dests[0]), "blind_id": map_byte_to_address(src), "channel": chl,
                        "action": "position", "rssi": rssi, "position": blind_pos}
        except:
            print("Exception")
        return None

    def driver(self):
        return self.elero

    def buildMsg(self, remote, blindid, command):
        blindid += "51"
        print(f"Blind id: {blindid}")
        print(f"remote id: {remote}")
        add_remote = map_from_str(remote)
        add_blind = map_from_str(blindid)
        print(f"remote id converted: {add_remote}")
        print(f"blind id converted: {add_blind}")
        return self.elero.construct_msg(remote_addr=add_remote, blind_addr=add_blind, command=command)
