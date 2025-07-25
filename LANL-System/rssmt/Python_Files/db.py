import sqlite3
from datetime import datetime, timezone
import pytz

def NMR_DB(StringData, NumericData, SignalData):
    """
    Writes data to a SQLite database.
    """
    conn = sqlite3.connect("//twist.phys.virginia.edu/www/spin/instance/flaskr.sqlite")
    cursor = conn.cursor()
    
    # Save_Path = StringData[0] 
    # Commentary = StringData[1]
    # QCurveFile = StringData[2]
    # QComment = StringData[3]
    # TEQFile = StringData[4]
    # TEQComment = StringData[5]
    # TuneFile = StringData[6]
    MeasurementType = str(StringData[0])

    RunNumber = int(NumericData[0])
    PeakAmp = float(NumericData[1])
    PeakCenter = float(NumericData[2])
    BeamON = int(NumericData[3])
    RFLevel = float(NumericData[4]) ## RF Power
    IFAtten = float(NumericData[5]) #IF Attenuation
    HeTemperature = float(NumericData[6]) #He4 Temperature
    HePressure = float(NumericData[7]) #He4 Pressure
    NMRChannel = int(NumericData[8]) #NMR Channel
    Temperature = float(NumericData[9]) #Temperature
    CalibrationConstant = float(NumericData[10]) #Calibration Constant

    Polarization = float(NumericData[11]) #Polarization
    PolarizationSTD = float(NumericData[12]) #Polarization STD
    SNR = float(NumericData[13]) #SNR
    StepWidth = float(NumericData[14]) #Step Width
    CenterFreq = float(NumericData[15]) #Step Center
    FreqSpan = float(NumericData[16]) #Step Frequency
    Area = float(NumericData[17]) #Area
    PhaseVoltage = float(NumericData[18]) #Phase Voltage
    TuneVoltage = float(NumericData[19]) #Tune Voltage


    # Create the table if it doesn't exist
    schema_path = r"C:\Users\Ptgroup\Documents\UVA-Lab-Software\GUI-Webserver\database_utils\schema.sql"
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)
    

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
    conn.commit()
    conn.close()
    
    return "Executed"