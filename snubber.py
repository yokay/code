import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, NullFormatter

st.title("RC缓冲电路计算器")

def format_value(value, prefixes=['p', 'n', 'μ', 'm', '', 'k', 'M', 'G']):
    if value == 0:
        return "0"
    
    exponent = min(max(int(np.floor(np.log10(abs(value))/3)), -4), 3)
    prefix = prefixes[exponent + 4]
    scaled_value = value / (10**(exponent*3))
    
    if abs(scaled_value) >= 100:
        return f"{scaled_value:.0f} {prefix}"
    elif abs(scaled_value) >= 10:
        return f"{scaled_value:.1f} {prefix}"
    else:
        return f"{scaled_value:.2f} {prefix}"

method = st.selectbox("选择计算方法", ["LCR测分布电容", "示波器测振荡频率"])

# LCR测分布电容（范围值单独一行）
if method == "LCR测分布电容":
    st.subheader("LCR测分布电容")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1: fr1_mhz = st.number_input("振荡频率 fr1 (MHz)", min_value=0.0, value=0.1, step=0.01)
    with col2: c_par_pf = st.number_input("分布电容 Cpar (pF)", min_value=0.0, value=1.0, step=0.1)
    with col3: fs_khz = st.number_input("开关频率 fs (kHz)", min_value=0.0, value=50.0, step=1.0)
    with col4: v_peak = st.number_input("峰值电压 Vpeak (V)", min_value=0.0, value=200.0, step=1.0)
    
    fr1 = fr1_mhz * 1e6; c_par = c_par_pf * 1e-12; fs = fs_khz * 1e3
    
    with st.spinner("计算中..."):
        l_par = 1 / ((2*np.pi*fr1)**2 * c_par)
        z = np.sqrt(l_par / c_par); r = z
        c_min, c_max = 7*c_par, 10*c_par
        tau_min, tau_max = r*c_min, r*c_max
        p_min, p_max = fs*c_min*v_peak**2, fs*c_max*v_peak**2
    
    st.header("计算结果")
    
    # 第一行：非范围值
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("寄生电感 Lpar", f"{format_value(l_par)}H")
    with col2: st.metric("特征阻抗 Z", f"{format_value(z)}Ω")
    with col3: st.metric("电阻 R", f"{format_value(r)}Ω")
    
    # 第二行：范围值（单独一行）
    col4, = st.columns(1)  # 单独一列显示范围值
    with col4:
        st.metric("电容 C", f"{format_value(c_min)}F ~ {format_value(c_max)}F")
        st.metric("时间常数 τ", f"{format_value(tau_min)}s ~ {format_value(tau_max)}s")
        st.metric("电阻功率", f"{format_value(p_min)}W ~ {format_value(p_max)}W")

# 示波器测振荡频率（无范围值，保持两行）
else:
    st.subheader("示波器测振荡频率")
    col1, col2 = st.columns(2)
    
    with col1: fr1_mhz = st.number_input("振荡频率 fr1 (MHz)", min_value=0.0, value=0.1, step=0.01)
    with col2: fr2_mhz = st.number_input("添加电容后的振荡频率 fr2 (MHz)", min_value=0.0, value=0.08, step=0.01)

    col3, col4 = st.columns(2)
    with col3: c_add_pf = st.number_input("添加的电容 Cadd (pF)", min_value=0.0, value=100.0, step=1.0)
    with col4: fs_khz = st.number_input("开关频率 fs (kHz)", min_value=0.0, value=50.0, step=1.0)
    
    v_peak = st.number_input("峰值电压 Vpeak (V)", min_value=0.0, value=200.0, step=1.0)
    fr1 = fr1_mhz * 1e6; fr2 = fr2_mhz * 1e6; c_add = c_add_pf * 1e-12; fs = fs_khz * 1e3
    
    with st.spinner("计算中..."):
        r = (1 / (2*np.pi*c_add*fr1)) * ((fr1**2 / fr2**2) - 1)
        c = 2 / (np.pi*fr1*r); tau = r*c
        l_par = 1 / ((2*np.pi*fr1)**2 * c); c_par = 1 / ((2*np.pi*fr1)**2 * l_par)
        p = fs * c * v_peak ** 2
    
    st.header("计算结果")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("寄生电感 Lpar", f"{format_value(l_par)}H")
    with col2: st.metric("分布电容 Cpar", f"{format_value(c_par)}F")
    with col3: st.metric("特征阻抗 Z", f"{format_value(r)}Ω")
    
    col4, col5, col6 = st.columns(3)
    with col4: st.metric("电阻 R", f"{format_value(r)}Ω")
    with col5: st.metric("电容 C", f"{format_value(c)}F")
    with col6: st.metric("电阻功率", f"{format_value(p)}W")

# 波形模拟（保持不变）
st.header("波形模拟")
t = np.linspace(0, 5/fr1, 1000) if 'fr1' in locals() else np.linspace(0, 1e-6, 1000)
damping_factor = 1/(2*r*c_min) if method=="LCR测分布电容" and 'c_min' in locals() else 1/(2*r*c) if 'c' in locals() else 1e6
lc_oscillation = np.exp(-t*damping_factor) * np.sin(2*np.pi*fr1*t)

rc_impedance = r / np.sqrt(1 + (2*np.pi*fr1*r*c_min)**2) if method=="LCR测分布电容" and 'c_min' in locals() else r / np.sqrt(1 + (2*np.pi*fr1*r*c)**2) if 'c' in locals() else r
attenuation_factor = rc_impedance / r if 'r' in locals() else 1
rc_time_constant = r*c_min if method=="LCR测分布电容" and 'c_min' in locals() else r*c if 'c' in locals() else 1e-6
decayed_oscillation = lc_oscillation * np.exp(-t/rc_time_constant) * attenuation_factor

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(t*1e6, lc_oscillation, 'b-', label='LC Oscillation (No RC)')
ax.plot(t*1e6, decayed_oscillation, 'r--', label='LC Oscillation with RC Snubber')
ax.set_title("Effect of RC Snubber on LC Oscillation")
ax.set_xlabel("Time (μs)"); ax.set_ylabel("Normalized Amplitude"); ax.grid(True); ax.legend()
st.pyplot(fig)

# Bode图（保持不变）
st.header("RC网络Bode图")
freq_mhz = np.logspace(-3, 3, 1000); freq_hz = freq_mhz * 1e6; omega = 2*np.pi*freq_hz

def calculate_rc_response(r, c, omega):
    h = 1 / (1 + 1j * omega * r * c)
    return 20*np.log10(np.abs(h)), np.degrees(np.angle(h))

fs_mhz = fs_khz / 1000

if method == "LCR测分布电容" and 'r' in locals() and 'c_min' in locals() and 'c_max' in locals():
    mag_min, phase_min = calculate_rc_response(r, c_min, omega)
    mag_max, phase_max = calculate_rc_response(r, c_max, omega)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    ax1.semilogx(freq_mhz, mag_min, 'b-', label=f'C = {format_value(c_min)}F')
    ax1.semilogx(freq_mhz, mag_max, 'r--', label=f'C = {format_value(c_max)}F')
    ax1.axvline(fr1_mhz, color='g', linestyle=':', label=f'fr1 = {fr1_mhz:.2f} MHz')
    ax1.axvline(fs_mhz, color='m', linestyle='--', label=f'fs = {fs_mhz:.2f} MHz')
    ax1.set_title('Magnitude Response'); ax1.set_ylabel('Gain (dB)'); ax1.grid(True); ax1.legend()
    
    ax2.semilogx(freq_mhz, phase_min, 'b-', label=f'C = {format_value(c_min)}F')
    ax2.semilogx(freq_mhz, phase_max, 'r--', label=f'C = {format_value(c_max)}F')
    ax2.axvline(fr1_mhz, color='g', linestyle=':', label=f'fr1 = {fr1_mhz:.2f} MHz')
    ax2.axvline(fs_mhz, color='m', linestyle='--', label=f'fs = {fs_mhz:.2f} MHz')
    ax2.set_title('Phase Response'); ax2.set_xlabel('Frequency (MHz)'); ax2.set_ylabel('Phase (degrees)'); ax2.grid(True); ax2.legend()
elif method == "示波器测振荡频率" and 'r' in locals() and 'c' in locals():
    mag, phase = calculate_rc_response(r, c, omega)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    ax1.semilogx(freq_mhz, mag, 'b-', label=f'C = {format_value(c)}F')
    ax1.axvline(fr1_mhz, color='g', linestyle=':', label=f'fr1 = {fr1_mhz:.2f} MHz')
    ax1.axvline(fs_mhz, color='m', linestyle='--', label=f'fs = {fs_mhz:.2f} MHz')
    ax1.set_title('Magnitude Response'); ax1.set_ylabel('Gain (dB)'); ax1.grid(True); ax1.legend()
    
    ax2.semilogx(freq_mhz, phase, 'b-', label=f'C = {format_value(c)}F')
    ax2.axvline(fr1_mhz, color='g', linestyle=':', label=f'fr1 = {fr1_mhz:.2f} MHz')
    ax2.axvline(fs_mhz, color='m', linestyle='--', label=f'fs = {fs_mhz:.2f} MHz')
    ax2.set_title('Phase Response'); ax2.set_xlabel('Frequency (MHz)'); ax2.set_ylabel('Phase (degrees)'); ax2.grid(True); ax2.legend()

for ax in [ax1, ax2] if 'ax1' in locals() else []:
    ax.xaxis.set_major_formatter(ScalarFormatter()); ax.xaxis.set_minor_formatter(NullFormatter())
if 'fig' in locals(): st.pyplot(fig)

# 设计建议（保持不变）
st.header("设计建议")
col1, col2, col3 = st.columns(3)
with col1: st.markdown("**电阻选型**：\n- 低感电阻\n- 功率降额70%\n- 合适封装")
with col2: st.markdown("**电容选型**：\n- 陶瓷/薄膜电容\n- 耐压>1.5×Vpeak\n- 从计算值开始调整")
with col3: st.markdown("**PCB布局**：\n- 靠近MOS管\n- 短粗连接线\n- 减少寄生参数")

