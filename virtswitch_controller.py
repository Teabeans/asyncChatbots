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

# For deep copy of dictionaries
# https://docs.python.org/2/library/copy.html
import copy

# For site querying
# http://docs.python-requests.org/en/master/
import requests

# For JSON file parsing
# https://docs.python.org/3/library/json.html#module-json
import json

# For randomized switch behavior
# https://docs.python.org/3/library/random.html
import random



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

# Global verbosity, false by default. Changed by virtswitch_controller
VERBOSE = False

# The maximum number of switches in a mesh
MAX_SWITCHES = 512

# The virtual mesh
the_mesh     = {}
# A mirror of the virtual mesh that holds final statuses
total_status = {}

control = mqtt.Client('000_Controller')
command_file = open('commands.txt', 'r')

#--------------------------------------|
#   Actual fields
#--------------------------------------|
_address              = None
_backplates           = {}
_channel              = ""
_faceplates           = {}
_floors               = {}
_groups               = {}
_icon                 = ""
_load_count           = 0
_loads                = {}
_mesh_api_rev         = 0
_mesh_passphrase      = ""
_name                 = ""
_ordered              = False
_orders               = {}
_role                 = ""
_rooms                = {}
_scenes               = {}
_schedules            = {}
_show_wifi_setup      = False
# Replaced by the_mesh{}
# _switches             = {}
_toggle_scene_enabled = False
_tz                   = ""
_uuid                 = ""
_wifi_bridge_checkin  = None
_wifi_bridge_ssid     = None
_wifi_bridge_state    = ""
_wifi_bridges         = {}



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
    _dimmage        = 0
    _room           = ''
    _group          = ''
    _client         = None
    message_ID      = ''
    message_command = ''
    opt_verbose     = False

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
#   #switch_unpack()
#--------------------------------------|
# Desc:    NULL
# Params:  NULL
# PreCons: NULL
# PosCons: NULL
# RetVal:  NULL
# MetCall: NULL
    def switch_unpack(self, client, userdata, message):
#        if (self.opt_verbose): print("({}) Message received: '{}'".format(self._mesh_id, str(message.payload.decode("utf-8"))))
        # if (self.opt_verbose): print("Message topic      :", message.topic)
        # if (self.opt_verbose): print("Message qos        :", message.qos)
        # if (self.opt_verbose): print("Message retain flag:", message.retain)

        # Decode the payload to a string
        decoded_payload = str(message.payload.decode("utf-8"))
        # Separate the ID from the decoded payload
        query_ID = self.parse_ID(decoded_payload)

        # Determine if a response is required
        if (query_ID == self._mesh_id or query_ID == 99999):
            # Slight pause to improve readability of debugging
            if (self.opt_verbose): time.sleep(1)
            if (self.opt_verbose): print("  ({} : {}) I should respond!".format(self._mesh_id, query_ID))
            # Separate the ID from the decoded payload
            query_command = self.parse_command(decoded_payload)
            query_cmd_val = self.parse_cmd_val(decoded_payload)
            # Respond
            self.respond(query_command, query_cmd_val)
        # else, do nothing

#--------------------------------------|
#   #switch_terminate()
#--------------------------------------|
# Desc:    Termination behavior for a switch MQTT client
# Params:  NULL
# PreCons: NULL
# PosCons: NULL
# RetVal:  NULL
# MetCall: NULL
    def switch_terminate(self, client, userdata, message):
        if (self.opt_verbose): print("({}) Termination callback, disconnected".format(self._mesh_id))

#--------------------------------------|
#   #parse_ID()
#--------------------------------------|
# Desc:    Parses a received message and returns the ID component of that message
# Params:  arg1 switch - This switch object
#          arg2 string - The decoded payload query
# PreCons: GIGO - Query is assumed to be formatted correctly, no error checking is performed
#          '<MeshID> <Command> <Value>'
# PosCons: NULL
# RetVal:  String - The command component of the received message
# MetCall: NULL
    def parse_ID(self, query):
        # Split the string by whitespace and take the first index position (0)
        retString = query.split(' ')[0]
        # Verbose print the result
        # if (self.opt_verbose): print("({}) parse_ID(query):".format(self._mesh_id), retString)
        return(int(retString))
    
#--------------------------------------|
#   #parse_command()
#--------------------------------------|
# Desc:    Parses a received message and returns the command component of that message
# Params:  arg1 switch - This switch object
#          arg2 string - The decoded payload query
# PreCons: GIGO - Query is assumed to be formatted correctly, no error checking is performed
#          '<MeshID> <Command> <Value>'
# PosCons: NULL
# RetVal:  String - The command component of the received message
# MetCall: NULL
    def parse_command(self, query):
        # Split the string by whitespace and take the second index position (1)
        retString = query.split(' ')[1]
        # Verbose print the result
        # if (self.opt_verbose): print("({}) parse_command(query):".format(self._mesh_id), retString)
        return(retString)

#--------------------------------------|
#   #parse_cmd_val()
#--------------------------------------|
# Desc:    Parses a received message and returns the command value component of that message
# Params:  arg1 switch - This switch object
#          arg2 string - The decoded payload query
# PreCons: GIGO - Query is assumed to be formatted correctly, no error checking is performed
#          '<MeshID> <Command> <Value>'
# PosCons: NULL
# RetVal:  String - The command value component of the received message
# MetCall: NULL
    def parse_cmd_val(self, query):
        # Split the string by whitespace and take the third index position (2)
        retString = query.split(' ')[2]
        # Verbose print the result
        # if (self.opt_verbose): print("({}) parse_cmd_val(query):".format(self._mesh_id), retString)
        return(retString)

#--------------------------------------|
#   #respond()
#--------------------------------------|
# Desc:    Switch response behavior for all query cases
# Params:  NULL
# PreCons: NULL
# PosCons: A PROPERLY FORMATTED string response to the query has been published
#          GIGO - No response is issued for bad queries
# RetVal:  None
# MetCall: NULL
    # Response behavior
    def respond(self, message, value):
        isQuery = False
        pubstring = '--NULL-- --NULL-- --NULL--'

        # All possible QUERIES a switch can receive go here

        if (message == "is_on"):
            isQuery = True
            pubstring = "{} {} {}".format(self._mesh_id, message, self._is_on)

        elif (message == "dimmage"):
            isQuery = True
            pubstring = "{} {} {}".format(self._mesh_id, message, self._dimmage)

        # End possible QUERIES

        # All possible COMMANDS a switch can receive go here

        elif (message == 'set_dimmage'):
            if (VERBOSE): print("({}) Executing command: '{}'".format(self._mesh_id, message))
            self._dimmage = value

        elif (message == 'set_on'):
            if (VERBOSE): print("({}) Executing command: '{}'".format(self._mesh_id, message))
            if (value == "!"):
                self._is_on = not self._is_on
            else:
                self._is_on = value


        # End possible COMMANDS




        # All possible queries handled, pubstring reflects this switch's response
        if (isQuery):
            if (self.opt_verbose): print("    ({}) Responding to query... '{}'".format(self._mesh_id, pubstring))
            self._client.publish(TOPIC_REPLY, pubstring)

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
        if (random.randint(0,100) < 50):
            self._is_on             = False
        self._room                  = ''
        self._group                 = ''
        self._client                = None
        self.message_ID             = ''
        self.message_command        = ''
        self.opt_verbose            = VERBOSE
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
        self._client.on_disconnect = self.switch_terminate
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
    print("  (CTRL) Message received: '{}'".format(payload))
    ID       = parse_reply_ID(payload)
    category = parse_reply_category(payload)
    value    = parse_reply_value(payload)
    process_reply(ID, category, value)

#--------------------------------------|
#   #control_terminate()
#--------------------------------------|
# Desc:    Termination behavior for the controller MQTT client
# Params:  NULL
# PreCons: NULL
# PosCons: NULL
# RetVal:  NULL
# MetCall: NULL
def control_terminate(client, userdata, message):
    if (VERBOSE): print("(CTRL) Termination callback, disconnected")



#---|---|---|---|------------------------------------------------------|------|
#
#   START EXECUTION
#
#---|---|---|---|------------------------------------------------------|------|

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
@click.option('--run', default = "commands.txt", help = "The command file to run (default 'commands.txt')")
@click.option('--broker_addy', default = "127.0.0.1", help = "The MQTT broker address (default '127.0.0.1'")
@click.option('-v', '--verbose', is_flag = True, help = 'Enables verbose mode')
@click.argument('mesh_file')
def virtswitch_controller(mesh_file, broker_addy, verbose, run):

    #--------------------------------------|
    #   Verbose Mode Setup
    #--------------------------------------|
    # TODO: Change the verbosity to a configuration instance that informs all other things in the program
    # Rather than a variable used throughout.
    # See 'Singleton pattern'

    global the_mesh
    global total_status
    # Verbosity of the switches (and other classes in the future)
    global VERBOSE
    # Global verbosity gets the local verbosity argument (TODO: Clean this up)
    VERBOSE = verbose

    # Verbosity of the controller
    if(verbose):
        def verboseprint(*args):
        # Print each argument separately so caller doesn't need to
        # stuff everything to be printed into a single string
            for arg in args:
                print(arg)
    else:   
        verboseprint = lambda *a: None      # do-nothing function



    #--------------------------------------|
    #   File Setup
    #--------------------------------------|

    if (verbose):
        print("Verify arg vector: broker_addy   :", broker_addy)
        print("Verify arg vector: mesh_file     :", mesh_file)
        print("Verify arg vector: command_file  :", run)
        print()

    # If the file directed to is different than the default...
    if (run != 'commands.txt'):
        # Close the current file
        command_file.close()
        # And reopen a different one
        command_file.open(run, 'r')

    # Check the file input
    command_strings = command_file.readlines()
    if (verbose):
        print("Command File Contents:", command_file)
        for line in command_strings:
            print(line, end='')
        print()


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
    if (verbose):
        print()
        print("JSON Profile ( 'response.json()' ):")
        print(type(a_profile))
        for i in a_profile:
            print(i)
            print(".")

        print()
        print("Switch Profiles ( 'response.json()['switches']' ):")
        print(type(switch_profiles))
        for i in switch_profiles:
            print(i)
            print(".")

        print()
        print("First Switch Profile ( 'response.json()['switches'][0]' ):")
        print(type(a_switch))
        for i in a_switch:
            print("-", i)

        print()
        print("First Switch fields ( 'response.json()['switches'][0]['<field>']' ):")
        for i in a_switch:
            print("- {0:<21}: ".format(i), end = '')
            print(a_switch[i], ' ', end = '')
            print(type(a_switch[i]))
        
        print()
    # --- FOR TESTING PURPOSES ONLY --- END ---

    #--------------------------------------|
    #   Mesh Generation Setup
    #--------------------------------------|

    # Generate a bank of switches
    # For every switch in the profile...
    vID = 0 # Only used to assign MQTT broker IDs
    shadow_vID = vID + MAX_SWITCHES

    for a_profile in switch_profiles:
        # By dictionary
        shadow_client = mqtt.Client(str(shadow_vID))
        # Generate a shadow switch with the same settings and append to status mesh
        shadow_switch = switch(shadow_client, broker_addy, a_profile)
        # Immediately disconnect the status switch
        shadow_switch._client.disconnect()
        if (VERBOSE): print("({}) Status-bank (shadow switch) disconnecting...".format(shadow_switch._mesh_id))

        # Make a new switch and append it to the the_mesh
        new_client = mqtt.Client(str(vID))

        # Generate and append a switch to the virt mesh
        mesh_switch = switch(new_client, broker_addy, a_profile)
        the_mesh[str(mesh_switch._mesh_id)] = mesh_switch
        
        #                                         KEY : VALUE
        # total_status.append( shadow_switch._mesh_id : shadow_switch )
        #            KEY                     = VALUE
        total_status[str(shadow_switch._mesh_id)] = shadow_switch
        # ASSUMES NO REPEAT MESH IDS, OTHERWISE WE'LL LOST VALUES

        # Increment the vID numbers
        vID += 1
        shadow_vID += 1



    #--------------------------------------|
    #   Status Tracking Setup
    #--------------------------------------|

    # Collate all statuses together by...
    # Generating a status-tracking duplicate of the_mesh
    verboseprint("Status Mesh (shadow mesh) status:")
    if (verbose):
        for status_switch in total_status:
            print (status_switch)
    verboseprint("")



    #--------------------------------------|
    #   Controller MQTT Client Setup
    #--------------------------------------|

    verboseprint("Controller (CTRL) MQTT client setting up...")
    verboseprint("")

    # Create a control client
    control.on_message = control_unpack       # Attach on-message behavior to callback
    control.on_disconnect = control_terminate # Attach on-terminate behavior to callback

    # Connect to broker
    control.connect(broker_addy)

    # ???
    control.loop_start() #start the loop

    # Subscribe to topic channel
    control.subscribe(TOPIC_REPLY)



    #--------------------------------------|
    #   Mesh Summary Operations
    #--------------------------------------|

    # Execute the command file
    execute(command_strings)

    time.sleep(5) # wait

    # Check status of switch '003' is_on again
#    print()
#    print("003 is_on: {}".format(total_status[1][2]))
#    print()

    # Closes all connections and frees all resources before closure
    obliviate()

    time.sleep(1)
    control.loop_stop() #stop the loop

    print()
    print("Goodbye, World!")
    print()

#--------------------------------------|
#   End #virtswitch_controller()
#--------------------------------------|

#---|---|---|---|------------------------------------------------------|------|
#
#   END EXECUTION
#
#---|---|---|---|------------------------------------------------------|------|

#--------------------------------------|
#   #execute()
#--------------------------------------|
# Desc:    Parses and executes the command file
# Params:  None
# PreCons: GIGO - Assumes correct command formatting, no error checking is performed
# PosCons: All commands have been executed
# RetVal:  None
# MetCall: None
def execute(command_array):
    global total_status
    if (VERBOSE):
        print("Executing Command File:", command_file)
        for line in command_array:
            print(line, end='')
        print()
    tgt = 0
    cmd = ''
    val = ''
    if (VERBOSE): print()
    for line in command_array:
        tgt = line.split(' ')[0]
        cmd = line.split(' ')[1]
        val = line.split(' ')[2]
        if (VERBOSE): print("(CTRL) EXECUTING COMMAND --- '{} : {} : {}'".format(tgt, cmd, val))

        # All possible commands go in here
        # '0 report is_on'
        if (cmd == 'report'):
            if (val == 'is_on'):
                print("(CTRL) Reporting: 'is_on'")
                for i in total_status:
                    print("  ({}) is_on == ({})".format(total_status[i]._mesh_id, total_status[i]._is_on))

        elif (cmd == 'build'):
            print("(CTRL) Build command detected. TODO: Write this")
            #TODO: actually build the virt mesh
        elif (cmd == 'is_on'):
            control.publish(TOPIC_QUERY, "{} {} {}".format(tgt, cmd, val)) #val is not used but must be sent

        elif (cmd == 'dimmage'):
            control.publish(TOPIC_QUERY, "{} {} {}".format(tgt, cmd, val))

        elif (cmd == 'set_dimmage'):
            control.publish(TOPIC_QUERY, "{} {} {}".format(tgt, cmd, val))

        elif (cmd == 'set_on'):
            control.publish(TOPIC_QUERY, "{} {} {}".format(tgt, cmd, val))

#        elif (cmd == ''):
#            control.publish(TOPIC_QUERY, "{} {} {}".format(tgt)

#        elif (cmd == ''):
#            control.publish(TOPIC_QUERY, "{} {} {}".format(tgt)

#        elif (cmd == ''):
#            control.publish(TOPIC_QUERY, "{} {} {}".format(tgt)

        # End possible commands

        if (VERBOSE): input()
        print()
        print()

#--------------------------------------|
#   #obliviate()
#--------------------------------------|
# Desc:    Deallocates all resources and closes all connections
# Params:  None
# PreCons: None
# PosCons: All connections have been closed and resources deallocated
# RetVal:  None
# MetCall: None
def obliviate():
    global total_status
    # Disconnect all MQTT switch clients
    for i in the_mesh:
        if (VERBOSE): print("({}) Disconnecting...".format(total_status[i]._mesh_id))
        total_status[i]._client.disconnect()
    # Disconnect the controller MQTT client
    if (VERBOSE): print("(CTRL) Closing control MQTT client...")
    control.disconnect()

    # Close the command file
    if (VERBOSE): print("(CTRL) Closing command file...")
    command_file.close()

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
# Desc:    (CTRL) Parses a response payload, identifying the mesh_id of the sender
#          <int>     <string>   <variable>
#          <mesh_id> <category> <value>
#          "33045    is_on      True"
# Params:  string arg1 - The query (payload)
# PreCons: GIGO - Assumes correctly formatted input, no error checking is performed
# PosCons: None
# RetVal:  int - The mesh_id from where the reply originated
# MetCall: None
def parse_reply_ID(response):
    # Split the string by whitespace and take the first index position (0)
    response_ID = response.split(' ')[0]
    return(response_ID)

#--------------------------------------|
#   #parse_reply_category()
#--------------------------------------|
# Desc:    (CTRL) Parses a response payload, identifying the response type
#          <int>     <string>   <variable>
#          <mesh_id> <category> <value>
#          "33045    is_on      True"
# Params:  string arg1 - The query (payload)
# PreCons: GIGO - Assumes correctly formatted input, no error checking is performed
# PosCons: None
# RetVal:  string - The category or type of the reply
# MetCall: None
def parse_reply_category(response):
    # Split the string by whitespace and take the second index position (1)
    response_category = response.split(' ')[1]
    return(response_category)

#--------------------------------------|
#   #parse_reply_value()
#--------------------------------------|
# Desc:    (CTRL) Parses a response payload, identifying the value
#          <int>     <string>   <variable>
#          <mesh_id> <category> <value>
#          "33045 is_on True"
# Params:  string arg1 - The query (decoded payload)
# PreCons: GIGO - Assumes correctly formatted input, no error checking is performed
# PosCons: The response has been captured as an int, string, and bool, as applicable
# RetVal:  dictionary - Wrapper for the value contained in the response string. In format:
#                       [int:val, string:val, bool:val]
# MetCall: None
def parse_reply_value(query):
    # Split the string by whitespace and take the third index position (2)
    value = query.split(' ')[2]

    # Declare the return dictionary
    retDict = {}

    # Set the string representation of the command value
    retDict['string'] = value

    # Set the int representation of the command value
    retDict['int']    = 0
    # In the case of a boolean 'True'
    if (value == 'True' or value == 'true'):
        retDict['int'] = 1
    else:
        try:
            retDict['int'] = int(value)
        except ValueError:
            if(value == 'False'):
                retDict['int'] = 0
            elif(value == 'True'):
                retDict['int'] = 1
            elif(VERBOSE): print("Value is not an int: {}".format(value))

    # Set the bool representation of the command value
    retDict['bool']   = False
    if (value == 'True' or value == 'true' or value == '1' ):
        retDict['bool'] = True

    # Return the encapsulated responses
    # In format: { string:'value' , int:# , bool:True/False }
    return(retDict)

#--------------------------------------|
#   #process_reply()
#--------------------------------------|
# Desc:    (CTRL) Updates status mesh based on messages from the Broker.
# Params:  int arg1        - The mesh_id of the responding switch
#          string arg2     - The category of the response
#          <variable> arg3 - The response value
# PreCons: GIGO - Valid arguments are passed, no error checking is performed
# PosCons: Controller registers are updated
# RetVal:  None
# MetCall: None
def process_reply(mesh_id, category, value):
    global total_status

    # if(VERBOSE): print('  (CTRL) Processing: {} : {} : {}'.format(mesh_id, category, value))
    # TODO: Processing behavior goes here
    # Access the target switch
    # target = total_status['mesh_id'][mesh_id]

    # 'is_on' response behavior
    if (category == 'is_on'):
        # Assign value to the status switch
        total_status[mesh_id]._is_on = value['bool']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_is_on" set to ({})'.format(mesh_id, value['bool']))

    elif (category == 'room'):
        total_status[mesh_id]._room = value['string']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_room" set to ({})'.format(mesh_id, value['string']))

    elif (category == 'group'):
        total_status[mesh_id]._group = value['string']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_group" set to ({})'.format(mesh_id, value['string']))

    elif (category == 'client'):
        total_status[mesh_id]._client = value['string']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_client" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'backplate_slot'):
        total_status[mesh_id]._backplate_slot = value['int']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_backplate_slot" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'device_type'):
        total_status[mesh_id]._device_type = value['string']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_device_type" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'downstream'):
        total_status[mesh_id]._downstream = value['bool']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_downstream" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'enabled'):
        total_status[mesh_id]._enabled = value['bool']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_enabled" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'faceplate_slot'):
        total_status[mesh_id]._faceplate_slot = value['int']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_faceplate_slot" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'firmware_rev'):
        total_status[mesh_id]._firmware_rev = value['string']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_firmware_rev" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'kebab_brightness'):
        total_status[mesh_id]._kebab_brightness = value['bool']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_kebab_brightness" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'keypad'):
        total_status[mesh_id]._keypad = value['bool']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_keypad" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'keypad_timeout'):
        total_status[mesh_id]._keypad_timeout = value['int']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_keypad_timeout" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'last_checkin'):
        total_status[mesh_id]._last_checkin = value['string']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_last_checkin" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'load_id'):
        total_status[mesh_id]._load_id = value['string']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_load_id" set to ({})'.format(mesh_id, value['string']))

    elif (category == 'load_name'):
        total_status[mesh_id]._load_name = value['string']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_load_name" set to ({})'.format(mesh_id, value['string']))

    elif (category == 'location'):
        total_status[mesh_id]._location = value['string']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_location" set to ({})'.format(mesh_id, value['string']))

    elif (category == 'mesh_id'):
        total_status[mesh_id]._mesh_id = value['int']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_mesh_id" set to ({})'.format(mesh_id, value['string']))

    elif (category == 'multiway'):
        total_status[mesh_id]._multiway = value['bool']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_multiway" set to ({})'.format(mesh_id, value['string']))

    elif (category == 'nightlight_brightness'):
        total_status[mesh_id]._nightlight_brightness = value['int']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_nightlight_brightness" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'nightlight_enabled'):
        total_status[mesh_id]._nightlight_enabled = value['bool']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_nightlight_enabled" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'order_id'):
        total_status[mesh_id]._order_id = value['string']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_order_id" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'sn'):
        total_status[mesh_id]._sn = value['string']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_sn" set to ({})'.format(mesh_id, value['string']))        

    elif (category == 'uuid'):
        total_status[mesh_id]._uuid = value['string']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_uuid" set to ({})'.format(mesh_id, value['string']))

    elif (category == 'dimmage'):
        total_status[mesh_id]._dimmage = value['int']
        if(VERBOSE): print('    (CTRL) ({}) accessed. "_dimmage" set to ({})'.format(mesh_id, value['int']))


#---|---|---|---|------------------------------------------------------|------|
#   Execution call
#---|---|---|---|------------------------------------------------------|------|

if __name__ == '__main__':
    virtswitch_controller()