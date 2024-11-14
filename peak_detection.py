from pydwf import DwfLibrary
from pydwf.utilities import openDwfDevice
import numpy as np
import matplotlib.pyplot as plt
import time
from libs.pydwf_wrapper import generate_sine_wave, measure_voltage, generate_sine_wave_with_noise, load_waveform_from_file, save_waveform_to_file, output_waveform_to_dwf

# DWF 라이브러리 초기화
dwf = DwfLibrary()
device = openDwfDevice(dwf)

# 전원 공급 설정
device.analogIO.channelNodeSet(0, 0, True)  # V+ 채널 활성화
device.analogIO.channelNodeSet(0, 1, 5.0)  # V+를 5V로 설정
device.analogIO.channelNodeSet(1, 0, True)  # V- 채널 활성화
device.analogIO.channelNodeSet(1, 1, -5.0)  # V-를 -5V로 설정
device.analogIO.enableSet(True)  # 전원 공급 활성화

# 주파수와 진폭 설정
frequency = 100  # 주파수 10Hz
amplitude = 3.0  # 진폭 4V
noise_std_dev = 1  # 노이즈 표준편차
duration = 1  # 주기 (초)
samples_per_cycle = 1000  # 샘플 수

# 노이즈가 추가된 사인파를 출력 채널에 설정
output_channel = device.analogOut
generate_sine_wave(output_channel, frequency, amplitude)

# Ch2에서 원본 신호(노이즈 추가된 사인파)를 측정하고 Ch1에서 V_out 측정
record_time = 10 / frequency  # 측정 시간 (초)
sampling_frequency = frequency * 1000  # 샘플링 주파수 (샘플/초)
number_of_channel = 2  # 채널 2개 측정

# 채널 1과 채널 2의 전압을 측정
input_channel = device.analogIn
data = measure_voltage(input_channel, record_time, sampling_frequency, number_of_channel)

# 시간 데이터와 전압 데이터를 추출
time_data = data["time"]
voltage_ch1_data = data["CH1"]  # V_out
voltage_ch2_data = data["CH2"]  # 원본 신호 (노이즈 추가된 사인파)

# 그래프 그리기
plt.figure(figsize=(10, 6))

# 원본 신호(노이즈 추가된 사인파)와 V_out 신호를 함께 그리기
plt.plot(time_data, voltage_ch2_data, label="Input Wave (Ch2)", linestyle='--')
plt.plot(time_data, voltage_ch1_data, label="Measured V_out (Ch1)", linestyle='-')

# 그래프 설정
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Original Noisy Sine Wave and Measured V_out (Ch1) over Time")
plt.legend(loc="upper right")
plt.grid(True)

# 그래프 출력
plt.show()

# 정리
device.analogOut.reset(-1)
device.analogIO.enableSet(False)
device.close()