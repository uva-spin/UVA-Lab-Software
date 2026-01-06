from RsInstrument import * 
RsInstrument.assert_minimum_version('1.102.0')
instr_list = RsInstrument.list_resources('?*')
if not instr_list:
    print("No instruments found")
    exit()
print(instr_list)

instr = RsInstrument('USB0::0x0AAD::0x0048::101548::INSTR', True, True,options='TerminationCharacter = \r\n')
idn = instr.query_str('*IDN?')
print(f"\nHello, I am: '{idn}'")

print(f'RsInstrument driver version: {instr.driver_version}')

print(f'Visa manufacturer: {instr.visa_manufacturer}')

print(f'Instrument full name: {instr.full_instrument_model_name}')

print(f'Instrument installed options: {",".join(instr.instrument_options)}')

instr.visa_timeout = 3000
instr.write('*RST')
# instr.write('SOURCE:FREQUENCY:CW 213MHz')
instr.write('SOURCE:FREQuency:START 212MHz')
instr.write('SOURCE:FREQuency:STOP 214MHz')
instr.write('SOURCE:SWEEP:SPACING LINear')
# instr.write('SOURCE:FUNCTION:SHAPE SIN')
# instr.write('SOURCE:FREQ:STEP 10kHz')
instr.write('SOURCE:SWEEP:POINTS 500')
instr.write('SOURCE:POWER:POWER 12')
instr.write('SOURCE:FREQUENCY:MODE SWEep')
instr.write('SOURCE:SWEEP:DWELl 10ms')
instr.write('SOURCE:SWEEP:MODE AUTO')
instr.write('OUTPUT:STATE ON')

freq = instr.query_float('SOURCE:FREQUENCY:CW?')
power = instr.query_float('SOURCE:POWER:POWER?')
output = instr.query_bool('OUTPUT:STATE?')
sweep_points = instr.query_int('SOURCE:SWEEP:POINTS?')

print(f'Frequency: {freq}')
print(f'Power: {power} dBm')
print(f'Output: {output}')
print(f'Sweep points: {sweep_points}')

instr.close()
