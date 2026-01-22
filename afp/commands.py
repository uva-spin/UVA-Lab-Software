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
    
    def set_center_freq(self, freq: float):
        self.instr.write(f'SOURCE:FREQUENCY:CW {freq}MHz')
    
    def set_freq_width(self, width: float):
        self.instr.write(f'SOURCE:FREQUENCY:SPAN {width}MHz')
         
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
        # Preserve FM state when changing modes (some instruments disable FM on mode change)
        fm_was_enabled = False
        try:
            fm_was_enabled = self.get_fm_state()
        except:
            pass  # If we can't query FM state, continue anyway
        
        self.instr.write(f'SOURCE:FREQUENCY:MODE {mode}')
        
        # Re-enable FM if it was enabled before (so FM works with CW setting)
        if fm_was_enabled:
            try:
                self.set_fm_state(True)
            except:
                pass  # If re-enabling fails, continue anyway
         

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
         
        return freq  

    def get_stop_freq(self):
        freq = self.instr.query_float('SOURCE:FREQUENCY:STOP?')
         
        return freq 

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

    # === Frequency Modulation (FM) Methods ===
    
    def set_fm_state(self, enabled: bool):
        """Enable or disable frequency modulation"""
        state = "ON" if enabled else "OFF"
        self.instr.write(f'SOURCE:FM:STATE {state}')

    def get_fm_state(self) -> bool:
        """Get FM state (on/off)"""
        return self.instr.query_bool('SOURCE:FM:STATE?')

    def set_fm_deviation(self, deviation: float):
        """Set FM deviation in kHz"""
        self.instr.write(f'SOURCE:FM:DEViation {deviation}kHz')

    def get_fm_deviation(self) -> float:
        """Get FM deviation in kHz"""
        return self.instr.query_float('SOURCE:FM:DEViation?') / 1000  # Convert to kHz

    def set_fm_frequency(self, frequency: float):
        """Set FM modulation frequency in Hz"""
        self.instr.write(f'SOURCE:FM:INTernal:FREQuency {frequency}Hz')

    def get_fm_frequency(self) -> float:
        """Get FM modulation frequency in Hz"""
        return self.instr.query_float('SOURCE:FM:INTernal:FREQuency?')

    def set_fm_source(self, source: str):
        """Set FM source (INT or EXT)"""
        self.instr.write(f'SOURCE:FM:SOURce {source}')

    def get_fm_source(self) -> str:
        """Get FM source"""
        return self.instr.query_str('SOURCE:FM:SOURce?').strip()

    # === Amplitude Modulation (AM) Methods ===
    
    def set_am_state(self, enabled: bool):
        """Enable or disable amplitude modulation"""
        state = "ON" if enabled else "OFF"
        self.instr.write(f'SOURCE:AM:STATE {state}')

    def get_am_state(self) -> bool:
        """Get AM state (on/off)"""
        return self.instr.query_bool('SOURCE:AM:STATE?')

    def set_am_depth(self, depth: float):
        """Set AM depth in percent"""
        self.instr.write(f'SOURCE:AM:DEPTh {depth}')

    def get_am_depth(self) -> float:
        """Get AM depth in percent"""
        return self.instr.query_float('SOURCE:AM:DEPTh?')

    def set_am_frequency(self, frequency: float):
        """Set AM modulation frequency in Hz"""
        self.instr.write(f'SOURCE:AM:INTernal:FREQuency {frequency}Hz')

    def get_am_frequency(self) -> float:
        """Get AM modulation frequency in Hz"""
        return self.instr.query_float('SOURCE:AM:INTernal:FREQuency?')

    def set_am_source(self, source: str):
        """Set AM source (INT or EXT)"""
        self.instr.write(f'SOURCE:AM:SOURce {source}')

    def get_am_source(self) -> str:
        """Get AM source"""
        return self.instr.query_str('SOURCE:AM:SOURce?').strip()

    def close(self):
        self.instr.close()