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
from scipy import stats

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
    print("time plotting started")
    create_folder(f"{results_folder}/{folder_name}/")
    for result in total_results:
        fig, ax = plt.subplots(1, 1, figsize=(8, 4))
        ax.plot(result["time"], result["CH1"], "r.", label="after rectification")
        ax.plot(result["time"], result["CH2"], "k.", label="drive input")
        ax.set_xlabel("time [s]")
        ax.set_ylabel("Voltage [V]")
        ax.set_title(
            f"Rectification circuit time plot of {result["config"]["frequency"]:.4f}Hz"
        )
        ax.legend(loc="upper right")

        fig.savefig(
            f"{results_folder}/{folder_name}/drive_frequency ({result["config"]["frequency"]:.4f}).png"
        )

        del fig


def log_log_plotter(total_results, name, bins=20):
    def get_voltage_info(result, bins):
        N = len(result["CH1"])
        max_vals = []
        min_vals = []
        for i in range(bins):
            binned_region = result["CH1"][int(N / bins * i) : int(N / bins * (i + 1))]
            max_vals.append(np.max(binned_region))
            min_vals.append(np.min(binned_region))

        return np.mean(max_vals), np.mean(min_vals), np.std(max_vals), np.std(min_vals)

    # print("log log plotting started")
    create_folder(f"{results_folder}")

    max_reactions = []
    min_reactions = []
    max_errs = []
    min_errs = []
    frequencies = []
    for result in total_results:
        max, min, max_err, min_err = get_voltage_info(result, bins)
        max_reactions.append(max)
        min_reactions.append(min)
        max_errs.append(max_err)
        min_errs.append(min_err)
        frequencies.append(result["config"]["frequency"])

    V_rips = [max_V - min_V for max_V, min_V in zip(max_reactions, min_reactions)]
    V_rips_err = [
        np.sqrt(max_e**2 + min_e**2) for max_e, min_e in zip(max_errs, min_errs)
    ]
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))

    ax.plot(frequencies, V_rips, "k.")
    ax.errorbar(frequencies, V_rips, fmt="k.", yerr=V_rips_err, linewidth=0.8)
    ax.set_xlabel("drive frequency [Hz]")
    ax.set_ylabel("Ripple Voltage [V]")
    ax.set_title(f"Ripple Voltage - Frequency of {name}")

    fig.savefig(f"{results_folder}/ripple_voltage_frequency_{name}_({bins}).png")

    log_V_rips = np.log(V_rips)
    log_V_err = [v_e / v for v_e, v in zip(V_rips_err, V_rips)]
    log_f = np.log(frequencies)
    log_f_min = -2.8
    log_f_max = +2.8
    filtered_indices = [i for i, x in enumerate(log_f) if log_f_min < x < log_f_max]
    x_filtered = [log_V_rips[i] for i in filtered_indices]
    y_filtered = [log_f[i] for i in filtered_indices]
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        x_filtered, y_filtered
    )
    print(
        f"${name}$ & ${slope:.4f}\\pm{std_err:.4f}$ & ${intercept:.4f}\\pm{std_err:.4f}$ & ${r_value**2:.4f}$  \\\\ \n \\hline"
    )
    x_con = np.linspace(-3, 3, 10)
    y_con = [slope * x + intercept for x in x_con]

    fig, ax = plt.subplots(1, 1, figsize=(6, 4))

    ax.plot(log_f, log_V_rips, "k.")
    ax.plot(x_con, y_con, "r-")
    ax.errorbar(log_f, log_V_rips, fmt="k.", yerr=log_V_err, linewidth=0.8)
    ax.plot()
    ax.set_xlabel("$log f$ drive frequency [-]")
    ax.set_ylabel("$log V$ Ripple Voltage [-]")
    ax.set_title(f"log Ripple Voltage - log Frequency of {name}")

    fig.savefig(f"{results_folder}/ripple_voltage_frequency_log_log_{name}_{bins}.png")


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


time_plotting = False
tau_fitting = False
log_log_plotting = True

C_list = [
    (1.17 * 1e-6, "1.17uF"),
    (1.57 * 1e-6, "1.57uF"),
    (2.35 * 1e-6, "2.35uF"),
    (4.7 * 1e-6, "4.7uF"),
    (100 * 1e-6, "100uF"),
]

if time_plotting:
    for C, name in C_list:
        total_results = load_results()
        filtered_results = filter_results(total_results, {"C": C})
        time_plot_plotter(filtered_results, f"raw_figs({name})")

if tau_fitting:
    fit_result = fit_R_C_from_total_results(total_results)
    print(f"fitted_result : {fit_result}")


if log_log_plotting:
    for C, name in C_list:
        total_results = load_results()
        filtered_results = filter_results(total_results, {"C": C})
        log_log_plotter(filtered_results, f"({name})")
        # log_log_plotter(filtered_results, f"({name})", bins=10)
