import numpy as np
from kwave import kspaceFirstOrder3D, makeGrid, kWaveMedium, kWaveSource, kWaveSensor

# 定义环形阵列参数
radius = 0.05  # 环形阵列半径（米）
num_elements = 32  # 阵元数量
element_spacing = 0.001  # 阵元间距（米）
frequency = 1e6  # 超声频率（Hz）
speed_of_sound = 1500  # 介质声速（m/s）
amplitude = 1  # 超声振幅

# 计算阵元位置
theta = np.linspace(0, 2 * np.pi, num_elements, endpoint=False)
element_x = radius * np.cos(theta)
element_y = radius * np.sin(theta)

# 计算焦点位置
focus_x = 0
focus_y = 0
focus_z = 0.1  # 假设焦点在 z 轴 0.1 米处

# 计算每个阵元到焦点的距离
distances = np.sqrt((element_x - focus_x) ** 2 + (element_y - focus_y) ** 2 + focus_z ** 2)

# 计算时间延迟
time_delays = (distances - radius) / speed_of_sound

# 创建计算网格
Nx = 100
Ny = 100
Nz = 100
dx = 0.001
dy = 0.001
dz = 0.001
kgrid = makeGrid(Nx, dx, Ny, dy, Nz, dz)

# 定义介质属性
medium = kWaveMedium(sound_speed=speed_of_sound)

# 配置声源
source = kWaveSource()
source.p = np.zeros((Nx, Ny, Nz))
for i in range(num_elements):
    # 生成具有一定持续时间的正弦波信号包络，这里假设持续时间为 5 个周期
    t = np.linspace(0, 5 * 1 / frequency, len(kgrid.t_array))
    signal_envelope = np.sin(2 * np.pi * frequency * t) * (t <= 5 * 1 / frequency)
    # 应用时间延迟和振幅到每个阵元的信号
    delayed_signal = amplitude * np.roll(signal_envelope, int(-time_delays[i] / kgrid.dt))
    # 根据阵元位置将信号添加到声源数组中，确保索引在有效范围内
    x_index = np.clip(int((element_x[i] + Nx/2) / dx), 0, Nx - 1)
    y_index = np.clip(int((element_y[i] + Ny/2) / dy), 0, Ny - 1)
    source.p[x_index, y_index, int(focus_z / dz)] += delayed_signal

# 配置传感器
sensor = kWaveSensor()
sensor.mask = np.zeros((Nx, Ny, Nz))
# 在焦点位置设置传感器
sensor.mask[int(focus_x / dx + Nx/2), int(focus_y / dy + Ny/2), int(focus_z / dz)] = 1

# 执行模拟
sensor_data = kspaceFirstOrder3D(kgrid, medium, source, sensor)

# 分析结果，这里可以根据需求进一步处理传感器数据，例如查看焦点处的压力等
pressure_at_focus = sensor_data[0, 0, 0]
print("焦点处的压力:", pressure_at_focus)

# 可视化结果（这里只是一个简单的示例，可能需要根据实际情况调整）
import matplotlib.pyplot as plt
plt.imshow(sensor_data[:, :, int(focus_z / dz)].T, origin='lower', extent=[0, Nx * dx, 0, Ny * dy])
plt.colorbar()
plt.xlabel('x (m)')
plt.ylabel('y (m)')
plt.title('Pressure at the focal plane')
plt.show()