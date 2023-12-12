import json
import time
from config.config import Config
from protocol.handler import Handler
import paho.mqtt.client as mqtt

from radio.radio import Radio

config = None

last_tick = None
status_topic = None


def on_new_blind_discovery(source_address, dest_address, channel, position):
    print(f"New blind discovered: {source_address} -> {dest_address} [{channel}]")
    if position is None:
        online_blind = {"status": "new_blind", "source": source_address, "destination": dest_address}
        client.publish(topic=status_topic, msg=json.dumps(online_blind))
    else:
        online_blind = {"status": "blind_position", "source": source_address, "destination": dest_address,
                        "position": position}
        client.publish(topic=status_topic, msg=json.dumps(online_blind))
    # config.add_address(source_address, dest_address, channel)
    pass


def on_receive_data(data):
    rcv = protocol_handler.on_receive_data(data)
    if rcv is not None:
        client.publish(topic=base_topic + rcv["remote"] + "/" + rcv["blind_id"] + "/availability", msg="online")
        if rcv["action"] == "position":
            client.publish(topic=base_topic + rcv["remote"] + "/" + rcv["blind_id"] + "/status", msg=rcv["position"])
    pass


def send_ping():
    global attributes_topic
    client.ping()


def ext_handler():
    global last_tick
    try:

        if last_tick == None:
            last_tick = time.time()
            print("setted tick time")
        else:
            if time.time() - last_tick > 5:
                send_ping()
                last_tick = time.time()
                print("Sent ping!")
                # b_id = [0xC3, 0x01, 0x38, 0x01]
                # r_id = [0xCE, 0x73, 0x55]
                # radiomessage = protocol_handler.elero.construct_msg(remote_addr=r_id, blind_addr=b_id, command="Check")
                # radio.raw_transmit(radiomessage, 10)

    except OSError as e:
        print(f"Error occurred: {e}")


def sub_cb(client, userdata,  msg):
    str_topic = msg.topic
    str_payload = msg.payload.decode()
    destination_str = str_topic.replace("elero/action/", "")
    destination = destination_str.split("/")
    radiomessage = protocol_handler.buildMsg(destination[0], destination[1], str_payload)
    print(radiomessage)
    radio.raw_transmit(radiomessage, 3)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    print(f"Userdata: {userdata} - flags: {flags}")
    client.subscribe(base_topic + "action/#")
    print(f"Subscribed to {base_topic} + action/#")
    client.publish(topic=availability_topic, payload="online", retain=False)
    print(f"Published alive to {availability_topic}")

def connect_and_subscribe(client_name, mqtt_server, mqtt_port, topic_sub):
    print(f"Connecting to broker {mqtt_server}...")
    client = mqtt.Client()
    client.username_pw_set(username="esp_pub", password="esp_pub")
    client.on_message = sub_cb
    client.on_connect = on_connect
    client.connect(host=mqtt_server, port=mqtt_port)

    print(f"Connecting to... ({mqtt_server}:{mqtt_port}")
    return client



try:
    config = Config()
    mqtt_server = config.get_config()["mqtt"]["server_address"]
    mqtt_port = config.get_config()["mqtt"]["server_port"]
    mqtt_topic = config.get_config()["mqtt"]["action_topic"]
    status_topic = config.get_config()["mqtt"]["status_topic"]
    availability_topic = config.get_config()["mqtt"]["availability_topic"]
    attributes_topic = config.get_config()["mqtt"]["attributes_topic"]
    mqtt_client_name = config.get_config()["mqtt"]["client_name"]
    base_topic = config.get_config()["mqtt"]["base_topic"]
    client = connect_and_subscribe(mqtt_server=mqtt_server, mqtt_port=mqtt_port, client_name=mqtt_client_name,
                                   topic_sub=mqtt_topic)
    print("OK!!")
    radio = Radio(radio_config=config.get_config()["radio"], radio_wiring=config.get_config()["wiring"])
    protocol_handler = Handler(addresses=config.get_config()["addresses"], debug=config.get_config()["debug"],
                               autodiscovery_callback=on_new_blind_discovery)
    client.loop_start()
    radio.client_loop(callback=on_receive_data, svc_handler=ext_handler)

except OSError as e:
    print(f"Error occurred: {e}")
