import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import linregress


def plot_gain(file_name):
    # Read the Excel file
    xls = pd.ExcelFile(file_name)

    frequencies = []
    a_min_values = []
    a_max_values = []
    a_min_errors = []
    a_max_errors = []

    # Iterate through each sheet in the Excel file
    for sheet_name in xls.sheet_names:
        # Extract frequency from the sheet name
        frequency = float(sheet_name.split("=")[1].split("Hz")[0].strip())
        frequencies.append(frequency)

        # Read the sheet into a DataFrame
        df = pd.read_excel(xls, sheet_name=sheet_name)

        # Perform linear regression for min and max voltages
        a_min, _, _, _, a_min_stderr = linregress(
            df["Input Voltage (V)"], df["Min Voltage (CH2)"]
        )
        a_max, _, _, _, a_max_stderr = linregress(
            df["Input Voltage (V)"], df["Max Voltage (CH2)"]
        )

        a_min_values.append(a_min)
        a_max_values.append(a_max)
        a_min_errors.append(a_min_stderr)
        a_max_errors.append(a_max_stderr)

    # Plotting the results
    plt.figure(figsize=(10, 6))
    # plt.plot(frequencies, a_min_values, "ko", label="Min Voltage Gain")
    # plt.plot(
    #     frequencies,
    #     a_max_values,
    #     "ro",
    #     label="Max Voltage Gain",
    # )
    plt.errorbar(
        frequencies, a_min_values, fmt="ko", yerr=a_min_errors, label="Min Voltage Gain"
    )
    plt.errorbar(
        frequencies,
        a_max_values,
        fmt="ro",
        yerr=a_max_errors,
        label="Max Voltage Gain",
    )
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Gain []")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.show()


def plot_first_sheet_regression(file_name):
    # Read the Excel file
    xls = pd.ExcelFile(file_name)
    first_sheet_name = xls.sheet_names[0]

    # Read the first sheet into a DataFrame
    df = pd.read_excel(xls, sheet_name=first_sheet_name)

    # Perform linear regression for min and max voltages
    a_min, b_min, _, _, _ = linregress(df["Input Voltage (V)"], df["Min Voltage (CH2)"])
    a_max, b_max, _, _, _ = linregress(df["Input Voltage (V)"], df["Max Voltage (CH2)"])

    # Generate linear regression lines
    input_voltage = df["Input Voltage (V)"]
    min_voltage_fit = a_min * input_voltage + b_min
    max_voltage_fit = a_max * input_voltage + b_max

    # Plotting the min and max voltage data and their linear regression results
    plt.figure(figsize=(10, 6))
    plt.scatter(
        input_voltage,
        df["Min Voltage (CH2)"],
        label="Min Voltage",
        color="blue",
        alpha=0.6,
    )
    plt.plot(
        input_voltage,
        min_voltage_fit,
        label="Linear Fit (Min Voltage)",
        color="blue",
        linestyle="--",
    )
    plt.scatter(
        input_voltage,
        df["Max Voltage (CH2)"],
        label="Max Voltage",
        color="red",
        alpha=0.6,
    )
    plt.plot(
        input_voltage,
        max_voltage_fit,
        label="Linear Fit (Max Voltage)",
        color="red",
        linestyle="--",
    )
    plt.xlabel("Input Voltage [V]")
    plt.ylabel("Output Voltage [V]")
    plt.legend()
    plt.grid(True)
    plt.show()


plot_gain("./peak_detection_results/integrated sine reaction of amplifier circuit.xlsx")
plot_gain("./peak_detection_results/sine reaction of peak detector.xlsx")

plot_first_sheet_regression(
    "./peak_detection_results/integrated sine reaction of amplifier circuit.xlsx"
)
plot_first_sheet_regression(
    "./peak_detection_results/sine reaction of peak detector.xlsx"
)
