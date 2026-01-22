"""
NI DAQ Triangular Waveform Generator
Generates triangular waveforms for FM modulation clock using NI PCIe 6321 and BNC-2110
"""

import numpy as np
try:
    import nidaqmx
    from nidaqmx import stream_writers
    from nidaqmx.constants import AcquisitionType, Signal
    NI_DAQ_AVAILABLE = True
except ImportError:
    NI_DAQ_AVAILABLE = False
    print("Warning: nidaqmx not available. Install with: pip install nidaqmx")


class TriangularWaveformGenerator:
    """
    Generate triangular waveforms for FM modulation clock.
    
    Note: This generator produces the modulation waveform (modulation rate in Hz).
    The RF carrier center frequency (in MHz) is controlled separately by the
    signal generator and can be swept independently while this waveform is active.
    """
    
    def __init__(self, device_name: str = "Dev1/ao0", voltage_range: tuple = (-2.0, 2.0)):
        """
        Initialize the triangular waveform generator
        
        Args:
            device_name: NI DAQ device and analog output channel (e.g., "Dev1/ao0")
            voltage_range: Tuple of (min_voltage, max_voltage) for output range
        """
        if not NI_DAQ_AVAILABLE:
            raise ImportError("nidaqmx library is not installed. Install with: pip install nidaqmx")
        
        self.device_name = device_name
        self.voltage_range = voltage_range
        self.task = None
        self.is_running = False
        self.frequency = 1.0  # Hz (default 1 Hz)
        self.amplitude = 2.0   # Volts (waveform goes from -amplitude to +amplitude, so -2V to +2V)
        self.offset = 0.0      # DC offset in Volts
        self.sample_rate = 1000  # Samples per second
        self.dwell_time = 0.01  # Dwell time per step in seconds (default 10ms)
        
    def generate_triangular_waveform(self, frequency: float, duration: float = None, 
                                     amplitude: float = None, offset: float = None,
                                     dwell_time: float = None) -> np.ndarray:
        """
        Generate a stepped triangular waveform with uniform step duration
        
        Args:
            frequency: Frequency of the triangular wave in Hz
            duration: Duration to generate in seconds (None = one period)
            amplitude: Peak amplitude in Volts (None = use self.amplitude)
            offset: DC offset in Volts (None = use self.offset)
            dwell_time: Dwell time per step in seconds (None = use self.dwell_time)
            
        Returns:
            numpy array of voltage values
        """
        if amplitude is None:
            amplitude = self.amplitude
        if offset is None:
            offset = self.offset
        if dwell_time is None:
            dwell_time = self.dwell_time
            
        period = 1.0 / frequency
        
        # Calculate number of steps in one period (must be even for symmetric triangle)
        # Each step has uniform duration = dwell_time
        steps_per_period = max(2, int(period / dwell_time))
        # Make it even for symmetric up/down triangle
        if steps_per_period % 2 != 0:
            steps_per_period += 1
        
        # Calculate actual dwell time to fit exactly in period
        actual_dwell = period / steps_per_period
        
        # Generate voltage levels for each step
        # Triangle goes from -amplitude to +amplitude and back
        # First half: -amplitude to +amplitude (steps_per_period/2 steps)
        # Second half: +amplitude to -amplitude (steps_per_period/2 steps)
        half_steps = steps_per_period // 2
        
        # Create voltage levels for one period
        voltage_levels = []
        # Upward ramp: -amplitude to +amplitude
        for i in range(half_steps + 1):
            voltage = -amplitude + (2 * amplitude * i / half_steps)
            voltage_levels.append(voltage)
        # Downward ramp: +amplitude to -amplitude (skip first point to avoid duplicate)
        for i in range(1, half_steps + 1):
            voltage = amplitude - (2 * amplitude * i / half_steps)
            voltage_levels.append(voltage)
        
        # Remove duplicate at the end (last point = first point for next period)
        voltage_levels = voltage_levels[:-1]
        
        # Calculate how many periods to generate
        if duration is None:
            num_periods = 1
        else:
            num_periods = max(1, int(duration / period))
        
        # Generate samples for each step
        samples_per_step = max(1, int(self.sample_rate * actual_dwell))
        waveform = []
        
        for period_idx in range(num_periods):
            for step_idx, voltage_level in enumerate(voltage_levels):
                # Hold this voltage level for dwell_time
                step_samples = [voltage_level + offset] * samples_per_step
                waveform.extend(step_samples)
        
        waveform = np.array(waveform, dtype=np.float64)
        
        # Clamp to voltage range
        waveform = np.clip(waveform, self.voltage_range[0], self.voltage_range[1])
        
        return waveform
    
    def start_continuous_waveform(self, frequency: float, amplitude: float = None, 
                                  offset: float = None, sample_rate: float = None,
                                  dwell_time: float = None):
        """
        Start generating a continuous stepped triangular waveform
        
        Args:
            frequency: Frequency of the triangular wave in Hz
            amplitude: Peak amplitude in Volts (None = use self.amplitude)
            offset: DC offset in Volts (None = use self.offset)
            sample_rate: Sample rate in Hz (None = use self.sample_rate)
            dwell_time: Dwell time per step in seconds (None = use self.dwell_time)
        """
        if self.is_running:
            self.stop()
            
        if amplitude is None:
            amplitude = self.amplitude
        if offset is None:
            offset = self.offset
        if sample_rate is None:
            sample_rate = self.sample_rate
        if dwell_time is None:
            dwell_time = self.dwell_time
            
        self.frequency = frequency  # Frequency is already in Hz
        self.amplitude = amplitude
        self.offset = offset
        self.sample_rate = sample_rate
        self.dwell_time = dwell_time
        
        try:
            # Create a new task
            self.task = nidaqmx.Task()
            
            # Add analog output channel
            self.task.ao_channels.add_ao_voltage_chan(
                self.device_name,
                min_val=self.voltage_range[0],
                max_val=self.voltage_range[1]
            )
            
            # Generate one period of the stepped waveform
            waveform = self.generate_triangular_waveform(
                self.frequency, 
                amplitude=amplitude, 
                offset=offset,
                dwell_time=dwell_time
            )
            
            # Configure timing for continuous generation
            self.task.timing.cfg_samp_clk_timing(
                rate=sample_rate,
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=len(waveform)
            )
            
            # Create stream writer
            writer = stream_writers.AnalogSingleChannelWriter(self.task.out_stream, auto_start=False)
            
            # Write the waveform (it will repeat continuously)
            writer.write_many_sample(waveform)
            
            # Start the task
            self.task.start()
            self.is_running = True
            
        except Exception as e:
            if self.task is not None:
                try:
                    self.task.close()
                except:
                    pass
                self.task = None
            raise Exception(f"Failed to start waveform generation: {str(e)}")
    
    def stop(self):
        """Stop waveform generation"""
        if self.task is not None:
            try:
                if self.is_running:
                    self.task.stop()
                self.task.close()
            except Exception as e:
                print(f"Error stopping waveform: {str(e)}")
            finally:
                self.task = None
                self.is_running = False
    
    def is_active(self) -> bool:
        """Check if waveform generation is active"""
        return self.is_running and self.task is not None
    
    def close(self):
        """Clean up resources"""
        self.stop()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
