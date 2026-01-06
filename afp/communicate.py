from RsInstrument import * 
RsInstrument.assert_minimum_version('1.102.0')
instr_list = RsInstrument.list_resources('?*')
if not instr_list:
    print("No instruments found")
    exit()
print(instr_list)

isntr = RsInstrument('GPIB::28:INSTR', True, True, "SelectVisa='rs'")

print(isntr.check_status())

print(isntr.query('*IDN?'))
print(isntr.full_instrument_model_name())
isntr.close()

# isntr.write_float('CONF:VOLT:DC', 10)
# isntr.write_float('CONF:CURR:DC', 1)
# isntr.write_float('CONF:FREQ', 1000)

# print(isntr.query_float('CONF:VOLT:DC?'))
# print(isntr.query_float('CONF:CURR:DC?'))
# print(isntr.query_float('CONF:FREQ?'))


