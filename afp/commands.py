from dataclasses import dataclass
from RsInstrument import * 
from typing import List, Union, Optional
from more_itertools import always_iterable

try:
    from ni_daq_waveform import TriangularWaveformGenerator, NI_DAQ_AVAILABLE
except ImportError:
    NI_DAQ_AVAILABLE = False
    TriangularWaveformGenerator = None

@dataclass
class Controller:
    def __init__(self, instr: RsInstrument, ni_daq_device: str = "Dev1/ao0"):
        self.instr = instr
        self.rf_status = False
        self.device_info = {'RsInstrument driver version': self.instr.driver_version,
                            'Visa manufacturer': self.instr.visa_manufacturer,
                            'Instrument full name': self.instr.full_instrument_model_name,
                            'Instrument installed options': ",".join(self.instr.instrument_options)}
        self.ni_daq_device = ni_daq_device
        self.waveform_generator: Optional[TriangularWaveformGenerator] = None
        self.last_dwell_time = 0.01  # Default 10ms, stored for use when starting waveform from state changes
        if NI_DAQ_AVAILABLE and TriangularWaveformGenerator:
            try:
                self.waveform_generator = TriangularWaveformGenerator(device_name=ni_daq_device)
            except Exception as e:
                print(f"Warning: Could not initialize NI DAQ waveform generator: {e}")
                self.waveform_generator = None

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

    def get_center_freq(self):
        """Get center frequency in MHz"""
        freq = self.instr.query_float('SOURCE:FREQUENCY:CW?')
        # Instrument returns Hz, convert to MHz
        return freq / 1_000_000

    def get_freq_width(self):
        """Get frequency width (span) in MHz"""
        span = self.instr.query_float('SOURCE:FREQUENCY:SPAN?')
        # Instrument returns Hz, convert to MHz
        return span / 1_000_000

    def get_start_freq(self):
        freq = self.instr.query_float('SOURCE:FREQUENCY:START?')
        # Instrument returns Hz, convert to MHz
        return freq / 1_000_000

    def get_stop_freq(self):
        freq = self.instr.query_float('SOURCE:FREQUENCY:STOP?')
        # Instrument returns Hz, convert to MHz
        return freq / 1_000_000 

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
        
        # Manage external waveform generator
        if self.waveform_generator:
            try:
                current_source = self.get_fm_source()
                if enabled and current_source == "EXT":
                    # Set coupling to DC when enabling FM with external source
                    try:
                        self.instr.write('SOURCE:FM:EXTERNAL:COUPling DC')
                    except Exception as e:
                        print(f"Warning: Could not set FM coupling to DC: {e}")
                    # Start external waveform when FM is enabled with EXT source
                    fm_freq = self.get_fm_frequency()
                    if fm_freq > 0:
                        # Check if AM is also using EXT - if so, use FM frequency (they share the waveform)
                        am_source = self.get_am_source()
                        am_enabled = self.get_am_state()
                        if am_enabled and am_source == "EXT":
                            # Both FM and AM using EXT - waveform already handles both
                            pass
                        self.waveform_generator.start_continuous_waveform(fm_freq, dwell_time=self.last_dwell_time)
                elif not enabled:
                    # Stop external waveform when FM is disabled, but only if AM is not using it
                    am_source = self.get_am_source()
                    am_enabled = self.get_am_state()
                    if not (am_enabled and am_source == "EXT"):
                        if self.waveform_generator.is_active():
                            self.waveform_generator.stop()
            except Exception as e:
                print(f"Warning: Could not manage external waveform: {e}")

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
        # If using external source, update the waveform generator
        try:
            current_source = self.get_fm_source()
            if current_source == "EXT" and self.waveform_generator:
                # Restart waveform with new frequency if it's running
                if self.waveform_generator.is_active():
                    self.waveform_generator.stop()
                    self.waveform_generator.start_continuous_waveform(frequency, dwell_time=self.last_dwell_time)
        except Exception as e:
            print(f"Warning: Could not update external waveform frequency: {e}")
        
        # Set internal frequency (used when source is INT)
        self.instr.write(f'SOURCE:FM:INTernal:FREQuency {frequency}Hz')

    def get_fm_frequency(self) -> float:
        """Get FM modulation frequency in Hz"""
        return self.instr.query_float('SOURCE:FM:INTernal:FREQuency?')

    def set_fm_source(self, source: str):
        """Set FM source (INT or EXT)"""
        self.instr.write(f'SOURCE:FM:SOURce {source}')
        # When using external source, set coupling to DC
        if source == "EXT":
            try:
                self.instr.write('SOURCE:FM:EXTERNAL:COUPling DC')
            except Exception as e:
                print(f"Warning: Could not set FM coupling to DC: {e}")
        # If switching to EXT, ensure waveform generator is ready
        # If switching to INT, stop external waveform (but don't disable FM)
        if source == "EXT" and self.waveform_generator and not self.waveform_generator.is_active():
            # Waveform will be started when FM frequency is set
            pass
        elif source == "INT" and self.waveform_generator and self.waveform_generator.is_active():
            # Stop external waveform when switching to internal
            try:
                self.waveform_generator.stop()
            except Exception as e:
                print(f"Warning: Could not stop waveform generator: {e}")

    def get_fm_source(self) -> str:
        """Get FM source"""
        return self.instr.query_str('SOURCE:FM:SOURce?').strip()

    # === Amplitude Modulation (AM) Methods ===
    
    def set_am_state(self, enabled: bool):
        """Enable or disable amplitude modulation"""
        state = "ON" if enabled else "OFF"
        self.instr.write(f'SOURCE:AM:STATE {state}')
        
        # Manage external waveform generator when AM uses EXT source
        if self.waveform_generator:
            try:
                current_source = self.get_am_source()
                fm_source = self.get_fm_source()
                fm_enabled = self.get_fm_state()
                
                if enabled and current_source == "EXT":
                    # AM enabled with EXT source - start waveform if not already running
                    if not self.waveform_generator.is_active():
                        # Use FM frequency if FM is also using EXT, otherwise use AM frequency
                        if fm_enabled and fm_source == "EXT":
                            freq = self.get_fm_frequency()
                        else:
                            freq = self.get_am_frequency()
                        if freq > 0:
                            self.waveform_generator.start_continuous_waveform(freq, dwell_time=self.last_dwell_time)
                elif not enabled:
                    # AM disabled - stop waveform only if FM is not using it
                    if not (fm_enabled and fm_source == "EXT"):
                        if self.waveform_generator.is_active():
                            self.waveform_generator.stop()
            except Exception as e:
                print(f"Warning: Could not manage external waveform for AM: {e}")

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
        # If switching to EXT and AM is enabled, start the waveform
        # If switching away from EXT, stop waveform only if FM is not using it
        if self.waveform_generator:
            try:
                am_enabled = self.get_am_state()
                fm_source = self.get_fm_source()
                fm_enabled = self.get_fm_state()
                
                if source == "EXT" and am_enabled:
                    # AM wants external source - start waveform if not already running
                    if not self.waveform_generator.is_active():
                        # Use FM frequency if FM is also using EXT, otherwise use AM frequency
                        if fm_enabled and fm_source == "EXT":
                            freq = self.get_fm_frequency()
                        else:
                            freq = self.get_am_frequency()
                        if freq > 0:
                            self.waveform_generator.start_continuous_waveform(freq, dwell_time=self.last_dwell_time)
                elif source != "EXT" and am_enabled:
                    # AM no longer wants external - stop only if FM is not using it
                    if not (fm_enabled and fm_source == "EXT"):
                        if self.waveform_generator.is_active():
                            self.waveform_generator.stop()
            except Exception as e:
                print(f"Warning: Could not manage external waveform for AM: {e}")

    def get_am_source(self) -> str:
        """Get AM source"""
        return self.instr.query_str('SOURCE:AM:SOURce?').strip()

    def start_external_waveform(self, frequency: float, amplitude: float = 5.0, offset: float = 0.0, dwell_time: float = 0.01):
        """Start the external triangular waveform generator
        
        Args:
            frequency: Waveform frequency in Hz
            amplitude: Peak amplitude in Volts
            offset: DC offset in Volts
            dwell_time: Dwell time per step in seconds (default 10ms)
        """
        if not self.waveform_generator:
            raise RuntimeError("NI DAQ waveform generator is not available")
        if self.waveform_generator.is_active():
            self.waveform_generator.stop()
        self.last_dwell_time = dwell_time  # Store for use in state change handlers
        self.waveform_generator.start_continuous_waveform(frequency, amplitude, offset, dwell_time=dwell_time)
    
    def stop_external_waveform(self):
        """Stop the external triangular waveform generator"""
        if self.waveform_generator and self.waveform_generator.is_active():
            self.waveform_generator.stop()
    
    def is_external_waveform_active(self) -> bool:
        """Check if external waveform is currently active"""
        return self.waveform_generator is not None and self.waveform_generator.is_active()
    
    def close(self):
        """Close controller and cleanup resources"""
        if self.waveform_generator:
            try:
                self.waveform_generator.close()
            except Exception as e:
                print(f"Warning: Error closing waveform generator: {e}")
        self.instr.close()