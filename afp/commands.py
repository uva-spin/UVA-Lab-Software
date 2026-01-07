from dataclasses import dataclass
from RsInstrument import * 
from typing import List, Union
from more_itertools import always_iterable

@dataclass
class Controller:
    def __init__(self, instr: RsInstrument):
        self.instr = instr
        self.rf_status = False
        self.device_info = {'RsInstrument driver version': self.instr.driver_version,
                            'Visa manufacturer': self.instr.visa_manufacturer,
                            'Instrument full name': self.instr.full_instrument_model_name,
                            'Instrument installed options': ",".join(self.instr.instrument_options)}

    def status(self):
        return self.instr.query_str('*IDN?')

    def set_start_freq(self, freq: float):
        self.instr.write(f'SOURCE:FREQUENCY:START {freq}MHz')
         
    
    def set_stop_freq(self, freq: float):
        self.instr.write(f'SOURCE:FREQUENCY:STOP {freq}MHz')
         
    
    def set_spacing(self, spacing: str):
        '''
        SPACING can be:
        - LINear
        '''
        self.instr.write(f'SOURCE:SWEEP:SPACING {spacing}')
         

    def set_power(self, power: float):
        self.instr.write(f'SOURCE:POWER:POWER {power:.1f}dBm')
         

    def set_mode(self, mode: str):
        '''
        MODE can be:
        - CW
        - SWEep
        '''
        self.instr.write(f'SOURCE:FREQUENCY:MODE {mode}')
         

    def set_sweep_points(self, points: int):
        self.instr.write(f'SOURCE:SWEEP:POINTS {points}')
         

    def set_sweep_dwell(self, dwell: float):
        self.instr.write(f'SOURCE:SWEEP:DWELl {dwell}ms')
         

    def activate_rf(self):
        self.rf_status = not self.rf_status
        if self.rf_status:
            self.instr.write('OUTPUT:STATE ON')
        else:
            self.instr.write('OUTPUT:STATE OFF')
         

    def get_rf_status(self):
        rf_status = self.instr.query_bool('OUTPUT:STATE?')
         
        return rf_status

    def get_frequency(self):
        freq = self.instr.query_float('SOURCE:FREQUENCY:CW?')
         
        return freq

    def get_start_freq(self):
        freq = self.instr.query_float('SOURCE:FREQUENCY:START?')
         
        return freq / 1e6  # Convert to MHz

    def get_stop_freq(self):
        freq = self.instr.query_float('SOURCE:FREQUENCY:STOP?')
         
        return freq / 1e6  # Convert to MHz

    def get_mode(self):
        mode = self.instr.query_str('SOURCE:FREQUENCY:MODE?')
         
        return mode.strip()

    def get_power(self):
        power = self.instr.query_float('SOURCE:POWER:POWER?')
         
        return power

    def get_sweep_points(self):
        sweep_points = self.instr.query_int('SOURCE:SWEEP:POINTS?')
         
        return sweep_points

    def get_sweep_dwell(self):
        sweep_dwell = self.instr.query_float('SOURCE:SWEEP:DWELl?')
         
        return sweep_dwell

    def get_sweep_mode(self):
        sweep_mode = self.instr.query_str('SOURCE:SWEEP:MODE?')
         
        return sweep_mode

    def get_sweep_spacing(self):
        sweep_spacing = self.instr.query_str('SOURCE:SWEEP:SPACING?')
         
        return sweep_spacing

    def close(self):
        self.instr.close()