from hardware_comms.spectrometers.yokogawa import YokogawaAQ6375E
from plottools.spectrometerdata import OSAData
import matplotlib.pyplot as plt
from time import sleep, time
from datetime import datetime
from pathlib import Path
from json import dump
from numpy import savetxt
from sched import scheduler

# Connect to PYVISA instance. Use either an alias or the full path (e.g. :INSTR) 
spectrometer = YokogawaAQ6375E("TCPIP::192.168.1.8::INSTR")

# Configure spectrometer settings
spectrometer.fix_all()
spectrometer.resolution = 0.5
spectrometer.sensitivity = "NORM"
spectrometer.wavelength_span= (1100, 1900)
spectrometer.active_trace = "TRB"
spectrometer.active_trace_status = "WRITE"
spectrometer.level_scale = "LOG"

# Configure data collection settings
start_time = datetime.now()
data_directory = Path('Z:/Research Projects/UVDCS/Data') / \
    f"{start_time.month}-{start_time.day}-{start_time.year}" / \
        f"{start_time.hour}h-{start_time.minute}m_spectrum_time_series"
spectrum_file_template = "%Hh-%Mm-%Ss.csv"
config_file = "configs.json"
interval_mins = 1 
duration_mins = 240
 


# Create folder and config file
configs = spectrometer.sweep_parameters()
data_directory.mkdir(parents=True, exist_ok=True)
with open (data_directory / config_file, 'w') as file:
    dump(configs, file)

# Create monitor plot
# f, ax = plt.subplots(1,1)
# ax.set_ylabel(f"Spectral Power ({configs["level"]["level_unit"]})")
# ax.set_xlabel("Wavelength (nm)")
# ax.grid()
# plt.show(block=False)
# plt.pause(0.1)

# Run data collection
interval_s = interval_mins * 60
duration_s = duration_mins * 60
timer = scheduler(time, sleep)

def collect_spectrum():
    current_time = datetime.now()
    hour = current_time.hour
    minute = current_time.minute
    second = current_time.second
    spectrum = spectrometer.get_new_single()
    # ax.plot(spectrum[0], spectrum[1], label=current_time.strftime('%H:%M:%S'))
    # plt.legend()
    # f.canvas.draw()
    # plt.pause(0.1)
    filename = current_time.strftime(spectrum_file_template)
    savetxt(data_directory / filename, spectrum, delimiter=',')

current_time = time()
event_time = current_time 
end_time = current_time + duration_s
while event_time < end_time:
    timer.enterabs(event_time, 1, collect_spectrum)
    event_time += interval_s
timer.run()










