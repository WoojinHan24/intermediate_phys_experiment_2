from pydwf import DwfLibrary
from pydwf.utilities import openDwfDevice
import numpy as np
from libs.pydwf_wrapper import generate_sine_wave, measure_voltage
import matplotlib.pyplot as plt
import time
import os
import pickle
from alive_progress import alive_bar

dwf = DwfLibrary()
root = os.getcwd()
results_folder = "./rectification_results"


def create_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def experiment(experiment_config):
    create_folder(results_folder)
    with openDwfDevice(dwf) as device:
        total_results = []
        amplitude = 5
        freq_ini = 0.02
        freq_fin = 0.2
        num = 10
        
        with alive_bar(num) as bar:
            for frequency in np.linspace(freq_ini, freq_fin, num):

                output_channel = device.analogOut
                generate_sine_wave(output_channel, frequency=frequency, amplitude=amplitude)

                time.sleep(1)
                input_channel = device.analogIn
                result = measure_voltage(
                    input_channel,
                    record_time=1 / frequency * 10,
                    sampling_frequency=frequency * 100,
                    number_of_channel=2,
                )

                config_dict = experiment_config.copy()
                config_dict["frequency"]= frequency
                config_dict["amplitude"]= amplitude
                result["config"] = config_dict

                total_results.append(result)
                bar()

    return total_results

def is_plotting_filtered(result, filter_config):
    for key in filter_config.keys():
        try:
            if result['config'][key] != filter_config[key]:
                return True
        except KeyError:
            return True
    
    return False

def filter_results(total_result, filter_config):
    filtered_result = []
    for result in total_result:
        if is_plotting_filtered(result, filter_config):
            continue
        filtered_result.append(result)
        
    return filtered_result
            

def time_plot_plotter(total_results, folder_name= "raw_figures"):
    print("plotting started")
    create_folder(f"{results_folder}/{folder_name}/")
    for result in total_results:
        fig, ax = plt.subplots(1, 1, figsize=(16, 8))
        ax.plot(result["time"], result["CH2"], "k.", label="drive input")
        ax.plot(result["time"], result["CH1"], "r.", label="after rectification")
        ax.set_xlabel("time [s]")
        ax.set_ylabel("Voltage [V]")
        ax.set_title(f"Rectification efficiency {result["config"]["frequency"]}")
        ax.legend(loc ="upper right")

        fig.savefig(f"{results_folder}/{folder_name}/drive_frequency ({result["config"]["frequency"]:.4f}).png")
        
        del fig

def load_results():
    if not os.path.exists(f"{results_folder}/total_data.pkl"):
        return []
    else:
        with open(file=f"{results_folder}/total_data.pkl", mode="rb") as f:
            prev_results = pickle.load(f)
        return prev_results

def save_results(total_results, concat = True):
    if concat:
        prev_results = load_results()
        total_results.extend(prev_results)            
        
    with open(file=f"{results_folder}/total_data.pkl", mode="wb") as f:
        pickle.dump(total_results, f)
    
    return total_results

# current_results = experiment(experiment_config= {
#     "C" : 1.17*1e-6,
#     "R" : 0,
#     "L" : 0
# })
# total_results = save_results(current_results)
total_results = load_results()
filtered_results = filter_results(total_results, filter_config = {
    "C" : 1.17*1e-6,
})
print(filtered_results[0]["config"]["frequency"], np.max(filtered_results[0]["CH1"])-np.min(filtered_results[0]["CH1"]))
# time_plot_plotter(filtered_results, folder_name = "raw_figs(1.17uF)")
