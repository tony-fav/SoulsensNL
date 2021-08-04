import serial
from time import sleep
while 1:
    try:
        ser = serial.Serial("COM3")
        break
    except PermissionError:
        pass
    except Exception as e:
        print(e)
        sleep(1)
# ser = serial.Serial("COM3")

print(ser.name)

spu_types = {0: 'raw', 1: 'bool', 2: 'value', 3: 'string', 4: 'enum', 5: 'bitmap'}
leisure_modes = {1: 'Breathe', 2: 'Leap', 3: 'Sunset', 4: 'Candle'}
all_sounds = ['None', 'Ocean', 'Thunder', 'Rain', 'Stream','Rainforest','Wind','Deep space','Bird','Cricket','Whale','White Noise', 'Pink Noise','Fan','Hairdryer','Lullaby','Piano','Wind Chimes']

tuya_comm = []
first_heartbeat = True
while 1:
    x = ser.read()
    if x == b'\x55':
        y = ser.read()
        if y == b'\xaa':
            ver = ser.read()
            com = ser.read()
            comm_len1 = ser.read()
            comm_len2 = ser.read()
            comm_len = int.from_bytes(comm_len1+comm_len2, 'big')
            tuya_comm = []
            tuya_comm.append(ord(x))
            tuya_comm.append(ord(y))
            tuya_comm.append(ord(ver))
            tuya_comm.append(ord(com))
            tuya_comm.append(ord(comm_len1))
            tuya_comm.append(ord(comm_len2))
            for n in range(comm_len):
                bit = ser.read()
                tuya_comm.append(ord(bit))
            chk = ser.read()
            tuya_comm.append(ord(chk))

            ts = ''.join('%02x' % b for b in tuya_comm)
            print(ts)
            if len(tuya_comm) == 0:
                pass
            elif ts == '55aa00000000ff': 
                print('Heart Beat') # Heart Beat
                if first_heartbeat:
                    ser.write(bytearray.fromhex('55AA030000010003'))
                    first_heartbeat = False
                else:
                    ser.write(bytearray.fromhex('55AA030000010104'))
            elif tuya_comm[3] == ord(b'\x01'): 
                print('Query Product Info')
                # got this by sending "SerialSend5 55aa0001000000" with  "Weblog 2"
                # {"p":"ta9o0ngbphd4kpo2","v":"1.1.2","m":0}
                ser.write(bytearray.fromhex('55AA0301002A7B2270223A227461396F306E6762706864346B706F32222C2276223A22312E312E32222C226D223A307DC2'))
            elif tuya_comm[3] == ord(b'\x02'): 
                print('Query Working Mode')
                ser.write(bytearray.fromhex('55AA0302000004'))
            elif tuya_comm[3] == ord(b'\x03'): 
                print('Network Status')
                ser.write(bytearray.fromhex('55AA0303000005'))
            elif tuya_comm[3] == ord(b'\x08'): 
                print('Query Status') 
                ser.write(bytearray.fromhex('55AA0307000F7100000B0100110001140000000A01C6'))
                ser.write(bytearray.fromhex('55AA03070007700000030105018A'))
                ser.write(bytearray.fromhex('55AA030700066F0000021E009E'))
                ser.write(bytearray.fromhex('55AA03070008680000040011060094'))
                ser.write(bytearray.fromhex('55AA0307000F6700000B00010A350012005A00110148'))
                ser.write(bytearray.fromhex('55AA030700056B010001017C'))
                ser.write(bytearray.fromhex('55AA0307000569040001017D'))
            elif tuya_comm[3] == ord(b'\x1c'): 
                print('Send Local Time')
                ser.write(bytearray.fromhex('55AA001C0008011508031731020290'))
            elif tuya_comm[3] == ord(b'\x06'):
                ts_ack = list(ts[:])
                ts_ack[5] = '3'
                ts_ack[7] = '7'
                chk1 = ts_ack[-2]
                chk2 = ts_ack[-1]
                chk = '%02X' % ((int.from_bytes(bytearray.fromhex(chk1+chk2), byteorder='big') + 4) % 256)
                ts_ack[-2] = chk[0]
                ts_ack[-1] = chk[1]
                ser.write(bytearray.fromhex(''.join(ts_ack)))

                # need to reply with ack
                print('Data Unit')
                data_len = int.from_bytes(tuya_comm[4:6], 'big')
                print('  Data Length: %d' % data_len)
                data = tuya_comm[6:7+data_len]
                print('  Data: %s' % ''.join('%02x' % b for b in data))
                n = 0
                while 1:
                    sdu_dpid = data[n]
                    sdu_type = data[n+1]
                    sdu_len = int.from_bytes(data[n+2:n+4], 'big')
                    sdu_data = data[n+4:n+4+sdu_len]
                    print('    DPID: %d' % sdu_dpid)
                    print('    TYPE: %s' % spu_types[sdu_type])
                    print('    DATA: %s' % ''.join('%02x' % b for b in sdu_data))

                    if sdu_dpid == 20:
                        if sdu_data[0]:
                            print('DEVICE ON')
                        else:
                            print('DEVICE OFF')

                    elif sdu_dpid == 101:
                        print('------')
                        print('ALARM 1')
                        m = 0
                        print(' - ON/OFF: %d' % sdu_data[m+0])
                        alarm_time_raw = int.from_bytes(sdu_data[m+1:m+3], 'big')/60
                        alarm_hrs = int(alarm_time_raw)
                        alarm_min = (alarm_time_raw*60) % 60
                        print(' - Time: %02d:%02d' % (alarm_hrs, alarm_min))
                        print(' - Brightness: %d' % sdu_data[m+3])
                        print(' - Day Bitmask (SMTWTFS): %s' % bin(sdu_data[m+4])[2:])
                        print(' - Sound Option: %s' % all_sounds[sdu_data[m+5]])
                        print(' - Volume: %d' % sdu_data[m+6])
                        print(' - Snooze (min): %d' % sdu_data[m+7])

                        print('ALARM 2')
                        m = 8
                        print(' - ON/OFF: %d' % sdu_data[m+0])
                        alarm_time_raw = int.from_bytes(sdu_data[m+1:m+3], 'big')/60
                        alarm_hrs = int(alarm_time_raw)
                        alarm_min = (alarm_time_raw*60) % 60
                        print(' - Time: %02d:%02d' % (alarm_hrs, alarm_min))
                        print(' - Brightness: %d' % sdu_data[m+3])
                        print(' - Day Bitmask (SMTWTFS): %s' % bin(sdu_data[m+4])[2:])
                        print(' - Sound Option: %s' % all_sounds[sdu_data[m+5]])
                        print(' - Volume: %d' % sdu_data[m+6])
                        print(' - Snooze (min): %d' % sdu_data[m+7])

                        print('ALARM 3')
                        m = 16
                        print(' - ON/OFF: %d' % sdu_data[m+0])
                        alarm_time_raw = int.from_bytes(sdu_data[m+1:m+3], 'big')/60
                        alarm_hrs = int(alarm_time_raw)
                        alarm_min = (alarm_time_raw*60) % 60
                        print(' - Time: %02d:%02d' % (alarm_hrs, alarm_min))
                        print(' - Brightness: %d' % sdu_data[m+3])
                        print(' - Day Bitmask (SMTWTFS): %s' % bin(sdu_data[m+4])[2:])
                        print(' - Sound Option: %s' % all_sounds[sdu_data[m+5]])
                        print(' - Volume: %d' % sdu_data[m+6])
                        print(' - Snooze (min): %d' % sdu_data[m+7])

                        print('ALARM 4')
                        m = 24
                        print(' - ON/OFF: %d' % sdu_data[m+0])
                        alarm_time_raw = int.from_bytes(sdu_data[m+1:m+3], 'big')/60
                        alarm_hrs = int(alarm_time_raw)
                        alarm_min = (alarm_time_raw*60) % 60
                        print(' - Time: %02d:%02d' % (alarm_hrs, alarm_min))
                        print(' - Brightness: %d' % sdu_data[m+3])
                        print(' - Day Bitmask (SMTWTFS): %s' % bin(sdu_data[m+4])[2:])
                        print(' - Sound Option: %s' % all_sounds[sdu_data[m+5]])
                        print(' - Volume: %d' % sdu_data[m+6])
                        print(' - Snooze (min): %d' % sdu_data[m+7])

                    elif sdu_dpid == 102:
                        print('------ Sleep Screen')
                        # first 2 bits are amount of time to be on (DPID 111)
                            # bit 1: minutes
                            # bit 2: seconds
                        # next 1 is on or off
                        # next 3 is the sound settings (DPID 112)
                        # next rest are the light settings (DPID 113)
                        # the sleep off command tunrs the entire device off

                    elif sdu_dpid == 103:
                        print('------ Light Screen')
                        print('Light Status: %d' % sdu_data[0])
                        if sdu_data[1] == 1:
                            print('- White')
                            print('-- Brightness: %d' % sdu_data[2])
                            print('-- WW->CC (0-100): %d' % sdu_data[3])
                        elif sdu_data[4] == 1:
                            print('- RGB')
                            print('-- Brightness: %d' % sdu_data[5])
                            print('-- Color Angle (0-360): %d' % int.from_bytes(sdu_data[6:8], 'big'))
                        elif sdu_data[8] == 1:
                            print('- Leisure')
                            print('-- Brightness: %d' % sdu_data[9])
                            print('-- Mode: %s' % leisure_modes[sdu_data[10]])
                        else:
                            pass

                    elif sdu_dpid == 104:
                        print('-----')
                        print('Sound Status: %d' % sdu_data[0])
                        print(' - Sound Option: %s' % all_sounds[sdu_data[1]])
                        print(' - Volume (0-15): %d' % sdu_data[2])
                        print(' - Timer (min): %d' % sdu_data[3])
                    
                    elif sdu_dpid == 105:
                        print('-----')
                        if int(sdu_data[0]) == 0:
                            print('12 hour time')
                        elif int(sdu_data[0]) == 1:
                            print('24 hour time')
                        else:
                            print('unknown time format option')

                    elif sdu_dpid == 106:
                        print('-----')
                        print('Set Manual Time')
                        time_raw = int.from_bytes(sdu_data, 'big')/60
                        hrs = int(time_raw)
                        minutes = (time_raw*60) % 60
                        print(' - Time: %02d:%02d' % (hrs, minutes))
                    
                    elif sdu_dpid == 107:
                        print('-----')
                        if int(sdu_data[0]) == 0:
                            print('Auto time off')
                        elif int(sdu_data[0]) == 1:
                            print('Auto time on')
                        else:
                            print('unknown auto time option')
                        
                    elif sdu_dpid == 110:
                        print('-----')
                        print('Inc Sound Option Up/Down: %d' % sdu_data[0])

                    elif sdu_dpid == 111:
                        print('-----')
                        print('Sleep Time: %d' % sdu_data[0])
                        print('D1: %d' % sdu_data[1])

                    elif sdu_dpid == 112:
                        print('------ Sleep Sounds Screen')
                        print('ON/OFF: %d' % sdu_data[0])
                        print('CHOICE: %d' % sdu_data[1])
                        print('VOLUME: %d' % sdu_data[2])

                    elif sdu_dpid == 113:
                        print('------ Sleep Light Screen')
                        print('ON/OFF: %d' % sdu_data[0])
                        print('WHITE : %d' % sdu_data[1])
                        print('BRIGHT: %d' % sdu_data[2])
                        print('WW->CC: %d' % sdu_data[3])
                        print('COLOR : %d' % sdu_data[4])
                        print('BRIGHT: %d' % sdu_data[5])
                        print('ANGLE : %d' % int.from_bytes(sdu_data[6:8], 'big'))
                        print('LEISUR: %d' % sdu_data[8])
                        print('BRIGHT: %d' % sdu_data[9])
                        print('MODE  : %s' % leisure_modes[sdu_data[10]])

                    if (n+4+sdu_len) == data_len:
                        break
                    else:
                        n = n+4+sdu_len
            else:
                print(ts)