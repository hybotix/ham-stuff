Universal and dedicated bridges to allow GQRX and any other software that requires
  rigctld for rig control. This bridge replaces rigctld and solves a but with
  hamlib rig control. GQRX will work perfectly unmodified with either bridge.

## Credits

Developed by Dale Weber/N7PKT <dalew@n7pkt.org>

Bridge architecture and Python implementation created with assistance from 
Anthropic's Claude AI (October 2025).

Special thanks to:
- FlRig developers for reliable rig control software
- GQRX/GNU Radio community
- Xiegu G90 user community

Allows any rigctld client to talk to FlRig.

Requirements:
    GQRX must have remote control enabled and connect to localhost:4532

    You must have FlRig installed in the standard configuration at localhost:12345

    Run the start-g90-sdr.bash script to start everything in the proper
      order with slight delays to give each program time to start up.

For instance, GQRX will use this to control my G90.

Included software:

flrig-gqrx-bridge.py
  This is a dedicated bridge that works with GQRX only.

start-g90-sdr.bash
  Start-up script to load FlRig, GQRX, and then the dedicated
    bridge.

universal_flrig_bridge.py
  Universal bridge that works with GQRX as well as any software that usually
    requires rigctld for rig control.

                  Copyright (c) 2025 by Dale Weber, N7PKT
