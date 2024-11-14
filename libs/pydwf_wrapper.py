from pydwf import (
    DwfLibrary,
    DwfAnalogOutNode,
    DwfAnalogOutFunction,
    DwfAcquisitionMode,
    DwfState,
    DwfAnalogOutIdle,
    DwfTriggerSource,
)
from pydwf.utilities import openDwfDevice
import numpy as np
import pydwf


def generate_sine_wave(
    output_channel, frequency, amplitude, channel_index=0, offset=0.0
):
    # this generates sine wave at W1 - ground in respective frequency and amplitude.
    # returns nothing, and there are no methods to stop this yet.
    print(
        f"Sine Wave Generated in CH{channel_index+1}\nf = {frequency:.2f}Hz, A = {amplitude:.2f}V, with Offset = {offset}V\n-----------"
    )
    node = DwfAnalogOutNode.Carrier
    output_channel.reset(channel_index)

    output_channel.nodeEnableSet(channel_index, node, True)
    output_channel.nodeFunctionSet(channel_index, node, DwfAnalogOutFunction.Sine)
    output_channel.nodeFrequencySet(channel_index, node, frequency)
    output_channel.nodeAmplitudeSet(channel_index, node, amplitude)
    output_channel.nodeOffsetSet(channel_index, node, offset)
    output_channel.configure(channel_index, True)


def generate_square_wave(
    output_channel, frequency, amplitude, channel_index=0, offset=0.0
):
    # this generates sine wave at W1 - ground in respective frequency and amplitude.
    # returns nothing, and there are no methods to stop this yet.
    print(
        f"Square Wave Generated in CH{channel_index+1}!!\nf = {frequency:.2f}Hz, A = {amplitude:.2f}V, with Offset = {offset}V\n-----------"
    )
    node = DwfAnalogOutNode.Carrier
    output_channel.reset(channel_index)

    output_channel.nodeEnableSet(channel_index, node, True)
    output_channel.nodeFunctionSet(channel_index, node, DwfAnalogOutFunction.Square)
    output_channel.nodeFrequencySet(channel_index, node, frequency)
    output_channel.nodeAmplitudeSet(channel_index, node, amplitude)
    output_channel.nodeOffsetSet(channel_index, node, offset)
    output_channel.configure(channel_index, True)


def generate_custom_wave(output_channel, wave, period, channel_index=0):
    # this generates custom wave outputs from wave and period input.
    # in period, the voltage in the list (wave) is iterates respectively
    # the signal is repeated indefinitely
    print(
        f"Custom Wave Generated in CH{channel_index+1}!!\nT = {period:.2f}Hz\n-----------"
    )
    node = DwfAnalogOutNode.Carrier
    output_channel.reset(channel_index)
    output_channel.device.triggerSet(0, DwfTriggerSource.AnalogOut1)

    output_channel.nodeEnableSet(channel_index, node, True)
    output_channel.nodeFunctionSet(channel_index, node, DwfAnalogOutFunction.Custom)
    (amplitude_min, amplitude_max) = output_channel.nodeAmplitudeInfo(
        channel_index, node
    )
    output_channel.nodeAmplitudeSet(channel_index, node, 5.0)
    output_channel.nodeOffsetSet(channel_index, node, 0.0)

    samples = wave / amplitude_max
    output_channel.nodeDataSet(channel_index, node, samples)
    output_channel.waitSet(channel_index, 0.0)
    output_channel.nodeFrequencySet(channel_index, node, 1 / period)
    output_channel.runSet(channel_index, 20.0)
    output_channel.repeatSet(channel_index, 0)
    output_channel.idleSet(channel_index, DwfAnalogOutIdle.Initial)

    output_channel.configure(False, True)


def get_noise_wave(noise_size, signal_size, frequency_of_signal, signal_duration):
    # create peak signals in signal size in frequency of signal (/s)
    # the signal width is signal_duration.
    # there are natural noise size generated in abs value of noise size
    sampling_rate = 1000
    duration = 1  # Duration in seconds
    t = np.linspace(0, duration, int(sampling_rate * duration))

    noise = noise_size * (np.random.rand(len(t)) * 2 - 1)

    signal = np.zeros_like(t)
    peak_interval = int(sampling_rate / frequency_of_signal)
    peak_length = int(sampling_rate * signal_duration)

    for i in range(0, len(t), peak_interval):
        if i < len(t):
            for j in range(peak_length):
                signal[i + j] = signal_size

    wave = noise + signal

    wave = np.clip(wave, -5, 5)
    return wave


def get_sample_wave():
    x = np.linspace(-1, 1, 10000)
    w = 0.5 * (1 + np.cos(11 * np.pi * x))
    y = 0.5 * (1 + np.cos(np.pi * x))
    waveform = -2.0 + w * y * 6.0
    print(waveform[5000])
    return waveform


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

    print(f"measuring started, wait {record_time}s")
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


def generate_power_supply(device, Positive_voltage, Negative_voltage):
    print(
        f"{pydwf.AnalogIO.channelName(device,0)[0]} set to be {Positive_voltage} which is expected to be V+"
    )
    pydwf.AnalogIO.channelNodeSet(device, 0, 0, True)
    pydwf.AnalogIO.channelNodeSet(device, 0, 1, Positive_voltage)
    pydwf.AnalogIO.enableSet(device, True)
    print(
        f"{pydwf.AnalogIO.channelName(device,1)[0]} set to be {Negative_voltage} which is expected to be V-"
    )
    pydwf.AnalogIO.channelNodeSet(device, 1, 0, True)
    pydwf.AnalogIO.channelNodeSet(device, 1, 1, Negative_voltage)
