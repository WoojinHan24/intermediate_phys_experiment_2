from pydwf import DwfLibrary
from pydwf.utilities import openDwfDevice
import numpy as np
from libs.pydwf_wrapper import generate_sine_wave, measure_voltage
import matplotlib.pyplot as plt
import time
import os
import pickle
from alive_progress import alive_bar
from scipy.optimize import minimize

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
                generate_sine_wave(
                    output_channel, frequency=frequency, amplitude=amplitude
                )

                time.sleep(1)
                input_channel = device.analogIn
                result = measure_voltage(
                    input_channel,
                    record_time=1 / frequency * 10,
                    sampling_frequency=frequency * 100,
                    number_of_channel=2,
                )

                config_dict = experiment_config.copy()
                config_dict["frequency"] = frequency
                config_dict["amplitude"] = amplitude
                result["config"] = config_dict

                total_results.append(result)
                bar()

    return total_results


def is_plotting_filtered(result, filter_config):
    for key in filter_config.keys():
        try:
            if result["config"][key] != filter_config[key]:
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


def time_plot_plotter(total_results, folder_name="raw_figures"):
    print("plotting started")
    create_folder(f"{results_folder}/{folder_name}/")
    for result in total_results:
        fig, ax = plt.subplots(1, 1, figsize=(16, 8))
        ax.plot(result["time"], result["CH1"], "r.", label="after rectification")
        ax.plot(result["time"], result["CH2"], "k.", label="drive input")
        ax.set_xlabel("time [s]")
        ax.set_ylabel("Voltage [V]")
        ax.set_title(f"Rectification efficiency {result["config"]["frequency"]}")
        ax.legend(loc="upper right")

        fig.savefig(
            f"{results_folder}/{folder_name}/drive_frequency ({result["config"]["frequency"]:.4f}).png"
        )

        del fig


def load_results():
    if not os.path.exists(f"{results_folder}/total_data.pkl"):
        return []
    else:
        with open(file=f"{results_folder}/total_data.pkl", mode="rb") as f:
            prev_results = pickle.load(f)
        return prev_results


def save_results(total_results, concat=True):
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


def evaluate_result(drive, time, reaction, r1, r2, c, debug=False):
    eval = 0.0
    for i, (V_d, t, V) in enumerate(zip(drive[:-1], time[:-1], reaction[:-1])):
        if V_d - V >= 0:
            r = r1
        if V_d - V < 0:
            r = r2

        dt = time[i + 1] - time[i]
        dV_exp = (V_d - V) / r / c * dt
        dV_real = reaction[i + 1] - reaction[i]

        eval += (dV_real - dV_exp) ** 2

        if debug:
            print(f"time diff : {dt}, dV_exp = {dV_exp}, real_dV = {dV_real}")

    # print(eval)
    return eval


def fit_R_C_from_total_results(total_result):

    def total_eval(r1, r2):
        eval = 0
        for result in total_result:
            drive = result["CH2"]
            time = result["time"]
            reaction = result["CH1"]
            C = result["config"]["C"]
            eval += evaluate_result(drive, time, reaction, r1, r2, C)
        return eval

    result = minimize(
        lambda x: total_eval(x[0], x[1]),
        x0=[1e3, 1e3],
    )

    # evaluate_result(drive, time, reaction, *result.x, C, debug=True)
    # raise ()

    return [result]


C_list = [1.17 * 1e-6, 1.57 * 1e-6, 2.35 * 1e-6, 4.7 * 1e-6, 100 * 1e-6]
total_results = load_results()


fit_result = fit_R_C_from_total_results(total_results)
print(f"fitted_result : {fit_result}")
# fit_list = []
# for C in C_list:
#     filtered_results = filter_results(
#         total_results,
#         filter_config={
#             "C": C,
#         },
#     )

#     for result in filtered_results:
#         fit_list.append(fit_result)


# R_1 = [x[0] for x in fit_list if x[0] < 1e5]

# plt.hist(R_1, 100)
# plt.show()
