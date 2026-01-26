"""
NI DAQ Triangular Waveform Generator
Generates triangular waveforms for FM modulation clock using NI PCIe 6321 and BNC-2110
"""

import numpy as np
import time
try:
    import nidaqmx
    from nidaqmx import stream_writers
    from nidaqmx.constants import AcquisitionType
    from scipy import signal
    import matplotlib.pyplot as plt
    NI_DAQ_AVAILABLE = True
except ImportError:
    NI_DAQ_AVAILABLE = False
    print("Warning: nidaqmx not available. Install with: pip install nidaqmx")


class WaveformGenerator:
    """
    Generate triangular waveforms for FM modulation clock.
    
    Note: This generator produces the modulation waveform (modulation rate in Hz).
    The RF carrier center frequency (in MHz) is controlled separately by the
    signal generator and can be swept independently while this waveform is active.
    """
    
    def __init__(self, device_name: str = "Dev1/ao0", voltage_range: tuple = (-2.0, 2.0), waveform_type: str = "triangular"):
        """
        Initialize the triangular waveform generator
        
        Args:
            device_name: NI DAQ device and analog output channel (e.g., "Dev1/ao0")
            voltage_range: Tuple of (min_voltage, max_voltage) for output range
            waveform_type: Type of waveform to generate (triangular, square, sawtooth)
        """
        if not NI_DAQ_AVAILABLE:
            raise ImportError("nidaqmx library is not installed. Install with: pip install nidaqmx")
        
        self.device_name = device_name
        self.voltage_range = voltage_range
        self.task = None
        self.is_running = False
        self.amplitude = 2.0   # Volts (waveform goes from -amplitude to +amplitude, so -2V to +2V)
        self.offset = 0.0      # DC offset in Volts
        self.sample_rate = 1000  # Samples per second
        self.waveform_type = waveform_type

    def generate_triangular_waveform(self, num_steps: int = None, time_of_sweep: float = None, 
                                     amplitude: float = None, offset: float = None, 
                                     num_sweeps: int = None) -> np.ndarray:
        """
        Generate a stepped triangular waveform with uniform step duration
        
        Args:
            num_steps: Number of steps per triangular period
            time_of_sweep: Total time of the sweep in seconds
            amplitude: Peak amplitude in Volts
            offset: DC offset in Volts
            num_sweeps: Number of complete triangular sweeps (periods)
        """
        num_steps = num_steps or 100
        time_of_sweep = time_of_sweep or 1.0
        amplitude = amplitude or 2.0
        offset = offset or 0.0
        num_sweeps = num_sweeps or 1

        # Ensure even number of steps for symmetric triangle
        steps_per_period = max(2, num_steps)
        if steps_per_period % 2 != 0:
            steps_per_period += 1
        
        # Calculate period from time_of_sweep and num_sweeps
        period = time_of_sweep / num_sweeps
        
        time_per_step = period / steps_per_period
        samples_per_step = max(1, int(self.sample_rate * time_per_step))
        
        # Generate triangular waveform using signal.sawtooth (width=0.5 creates symmetric triangle)
        t = np.linspace(0, 2 * np.pi * num_sweeps, steps_per_period * num_sweeps, endpoint=False)
        voltage_levels = amplitude * signal.sawtooth(t, width=0.5) + offset

        # Generate samples for each step
        waveform = np.repeat(voltage_levels, samples_per_step)
        
        return np.clip(waveform, self.voltage_range[0], self.voltage_range[1])

    def generate_square_waveform(self, num_steps: int = None, time_of_sweep: float = None, 
                                 amplitude: float = None, offset: float = None, 
                                 num_sweeps: int = None) -> np.ndarray:
        """
        Generate a stepped square waveform with uniform step duration
        """
        num_steps = num_steps or 100
        time_of_sweep = time_of_sweep or 1.0
        amplitude = amplitude or 2.0

        steps_per_period = max(2, num_steps)
        if steps_per_period % 2 != 0:
            steps_per_period += 1
        
        period = time_of_sweep / num_sweeps
        time_per_step = period / steps_per_period
        samples_per_step = max(1, int(self.sample_rate * time_per_step))
        
        # Generate square waveform
        t = np.linspace(0, 2 * np.pi * num_sweeps, steps_per_period * num_sweeps, endpoint=False)
        voltage_levels = amplitude * signal.square(t, duty=0.5) + offset
        # Generate samples for each step
        waveform = np.repeat(voltage_levels, samples_per_step)
        
        return np.clip(waveform, self.voltage_range[0], self.voltage_range[1])

    
    def generate_sawtooth_waveform(self, num_steps: int = None, time_of_sweep: float = None, 
                                 amplitude: float = None, offset: float = None, 
                                 num_sweeps: int = None) -> np.ndarray:
        """
        Generate a stepped sawtooth waveform with uniform step duration
        """
        num_steps = num_steps or 100
        time_of_sweep = time_of_sweep or 1.0
        amplitude = amplitude or 2.0
        
        steps_per_period = max(2, num_steps)
        if steps_per_period % 2 != 0:
            steps_per_period += 1
        
        period = time_of_sweep / num_sweeps
        time_per_step = period / steps_per_period
        samples_per_step = max(1, int(self.sample_rate * time_per_step))
        
        # Generate sawtooth waveform
        t = np.linspace(0, 2 * np.pi * num_sweeps, steps_per_period * num_sweeps, endpoint=False)
        voltage_levels = amplitude * signal.sawtooth(t, width=1.0) + offset
        
        # Generate samples for each step
        waveform = np.repeat(voltage_levels, samples_per_step)
        
        return np.clip(waveform, self.voltage_range[0], self.voltage_range[1])

    
    def start_continuous_waveform(self, num_steps: int = None, time_of_sweep: float = None, 
                                    amplitude: float = None, offset: float = None, 
                                    sample_rate: float = None,
                                    num_sweeps: int = None):
        """
        Start generating a continuous stepped triangular waveform
        
        Args:
            num_steps: Number of steps per period (None = calculated automatically)
            time_of_sweep: Total time of the sweep in seconds
            amplitude: Peak amplitude in Volts (None = use self.amplitude)
            offset: DC offset in Volts (None = use self.offset)
            sample_rate: Sample rate in Hz (None = use self.sample_rate)
            num_sweeps: Number of complete triangular sweeps (periods)
        """
        if self.is_running:
            self.stop()
            
        amplitude = amplitude or 2.0
        offset = offset or 0.0
        sample_rate = sample_rate or self.sample_rate
        num_sweeps = num_sweeps or 1
        time_of_sweep = time_of_sweep or 1.0

        period = time_of_sweep / num_sweeps
        
        # Calculate num_steps if not provided
        # Use a minimum step duration of 1ms to ensure reasonable resolution
        min_step_duration = 0.001  # 1ms
        if num_steps is None:
            num_steps = max(2, int(period / min_step_duration))
            
        try:
            self.task = nidaqmx.Task()
            self.task.ao_channels.add_ao_voltage_chan(
                self.device_name,
                min_val=self.voltage_range[0],
                max_val=self.voltage_range[1]
            )
            
            # Calculate parameters for one period
            # Generate one period of the waveform
            if self.waveform_type == "triangular":
                waveform = self.generate_triangular_waveform(
                    num_steps=num_steps,
                    time_of_sweep=period,
                    amplitude=amplitude,
                    offset=offset,
                    num_sweeps=num_sweeps
                )
            elif self.waveform_type == "square":
                waveform = self.generate_square_waveform(
                    num_steps=num_steps,
                    time_of_sweep=period,
                    amplitude=amplitude,
                    offset=offset,
                    num_sweeps=num_sweeps
                )
            elif self.waveform_type == "sawtooth":
                waveform = self.generate_sawtooth_waveform(
                    num_steps=num_steps,
                    time_of_sweep=period,
                    amplitude=amplitude,
                    offset=offset,
                    num_sweeps=num_sweeps
                )
            else:
                raise ValueError(f"Invalid waveform type: {self.waveform_type}")
            
            self.task.timing.cfg_samp_clk_timing(
                rate=sample_rate,
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=len(waveform)
            )
            
            writer = stream_writers.AnalogSingleChannelWriter(self.task.out_stream, auto_start=False)
            writer.write_many_sample(waveform)
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
    
    def close(self):
        self.stop()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == "__main__":
    waveform_generator = WaveformGenerator(device_name="Dev1/ao0", waveform_type="triangular")
    waveform_triangular = waveform_generator.generate_triangular_waveform(num_steps=100, time_of_sweep=10.0, amplitude=2.0, offset=0.0, num_sweeps=1)
    plt.plot(waveform_triangular)
    plt.show()
    waveform_square = waveform_generator.generate_square_waveform(num_steps=500, time_of_sweep=10.0, amplitude=2.0, offset=0.0, num_sweeps=10)
    plt.plot(waveform_square)
    plt.show()
    waveform_sawtooth = waveform_generator.generate_sawtooth_waveform(num_steps=500, time_of_sweep=10.0, amplitude=2.0, offset=0.0, num_sweeps=10)
    plt.plot(waveform_sawtooth)
    plt.show()