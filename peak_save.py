import numpy as np
import pandas as pd
from pydwf import DwfLibrary
from pydwf.utilities import openDwfDevice
import time
from libs.pydwf_wrapper import generate_sine_wave, measure_voltage
import matplotlib.pyplot as plt

# Initialize DWF Library and open device
dwf = DwfLibrary()
device = openDwfDevice(dwf)

# Set power supply
device.analogIO.channelNodeSet(0, 0, True)  # Enable V+ channel
device.analogIO.channelNodeSet(0, 1, 5.0)   # Set V+ to 5V
device.analogIO.channelNodeSet(1, 0, True)  # Enable V- channel
device.analogIO.channelNodeSet(1, 1, -5.0)  # Set V- to -5V
device.analogIO.enableSet(True)             # Enable power supply

# Define frequency and voltage ranges
frequencies = np.logspace(np.log10(2), np.log10(200), num=20)  # 10 frequencies from 2Hz to 200Hz, logarithmically spaced
voltages = np.arange(0, 0.25, 0.005)  # Voltages from 0 to 0.4V in steps of 0.05V

# Prepare an Excel writer to save data into an xlsx file
output_filename = "voltage_measurements.xlsx"
writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')

# Iterate over each frequency
for frequency in frequencies:
    # Initialize a DataFrame to store data for each frequency
    data_for_frequency = []

    # Iterate over each input voltage
    for amplitude in voltages:
        # Set the output signal with the given frequency and amplitude
        output_channel = device.analogOut
        generate_sine_wave(output_channel, frequency, amplitude)

        # Define measurement parameters
        record_time = 10 / frequency
        sampling_frequency = frequency * 1000
        number_of_channel = 2

        # Measure voltage for Ch1 and Ch2
        input_channel = device.analogIn

        time.sleep(0.5)

        data = measure_voltage(input_channel, record_time, sampling_frequency, number_of_channel)
        
        # Extract time data and voltage data
        voltage_ch2_data = data["CH2"]  # Original noisy sine wave

        print(voltage_ch2_data[0])
        # Calculate min and max values for CH2
        min_voltage = np.min(voltage_ch2_data)
        max_voltage = np.max(voltage_ch2_data)
        # print(min_voltage, max_voltage, voltage_ch2_data[0])
        # raise()
        # Append measurement results to the DataFrame
        data_for_frequency.append({
            "Frequency (Hz)": frequency,
            "Input Voltage (V)": amplitude,
            "Min Voltage (CH2)": min_voltage,
            "Max Voltage (CH2)": max_voltage
        })

    # Convert data for this frequency into a DataFrame and save to a separate sheet
    df = pd.DataFrame(data_for_frequency)
    sheet_name = f"Input frequency = {frequency:.2f}Hz"
    df.to_excel(writer, sheet_name=sheet_name, index=False)

# Close the Excel writer to save the file
writer.close()

# Reset device settings
device.analogOut.reset(-1)
device.analogIO.enableSet(False)
device.close()