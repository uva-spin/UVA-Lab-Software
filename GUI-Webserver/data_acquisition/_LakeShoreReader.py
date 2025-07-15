import visa

rm = visa.ResourceManager()

try:
    instrument = rm.open_resource('GPIB::12')

    idn_response = instrument.query('*IDN?')
    print(f"Instrument ID: {idn_response.strip()}")

    instrument.write('VOLT 5')

    current_reading = instrument.query('MEAS:CURR?')
    print(f"Current reading: {current_reading.strip()}")

except visa.errors.VisaIOError as e:
    print(f"VISA Error: {e}")

finally:

    if 'instrument' in locals() and instrument:
        instrument.close()
