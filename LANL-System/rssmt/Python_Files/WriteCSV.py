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

def Write_To_CSV(StringData, NumericData, SignalData):
    """
    Writes data to a CSV file in a format compatible with LabVIEW.
    If the file exists, appends the new data. If not, creates a new file.
    Includes path validation and sanitization.
    """
    import csv
    import datetime 
    import os
    import tempfile


    ### Let's also include:

    # 1. Polarization
    # 2. Area
    # 3. Scan Sweeps
    # 4. Scan Steps
    # 5. Scan Frequency
    # 6. RF Frequency
    # 7. RF Modulation
    # 8. Yale Gain (May not need)
    # 9. DC Level
    # 10. He3 Pressure
    # 11. He3 Temperature
    # 12. Sep Flow
    # 13. Main flow
    # 14. MagLevel
    # 15. RF Volts
    # 16. LN2 Level
    # 17. Vacuum Pressure


    # Save_Path = StringData[0] 
    # Commentary = StringData[1]
    # QCurveFile = StringData[2]
    # QComment = StringData[3]
    # TEQFile = StringData[4]
    # TEQComment = StringData[5]
    # TuneFile = StringData[6]
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

    Polarization = NumericData[11] #Polarization
    PolarizationSTD = NumericData[12] #Polarization STD
    SNR = NumericData[13] #SNR
    StepWidth = NumericData[14] #Step Width
    CenterFreq = NumericData[15] #Step Center
    FreqSpan = NumericData[16] #Step Frequency
    Area = NumericData[17] #Area
    PhaseVoltage = NumericData[18] #Phase Voltage
    TuneVoltage = NumericData[19] #Tune Voltage


    try:
        # Create a timestamp for the event number
        EventNumber = int(datetime.datetime.now().timestamp())
        
        # Prepare data row
        base_data = [RunNumber, EventNumber, Commentary, QCurveFile, QComment, TEQFile, TEQComment, TuneFile, 
                    PeakAmp, PeakCenter, BeamON, RFLevel, IFAtten, 
                    HeTemperature, HePressure, NMRChannel, Temperature, CalibrationConstant, MeasurementType,
                    Polarization, PolarizationSTD, SNR, StepWidth, CenterFreq, FreqSpan, Area, PhaseVoltage, TuneVoltage]
        
        RunNumber = int(RunNumber)
        
        # Define headers
        base_headers = ["Run Number", "Event Number", "Commentary", "Q Curve File", "Q Comment", "TEQ File", "TEQ Comment", "Tune File", 
                    "Peak Amp (V)", "Peak Center (MHz)", "Beam ON", "RF Level (dBm)", "IF Atten", 
                    "He Temperature", "He Pressure", "NMR Channel", "Temperature", "CC", "Measurement Type",
                    "Polarization", "Polarization STD", "SNR", "Step Width", "Center Freq", "Freq Span", "Area", "Phase Voltage", "Tune Voltage"]
        
        signal_headers = [f"ADC_{i}" for i in range(len(SignalData))]   
        all_headers = base_headers + signal_headers
        
        # Sanitize the path - remove any quotes or problematic characters
        if Save_Path is None:
            # Default to a safe location if None is provided
            Save_Path = os.path.join(os.path.expanduser("~"), "Documents", "LabVIEW_Data")
        else:
            # Remove quotes and normalize path
            Save_Path = Save_Path.strip().strip("'").strip('"')
            # Fix path separators
            Save_Path = os.path.normpath(Save_Path)
        
        # Print the path we're trying to use for debugging
        print(f"Attempting to save to directory: {Save_Path}")
        
        # Create full file path
        filename = f"Run_{RunNumber}.csv"
        
        try:
            # First attempt: Try specified path
            if not os.path.exists(Save_Path):
                os.makedirs(Save_Path)
            
            save_file = os.path.join(Save_Path, filename)
            print(f"Full file path: {save_file}")
            
            # Write data to file
            if os.path.exists(save_file):
                with open(save_file, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(base_data + SignalData)
            else:
                with open(save_file, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(all_headers)
                    writer.writerow(base_data + SignalData)
                    
            return f"Data saved to {save_file}"
            
        except (PermissionError, OSError) as e:
            print(f"Failed to write to primary path: {str(e)}")
            # Second attempt: Try Documents folder
            user_dir = os.path.expanduser("~")
            documents_dir = os.path.join(user_dir, "Documents")
            backup_dir = os.path.join(documents_dir, "LabVIEW_Data")
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
                
            backup_file = os.path.join(backup_dir, filename)
            print(f"Trying backup location: {backup_file}")
            
            try:
                if os.path.exists(backup_file):
                    with open(backup_file, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(base_data + SignalData)
                else:
                    with open(backup_file, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(all_headers)
                        writer.writerow(base_data + SignalData)
                        
                return f"Original path failed. Data saved to {backup_file}"
            except Exception as e2:
                print(f"Failed to write to backup path: {str(e2)}")
                # Last resort: temp directory
                temp_dir = tempfile.gettempdir()
                temp_file = os.path.join(temp_dir, filename)
                print(f"Trying temp location: {temp_file}")
                
                with open(temp_file, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(all_headers)
                    writer.writerow(base_data + SignalData)
                    
                return f"Emergency backup saved to {temp_file}"
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        
        # Last resort: Try to save to temp directory with a unique name
        try:
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = os.path.join(temp_dir, f"Emergency_Run_{RunNumber}_{timestamp}.csv")
            
            with open(temp_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(all_headers)
                writer.writerow(base_data + SignalData)
                
            return f"Original error: {error_msg}. Emergency backup saved to {temp_file}"
        except Exception as final_e:
            return f"Failed to write data anywhere. Original error: {error_msg}. Final error: {str(final_e)}"
