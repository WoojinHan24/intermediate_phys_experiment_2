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

dwf = DwfLibrary()

root = os.getcwd()
results_folder = "./amplifier_circuit_results"


def maximize_analog_out_buffer_size(configuration_parameters):
    """Select the configuration with the highest possible analog out buffer size."""
    return configuration_parameters[DwfEnumConfigInfo.AnalogOutBufferSize]


print("hello world")
with openDwfDevice(
    dwf,
    score_func=maximize_analog_out_buffer_size,
) as device:
    frequency = 10
    sine_amplitude = 3
    output_channel = device.analogOut
    # generate_sine_wave(
    #     output_channel, frequency, sine_amplitude, channel_index=0, offset=0
    # )
    generate_custom_wave(output_channel, get_noise_wave(1, 3, 2, 0.01), 1 / frequency)

    time.sleep(1)
    input_channel = device.analogIn
    result = measure_voltage(
        input_channel,
        record_time=5 / frequency,
        sampling_frequency=1000,
        number_of_channel=2,
    )


plt.plot(result["time"], result["CH1"], "k-")
# plt.plot(result["time"], result["CH2"], "r.")
plt.show()
