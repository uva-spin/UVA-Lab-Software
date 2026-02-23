/**
 * Shared data structure for parameter selection across History, Averaging, and Sidebar.
 * Lab36 sidebar may include additional sensors - use getDataStructure(labType) for lab-specific overrides.
 */

export const BASE_DATA_STRUCTURE = {
  QT: {
    Pressures: ['pt501_ai', 'pt502_ai', 'pt503_ai', 'pt504_ai'],
    Flows: ['fc501_ai', 'fc501_out', 'fc502_ai', 'fc502_out'],
    Temperatures: ['ait501_ai', 'ti501_ai', 'ti502_ai', 'ti503_ai', 'ti504_ai', 'ti505_ai', 'ti523_ai'],
    'Level Indicators': ['lit501_ai'],
    'Purity Meter': ['ait501_ai'],
  },
  Pressures: [
    'root_exhaust_pressure', 'buffer_pressure', 'magnet_pressure',
    'purifier_inlet_pressure', 'fridge_vapor_pressure', 'maxigauge_seperator_inlet_pressure', 'ivc_pressure',
  ],
  Temperatures: [
    'thermocouple', 'magnet_bottom_temperature', 'magnet_top_temperature',
    'fridge_target_top_up_temperature', 'fridge_target_top_up_center_temperature',
    'fridge_target_top_down_temperature', 'fridge_target_bottom_up_temperature',
    'fridge_target_bottom_up_center_temperature', 'fridge_target_bottom_down_temperature',
    'fridge_target_top_cernox_temperature', 'fridge_target_bottom_cernox_temperature',
    'magnet_channel_1', 'magnet_channel_2', 'magnet_channel_3', 'magnet_channel_4',
    'magnet_channel_5', 'magnet_channel_6', 'magnet_channel_7', 'magnet_channel_8',
  ],
  Flows: [
    'seperator_flow', 'magnet_flow', 'main_flow', 'microwave_flow', 'heat_exchanger_flow',
  ],
  NMR: [
    'run_number', 'measurement_type', 'peak_amp', 'peak_center', 'beam_on', 'rf_level',
    'if_atten', 'he_temperature', 'he_pressure', 'nmr_channel', 'temperature',
    'calibration_constant', 'polarization', 'polarization_std', 'snr', 'step_width',
    'center_freq', 'freq_span', 'area', 'phase_voltage', 'tune_voltage',
  ],
};

/** Lab36 sidebar has additional sensors (typos preserved for DB compatibility) */
const LAB36_SIDEBAR_OVERRIDES = {
  Pressures: [
    'root_exhaust_pressure', 'buffer_pressure', 'magnet_pressure',
    'purifier_inlet_pressure', 'fridge_vapor_pressure', 'maxigauge_seperator_inlet_pressure', 'ivc_pressure',
  ],
  Temperatures: [
    ...BASE_DATA_STRUCTURE.Temperatures,
    'target_stick_buffer_top_temperature', 'target_stick_buffer_bottom_temperature',
    'target_stick_seperator_top_temperature', 'target_stick_seperator_bottom_temperature',
    'target_stick_heat_exchanger_top_temperature', 'target_stick_heat_exchanger_bottom_temperature',
    'target_stick_annealing_plate_bar_temperature', 'target_stick_annealing_plate_top_temperature',
  ],
  Flows: [
    'seperator_flow', 'magnet_flow', 'main_flow', 'microwave_flow', 'heat_exchanger_flow',
  ],
};

export function getDataStructure(labType, forSidebar = false) {
  if (!forSidebar || labType !== 'lab36') return BASE_DATA_STRUCTURE;
  return {
    ...BASE_DATA_STRUCTURE,
    ...LAB36_SIDEBAR_OVERRIDES,
  };
}

export function getQTOptions(dataStructure = BASE_DATA_STRUCTURE) {
  const qtOptions = [];
  Object.entries(dataStructure.QT).forEach(([subCategory, items]) => {
    items.forEach((item) => qtOptions.push(`${subCategory}: ${item}`));
  });
  return qtOptions;
}

export function processQTParams(qtParams) {
  return qtParams.map((param) => {
    const match = param.match(/^[^:]+:\s*(.+)$/);
    return match ? match[1].trim() : param;
  });
}

/** Strip "Category: " prefix from any param (e.g. "Pressures: pt501_ai" -> "pt501_ai") */
export function processParam(param) {
  if (typeof param !== 'string') return param;
  const match = param.match(/^[^:]+:\s*(.+)$/);
  return match ? match[1].trim() : param;
}

/** Process all selected params to ensure clean column names for the API */
export function processAllParams(selectedData) {
  const raw = [
    ...selectedData.qt,
    ...selectedData.pressures,
    ...selectedData.temperatures,
    ...selectedData.flows,
    ...selectedData.nmr,
  ];
  return raw.map(processParam).filter(Boolean);
}
