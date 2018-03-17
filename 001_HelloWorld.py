# Necessary for all Mosquito MQTT operations
import paho.mqtt.client as mqtt
# Necessary for time operations (delays, waits)
import time

# Implicitly 'Global'
storage_bucket = ""

#---|---|---|---|------------------------------------------------------|------|
#   #on_message()
#---|---|---|---|------------------------------------------------------|------|
# Desc:    Determines whether this customer and index creates a collision
# Params:  NULL
# PreCons: NULL
# PosCons: NULL
# RetVal:  None (default 0?)
# MetCall: NULL
def on_message_behavior(client, userdata, message):
    # States that within this scope, we are to use the global storage_bucket
    global storage_bucket
    storage_bucket = str(message.payload.decode("utf-8"))
    if (storage_bucket == "IS_ON"):
        client.publish("dev/test2","False. Imma_off")
    print("message.topic   : ", message.topic)
    print("message.qos     : ", message.qos)
    print("message.retain  : ", message.retain)
    print(storage_bucket)

#---|---|---|---|------------------------------------------------------|------|
#   #main()
#---|---|---|---|------------------------------------------------------|------|
# Desc:    Determines whether this customer and index creates a collision
# Params:  NULL
# PreCons: NULL
# PosCons: NULL
# RetVal:  None (default 0?)
# MetCall: NULL
def main():
    # States that within this scope, we are to use the global storage_bucket
    global storage_bucket

    # Set the address of the broker
    broker_address = "127.0.0.1"
    # Use for cloud broker
    #broker_address="iot.eclipse.org"    

    # The topics to subscribe to
    broker_topic1 = "dev/test1"
    broker_topic2 = "dev/test2"

    # Set client names
    client_name1 = "P1"
    client_name2 = "P2"

    # Time delay (connection period, in seconds)
    delay = 20

    # Create new instance (P1)
    print("Creating new instance: " + client_name1)
    client1 = mqtt.Client(client_name1)
    # .on_message callback triggered by 'Event Message Received'
    # on_message_behavior is assigned to the callback
    # Paho Client does not utilize default callback behaviors
    client1.on_message = on_message_behavior

    # Create new instance (P2)
    print("Creating new instance: " + client_name2)
    client2 = mqtt.Client(client_name2)
    # .on_message callback triggered by 'Event Message Received'
    # on_message_behavior is assigned to the callback
    # Paho Client does not utilize default callback behaviors
    client2.on_message = on_message_behavior

    # Connect to the broker and begin listening
    print("Connecting to broker:  " + broker_address)
    client1.connect(broker_address)
    client1.loop_start()
    client2.connect(broker_address)
    client2.loop_start()

    print("Subscribing to topics")
    client2.subscribe(broker_topic1)
    client2.subscribe(broker_topic2)

    #print("Publishing message to topic",broker_topic)
    #client.publish(broker_topic,"Pie pie pie pie")
    
    # Stop the clients after a delay
    time.sleep(delay)
    client1.loop_stop() #stop the loop
    client2.loop_stop() #stop the loop

    # Print the output
    print("End of program results: " + storage_bucket)

#---|---|---|---|------------------------------------------------------|------|
#   #EXECUTION
#---|---|---|---|------------------------------------------------------|------|
if __name__ == "__main__":
    main()
