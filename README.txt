//-------|---------|---------|---------|---------|---------|---------|---------|
//
// Deako Smart Lighting - Virtual Switches
// README.txt
//
//-------|---------|---------|---------|---------|---------|---------|---------|

//-----------------------------------------------------------------------------|
// Authorship
//-----------------------------------------------------------------------------|

Tim Lum
twhlum@gmail.com
Created:  2018.03.12
Modified: 2018.06.28



//-----------------------------------------------------------------------------|
// Project Description
//-----------------------------------------------------------------------------|

Effort to virtualize a bank of smart switches, to support sending and
receipt of correctly formatted MQTT packets, with appropriate responses
from the virtualized hardware side back to a user.



//-----------------------------------------------------------------------------|
// Package Files
//-----------------------------------------------------------------------------|
|
|--MQTT Broker.zip - Configured MQTT broker which will receive and distribute messages
|  |--Note: Must be unzipped to operate
|  |--Note: If run from the run.sh script below, do not activate a prior instance (you'll have two brokers)
|
|--README.txt - This file, describes project and dependencies
|
|--ayncio.txt - (Incomplete) Notes on the use of async functions in Python
|  |--Note: May not be necessary if switches continue to use the thread library
|  |--(TODO) Move contents to README.txt and delete file
|
|--commands.txt - A command script, contains instructions executable by the Virtual Controller
|  |--Note: Building the bank is a distinct command in the commands.txt file, it is not automatic
|  |--(TODO) Command arguments do not yet correspond to real switch communication packets
|  |  |--Commands do not need modification, but the MQTT packet they send do
|  |--(TODO) Move instructions for use to README.txt. Redirect to README from commands.txt
|
|--requirements.txt - (Incomplete) List of packages or installations needed to operate the Virtual Switch Bank
|  |--Note: This is an unexplored component of automated setup
|  |--(TODO) Complete or abandon - discuss with Andy/Kurtiss how to best deploy the Virtual Switch Bank to a new machine
|  |--(TODO) Tether to Git?
|
|--run.sh - (Adjustment Needed) Shell script to activate and run the Virtual Switch Bank
|  |--(TODO) Change path name to Git working directory
|
|--sample_profile.json - A profile for the controller to parse in .json format
|  |--Note: For offline-work. It is preferred that a real profile be loaded with a command-line argument
|  |--Note: The controller should generate a bank of virtual switches using a JSON profile
|
|--sample_switch.json - A switch profile
|  |--Note: For testing/validation purposes. Is not invoked in normal operation
|
|--virt_switch.py - A Virtual Switch object definition
|  |--Note: Wraps both a switch's real JSON fields, as well as fields needed for virtualization
|
|--virtswitch_controller.py - A Virtual Switch Controller (the driver)
   |--Note: Requires a commands.txt file to perform actions
   |--Note: Uses virt_switch.py when generating switch objects for the virtual switch bank
   |--Note: Requires an operating MQTT broker to communicate with the virtual switch bank
      |--Reliability of the broker does affect system operation


//-----------------------------------------------------------------------------|
// Setup (Provisional)
//-----------------------------------------------------------------------------|
Note: Not all of the procedures below are complete or currently relevant.
They are included in case you need to perform one of the setups and wish to check prior work.


//-------|---------|---------|---------|
Setting up the HBMQTT Python Client (preferred)
2018.03.25
//-------|---------|---------|---------|

https://hbmqtt.readthedocs.io/en/latest/
I) Acquire the hbmqtt library
   A) In the Anaconda console (VSCode), type (sans quotes):
   B) "pip install hbmqtt"
   C) 



//-------|---------|---------|---------|
Setting up the Paho MQTT Python Client
2018.03.25
//-------|---------|---------|---------|

https://www.eclipse.org/paho/clients/python/docs/
I) In the Anaconda console (VSCode)
   A) Install the (Paho MQTT client) class
      1) 'Paho' is a community project
         a) https://wiki.eclipse.org/Paho
      2) 'MQTT' is a communication protocol
         a) Message Queueing Telemetry Transport
         b) Operates on top of the TCP/IP protocol
         c) https://en.wikipedia.org/wiki/MQTT
         d) https://www.iso.org/standard/69466.html - ISO/IEC 20922:2016
         e) Intended to decouple:
            i) Application specifics
            ii) Contents of a payload
         f) Has 3 qualities of service for message delivery:
            i)   "At Most Once"  (AMO)
            ii)  "At Least Once" (ALO)
            iii) "Exactly Once"  (XO)
   B) In Pip (a package management system for Python)
      1) $ pip install paho-mqtt
   C) Add import statement to Python program
      1) import paho.mqtt.client as mqtt
      2) https://pypi.python.org/pypi/paho-mqtt#network-loop

II) Create a Client (instance)
   A) ie. Client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311, transport="tcp")
   B) client_id - Unique - Required
   C) Other fields - Optional
   D) client =mqtt.Client(client_name)

III) Connect the Client to a Broker (Server)
   A) ie. connect(host, port=1883, keepalive=60, bind_address="")
   B) host - Broker's name or IP address - Required
   C) client.connect(host_name)
   D) For more information: http://www.steves-internet-guide.com/client-connections-python-mqtt/

IV) Subscribing to topics
   A) ie. subscribe(topic, qos=0)
   B) topic - The topic to subscribe to - Required
   C) qos - The Quality Of Service (AMO, ALO, XO, from 0 to 2 - Optional
   D) client.subscribe("deako/virtual/switch001")
   
V) Publish messages from the Client to the Broker (requires subscription)
   A) ie. publish(topic, payload=None, qos=0, retain=False)
   B) topic - The "thread" to which the method is being published - Required
   C) payload - The message being published - Required
   D) client.publish("deako/virtual/switch001","STATUS")

VI) Example script:
import paho.mqtt.client as mqtt #import the client1
broker_address="192.168.1.184"
#broker_address="iot.eclipse.org" #Use for an externally hosted broker
client = mqtt.Client("P1") #create new instance
client.connect(broker_address) #connect to broker
client.subscribe("deako/virtual/switch001")
client.publish("deako/virtual/switch001","STATUS") #"STATUS" is the payload

VII) Reading messages:
   A) 'message' class members:
      1) topic
      2) qos
      3) payload
      4) retain
   B) Requires an on_message callback to read the message
   C) http://www.steves-internet-guide.com/mqtt-python-callbacks/
   D) Example script:
def on_message(client, userdata, message):
print("message received " ,str(message.payload.decode("utf-8")))
print("message topic=",message.topic)
print("message qos=",message.qos)
print("message retain flag=",message.retain)
   E) client.on_message=on_message # attaches function to callback
   F) Requires running a loop to see the callbacks
      1) Loops - http://www.steves-internet-guide.com/loop-python-mqtt-client/
      2) Callbacks - http://www.steves-internet-guide.com/mqtt-python-callbacks/
      3) client.loop_start()
      4) client.loop_stop()

VIII) Complete example script:
import paho.mqtt.client as mqtt #import the client1
import time
############
def on_message(client, userdata, message):
print("message received " ,str(message.payload.decode("utf-8")))
print("message topic=",message.topic)
print("message qos=",message.qos)
print("message retain flag=",message.retain)
########################################
broker_address="192.168.1.184"
#broker_address="iot.eclipse.org"
print("creating new instance")
client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker")
client.connect(broker_address) #connect to broker
client.loop_start() #start the loop
print("Subscribing to topic","house/bulbs/bulb1")
client.subscribe("house/bulbs/bulb1")
print("Publishing message to topic","house/bulbs/bulb1")
client.publish("house/bulbs/bulb1","OFF")
time.sleep(4) # wait
client.loop_stop() #stop the loop

VIII) Setting up a local Broker
   A) 

IX) Setting up a cloud Broker
   A) 

//-------|---------|---------|---------|
Setting up multithreading in Python
2018.03.25
//-------|---------|---------|---------|

(Do not use multithreading for this project; see asynchronous programming)
https://en.wikipedia.org/wiki/Thread_(computing)

I) import threading

II) Create a thread
   A) threading.someThread1(target=someTask, args=(someArgument,))
   B) threading.someThread2(target=someTask, args=(someArgument,))

III) Run the thread
   A) someThread1.start()
   B) someThread2.start()

IV) (Optional) Join the threads
   A) someThread1.join()
   B) someThread2.join()
   C) Waits until the thread terminates. This blocks the calling thread
      until the thread whose join() method is called terminates – either
      normally or through an unhandled exception – or until the optional
      timeout occurs.

Setting up a Kotlin IDE environment
I) Selected platforms:
   A) Java SE Development Kit 8
      1) http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html
      2) 'Java SE Development Kit 8u162'
      3) Windows x86
   B) IntelliJ
      1) https://www.jetbrains.com/idea/download/#section=windows
      2) Community version



//-------|---------|---------|---------|
Asynchronous I/O
2018.03.25
//-------|---------|---------|---------|

https://en.wikipedia.org/wiki/Asynchronous_I/O




//-------|---------|---------|---------|
Install and set up Mosquitto MQTT Broker on a Windows platform:
2018.03.25
//-------|---------|---------|---------|

I) http://www.steves-internet-guide.com/install-mosquitto-broker/
   A) "However the advantage is that you can install Mosquitto as a service which starts automatically. This is not important for a test environment."
   B) Otherwise, just copy the zipped install from a pre-configured setup
   C) http://www.steves-internet-guide.com/downloads/
   D) Unzip, go to directory, and run the broker manually
      1) .7z (7-zip) format - https://www.7-zip.org/ for unzipper
      2) Readme:
      // --- Begin Readme ---
      
         Mosquitto
         =========

         Mosquitto is an open source implementation of a server for version 3.1 and
         3.1.1 of the MQTT protocol.

         See the following links for more information on MQTT:

         - Community page: <http://mqtt.org/>
         - MQTT v3.1.1 standard: <http://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html>

         Mosquitto project information is available at the following locations:

         - Main homepage: <http://mosquitto.org/>
         - Find existing bugs: <https://bugs.eclipse.org/bugs/buglist.cgi?product=Mosquitto>
         - Submit a bug: <https://bugs.eclipse.org/bugs/enter_bug.cgi?product=Mosquitto>
         - Source code repository: <http://git.eclipse.org/c/mosquitto/org.eclipse.mosquitto.git/>

         There is also a public test server available at <http://test.mosquitto.org/>

         Mosquitto was written by Roger Light <roger@atchoo.org>
         
      // --- End Readme ---

II) To establish a broker, once Mosquitto is installed
   A) (help file) mosquitto -h
   B) Use the -d option to place the Broker (as a daemon) into the background after starting
   C) 
   
III) To verify that the broker is running
   A) On the command line:
   B) netstat -a
   C) Search for a process listening on 0.0.0.0:1883 (this is the Mosquitto Broker)
   D) ctrl+c to exit

III) To establish the Listener (Subscriber), once Mosquitto is installed
   A) Use the (???) option to place the Listener (as a daemon) into the background after starting
   B) (help file) mosquitto_sub --help

IV) To establish a Sender (Publisher), once Mosquitto is installed
   A) Recommended not to place in the background
   B) (help file) mosquitto_pub --help



//-------|---------|---------|---------|
Converting a Python 2.7 script to .exe
2018.03.25
//-------|---------|---------|---------|

I) Acquire the 'py2exe' compilet
   A) https://null-byte.wonderhowto.com/how-to/convert-python-script-exe-0163965/
II) Write the script you want to be a .exe
III) Create setup.py
   A) Additional script that handles compilation to .exe
   B) Begin script:
      # --- Begin script ---
      #setup.py
      from distutil.core import setup
      import py2exe
      
      setup(console=['myscript.py'])
      # --- End script ---
   C) Third-party modules must be specified in the above script as follows:
   D) Begin script:
      # --- Begin script ---
      #setup.py
      from distutil.core import setup
      import py2exe
      
      setup(console=['myscript.py'],
          options = {
              'py2exe': {
                  'packages': ['pandas']
              }
          }
      )
      # --- End script ---
IV) Compile from the command prompt
   A) python setup.py py2exe
V) (No further instructions available - Not Python 2.7)



//-------|---------|---------|---------|
Converting a Python 3.6 script to .exe
2018.03.25
//-------|---------|---------|---------|

I) Assumes Python 3.6 is installed (as through Anaconda)
II) Install cx_Freeze
   A) From VSCode or other command line: pip install cx_Freeze
   B) If Python was installed via Anaconda, VSCode must be accessed through Anaconda
   C) Computer must be connected to the internet to download the package
   D) Documentation: http://cx-freeze.readthedocs.io/en/latest/overview.html
III) Install idna (if not done already)
   A) From VSCode or other command line: pip install idna
   B) If Python was installed via Anaconda, VSCode must be accessed through Anaconda
   C) Computer must be connected to the internet to download the package
IV) Write a .py script (ie. "hello_world.py")
   A) This is the program we wish to convert to .exe
V) Create a new python file named ‘setup.py’ on the current directory of the script we wish to convert
   A) This script will be responsible for converting "hello_world.py" to a .exe
VI) On the setup.py, code the following:
   A)
# --- Begin script ---
from cx_Freeze import setup, Executable

base = None

executables = [Executable("hello_world.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {
        'packages':packages,
    },
}

setup(
    name = "<any name>",
    options = options,
    version = "<any number>",
    description = '<any description>',
    executables = executables
)
# --- End script ---

VII) Run the setup script
   A) python setup.py build
IX) Confirm that no errors are reported
X) Check the newly created folder ‘build‘. It has another folder in it. Within that folder you can find your application. Run it. Make yourself happy.



//-------|---------|---------|---------|
To run multiple python scripts concurrently
2018.03.25
//-------|---------|---------|---------|

I) Simple solution: run from a bash file
   A) Instruct each process to go into the background with the '&' shell operator
   B) python script1.py&
      python script2.py&
II) More correct solution: Generate multiple background executables
   A) Then just double click the .exe to run it