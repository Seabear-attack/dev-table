from pathlib import Path
from plottools.spectrometerdata import readFromFiles
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pandas import read_csv, concat, to_datetime, read_excel
from datetime import datetime
import matplotlib.dates as mdates

# Load data files
data_path_1 = Path(r"Z:/Research Projects/UVDCS\Data/6-6-2025/mikey_power_into_ZnO_4hrs.csv")
data_1 = read_csv(data_path_1, delimiter=";", skiprows=14)

data_path_2 = Path(r"Z:/Research Projects/UVDCS\Data/6-6-2025/mikey_power_into_ZnO_4hrs_2.csv")
data_2 = read_csv(data_path_2, delimiter=";", skiprows=14)

data = concat([data_1,data_2], ignore_index=True)

temp_data_path = Path(r"Z:/Research Projects/UVDCS\Data/6-6-2025/ambient_temp.xlsx")
temp_data = read_excel(temp_data_path, skiprows=6)
# Strip out time data
# for time in data["Time of day (hh:mm:ss) "]: 
    # time = datetime.strptime(time, " %H:%M:%S.%f")
data["Time of day (hh:mm:ss) "] = to_datetime(data["Time of day (hh:mm:ss) "],format=r" %H:%M:%S.%f")
data['Power (W)'] = data['Power (W)'].str.replace(',', '.', regex=False).astype(float)

temp_data["Time"] = to_datetime(temp_data["Time"])
common_date = datetime.now()

# Assume both Series are parsed with pd.to_datetime() already
data["Time of day (hh:mm:ss) "] = data["Time of day (hh:mm:ss) "].apply(
    lambda t: common_date.replace(hour=t.hour, minute=t.minute, second=t.second)
)

temp_data["Time"] = temp_data["Time"].apply(
    lambda t: common_date.replace(hour=t.hour, minute=t.minute, second=t.second)
)
print(data)
print(temp_data)

ax = plt.gca()
ax2 = ax.twinx()
# ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))  # Only for numeric axes
# ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=8))  # Only for numeric axes
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
# ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

ax.plot(data["Time of day (hh:mm:ss) "], data["Power (W)"],label="Power", color='tab:red')
ax2.plot(temp_data["Time"], temp_data["8-Ambient (°C)"],label="Temperature")

ax.set_xlim(to_datetime('14:00'), to_datetime('18:00'))
ax.set_xlabel('Time')
ax.set_ylabel('Optical Power (W)')
ax2.set_ylabel('Ambient Temperature (°C)')
# Optional: rotate labels for readability
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid()
lines_1, labels_1 = ax.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax.legend(lines_1 + lines_2, labels_1 + labels_2)
plt.show()