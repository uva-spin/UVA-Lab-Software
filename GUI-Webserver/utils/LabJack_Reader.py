import sys
import traceback
from datetime import datetime
import u3
import numpy as np

class LabJack:

    def data_stream(self):
        # MAX_REQUESTS is the number of packets to be read.
        MAX_REQUESTS = 75
        # SCAN_FREQUENCY is the scan frequency of stream mode in Hz
        SCAN_FREQUENCY = 5000

        d = None
        # At high frequencies ( >5 kHz), the number of samples will be MAX_REQUESTS
        # times 48 (packets per request) times 25 (samples per packet).
        d = u3.U3()

        # To learn the if the U3 is an HV
        d.configU3()

        # For applying the proper calibration to readings.
        d.getCalibrationData()

        # Set the FIO0 and FIO1 to Analog (d3 = b00000011)
        d.configIO(FIOAnalog=3)

        print("Configuring U3 stream")
        d.streamConfig(NumChannels=2, PChannels=[0, 1], NChannels=[31, 31], Resolution=3, ScanFrequency=SCAN_FREQUENCY)
        if d is None:
            print("Configure a device first.")
            sys.exit(0)

        try:
            print("Start stream")
            d.streamStart()
            start = datetime.now()
            print("Start time is %s" % start)

            missed = 0
            dataCount = 0
            packetCount = 0
            data_R2 = np.zeros(MAX_REQUESTS)

            for i, r in enumerate(d.streamData()):
                if r is not None:
                    # Our stop condition
                    if dataCount >= MAX_REQUESTS:
                        break

                    if r["errors"] != 0:
                        print("Errors counted: %s ; %s" % (r["errors"], datetime.now()))

                    if r["numPackets"] != d.packetsPerRequest:
                        print("----- UNDERFLOW : %s ; %s" %
                            (r["numPackets"], datetime.now()))

                    if r["missed"] != 0:
                        missed += r['missed']
                        print("+++ Missed %s" % r["missed"])

                    vOut = sum(r["AIN0"]) / len(r["AIN0"])
                    vIn = 10
                    R1 = 100
                    R2 = R1*(1/((vIn/vOut)-1))
                    

                    #print("The Magnet Resistor is %s" %R1)
                    #print("The voltage is: %s" %vOut)

                    dataCount += 1
                    packetCount += r['numPackets']

                    data_R2[i] = R2
                else:
                    # Got no data back from our read.
                    # This only happens if your stream isn't faster than the USB read
                    # timeout, ~1 sec.
                    print("No data ; %s" % datetime.now())
        except:
            print("".join(i for i in traceback.format_exc()))
        finally:
            stop = datetime.now()
            d.streamStop()
            #print("Stream stopped.\n")
            d.close()
        return(np.average(data_R2))

        
def get_r_value():
    labjack_device = LabJack()  
    return labjack_device.data_stream()  


if __name__ == "__main__":
    labjack_device = LabJack()  # Create an instance of LabJack class
    R2 = labjack_device.data_stream()  # Run the data stream method
    print("This is the average of R1: %s" % np.round(R2,2))