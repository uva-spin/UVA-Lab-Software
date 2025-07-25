import sqlite3

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
    MeasurementType = StringData[0]

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

    Polarization = NumericData[11] #Polarization
    PolarizationSTD = NumericData[12] #Polarization STD
    SNR = NumericData[13] #SNR
    StepWidth = NumericData[14] #Step Width
    CenterFreq = NumericData[15] #Step Center
    FreqSpan = NumericData[16] #Step Frequency
    Area = NumericData[17] #Area
    PhaseVoltage = NumericData[18] #Phase Voltage
    TuneVoltage = NumericData[19] #Tune Voltage


    # Create the table if it doesn't exist
    schema_path = "../../../GUI-Webserver/database_utils/schema.sql"
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)
    

    cursor.execute('''INSERT INTO NMR ( 
                   run_number, measurement_type, peak_amp, peak_center,
                   beam_on, rf_level, if_atten,nmr_channel, temperature, calibration_constant, 
                   he_temperature, he_pressure, polarization, polarization_std, snr, step_width, 
                   center_freq, freq_span, area, phase_voltage, tune_voltage
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (RunNumber, MeasurementType, PeakAmp, PeakCenter, RFLevel, IFAtten, 
                    BeamON, NMRChannel, Temperature, CalibrationConstant,
                    HeTemperature, HePressure, Polarization, PolarizationSTD, SNR, StepWidth, CenterFreq, 
                    FreqSpan, Area, PhaseVoltage, TuneVoltage))
    
    conn.commit()
    conn.close()