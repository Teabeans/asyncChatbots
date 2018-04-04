#---|---|---|---|------------------------------------------------------|------|
#
# Deako - Virtual Mesh Tool
# virtswitch_controller.py
#
#---|---|---|---|------------------------------------------------------|------|

#---|---|---|---|------------------------------------------------------|------|
# Authorship
#---|---|---|---|------------------------------------------------------|------|
#
# Tim Lum
# twhlum@gmail.com
# Created:  2018.03.03
# Modified: 2018.04.03
# For Deako internship
# Spring 2018
#

#---|---|---|---|------------------------------------------------------|------|
# File Description
#---|---|---|---|------------------------------------------------------|------|
#
# This is the implementation file for the virtual mesh, representing a
# collection of switches.
#

#---|---|---|---|------------------------------------------------------|------|
# Package Files
#---|---|---|---|------------------------------------------------------|------|
#
# See Github repository
# https://github.com/Teabeans/virt_mesh
#

#--------------------------------------|
# Begin Code
#--------------------------------------|

#---|---|---|---|------------------------------------------------------|------|
#   INCLUDE STATEMENTS
#   https://docs.python.org/3/py-modindex.html
#---|---|---|---|------------------------------------------------------|------|

# For all MQTT client operations
# https://www.eclipse.org/paho/clients/python/docs/
import paho.mqtt.client as mqtt

# For all time-related operations
# https://docs.python.org/3/library/time.html#module-time
import time

# For all asynchronous operations
# https://docs.python.org/3/library/asyncio.html#module-asyncio
import asyncio
# Note: The Paho MQTT loop is asynchronous by default and will function as such even without this

# For command-line interface generation
# http://click.pocoo.org/5/
import click

# For site querying
# http://docs.python-requests.org/en/master/
import requests

# For JSON file parsing
# https://docs.python.org/3/library/json.html#module-json
import json



#---|---|---|---|------------------------------------------------------|------|
#   GLOBAL VARIABLES
#---|---|---|---|------------------------------------------------------|------|

#--------------------------------------|
#   Virtualization fields
#--------------------------------------|

# The MQTT topic channel that switches watch for queries
TOPIC_QUERY = "deako/virt/query"

# The MQTT topic channel to which switches will send replies
TOPIC_REPLY = "deako/virt/reply"

# The broker address
BROKER = ""
the_mesh  = []
total_status = []

#--------------------------------------|
#   Actual fields
#--------------------------------------|
_address              = None
_backplates           = []
_channel              = ""
_faceplates           = []
_floors               = []
_groups               = []
_icon                 = ""
_load_count           = 0
_loads                = []
_mesh_api_rev         = 0
_mesh_passphrase      = ""
_name                 = ""
_ordered              = False
_orders               = []
_role                 = ""
_rooms                = []
_scenes               = []
_schedules            = []
_show_wifi_setup      = False
# Replaced by the_mesh[]
# _switches             = []
_toggle_scene_enabled = False
_tz                   = ""
_uuid                 = ""
_wifi_bridge_checkin  = None
_wifi_bridge_ssid     = None
_wifi_bridge_state    = ""
_wifi_bridges         = []



#---|---|---|---|------------------------------------------------------|------|
#   #switch
#---|---|---|---|------------------------------------------------------|------|
# Desc:    Class representing a switch object
# Params:  NULL
# PreCons: NULL
# PosCons: A normally instantiated switch will be connected to an MQTT broker
# RetVal:  NULL
# MetCall: NULL
class switch:

#---|---|---|---|------------------------------------------------------|------|
#   CLASS 'switch' VARIABLES
#---|---|---|---|------------------------------------------------------|------|

#--------------------------------------|
#   Virtualization fields
#--------------------------------------|
    _topic          = ''
    _is_on          = True
    _room           = ''
    _group          = ''
    _client         = None
    message_ID      = ''
    message_command = ''

#--------------------------------------|
#   Actual fields
#--------------------------------------|
    _backplate_slot        = 0
    _device_type           = "Smart"
    _downstream            = True
    _enabled               = True
    _faceplate_slot        = 0
    _firmware_rev          = ""
    _kebab_brightness      = 255
    _keypad                = True
    _keypad_timeout        = 5000
    _last_checkin          = None
    _load_id               = "31871bd7-fe36-4af2-9e7c-3a5036c51d70"
    _load_name             = "Porch lights"
    _location              = "x"
    _mesh_id               = 33057
    _multiway              = False
    _nightlight_brightness = 255
    _nightlight_enabled    = False
    _order_id              = "d8fe749a-089b-4227-afe3-9a6b96207149"
    _sn                    = "0DEAC00000003354"
    _uuid                  = "43805db7-fb82-45f8-9a61-56724e0a717c"

#--------------------------------------|
#   #parse_ID()
#--------------------------------------|
# Desc:    NULL
# Params:  NULL
# PreCons: NULL
# PosCons: NULL
# RetVal:  NULL
# MetCall: NULL
    def parse_ID(self, query):
        return(33045)
        # TODO: Write actual parse logic
    
#--------------------------------------|
#   #parse_commands()
#--------------------------------------|
# Desc:    NULL
# Params:  NULL
# PreCons: NULL
# PosCons: NULL
# RetVal:  NULL
# MetCall: NULL
    def parse_command(self, query):
        return("is_on")
        # TODO: Write actual parse logic

#--------------------------------------|
#   #respond()
#--------------------------------------|
# Desc:    NULL
# Params:  NULL
# PreCons: NULL
# PosCons: NULL
# RetVal:  NULL
# MetCall: NULL
    # Response behavior
    def respond(self, command):
        if (command == "is_on"):
            # TODO: Replace with field state
            self._client.publish(TOPIC_REPLY, "{} is_on True".format(self._mesh_id))

#--------------------------------------|
#   #switch_unpack()
#--------------------------------------|
# Desc:    NULL
# Params:  NULL
# PreCons: NULL
# PosCons: NULL
# RetVal:  NULL
# MetCall: NULL
    def switch_unpack(self, client, userdata, message):
        print("({}) Message received :".format(self._mesh_id), str(message.payload.decode("utf-8")), )
        # print("Message topic      :", message.topic)
        # print("Message qos        :", message.qos)
        # print("Message retain flag:", message.retain)
        query_ID      = self.parse_ID(message)
        query_command = self.parse_command(message)
        if (query_ID == self._mesh_id):
            print("({}) That's my number! I should respond!".format(self._mesh_id))
            self.respond(query_command)
        else:
            print("({}) That's not my number. I don't care.".format(self._mesh_id))

#--------------------------------------|
#   #__init__()
#--------------------------------------|
# Desc:    NULL
# Params:  NULL
# PreCons: NULL
# PosCons: NULL
# RetVal:  NULL
# MetCall: NULL
    def __init__(self, client, broker, switch_profile):
        # Virtualization fields
        self._topic                 = TOPIC_QUERY
        self._is_on                 = True
        self._room                  = ''
        self._group                 = ''
        self._client                = None
        self.message_ID             = ''
        self.message_command        = ''
        # Actual fields
        self._backplate_slot        = switch_profile['backplate_slot']
        self._device_type           = switch_profile['device_type']
        self._downstream            = switch_profile['downstream']
        self._enabled               = switch_profile['enabled']
        self._faceplate_slot        = switch_profile['faceplate_slot']
        self._firmware_rev          = switch_profile['firmware_rev']
        self._kebab_brightness      = switch_profile['kebab_brightness']
        self._keypad                = switch_profile['keypad']
        self._keypad_timeout        = switch_profile['keypad_timeout']
        self._last_checkin          = switch_profile['last_checkin']
        self._load_id               = switch_profile['load_id']
        self._load_name             = switch_profile['load_name']
        self._location              = switch_profile['location']
        self._mesh_id               = switch_profile['mesh_id']
        self._multiway              = switch_profile['multiway']
        self._nightlight_brightness = switch_profile['nightlight_brightness']
        self._nightlight_enabled    = switch_profile['nightlight_enabled']
        self._order_id              = switch_profile['order_id']
        self._sn                    = switch_profile['sn']
        self._uuid                  = switch_profile['uuid']
        
        # Connect and subscribe
        self._client = client
        self._client.on_message = self.switch_unpack
        self._client.connect(broker)
        self._client.loop_start()
        self._client.subscribe(self._topic)

#---|---|---|---|------------------------------------------------------|------|
#   # End class switch
#---|---|---|---|------------------------------------------------------|------|



#---|---|---|---|------------------------------------------------------|------|
#   GLOBAL (CONTROLLER) METHODS
#---|---|---|---|------------------------------------------------------|------|

#--------------------------------------|
#   #control_unpack()
#--------------------------------------|
# Desc:    NULL
# Params:  NULL
# PreCons: NULL
# PosCons: NULL
# RetVal:  NULL
# MetCall: NULL
def control_unpack(client, userdata, message):
    payload = str(message.payload.decode("utf-8"))
    print("(CTRL) Message received:" , payload)
    ID       = parse_reply_ID(payload)
    category = parse_reply_category(payload)
    value    = parse_reply_value(payload)
    process_reply(ID, category, value)

#--------------------------------------|
#   #virtswitch_controller()
#--------------------------------------|
# Desc:    Primary execution method (main())
#          Not named 'main()' due to use of 'click' library
# Params:  NULL
# PreCons: NULL
# PosCons: NULL
# RetVal:  NULL
# MetCall: NULL
@click.command()
@click.option('--broker_addy', default = "127.0.0.1", help = 'The MQTT broker address')
@click.option('-v', '--verbose', is_flag = True, help = 'Enables verbose mode')
@click.argument('mesh_file')
def virtswitch_controller(mesh_file, broker_addy, verbose):

    #--------------------------------------|
    #   Verbose Mode
    #--------------------------------------|

    if(verbose == True):
        def verboseprint(*args):
        # Print each argument separately so caller doesn't need to
        # stuff everything to be printed into a single string
            for arg in args:
                print(arg)
            print()
    else:   
        verboseprint = lambda *a: None      # do-nothing function



    # Setup
    print("Verify arg vector: broker_addy:", broker_addy)
    print("Verify arg vector: mesh_file  :", mesh_file)

    #--------------------------------------|
    #   Profile Acquisition Setup
    #--------------------------------------|

    # Acquire and parse JSON file
    params = {'limit': 16, 'country': 'us', 'apikey': 'API-KEY'}
    # Query the URL for a JSON file
    response = requests.get(mesh_file, params=params)

    # Assign the response (as a dictionary)
    a_profile       = response.json()
    switch_profiles = response.json()['switches']
    a_switch        = response.json()['switches'][0] # [0] [MAX]
    a_field         = response.json()['switches'][0]['uuid']

    # --- FOR TESTING PURPOSES ONLY --- START ---
    print()
    print("JSON Profile:")
    print(type(a_profile))
    print(a_profile)

    print()
    print("Switch Profiles:")
    print(type(switch_profiles))
    print(switch_profiles)

    print()
    print("First Switch Profile:")
    print(type(a_switch))
    print(a_switch)

    print()
    print("First Switch fields:")
    for i in a_switch:
        print(i, ":", a_switch[i], type(a_switch[i]))
    # --- FOR TESTING PURPOSES ONLY --- END ---

    # Parse the profile (mesh) fields
    print()
    print("Parse profiles:")
    parse_profile(a_profile)
    # For debugging
    # print_profile()

    #--------------------------------------|
    #   Mesh Generation Setup
    #--------------------------------------|

    # Generate a bank of switches
    # For every switch in the profile...
    vID = 0
    for a_profile in switch_profiles:
        # Make a new switch and append it to the the_mesh
        # By dictionary
        new_client = mqtt.Client(str(vID))
        the_mesh.append( switch(new_client, broker_addy, a_profile) )
        vID += 1
        # By fields
        # the_mesh.append(switch(TOPIC_QUERY, every_switch['uuid'], True, 'void', 'g3', mqtt.Client(every_switch['uuid'])))

    # the_mesh.append(switch(TOPIC_QUERY, '001', True, 'kitchen', 'g1', mqtt.Client('A_Switch1')))
    # the_mesh.append(switch(TOPIC_QUERY, '002', False, 'kitchen', 'g2', mqtt.Client('A_Switch2')))
    # the_mesh.append(switch(TOPIC_QUERY, '003', True, 'bath', 'g1', mqtt.Client('A_Switch3')))



    #--------------------------------------|
    #   Status Tracking Setup
    #--------------------------------------|

    # Collate all statuses together by...
    # Generating a status-tracking duplicate of the_mesh
    mesh_status = dict(the_mesh)

    ID_status    = ['001', '002', '003']
    is_on_status = [0, 1, 0]
    room_status  = ['kitchen', 'kitchen', 'bath']
    total_status.append(ID_status)
    total_status.append(is_on_status)
    total_status.append(room_status)



    #--------------------------------------|
    #   Controller MQTT Client Setup
    #--------------------------------------|

    # Create a control client
    control = mqtt.Client('000_Controller')
    control.on_message = control_unpack #attach function to callback

    # Connect to broker
    control.connect(broker_addy)

    # ???
    control.loop_start() #start the loop

    # Subscribe to topic channel
    control.subscribe(TOPIC_REPLY)



    #--------------------------------------|
    #   Mesh operations
    #--------------------------------------|

    # Check status of switch '003' is_on
    print()
    print("003 is_on: {}".format(total_status[1][2]))
    print()

    # Test connection
    control.publish(TOPIC_QUERY, "003 is_on")

    time.sleep(5) # wait

    # Check status of switch '003' is_on again
    print()
    print("003 is_on: {}".format(total_status[1][2]))
    print()

    control.loop_stop() #stop the loop

    print("Goodbye, World!")

#--------------------------------------|
#   End #virtswitch_controller()
#--------------------------------------|



#--------------------------------------|
#   #parse_profile()
#--------------------------------------|
# Desc:    Preperatory function - Breaks JSON file into component pieces
# Params:  [] arg1 - The JSON profile as a dictionary
# PreCons: GIGO - Assumes correctly formatted Deako JSON input.
#          No error checking is performed.
# PosCons: The fields of a Deako JSON profile are stored to global variables.
# RetVal:  None
# MetCall: None
def parse_profile(mesh_dict):
    global _address
    global _backplates
    global _channel
    global _faceplates
    global _floors
    global _groups
    global _icon
    global _load_count
    global _loads
    global _mesh_api_rev
    global _mesh_passphrase
    global _name
    global _ordered
    global _orders
    global _role
    global _rooms
    global _scenes
    global _schedules
    global _show_wifi_setup
    global _toggle_scene_enabled
    global _tz
    global _uuid
    global _wifi_bridge_checkin
    global _wifi_bridge_ssid
    global _wifi_bridge_state
    global _wifi_bridges
    _address              = mesh_dict["address"]
    _backplates           = mesh_dict["backplates"]
    _channel              = mesh_dict["channel"]
    _faceplates           = mesh_dict["faceplates"]
    _floors               = mesh_dict["floors"]
    _groups               = mesh_dict["groups"]
    _icon                 = mesh_dict["icon"]
    _load_count           = mesh_dict["load_count"]
    _loads                = mesh_dict["loads"]
    _mesh_api_rev         = mesh_dict["mesh_api_rev"]
    _mesh_passphrase      = mesh_dict["mesh_passphrase"]
    _name                 = mesh_dict['name']
    _ordered              = mesh_dict["ordered"]
    _orders               = mesh_dict["orders"]
    _role                 = mesh_dict["role"]
    _rooms                = mesh_dict["rooms"]
    _scenes               = mesh_dict["scenes"]
    _schedules            = mesh_dict["schedules"]
    _show_wifi_setup      = mesh_dict["show_wifi_setup"]
    # Replaced by the_mesh[]
    # _switches           = []
    _toggle_scene_enabled = mesh_dict["toggle_scene_enabled"]
    _tz                   = mesh_dict["tz"]
    _uuid                 = mesh_dict["uuid"]
    _wifi_bridge_checkin  = mesh_dict["wifi_bridge_checkin"]
    _wifi_bridge_ssid     = mesh_dict["wifi_bridge_ssid"]
    _wifi_bridge_state    = mesh_dict["wifi_bridge_state"]
    _wifi_bridges         = mesh_dict["wifi_bridges"]

#--------------------------------------|
#   #print_profile()
#--------------------------------------|
# Desc:    For debugging, prints the contents of this profile
# Params:  None
# PreCons: None
# PosCons: None
# RetVal:  None
# MetCall: None
def print_profile():
    print("Address        :", _address)
    print("Backplates     :", _backplates)
    print("Channel        :", _channel)
    print("Faceplates     :", _faceplates)
    print("Floors         :", _floors)
    print("Groups         :", _groups)
    print("Icon           :", _icon)
    print("Load Count     :", _load_count)
    print("Loads          :", _loads)
    print("Mesh_API_Rev   :", _mesh_api_rev)
    print("Mesh_Passphrase:", _mesh_passphrase)
    print("Name           :", _name)
    print("Ordered        :", _ordered)
    print("Orders         :", _orders)
    print("Role           :", _role)
    print("Rooms          :", _rooms)
    print("Scenes         :", _scenes)
    print("Schedules      :", _schedules)
    print("Show wifi setup:", _show_wifi_setup)
    print("Toggle_Scene   :", _toggle_scene_enabled)
    print("TZ             :", _tz)
    print("UUID           :", _uuid)
    print("Bridge Checkin :", _wifi_bridge_checkin)
    print("Bridge SSID    :", _wifi_bridge_ssid)
    print("Bridge state   :", _wifi_bridge_state)
    print("Bridges        :", _wifi_bridges)

#--------------------------------------|
#   #parse_reply_ID()
#--------------------------------------|
# Desc:    Parses a response payload, identifying the mesh_id of the sender
#          <int>     <string>   <variable>
#          <mesh_id> <category> <value>
#          "33045    is_on      True"
# Params:  string arg1 - The query (payload)
# PreCons: GIGO - Assumes correctly formatted input, no error checking is performed
# PosCons: None
# RetVal:  int - The mesh_id from where the reply originated
# MetCall: None
def parse_reply_ID(query):
    index = total_status[0].index("003")
    # print("Index:", index)
    return(index)
    # TODO: Determine actual response format
    # TODO: Write actual parse logic

#--------------------------------------|
#   #parse_reply_category()
#--------------------------------------|
# Desc:    Parses a response payload, identifying the response type
#          <int>     <string>   <variable>
#          <mesh_id> <category> <value>
#          "33045    is_on      True"
# Params:  string arg1 - The query (payload)
# PreCons: GIGO - Assumes correctly formatted input, no error checking is performed
# PosCons: None
# RetVal:  string - The category or type of the reply
# MetCall: None
def parse_reply_category(query):
    return("is_on")
    # TODO: Determine actual response format
    # TODO: Write actual parse logic

#--------------------------------------|
#   #print_profile()
#--------------------------------------|
# Desc:    Parses a response payload, identifying the value
#          <int>     <string>   <variable>
#          <mesh_id> <category> <value>
#          "33045    is_on      True"
# Params:  string arg1 - The query (payload)
# PreCons: GIGO - Assumes correctly formatted input, no error checking is performed
# PosCons: None
# RetVal:  <variable> - The value contained in the response string
# MetCall: None
def parse_reply_value(query):
    return(1) # True
    # TODO: Determine actual response format
    # TODO: Write actual parse logic

#--------------------------------------|
#   #process_reply()
#--------------------------------------|
# Desc:    Used by the controller to update its internal registers (logs) based
#          on arguments received from the mesh.
# Params:  int arg1        - The mesh_id of the responding switch
#          string arg2     - The category of the response
#          <variable> arg3 - The response value
# PreCons: GIGO - Valid arguments are passed, no error checking is performed
# PosCons: Controller registers are updated
# RetVal:  None
# MetCall: None
def process_reply(mesh_id, category, value):
    print('Processing: {} : {} : {}'.format(mesh_id, category, value))
    total_status[1][mesh_id] = value


#---|---|---|---|------------------------------------------------------|------|
#   #Execution
#---|---|---|---|------------------------------------------------------|------|

if __name__ == '__main__':
    virtswitch_controller()
