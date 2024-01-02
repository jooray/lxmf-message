# lxmf-message

Send LXMF message from command-line

## Purpose

This script is used to send LXMF message from command-line. I use it
from my project [signal-monitoring](https://github.com/jooray/signal-monitoring) as
another replacement for Signal (which started requiring CAPTCHA).

LXMF is based on Reticulum and should find a way. So for example it should be able
to send a monitoring message through LoRA and route it to me if my home connection
is down.

## Installation

You need to [install and configure Reticulum](https://reticulum.network/start.html) first.
When you first run this script, it will create an identity and save it to ~/.lxmf-notifybot/identity.
It will also print the hash of the identity (address) on stdout when creating. I recommend
adding this identity in Sideband as trusted, otherwise you will not get notifications.

## Usage

```bash
echo 'The internet went down' | python LXMF-NotifyBot.py <recipient-address> [<short-name>] [<propagation-node>]
```

The program accepts the message to be sent on stdin.

There are three parameters, the first is the recipient address, the second is the short name
of the script used in the announce message (it will display also in the first message if you
don't add the identity manually). The third optional parameter is a propagation node. If this
parameter is not present, propagation node will not be used. Note, that propagation node is
not very useful for my use-case, since I prefer immediate messages, but if you suspect "something's
up", you might want to sync with propagation node to see if you have missed any messages.

Consideration for running: I recommend running rnsd out of this process, otherwise it would start
and stop all the time. Also, in process rnsd can get stuck. Just run rnsd in background.

## Learning and credits

This is a simple script to send a LXMF message, so you might want to use it as a fairly minimal
example to send LXMF message. Note, that this is not a complete example, since it is not receive
any messages except for delivery receipts.

This script is based on [Michael Faragher's EchoBot example](https://github.com/faragher/ReticulumExamples/blob/main/EchoBot.py).
Credits to amazing [markqvist](https://github.com/markqvist/) for creating [Reticulum](https://github.com/markqvist/Reticulum).
