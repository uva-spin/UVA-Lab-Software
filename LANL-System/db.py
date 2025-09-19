### Headers ###

# Run Number
# Event Number
# Commentary
# Q Curve File
# Q Comment
# TEQ File
# TEQ Comment
# Tune File
# FLower
# FUpper
# Peak Amp (V)
# Peak Center (MHz)
# Beam ON
# RF Level (dBm)
# IF Atten (dB)
# Task3 Temperature
# Task3 Pressure
# NMR Channel
# ADC_1
# ADC_2
# ... (Up to 400)
# ADC_400

def is_connected(connection):
    try:
        connection.ping()
    except:
        return False
    return True

def reconnect(connection):
    while not is_connected(connection):
        connection.reconnect()
    print("Connected to the database")

def retry_commit(cursor):
    cursor.rollback()
    cursor.commit()


def toNMR_DB(StringData, NumericData, SignalData):

    import json
    import mariadb
    import datetime
    import pytz

    config = json.load(open("config.json"))

    conn = mariadb.connect(**config)

    MeasurementType = StringData[7]

    RunNumber = NumericData[0]
    PeakAmp = NumericData[1]
    PeakCenter = NumericData[2]
    BeamON = NumericData[3]
    RFLevel = NumericData[4] ## RF Power
    IFAtten = NumericData[5] #IF Attenuation
    HeTemperature = NumericData[6] #He4 Temperature
    HePressure = NumericData[7] #He4 Pressure
    NMRChannel = NumericData[8] #NMR Channel
    Temperature = NumericData[9] #Temperature
    CalibrationConstant = NumericData[10] #Calibration Constant

    Polarization = StringData[11] #Polarization
    PolarizationSTD = StringData[12] #Polarization STD
    SNR = StringData[13] #SNR
    StepWidth = StringData[14] #Step Width
    CenterFreq = StringData[15] #Step Center
    FreqSpan = StringData[16] #Step Frequency
    Area = StringData[17] #Area
    PhaseVoltage = StringData[18] #Phase Voltage
    TuneVoltage = StringData[19] #Tune Voltage

    cursor = conn.cursor()

    cursor.execute('''INSERT INTO NMR ( 
                   run_number, measurement_type, peak_amp, peak_center,
                   beam_on, rf_level, if_atten, nmr_channel, temperature, calibration_constant, 
                   he_temperature, he_pressure, polarization, polarization_std, snr, step_width, 
                   center_freq, freq_span, area, phase_voltage, tune_voltage, "Timestamp"
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (RunNumber, MeasurementType, PeakAmp, PeakCenter, 
                    BeamON, RFLevel, IFAtten, NMRChannel, Temperature, CalibrationConstant,
                    HeTemperature, HePressure, Polarization, PolarizationSTD, SNR, StepWidth, CenterFreq, 
                    FreqSpan, Area, PhaseVoltage, TuneVoltage, datetime.now(pytz.timezone("America/New_York")).strftime('%Y-%m-%d %H:%M:%S')))

    try:
        conn.commit()
    except Exception as e:
        print(f"Error inserting data: {e}. Retrying...")
        retry_commit(cursor)
    finally:
        cursor.close()  
        conn.close()
    
    return "Executed"


