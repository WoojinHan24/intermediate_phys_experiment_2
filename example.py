from pydwf import DwfLibrary
from pydwf.utilities import openDwfDevice
import numpy as np
from libs.pydwf_wrapper import generate_sine_wave, measure_voltage
import matplotlib.pyplot as plt
import time
import os
import pickle

dwf = DwfLibrary()
root = os.getcwd()
results_folder = "./results"

with openDwfDevice(dwf) as device:
    total_results = []
    for frequency in np.linspace(2, 20, 10):
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))

        output_channel = device.analogOut
        generate_sine_wave(output_channel, frequency=frequency, amplitude=5)

        time.sleep(1)
        input_channel = device.analogIn
        result = measure_voltage(
            input_channel,
            record_time=1 / frequency * 5,
            sampling_frequency=frequency * 50,
            number_of_channel=2,
        )

        ax.plot(result["time"], result["CH1"], "k.")
        ax.plot(result["time"], result["CH2"], "r.")
        ax.set_xlabel("time [s]")
        ax.set_ylabel("voltage [V]")
        ax.set_title(f"RC circuit voltage in frequency {frequency}")
        fig.savefig(f"{results_folder}/{frequency}.png")

        total_results.append(result)


with open(file=f"{results_folder}/total_data.pkl", mode="wb") as f:
    pickle.dump(total_results, f)
    # input("Producing a 1 kHz tone on CH1. Press Enter to quit ...")
