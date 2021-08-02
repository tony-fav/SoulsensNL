# SoulsensNL
Soulsens Night Light + Sound Machine Project

FCC ID on device brings you here: https://fccid.io/2AXDK-HP110B
Which in turn brings you here: https://fccid.io/2AWCB-KT-W01A
The physical buttons between the 2 FCCIDs are a bit different. The original one (Meross) shows a meross/mediatek chip that's pin equivalent to ESP12F. The device I received (Soulsens) had a WB3S. Only active pins though are TX and RX for Tuya serial communication. 

## Operation:
- On the Tasmota side, we set up some rules to publish the TuyaReceived for the various commands we'll use so we have them named and retained.
- In HA, we make MQTT sensors to get the raw dpid data for the various dpids we'll need (right now just 103=light and 104=sound)
- We use a script to send SerialSend5 commands to our device, but rather than having to compute the header and checksum in each MQTT publish command, the script does this for us.
## Status:
- Sniffed Tuya packets from WIFI Module to Tuya MCU for every button press in Tuya App (Didn't use Smart Life. Hopefully, it didn't have different functionality). See python script for how I did the sniffing and the results.
- Flashed Tasmota 9.5.0 on ESP12F with Module 54
- Transplanted WB3S for ESP12F (fairly proud of the soldering job and SMD resistor on the 12F board)
- Got each light mode (white, color, effects) working as 3 different template light entities. They properly behave mutually exclusively. See yaml, HA package files.
- Made an HA script to use as a service that behaves like a `TuyaSend<x>` command. Inputs: topic, dpid, dptype, dpdata.
- Removed excessive template sensors.

## Next Plans:
- Try to do the sound settings as a Media Player
- Implement the sound screens sleep timer.

## Things that would make things easier:
- A `TuyaSend<x>` in Tasmota that sent the `raw` data type.