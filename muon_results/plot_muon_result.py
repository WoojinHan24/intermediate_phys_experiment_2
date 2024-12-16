import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

dark_thresholds = [
    "0.024",
    "0.025",
    "0.026",
    "0.027",
    "0.028",
    "0.029",
    "0.03",
    "0.031",
    "0.032",
    "0.033",
    "0.0255",
    "0.0265",
    "0.0275",
    "0.0285",
    "0.0295",
]

dark_calibration_folder = "./dark_threshold_calibration"

thresholds = []
dark_counts = []
dark_counts_errors = []

fig, ax = plt.subplots(1, 1)

for threshold in dark_thresholds:
    df = pd.read_excel(dark_calibration_folder + f"/dark({threshold}).xlsx")
    times = list(df["time [s]"])
    cummulative_number = list(df["cummulative_number []"])
    peak_threshold = list(df["peak_threshold"])[0]
    if threshold in ["0.024", "0.025", "0.026", "0.03"]:
        ax.step(
            times,
            cummulative_number,
            label=f"peak counts over {peak_threshold}V",
        )
        ax.set_xlabel("time [s]")
        ax.set_ylabel("cummulative peak counts []")
    if cummulative_number[-1] > 5000:
        continue
    thresholds.append(peak_threshold)
    dark_counts.append(cummulative_number[-1])
    dark_counts_errors.append(np.sqrt(cummulative_number[-1]))

ax.legend(loc="upper left")
fig.savefig(f"./dark_figs/dark_counts_time.pdf")

fig, ax = plt.subplots(1, 1)
ax.errorbar(
    thresholds, dark_counts, dark_counts_errors, fmt="k.", label="dark counts for 200s"
)
ax.set_xlabel("peak threshold [V]")
ax.set_ylabel("dark counts")
ax.legend(loc="upper right")
fig.savefig(f"./dark_figs/threshold_counts.pdf")
