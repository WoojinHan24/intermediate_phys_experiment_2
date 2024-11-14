from pydwf import DwfLibrary, DwfEnumConfigInfo
from pydwf.utilities import openDwfDevice
import pydwf
import numpy as np
from libs.pydwf_wrapper import (
    generate_sine_wave,
    measure_voltage,
    generate_power_supply,
    generate_custom_wave,
    get_noise_wave,
    get_sample_wave,
)
import matplotlib.pyplot as plt
import time
import os
import pickle
from alive_progress import alive_bar
from scipy.optimize import minimize
from scipy import stats
import pandas as pd

dwf = DwfLibrary()

root = os.getcwd()
results_folder = "./amplifier_circuit_results"


def maximize_analog_out_buffer_size(configuration_parameters):
    """Select the configuration with the highest possible analog out buffer size."""
    return configuration_parameters[DwfEnumConfigInfo.AnalogOutBufferSize]


print("hello world")
output_filename = "sine reaction of amplifier circuit.xlsx"
writer = pd.ExcelWriter(output_filename, engine="xlsxwriter")
frequencies = np.logspace(np.log10(2), np.log10(200), num=2)
signal_sizes = np.arange(0, 0.25, 0.20)

with openDwfDevice(
    dwf,
    score_func=maximize_analog_out_buffer_size,
) as device:
    # frequency = 1
    noise_in_period = 2
    # sine_amplitude = 0.03
    output_channel = device.analogOut
    for frequency in frequencies:
        data_for_frequency = []

        for signal_size in signal_sizes:
            generate_power_supply(device, +5.0, -5.0)
            # generate_sine_wave(output_channel, frequency, signal_size)
            generate_custom_wave(
                output_channel,
                get_noise_wave(
                    noise_size=signal_size / 10,
                    signal_size=signal_size,
                    frequency_of_signal=frequency * noise_in_period,
                    signal_duration=1 / frequency * 1e-1,
                ),
                1 / frequency,
            )

            time.sleep(1)
            input_channel = device.analogIn
            result = measure_voltage(
                input_channel,
                record_time=20 / frequency,
                sampling_frequency=1000 * frequency,
                number_of_channel=2,
            )
            voltage_ch2_data = result["CH2"]
            min_voltage = np.min(voltage_ch2_data)
            max_voltage = np.max(voltage_ch2_data)
            data_for_frequency.append(
                {
                    "Frequency (Hz)": frequency,
                    "Input Voltage (V)": signal_size,
                    "Min Voltage (CH2)": min_voltage,
                    "Max Voltage (CH2)": max_voltage,
                }
            )
            plt.plot(result["time"], result["CH1"], "k.", label="Amplified Input")
            plt.plot(result["time"], result["CH2"], "r.", label="Peak Detector Output")
            plt.xlabel("time [s]")
            plt.ylabel("Voltage [V]")
            plt.legend(loc="upper right")
            plt.show()

        df = pd.DataFrame(data_for_frequency)
        sheet_name = f"Input frequency = {frequency:.2f}Hz"
        df.to_excel(writer, sheet_name=sheet_name, index=False)

writer.close()
