from pydwf import (
    DwfLibrary,
    DwfAnalogOutNode,
    DwfAnalogOutFunction,
    DwfAcquisitionMode,
    DwfState,
)
from pydwf.utilities import openDwfDevice
import numpy as np


def generate_sine_wave(output_channel, frequency, amplitude):
    # this generates sine wave at W1 - ground in respective frequency and amplitude.
    # returns nothing, and there are no methods to stop this yet.
    CH1 = 0
    node = DwfAnalogOutNode.Carrier
    output_channel.reset(CH1)

    output_channel.nodeEnableSet(CH1, node, True)
    output_channel.nodeFunctionSet(CH1, node, DwfAnalogOutFunction.Sine)
    output_channel.nodeFrequencySet(CH1, node, frequency)
    output_channel.nodeAmplitudeSet(CH1, node, amplitude)

    output_channel.configure(CH1, True)


def measure_voltage(input_channel, record_time, sampling_frequency, number_of_channel):
    # this measures the voltage of CH1 for duration record time.
    # this is expected to measure the value in frequency of sampling_frequency
    # number of channel should be 1 or 2.

    if number_of_channel >= 3:
        print(
            "the voltage measuring wrapper is not be able to measure 3 or more channels yet"
        )
        raise TypeError("the number of channel issue")

    list_of_channel = range(number_of_channel)
    for channel_number in list_of_channel:
        input_channel.channelEnableSet(channel_number, True)
        input_channel.channelRangeSet(channel_number, 10.0)

    input_channel.acquisitionModeSet(DwfAcquisitionMode.Record)
    input_channel.recordLengthSet(record_time)
    input_channel.frequencySet(sampling_frequency)

    total_samples_lost = 0
    total_samples_corrupted = 0
    return_dict = dict()

    for channel_number in list_of_channel:
        return_dict[f"CH{channel_number+1}"] = []

    input_channel.configure(False, True)
    while True:
        status = input_channel.status(True)

        (current_samples_available, current_samples_lost, current_samples_corrupted) = (
            input_channel.statusRecord()
        )

        total_samples_lost += current_samples_lost
        total_samples_corrupted += current_samples_corrupted
        if current_samples_available != 0:
            for channel_number in list_of_channel:
                current_samples = input_channel.statusData(
                    channel_number, current_samples_available
                )
                return_dict[f"CH{channel_number+1}"].extend(current_samples)

        if status == DwfState.Done:
            break

    if total_samples_lost != 0 or total_samples_corrupted != 0:
        print(
            f"Warning! sample {total_samples_lost} lost, {total_samples_corrupted} corrupted"
        )

    for channel_number in list_of_channel:
        number_of_samples = len(return_dict[f"CH{channel_number+1}"])
        return_dict[f"CH{channel_number+1}"] = return_dict[f"CH{channel_number+1}"][
            -int(number_of_samples / 2) :
        ]
    times = np.linspace(0, record_time, int(number_of_samples / 2))
    return_dict["time"] = times
    return return_dict
