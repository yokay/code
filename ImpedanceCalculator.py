import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Function to calculate the impedance of a capacitor
def impedance_capacitor(C, f):
    """
    Calculate the impedance of a capacitor.
    
    Args:
        C (float): Capacitance in Farads.
        f (float): Frequency in Hertz.
    
    Returns:
        complex: Impedance of the capacitor in Ohms.
    """
    return 1 / (2 * np.pi * f * C * 1j)

# Function to calculate the impedance of an inductor
def impedance_inductor(L, f):
    """
    Calculate the impedance of an inductor.
    
    Args:
        L (float): Inductance in Henrys.
        f (float): Frequency in Hertz.
    
    Returns:
        complex: Impedance of the inductor in Ohms.
    """
    return 2 * np.pi * f * L * 1j

# Function to calculate series impedance
def series_impedance(Z1, Z2):
    """
    Calculate the total impedance of two components in series.
    
    Args:
        Z1 (complex): Impedance of the first component.
        Z2 (complex): Impedance of the second component.
    
    Returns:
        complex: Total impedance in series.
    """
    return Z1 + Z2

# Function to calculate parallel impedance
def parallel_impedance(Z1, Z2):
    """
    Calculate the total impedance of two components in parallel.
    
    Args:
        Z1 (complex): Impedance of the first component.
        Z2 (complex): Impedance of the second component.
    
    Returns:
        complex: Total impedance in parallel.
    """
    return (Z1 * Z2) / (Z1 + Z2)

st.title('电容和电感阻抗计算器')

# Create input components with scientific notation support
C = st.number_input('电容值 (μF)', value=1e0, format="%.2e")/1e6
L = st.number_input('电感值 (μH)', value=1e0, format="%.2e")/1e6
f_min = st.number_input('最小频率 (MHz)', value=1e-6, format="%.2e")*1e6
f_max = st.number_input('最大频率 (MHz)', value=1e3, format="%.2e")*1e6

# Select connection type
connection_type = st.selectbox('连接方式', ['串联', '并联'])

# 输入典型频率，单位为 MHz
typical_frequencies_input = st.text_input('典型频率 (MHz, 用逗号分隔)', value='0.0001, 0.001, 0.01')
typical_frequencies = []
for f_str in typical_frequencies_input.split(','):
    f_str = f_str.strip()
    if f_str:
        try:
            # 将 MHz 转换为 Hz
            f = float(f_str) * 1e6
            typical_frequencies.append(f)
        except ValueError:
            st.warning(f"输入的频率 {f_str} 无效，请使用有效的数字格式（支持科学计数法，如 1e3）。")

# Generate frequency array
frequencies = np.logspace(np.log10(f_min), np.log10(f_max), 1000)

# Calculate impedance
Z_C = impedance_capacitor(C, frequencies)
Z_L = impedance_inductor(L, frequencies)

# Calculate combined impedance
if connection_type == '串联':
    Z_combined = series_impedance(Z_C, Z_L)
else:
    Z_combined = parallel_impedance(Z_C, Z_L)

# 计算典型频率下的阻抗
Z_C_typical = impedance_capacitor(C, np.array(typical_frequencies))
Z_L_typical = impedance_inductor(L, np.array(typical_frequencies))
if connection_type == '串联':
    Z_combined_typical = series_impedance(Z_C_typical, Z_L_typical)
else:
    Z_combined_typical = parallel_impedance(Z_C_typical, Z_L_typical)

# 打印典型频率下的阻抗值，显示频率单位为 MHz
st.write("典型频率下的组合阻抗:")
for f, z in zip(typical_frequencies, Z_combined_typical):
    magnitude = np.abs(z)
    phase = np.angle(z, deg=True)  # Convert phase angle to degrees
    st.write(f"频率: {f/1e6:.2f} MHz, 复数阻抗: {z:.2f}, 模: {magnitude:.2f} Ω, 相角: {phase:.2f}°")

# Plot the results
fig, ax = plt.subplots()
ax.loglog(frequencies, np.abs(Z_combined), label='Combined Impedance')

# 在图中标记典型频率点
ax.scatter(typical_frequencies, np.abs(Z_combined_typical), color='red', zorder=5, label='Typical Points')

ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Impedance (Ω)')
ax.set_title('Combined Impedance vs Frequency')
ax.legend()
ax.grid(True)

# Display the plot
st.pyplot(fig)

# Function to convert impedance to reflection coefficient
def impedance_to_gamma(Z, Z0=50):
    return (Z - Z0) / (Z + Z0)

# Calculate reflection coefficients
gamma_combined = impedance_to_gamma(Z_combined)

# Draw Smith chart
fig_smith, ax_smith = plt.subplots(figsize=(8, 8))

# Draw Smith chart grid
# Constant resistance circles
r_values = np.array([0, 0.2, 0.5, 1, 2, 5])
for r in r_values:
    center = r / (1 + r)
    radius = 1 / (1 + r)
    circle = plt.Circle((center, 0), radius, color='gray', fill=False, lw=0.5)
    ax_smith.add_artist(circle)

# Constant reactance arcs
x_values = np.array([0.2, 0.5, 1, 2, 5])
for x in x_values:
    center = 1
    radius = 1 / x
    arc = plt.Line2D([], [], color='gray', lw=0.5)
    arc.set_data(np.cos(np.linspace(0, np.pi / 2, 100)) * radius + center,
                 np.sin(np.linspace(0, np.pi / 2, 100)) * radius)
    ax_smith.add_artist(arc)
    arc = plt.Line2D([], [], color='gray', lw=0.5)
    arc.set_data(np.cos(np.linspace(0, -np.pi / 2, 100)) * radius + center,
                 np.sin(np.linspace(0, -np.pi / 2, 100)) * radius)
    ax_smith.add_artist(arc)

# Plot combined data
ax_smith.plot(np.real(gamma_combined), np.imag(gamma_combined), label='Combined', color='blue')

# Mark typical points on Smith chart
gamma_combined_typical = impedance_to_gamma(Z_combined_typical)
ax_smith.scatter(np.real(gamma_combined_typical), np.imag(gamma_combined_typical), color='red', zorder=5, label='Typical Points on Smith')

ax_smith.set_xlim(-1, 1)
ax_smith.set_ylim(-1, 1)
ax_smith.set_aspect('equal')
ax_smith.set_title('Smith Chart')
ax_smith.legend()
ax_smith.grid(False)

# Display the Smith chart
st.pyplot(fig_smith)
