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
    generate_square_wave,
    count_peaks,
)
import matplotlib.pyplot as plt
import time
import os
import pickle
from alive_progress import alive_bar
from scipy.optimize import minimize
from scipy import stats
import pandas as pd
import argparse
from dotenv import load_dotenv
import os

print("Expert AD2 Runner initialized.")
dwf = DwfLibrary()

root = os.getcwd()
parser = argparse.ArgumentParser(
    description="Run expert script with a specified .env file."
)
parser.add_argument("--env", required=True, help="Path to the .env configuration file.")
args = parser.parse_args()

load_dotenv(args.env)
print(f"Configuration loaded from {args.env}")


def maximize_analog_out_buffer_size(configuration_parameters):
    """Select the configuration with the highest possible analog out buffer size."""
    return configuration_parameters[DwfEnumConfigInfo.AnalogOutBufferSize]


def load_data(key, default, print_string, cast_function):
    try:
        value = cast_function(os.getenv(key))
        print(f"{print_string} = {value} set.")
    except:
        value = default
        print(f"{print_string} = {value} set as Default - Caution!")

    return value


def create_wave_from_config(output_channel, channel_index):
    channel_name = f"W{channel_index+1}"
    W_type = load_data(f"{channel_name}_type", "none", f"{channel_name} type", str)

    if W_type == "sine":
        frequency = load_data(
            f"{channel_name}_frequency", 0.0, f"{channel_name} frequency", float
        )
        amplitude = load_data(
            f"{channel_name}_amplitude", 0.0, f"{channel_name} amplitude", float
        )
        offset = load_data(
            f"{channel_name}_offset", 0.0, f"{channel_name} offset", float
        )
        generate_sine_wave(output_channel, frequency, amplitude, channel_index, offset)
    elif W_type == "square":
        frequency = load_data(
            f"{channel_name}_frequency", 0.0, f"{channel_name} frequency", float
        )
        amplitude = load_data(
            f"{channel_name}_amplitude", 0.0, f"{channel_name} amplitude", float
        )
        offset = load_data(
            f"{channel_name}_offset", 0.0, f"{channel_name} offset", float
        )

        generate_square_wave(
            output_channel, frequency, amplitude, channel_index, offset
        )
    elif W_type == "noise":
        frequency = load_data(
            f"{channel_name}_frequency", 0.0, f"{channel_name} frequency", float
        )
        noise_size = load_data(
            f"{channel_name}_noise_size", 0.0, f"{channel_name} noise size", float
        )
        signal_size = load_data(
            f"{channel_name}_signal_size", 0.0, f"{channel_name} signal size", float
        )
        frequency_of_signal = load_data(
            f"{channel_name}_frequency_of_signal",
            0.0,
            f"{channel_name} frequency of signal",
            float,
        )
        signal_duration = load_data(
            f"{channel_name}_signal_duration",
            0.0,
            f"{channel_name}_signal_duration",
            float,
        )

        generate_custom_wave(
            output_channel,
            get_noise_wave(
                noise_size=noise_size,
                signal_size=signal_size,
                frequency_of_signal=frequency_of_signal,
                signal_duration=signal_duration,
            ),
            1 / frequency,
        )
    elif W_type != "None":
        print(f"{W_type} wave type is not implemented! for index {channel_index}")
        raise ("")
    else:
        print(f"The waveform is not selecte for {channel_name} Caution!")


with openDwfDevice(
    dwf,
    score_func=maximize_analog_out_buffer_size,
) as device:
    output_channel = device.analogOut

    positive_voltage = load_data("V+", +5.0, "V+", float)
    negative_voltage = load_data("V-", -5.0, "V-", float)

    generate_power_supply(device, positive_voltage, negative_voltage)

    create_wave_from_config(output_channel, 0)
    create_wave_from_config(output_channel, 1)

    record_time = load_data("record_time", None, "record time", float)
    if record_time == None:
        time.sleep(2000000)

    peak_count_threshold = load_data(
        "peak_count_threshold", None, "peak count threshold", float
    )
    sampling_frequency = load_data(
        "sampling_frequency", 10000, "sampling frequency", float
    )
    number_of_channel = load_data(
        "number_of_record_channel", 2, "number of channel", int
    )
    save_as = load_data("save_as", None, "export path", str)

    time.sleep(1)
    input_channel = device.analogIn
    if peak_count_threshold is not None:
        result = count_peaks(
            input_channel,
            record_time,
            sampling_frequency,
            peak_count_threshold,
            number_of_channel,
        )

        plt.step(
            result["detected time"],
            result["CH1 cummulative_number"],
            label=f"peak counts {peak_count_threshold}",
        )
        plt.xlabel("time [s]")
        plt.ylabel("cummulative peak counts []")
        plt.legend(loc="upper right")

        plt.show()
        if save_as is not None:
            data_frame = pd.DataFrame(
                {
                    "time [s]": result["detected time"],
                    "cummulative_number []": result["CH1 cummulative_number"],
                    "total measure time": record_time,
                    "peak_threshold": peak_count_threshold,
                }
            )
            print(data_frame, save_as)
            data_frame.to_excel(save_as)

    else:
        result = measure_voltage(
            input_channel,
            record_time=record_time,
            sampling_frequency=sampling_frequency,
            number_of_channel=2,
        )
        plt.plot(result["time"], result["CH1"], "k.", label="CH1 voltage")
        if number_of_channel == 2:
            plt.plot(result["time"], result["CH2"], "r.", label="CH2  voltage")
        plt.xlabel("time [s]")
        plt.ylabel("Voltage [V]")
        plt.legend(loc="upper right")
        plt.show()
        if save_as is not None:
            data_frame = pd.DataFrame(
                {
                    "time [s]": result["time"],
                    "CH1": result["CH1"],
                    "total measure time": record_time,
                }
            )
            print(data_frame, save_as)
            data_frame.to_excel(save_as)
