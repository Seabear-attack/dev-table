from hardware_comms.spectrometers.yokogawa import YokogawaOSA
from plottools.spectrometerdata import OSAData
import matplotlib.pyplot as plt
from time import sleep, time
from datetime import datetime
from pathlib import Path
from json import dump
from numpy import savetxt
from sched import scheduler

# Connect to PYVISA instance. Use either an alias or the full path (e.g. :INSTR) 
spectrometer = YokogawaOSA("Yokogawa")

# Configure spectrometer settings
spectrometer.fix_all()
spectrometer.resolution = 0.5
spectrometer.sensitivity = "NORM"
# spectrometer.wavelength_span= ()
spectrometer.active_trace = "TRB"
spectrometer.active_trace_status = "WRITE"
spectrometer.level_scale = "LIN"

# Configure data collection settings
start_time = datetime.now()
data_directory = Path('Z:/Research Projects/UVDCS/Data') / \
    f"{start_time.month}-{start_time.day}-{start_time.year}" / \
        f"{start_time.hour}h-{start_time.minute}m_spectrum_time_series"
spectrum_file_template = "{hour}h-{minute}m-{second}s.csv"
config_file = "configs.json"
interval_mins = 0.25 
duration_mins = 120
 

# Create monitor plot
f, ax = plt.subplots(1,1)
plt.show(block=False)

# Create folder and config file
data_directory.mkdir(parents=True, exist_ok=True)
with open (data_directory / config_file, 'w') as file:
    dump(spectrometer.sweep_parameters(), file)

# Run data collection
interval_s = interval_mins * 60
duration_s = duration_mins * 60
timer = scheduler(time, sleep)

def collect_spectrum():
    spectrum = spectrometer.get_new_single()
    ax.plot(spectrum[0], spectrum[1])
    current_time = datetime.now()
    filename = spectrum_file_template.format(hour=current_time.hour, 
        minute=current_time.minute, second=current_time.second)
    savetxt(data_directory / filename, spectrum, delimiter=',')

current_time = time()
event_time = current_time 
end_time = current_time + duration_s
while event_time < end_time:
    timer.enterabs(event_time, 1, collect_spectrum)
    event_time += interval_s
timer.run()










