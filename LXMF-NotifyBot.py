#! /usr/bin/python3
import RNS
import os
import time
import LXMF
import sys

destination = sys.argv[1]
namestring = "LXMF-Monitoring"
if (len(sys.argv) > 2):
  namestring = sys.argv[2]

propagation_node = None
if (len(sys.argv) > 3):
  propagation_node = sys.argv[3]

# Read possibly multiline message from stdin to a string variable message
message = "".join(sys.stdin.readlines())

global_timeout = 600

# Name in bytes for transmission purposes
namebytes = bytes(namestring,"utf-8")

# Initialize Reticulum
reticulum = RNS.Reticulum()

userdir = os.path.expanduser("~")
configdir = userdir+"/.lxmf-notifybot"

if not os.path.isdir(configdir):
  os.makedirs(configdir)

identitypath = configdir+"/identity"
if os.path.exists(identitypath):
  ID = RNS.Identity.from_file(identitypath)
else:
  ID = RNS.Identity()
  ID.to_file(identitypath)
  print("Created new identity:")
  print(RNS.prettyhexrep(ID.hash))

lxm_router = LXMF.LXMRouter(identity = ID, storagepath = configdir)
local_lxmf_destination = lxm_router.register_delivery_identity(ID,display_name=namestring)
local_lxmf_destination.announce()

# Convert string to bytes below if you pass as a string
destination_bytes = bytes.fromhex(destination)

# Check to see if RNS knows the identity
destination_identity = RNS.Identity.recall(destination_bytes)

# If it doesn't know the identity:
if destination_identity == None:
    basetime = time.time()
    # Request it
    RNS.Transport.request_path(destination_bytes)
    # And wait until it arrives; timeout in 300s
    print("Don't have identity for " + destination + ", waiting for it to arrive for 300s")
    while destinantion_identity == None and (time.time() - basetime) < 300:
        destinantion_identity = RNS.Identity.recall(destination_bytes)
        time.sleep(1)
if destination_identity == None:
    print("Error: Cannot recall identity")
    sys.exit(1)

lxmf_destination = RNS.Destination(
    destination_identity,
    RNS.Destination.OUT,
    RNS.Destination.SINGLE,
    "lxmf",
    "delivery"
    )

# Create the lxm object
lxm = LXMF.LXMessage(
    lxmf_destination,
    local_lxmf_destination,
    message,
    desired_method=LXMF.LXMessage.DIRECT
    )

message_delivery_finished = False
message_propagated = False

def change_delivery_status(lxm):
  global message_delivery_finished
  message_delivery_finished = True

def change_propagated_status(lxm):
  global message_propagated
  change_delivery_status(lxm)
  message_propagated = True

def try_propagation(lxm):
   propagated_lxm = LXMF.LXMessage(
    lxmf_destination,
    local_lxmf_destination,
    message,
    desired_method=LXMF.LXMessage.PROPAGATED
    )
   propagated_lxm.register_delivery_callback(change_propagated_status)
   propagated_lxm.register_failed_callback(change_delivery_status)
   print("Direct delivery failed, sending the message through the configured propagation node")
   lxm_router.handle_outbound(propagated_lxm)


lxm.register_delivery_callback(change_delivery_status)

if (propagation_node != None):
   lxm_router.set_outbound_propagation_node(bytes.fromhex(propagation_node))
   lxm.register_failed_callback(try_propagation)
else:
   lxm.register_failed_callback(change_delivery_status)

# Send the message through the router
lxm_router.handle_outbound(lxm)

# Main Loop Definition
def MainLoop():
  delivery_started = time.time()
  while not message_delivery_finished:
    if time.time() > (delivery_started + global_timeout):
       print("Global timeout reached")
       sys.exit(2)
    time.sleep(1)
  if (lxm.state == LXMF.LXMessage.DELIVERED):
     # This does not look smart, but if the rns was started within this process, it can
     # be stuck, but we really want to quit. This should not happen if you run rnsd
     # outside of this process, which is preferred way in this case.
     sys.exit(0)
  else:
     if (message_propagated):
        print("Warning: Message sent to propagation node, not delivered.")
     else:
        print("Error: Message not delivered")
        sys.exit(1)

# Execute progam
MainLoop()
