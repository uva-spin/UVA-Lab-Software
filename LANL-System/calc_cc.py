from area_sum import riemman_sum
import math
import re
import numpy as np

def he3_p2t(press):
    """
    Convert He3 pressure to temperature using polynomial fit.
    
    Args:
        press (float): Pressure in torr
        
    Returns:
        float: Temperature in Kelvin
    """
    a = [1.053477, 0.980106, 0.676380, 0.372692, 0.151656,
         -0.002263, 0.006596, 0.088966, -0.004770, -0.054943]
    b = 7.3
    c = 4.3
    
    # Convert from torr to kPa
    press_kpa = press * 133.3
    
    temp = 0.0
    x = (math.log(press_kpa) - b) / c
    for i in range(10):  # 0 to 9 inclusive
        temp += a[i] * (x ** i)
    return temp

def he4_p2t(press):
    """
    Convert He4 pressure to temperature using ITS90 scale.
    See Pobell, Eq 11.6, p. 201
    
    Args:
        press (float): Pressure in torr
        
    Returns:
        float: Temperature in Kelvin
    """
    a = [[1.392408, 0.527153, 0.166756, 0.050988, 0.026514,
          0.001975, -0.017976, 0.005409, 0.013259, 0.000000],
         [3.146631, 1.357655, 0.413923, 0.091159, 0.016349,
          0.001826, -0.004325, -0.004973, 0.000000, 0.000000]]
    b = [5.6, 10.3]
    c = [2.9, 1.9]
    
    # Convert from torr to kPa
    press_kpa = press * 133.3
    
    # ITS90 is broken into 2 parts: above and below 2.18K(=5082kPa)
    if press_kpa < 5082.0:
        range_idx = 0
    else:
        range_idx = 1
    
    temp = 0.0
    x = (math.log(press_kpa) - b[range_idx]) / c[range_idx]
    for i in range(10):  # 0 to 9 inclusive
        temp += a[range_idx][i] * (x ** i)
    return temp

# NMR Species data and functions
def nmr_count():
    """Return the number of NMR species we're programmed to handle."""
    return 10

def nmr_name(idx):
    """
    Get the name of NMR species by index.
    
    Args:
        idx (int): Index from 1 to nmr_count()
        
    Returns:
        str: Name of the NMR species
    """
    list_nmr_name = [None,  # Index 0 is unused
        "Proton", "Deuteron", "6Li", "7Li", "13C", 
        "14N", "15N", "129Xe", "131Xe", "Electron"
    ]
    return list_nmr_name[idx]

def nmr_spec(idx):
    """
    Get the NMR isotope specification by index.
    
    Args:
        idx (int): Index from 1 to nmr_count()
        
    Returns:
        int: Isotope specification
    """
    list_nmr_spec = [None,  # Index 0 is unused
        1, 2, 6, 7, 13, 
        14, 15, 129, 131, 1
    ]
    return list_nmr_spec[idx]

def nmr_freq(idx):
    """
    Get NMR frequency by index (MHz per Tesla).
    
    Args:
        idx (int): Index from 1 to nmr_count()
        
    Returns:
        float: Frequency in MHz per Tesla
    """
    list_nmr_freq = [None,  # Index 0 is unused
        42.5764, 6.53573, 6.2660, 16.5478, 10.706, 
        3.0776, 4.3172, 11.776, 3.5158, 28024.4
    ]
    return list_nmr_freq[idx]

def nmr_spin(idx):
    """
    Get NMR spin by index.
    
    Args:
        idx (int): Index from 1 to nmr_count()
        
    Returns:
        int: Spin value
    """
    list_nmr_spin = [None,  # Index 0 is unused
        1, 2, 2, 3, 1, 
        2, 1, 1, 3, 1
    ]
    return list_nmr_spin[idx]

def nmr_momt(idx):
    """
    Get NMR moment by index.
    
    Args:
        idx (int): Index from 1 to nmr_count()
        
    Returns:
        float: Magnetic moment value
    """
    list_nmr_momt = [None,  # Index 0 is unused
        2.79268, 0.857387, 0.82192, 3.2560, 0.70218892, 
        0.40347, 0.28298, 0.00000, 0.0000, 1838.18
    ]
    return list_nmr_momt[idx]

nmr_data = {
    1: {"name": "Proton", "spec": 1, "freq": 42.5764, "spin": 1, "momt": 2.79268},
    2: {"name": "Deuteron", "spec": 2, "freq": 6.53573, "spin": 2, "momt": 0.857387},
    3: {"name": "6Li", "spec": 6, "freq": 6.2660, "spin": 2, "momt": 0.82192},
    4: {"name": "7Li", "spec": 7, "freq": 16.5478, "spin": 3, "momt": 3.2560},
    5: {"name": "13C", "spec": 13, "freq": 10.706, "spin": 1, "momt": 0.70218892},
    6: {"name": "14N", "spec": 14, "freq": 3.0776, "spin": 2, "momt": 0.40347},
    7: {"name": "15N", "spec": 15, "freq": 4.3172, "spin": 1, "momt": 0.28298},
    8: {"name": "129Xe", "spec": 129, "freq": 11.776, "spin": 1, "momt": 0.00000},
    9: {"name": "131Xe", "spec": 131, "freq": 3.5158, "spin": 3, "momt": 0.0000},
    10: {"name": "Electron", "spec": 1, "freq": 28024.4, "spin": 1, "momt": 1838.18}
}

def process_signal_data(signal, signal_fraction=1.0):
    """
    Process real-time LabVIEW signal data (400 bins) to calculate area and value statistics.
    
    Args:
        signal (array-like): Signal data with 400 bins from LabVIEW
        signal_fraction (float): Fraction of signal to use (default 1.0 for full signal)
        
    Returns:
        dict: Dictionary containing processed data statistics
    """
    # Convert to numpy array for easier processing
    signal = np.array(signal)
    
    # Ensure we have exactly 400 bins
    if len(signal) != 400:
        raise ValueError(f"Expected 400 bins, got {len(signal)}")
    
    n_points = int(400 * signal_fraction)
    
    signal_subset = signal[n_points:len(signal)-n_points]
    

    area = np.sum(signal_subset)
    
    avg_area = np.mean(signal_subset)
    std_area = np.std(signal_subset, ddof=1) 
    
    peak_value = np.max(signal_subset)
    avg_value = np.mean(signal_subset)
    std_value = np.std(signal_subset, ddof=1)
    
    return {
        'n_pt': n_points,
        'avg_area': avg_area,
        'std_area': std_area,
        'avg_value': avg_value,
        'std_value': std_value,
        'peak_value': peak_value,
        'total_area': area,
        'signal_data': signal_subset
    }

def process_multiple_signals(signals, signal_fraction=1.0):
    """
    Process multiple real-time LabVIEW signal data (400 bins each) to calculate averaged statistics.
    
    Args:
        signals (list): List of signal data arrays, each with 400 bins from LabVIEW
        signal_fraction (float): Fraction of signal to use (default 1.0 for full signal)
        
    Returns:
        dict: Dictionary containing averaged processed data statistics
    """
    if not signals:
        raise ValueError("No signals provided")
    
    # Process each signal individually
    individual_stats = []
    for i, signal in enumerate(signals):
        try:
            stats = process_signal_data(signal, signal_fraction)
            individual_stats.append(stats)
        except Exception as e:
            print(f"Warning: Error processing signal {i}: {e}")
            continue
    
    if not individual_stats:
        raise ValueError("No valid signals could be processed")
    
    # Calculate statistics across all signals
    n_signals = len(individual_stats)
    
    # Extract arrays for statistical analysis
    all_areas = [stats['total_area'] for stats in individual_stats]
    all_avg_areas = [stats['avg_area'] for stats in individual_stats]
    all_std_areas = [stats['std_area'] for stats in individual_stats]
    all_avg_values = [stats['avg_value'] for stats in individual_stats]
    all_std_values = [stats['std_value'] for stats in individual_stats]
    all_peak_values = [stats['peak_value'] for stats in individual_stats]
    
    # Calculate mean and standard deviation across signals
    mean_area = np.mean(all_areas)
    std_area = np.std(all_areas, ddof=1) if n_signals > 1 else 0
    
    mean_avg_area = np.mean(all_avg_areas)
    std_avg_area = np.std(all_avg_areas, ddof=1) if n_signals > 1 else 0
    
    mean_avg_value = np.mean(all_avg_values)
    std_avg_value = np.std(all_avg_values, ddof=1) if n_signals > 1 else 0
    
    mean_peak_value = np.mean(all_peak_values)
    std_peak_value = np.std(all_peak_values, ddof=1) if n_signals > 1 else 0
    
    # Calculate standard error of the mean
    sem_area = std_area / np.sqrt(n_signals) if n_signals > 1 else 0
    sem_avg_area = std_avg_area / np.sqrt(n_signals) if n_signals > 1 else 0
    sem_avg_value = std_avg_value / np.sqrt(n_signals) if n_signals > 1 else 0
    
    return {
        'n_signals': n_signals,
        'n_pt': individual_stats[0]['n_pt'],  # Same for all signals
        'mean_area': mean_area,
        'std_area': std_area,
        'sem_area': sem_area,
        'mean_avg_area': mean_avg_area,
        'std_avg_area': std_avg_area,
        'sem_avg_area': sem_avg_area,
        'mean_avg_value': mean_avg_value,
        'std_avg_value': std_avg_value,
        'sem_avg_value': sem_avg_value,
        'mean_peak_value': mean_peak_value,
        'std_peak_value': std_peak_value,
        'individual_stats': individual_stats,
        'all_areas': all_areas,
        'all_avg_areas': all_avg_areas,
        'all_avg_values': all_avg_values
    }

def convert_to_temp(value_type, avg_value, std_value):
    """
    Convert value to temperature based on value type.
    
    Args:
        value_type (int): Type of input value
            1 = temperature directly
            2 = He3 pressure
            3 = He4 pressure
        avg_value (float): Average value
        std_value (float): Standard deviation of value
        
    Returns:
        dict: Dictionary containing average and standard deviation of temperature
    """
    avg_temp = 0
    if value_type == 1:  
        avg_temp = avg_value
    elif value_type == 2:  
        avg_temp = he3_p2t(avg_value)
    elif value_type == 3:  
        avg_temp = he4_p2t(avg_value)
    else:
        pass
    
    std_temp = avg_temp * (std_value / avg_value) if avg_value != 0 else 0
    
    return {
        'avg_temp': avg_temp,
        'std_temp': std_temp
    }

def eval_cal_const(species, field, avg_area, std_area, avg_temp, std_temp):
    """
    Evaluate calibration constant for NMR species.
    
    Args:
        species (int): NMR species index
        field (float): Magnetic field strength
        avg_area (float): Average area
        std_area (float): Standard deviation of area
        avg_temp (float): Average temperature
        std_temp (float): Standard deviation of temperature
        
    Returns:
        dict: Dictionary containing calibration constant and related values
    """
    nuc_magneton = 3.152451e-14
    boltz_const = 8.617385e-11
    
    nmr_name_val = nmr_name(species)
    nmr_spin_val = nmr_spin(species)
    nmr_momt_val = nmr_momt(species)
    
    spin_name = ''
    te_pol = 0
    cal_const = 0
    cal_const_err = 0
    
    if nmr_spin_val == 1:  # spin one-half
        arg = (nmr_momt_val * nuc_magneton * field) / (boltz_const * avg_temp)
        te_pol = 100 * math.tanh(arg)
        cal_const = te_pol / avg_area
        dcc_da = std_area * te_pol / (avg_area ** 2)
        dcc_partial_t = 1 / (math.cosh(arg) ** 2) * arg / avg_temp
        dcc_dt = std_temp * dcc_partial_t / avg_area
        cal_const_err = math.sqrt(dcc_da ** 2 + dcc_dt ** 2)
        spin_name = "1/2"
    elif nmr_spin_val == 2:  # spin one, 
        arg = (nmr_momt_val * nuc_magneton * field) / (boltz_const * avg_temp)
        te_pol = 100 * 2 * math.sinh(arg) / (1 + 2 * math.cosh(arg))
        cal_const = te_pol / avg_area
        dcc_da = std_area * te_pol / (avg_area ** 2)
        dcc_partial_t = (4 + 2 * math.cosh(arg)) / ((1 + 2 * math.cosh(arg)) ** 2) * arg / avg_temp
        dcc_dt = std_temp * dcc_partial_t / avg_area
        cal_const_err = math.sqrt(dcc_da ** 2 + dcc_dt ** 2)
        spin_name = "1"
    elif nmr_spin_val == 3:  # spin three-halves
        arg = (nmr_momt_val * nuc_magneton * field) / (3 * boltz_const * avg_temp)
        te_pol = 100 * (5 * math.tanh(arg) + math.tanh(arg) ** 3) / (3 * (1 + math.tanh(arg) ** 2))
        cal_const = te_pol / avg_area
        spin_name = "3/2"
    else:
        print(f"Error in determining spin for {nmr_name_val}.")
    
    return {
        'nmr_name': nmr_name_val,
        'spin_name': spin_name,
        'te_pol': te_pol,
        'cal_const': cal_const,
        'cal_const_err': cal_const_err
    }

def cc(signals, signal_fraction, specimen):
    """
    Main function to calculate calibration constant from real-time signal data.
    
    Args:
        signals (list or array-like): List of signal data arrays, each with 400 bins from LabVIEW,
                                     or single signal array (for backward compatibility)
        signal_fraction (float): Fraction of signal to use
        specimen (str): Specimen type ("ND3", "NH3", etc.)
        
    Returns:
        dict: Complete analysis results
    """
    field = 5  
    
    signal_stats = process_multiple_signals(signals, signal_fraction)
    
    avg_value = signal_stats['mean_avg_value']
    std_value = signal_stats['std_avg_value']
    avg_area = signal_stats['mean_avg_area']
    std_area = signal_stats['std_avg_area']
    
    temp_data = convert_to_temp(1, avg_value, std_value)
    
    species_map = {
        "ND3": 2,  # Deuteron
        "NH3": 1,  # Proton
    }
    
    if specimen not in species_map:
        raise ValueError(f"Specimen {specimen} not supported")
    
    species = species_map[specimen]
    
    # Calculate calibration constant
    cal_const_data = eval_cal_const(
        species, field, 
        avg_area, std_area,
        temp_data['avg_temp'], temp_data['std_temp']
    )
    
    result = {
        'specimen': specimen,
        'species': species,
        'field': field,
        'signal_stats': signal_stats,
        'temp_data': temp_data,
        'cal_const_data': cal_const_data
    }
    
    return result