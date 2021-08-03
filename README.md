# HAtchmota

Getting local, WIFI control of the Soulsens Smart Nursery Light.

So, you've gotten the request to buy a Hatch Rest (Bluetooth) to be a night light and sound machine in a kids room, but you don't feel like spending \$60 on a bluetooth only device that won't work in any of your other home automation systems? Would you spend $30 on something you can make truly local? Enter the Soulsens Smart Nursery Light (https://amzn.to/3y3wgHb <-- digiblurdiy affiliate link). In the good ole days, we could be pretty confident that this device is running on an ESP chip we could flash with custom firmware. But, it's not the good ole days anymore. Enter the transplant.

## FCC Investigation

Using the FCC ID on the device brings you here: https://fccid.io/2AXDK-HP110B. That FCC application is just for a rebrand of a Meross night light (https://www.amazon.com/dp/B084WVW5CG/ $55, no thanks). Tracking to the Meross night light FCC ID, we find https://fccid.io/2AWCB-KT-W01A. They physical buttons on the 2 FCCIDs are a bit different. The Meross night light shows a Mediatek chip that's pin compatible with the ESP-12F. The Soulsens device that I received had a WB3S.

## Pre Transplant WB3S Sniffing

Opening up the night light (very easy, just some screws under the rubber feet pads), I got out the multimeter and checked the GPIO pins confirming the only active pins were TX and RX for Tuya serial communication. 

Before going through the trouble of transplanting the WB3S for an ESP-12F, I wanted to make sure I had all the possible actions the original Tuya/Smart Life app could send through the WB3S to the secondary Tuya MCU present on the board. To do this, I soldered on leads for TX, RX, GND, and 3V3 and powered the board with a USB UART (CP2102). Wanting to hear what the WB3S module was sending the MCU, I wired the TX on the WB3S to the RX on my UART. If I wanted to sniff on the MCU, I could do the RX on the WB3S to the RX on my UART. The `Tuya_Serial_Decode.py` script is the result of my sniffing out the WIFI module Tuya serial packets (see https://developer.tuya.com/en/docs/iot/tuya-cloud-universal-serial-port-access-protocol?id=K9hhi0xxtn9cb).

### DPIDs

If you are familiar with Tuya MCU controlled devices, you know that there are some pretty common DPIDs that conrol the operation. The Tasmota wiki has a good list of fairly common DPID usage (https://tasmota.github.io/docs/TuyaMCU/#dpid-function-tables). This device uses none of those which means we'll need to form Status Data Units and Send Commands ourselves to send from Home Assistant through Tasmota to the Tuya MCU. 

Here's a summary of the DPIDs I sniffed out:
```
 20  1 bool Device On/Off
101 32  raw Alarm Settings
102 17  raw Start/Stop Sleep with Full Settings
103 11  raw Light Settings
104  4  raw Sound Settings
105  1 enum Time Format
106  2  raw Manual Time Set
107  1 bool Auto or Manual Time
108 32  raw Preview Alarm Full Alarm Settings
109  1  raw Which Alarm to Preview
110  1  raw Sound Cycle 0 = <-, 1 ->
111  2  raw Sleep Time Setting
112  3  raw Sleep Sound Settings
113 11  raw Sleep Lights Settings
```
Check the Python script for the exact breakdown of the bits of each of these DPIDs

## The Transplant

Transplanting a WB3S to a 12F is straight forward (https://www.digiblur.com/2020/12/treatlife-dual-indoor-dimmable-smart.html) with the exception that the ESP-12F GPIO15 must be pulled low. The D1 mini does this with a 12K resistor, and the AI thinker documentation suggests using a 10K resistor, but if you don't intend to use the pin, you can simply bridge the connection between GND and GPIO15. I soldered on a 10K SMD resistor straight to the ESP-12F prior to transplanting because this device is just begging for a 3D printed base with sensors in the bottom of it.

PRIOR to the transplant, I flashed the ESP-12F with Tasmota and set the module to TuyaMCU (Module 54).

## DPIDs in Tasmota

Tasmota deals with a LOT of the communication between the ESP and MCU automatically. Heartbeats, local time, WIFI status, etc. It also requests the status of the product from the MCU and receives a push of all the DPIDs the MCU feels like reporting on boot (see below). The very first thing to notice are the "missing" DPIDs from the list we sniffed earlier.

```
16:08:56.308 {"TuyaReceived":{"Data":"55AA03070005140100010125","Cmnd":7,"CmndData":"1401000101","DpType1Id20":1,"20":{"DpId":20,"DpIdType":1,"DpIdData":"01"}}}
16:08:56.309 TYA: fnId=0 is set for dpId=20
16:08:56.353 {"TuyaReceived":{"Data":"55AA03070024650000200104A06441110F1400003C6469080F0A000000647F080F0A000000647F080F0A62","Cmnd":7,"CmndData":"650000200104A06441110F1400003C6469080F0A000000647F080F0A000000647F080F0A","DpType0Id101":"0x0104A06441110F1400003C6469080F0A000000647F080F0A000000647F080F0A","101":{"DpId":101,"DpIdType":0,"DpIdData":"0104A06441110F1400003C6469080F0A000000647F080F0A000000647F080F0A"}}}
16:08:56.355 TYA: fnId=0 is set for dpId=101
16:08:56.382 {"TuyaReceived":{"Data":"55AA0307001566000011B4000001010301001400010A004B000A03C6","Cmnd":7,"CmndData":"66000011B4000001010301001400010A004B000A03","DpType0Id102":"0xB4000001010301001400010A004B000A03","102":{"DpId":102,"DpIdType":0,"DpIdData":"B4000001010301001400010A004B000A03"}}}
16:08:56.384 TYA: fnId=0 is set for dpId=102
16:08:57.041 {"TuyaReceived":{"Data":"55AA0307000F6700000B01000664010200F0000801F1","Cmnd":7,"CmndData":"6700000B01000664010200F0000801","DpType0Id103":"0x01000664010200F0000801","103":{"DpId":103,"DpIdType":0,"DpIdData":"01000664010200F0000801"}}}
16:08:57.044 TYA: fnId=0 is set for dpId=103
16:08:57.018 {"TuyaReceived":{"Data":"55AA0307000868000004000D060090","Cmnd":7,"CmndData":"68000004000D0600","DpType0Id104":"0x000D0600","104":{"DpId":104,"DpIdType":0,"DpIdData":"000D0600"}}}
16:08:57.021 TYA: fnId=0 is set for dpId=104
16:08:57.066 {"TuyaReceived":{"Data":"55AA0307000569040001017D","Cmnd":7,"CmndData":"6904000101","DpType4Id105":1,"105":{"DpId":105,"DpIdType":4,"DpIdData":"01"}}}
16:08:57.068 TYA: fnId=0 is set for dpId=105
16:08:57.053 {"TuyaReceived":{"Data":"55AA030700056B010001017C","Cmnd":7,"CmndData":"6B01000101","DpType1Id107":1,"107":{"DpId":107,"DpIdType":1,"DpIdData":"01"}}}
16:08:57.056 TYA: fnId=0 is set for dpId=107
16:08:57.003 {"TuyaReceived":{"Data":"55AA030700066F000002B40034","Cmnd":7,"CmndData":"6F000002B400","DpType0Id111":"0xB400","111":{"DpId":111,"DpIdType":0,"DpIdData":"B400"}}}
16:08:57.005 TYA: fnId=0 is set for dpId=111
16:08:56.419 {"TuyaReceived":{"Data":"55AA030700077000000301010388","Cmnd":7,"CmndData":"70000003010103","DpType0Id112":"0x010103","112":{"DpId":112,"DpIdType":0,"DpIdData":"010103"}}}
16:08:56.421 TYA: fnId=0 is set for dpId=112
16:08:56.404 {"TuyaReceived":{"Data":"55AA0307000F7100000B01001400010A004B000A030C","Cmnd":7,"CmndData":"7100000B01001400010A004B000A03","DpType0Id113":"0x01001400010A004B000A03","113":{"DpId":113,"DpIdType":0,"DpIdData":"01001400010A004B000A03"}}}
16:08:56.406 TYA: fnId=0 is set for dpId=113
```
The missing DPIDs seem to be commands that the ESP sends that are solely commands but don't really result in stored data on the MCU side. So, the MCU doesn't volunteer up the info.

The DPIDs we care about moving forward are:
```
101 32  raw Alarm Settings
102 17  raw Start/Stop Sleep with Full Settings
103 11  raw Light Settings
104  4  raw Sound Settings
110  1  raw Sound Cycle 0 = <-, 1 ->
111  2  raw Sleep Time Setting
112  3  raw Sleep Sound Settings
113 11  raw Sleep Lights Settings
```
with these, we have complete control over the device.

## Tasmota Config

Currently, I've configured Tasmota with the following commands

```Module 54``` in Console

To get the ESP in TuyaMCU mode.

```GPIO02 -> LEDLink_i``` on the Configure Module Screen.

Because, why not?

```TuyaMCU 99,1``` in Console

TuyaMCU module assume DPID=1 is a switch. This command tells TuyaMCU to ignore DPID=1.

```SetOption66 1``` in Console

This gets us MQTT publishes on TuyaReceived.

```Backlog TimeStd 0,1,11,1,2,-300; TimeDst 0,2,3,1,2,-240; timezone 99``` in Console

This sets the time zone to US Eastern Time.

```
Rule1
  On TuyaReceived#103#DpIdData do publish2 soulsens/light %value% endon
  On TuyaReceived#104#DpIdData do publish2 soulsens/sound %value% endon
  On TuyaReceived#102#DpIdData do publish2 soulsens/sleep %value% endon
  On TuyaReceived#111#DpIdData do publish2 soulsens/sleep_time %value% endon
  On TuyaReceived#112#DpIdData do publish2 soulsens/sleep_sound %value% endon
  On TuyaReceived#113#DpIdData do publish2 soulsens/sleep_light %value% endon
  ```
then
`Rule1 1`

These rules republish the DpIdData to retained messages. This is not required, as we can setup MQTT Sensors in Home Assistant that can receive the publishes sent because of `SetOption66 1` but those publishes don't occur until the device restarts or changes. Check, the HA packages for the MQTT sensor using the republished MQTT vs the Tasmota MQTT (commented out or for currently unused DPIDs).

## Operation:
- On the Tasmota side, we set up some rules to publish the TuyaReceived for the various commands we'll use so we have them named and retained.
- In HA, we make MQTT sensors to get the raw dpid data for the various dpids we'll need (right now just 103=light and 104=sound)
- We use a script to send SerialSend5 commands to our device, but rather than having to compute the header and checksum in each MQTT publish command, the script does this for us.
## Home Assitant Status:
- Got Light Modes working (White, Color Effects).
  - Three different template lights.
- Built HA script to send DPID data.
- Got Sound Mode working as a template light.
- Got Sleep Mode working.
  - Three template lights for light. One template light for sound. Input number for time. Template swtich for on/off.

## Next Plans:
- Update the Sleep Mode full dpid on any change of the sub DPIDs
- Try out sound settings as a Universal Media Player.
- Implement the Sound Mode timer (different than Sleep Mode).
- Implement the 4 x Alarms.

## Notes:
- Sleep mode from the ESP locks out ALL physical buttons.
- Sleep mode form physical button locks out all physical buttons EXCEPT sleep button.
- Sleep mode from physical button does not lock out ESP control.

## Wishes from Other Packages:
- A `TuyaSend<x>` in Tasmota that sent the `raw` data type.
- Tasmota Support for Data from/to substring of Tuya packets.