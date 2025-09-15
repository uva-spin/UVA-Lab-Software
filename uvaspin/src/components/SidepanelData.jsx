import React from 'react';

function SidepanelColumns() {
    const columns = new Map([
        {
            names: 'QT',
            keys: {
                flows: {name: 'Flows', keys: ['fc501_ai', 'fc501_out', 'fc502_ai', 'fc502_out']},
                levels: {name: 'Levels', keys: ['lit501_ai']},
                pressures: {name: 'Pressures', keys: ['pt501_ai', 'pt502_ai', 'pt503_ai', 'pt504_ai']},
                temperatures: {name: 'Temperatures', keys: ['ait501_ai', 'ti501_ai', 'ti502_ai', 'ti503_ai', 'ti504_ai', 'ti505_ai', 'ti523_ai']},
            },
        },
        {
            names: "Pressures",
            keys: ['root_exhaust_pressure', 'buffer_pressure', 'magnet_pressure', 'purifier_inlet_pressure', 'fridge_vapor_pressure', 'maxigauge_pressure', 'ivc_pressure', 'separator_flow', 'magnet_flow', 'main_flow'],
        },
        {
            name: "Temperatures",
            keys: ['thermocouple', 'magnet_bottom_temperature', 'magnet_top_temperature', 'fridge_target_top_up_temperature', 'fridge_target_top_up_center_temperature', 'fridge_target_top_down_temperature', 'fridge_target_bottom_up_temperature', 'fridge_target_bottom_up_center_temperature', 'fridge_target_bottom_down_temperature', 'fridge_target_top_cernox_temperature', 'fridge_target_bottom_cernox_temperature', 'magnet_channel_1', 'magnet_channel_2', 'magnet_channel_3', 'magnet_channel_4', 'magnet_channel_5', 'magnet_channel_6', 'magnet_channel_7', 'magnet_channel_8'],
        },
        {
            name: "Flows",
            keys: ['separator_flow', 'magnet_flow', 'main_flow', 'microwave_flow', 'heat_exchanger_flow'],
        },
        {
            name: 'NMR',
            keys: ['run_number', 'measurement_type', 'peak_amp', 'peak_center', 'beam_on', 'rf_level', 'if_atten', 'he_temperature', 'he_pressure', 'nmr_channel', 'temperature', 'calibration_constant', 'polarization', 'polarization_std', 'snr', 'step_width', 'center_freq', 'freq_span', 'area', 'phase_voltage', 'tune_voltage'],
        }
    ]);
    return columns;
}



const SidepanelData = [
    {
        title: "QT",
        columns: [SidepanelColumns()[0].keys.flows, SidepanelColumns()[0].keys.levels, SidepanelColumns()[0].keys.pressures, SidepanelColumns()[0].keys.temperatures],
    },
    {
        title: "Pressures",
        columns: SidepanelColumns()[1].keys,
    },
    {
        title: "Temperatures",
        columns: SidepanelColumns()[2].keys,
    },
    {
        title: "Flows",
        columns: SidepanelColumns()[3].keys,
    },
    {
        title: "NMR",
        columns: SidepanelColumns()[4].keyss    ,
    }
]

export default SidepanelData;
    