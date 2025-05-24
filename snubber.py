import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, NullFormatter

# 设置页面标题和配置
st.set_page_config(page_title="RC缓冲电路计算器", layout="wide")
st.title("RC缓冲电路计算器")

# 辅助函数：格式化数值和单位
def format_value(value, prefixes=['p', 'n', 'μ', 'm', '', 'k', 'M', 'G']):
    if value == 0:
        return "0"
    
    exponent = min(max(int(np.floor(np.log10(abs(value))/3)), -4), 3)
    prefix = prefixes[exponent + 4]
    scaled_value = value / (10**(exponent*3))
    
    # 根据数值大小确定小数位数
    if abs(scaled_value) >= 100:
        return f"{scaled_value:.0f} {prefix}"
    elif abs(scaled_value) >= 10:
        return f"{scaled_value:.1f} {prefix}"
    else:
        return f"{scaled_value:.2f} {prefix}"

# 计算方法选择（下拉选项框）
method = st.selectbox("选择计算方法", ["LCR测分布电容", "示波器测振荡频率"])

# LCR测分布电容
if method == "LCR测分布电容":
    st.subheader("LCR测分布电容")
    
    # 水平布局输入框
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fr1_mhz = st.number_input("振荡频率 fr1 (MHz)", min_value=0.0, value=0.1, step=0.01)
    with col2:
        c_par_pf = st.number_input("分布电容 Cpar (pF)", min_value=0.0, value=1.0, step=0.1)
    with col3:
        fs_khz = st.number_input("开关频率 fs (kHz)", min_value=0.0, value=50.0, step=1.0)
    with col4:
        v_peak = st.number_input("峰值电压 Vpeak (V)", min_value=0.0, value=200.0, step=1.0)
    
    # 转换单位
    fr1 = fr1_mhz * 1e6  # MHz 转 Hz
    c_par = c_par_pf * 1e-12  # pF 转 F
    fs = fs_khz * 1e3  # kHz 转 Hz
    
    # 计算寄生电感和特征阻抗
    with st.spinner("计算中..."):
        # 计算寄生电感 Lpar
        l_par = 1 / ((2 * np.pi * fr1) ** 2 * c_par)
        
        # 计算特征阻抗 Z
        z = np.sqrt(l_par / c_par)
        
        # 计算RC值
        r = z
        c_min = 7 * c_par
        c_max = 10 * c_par
        
        # 计算RC时间常数
        tau_min = r * c_min
        tau_max = r * c_max
        
        # 计算功率
        p_min = fs * c_min * v_peak ** 2
        p_max = fs * c_max * v_peak ** 2
    
    # 显示计算结果 - 水平布局
    st.header("计算结果")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("寄生电感 Lpar", f"{format_value(l_par)}H")
    with col2:
        st.metric("特征阻抗 Z", f"{format_value(z)}Ω")
    with col3:
        st.metric("电阻 R", f"{format_value(r)}Ω")
    with col4:
        st.metric("电容 C", f"{format_value(c_min)}F ~ {format_value(c_max)}F")
    with col5:
        st.metric("时间常数 τ", f"{format_value(tau_min)}s ~ {format_value(tau_max)}s")
    with col6:
        st.metric("电阻功率", f"{format_value(p_min)}W ~ {format_value(p_max)}W")

# 示波器测振荡频率
else:
    st.subheader("示波器测振荡频率")
    
    # 水平布局输入框
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fr1_mhz = st.number_input("振荡频率 fr1 (MHz)", min_value=0.0, value=0.1, step=0.01)
    with col2:
        fr2_mhz = st.number_input("添加电容后的振荡频率 fr2 (MHz)", min_value=0.0, value=0.08, step=0.01)
    with col3:
        c_add_pf = st.number_input("添加的电容 Cadd (pF)", min_value=0.0, value=100.0, step=1.0)
    with col4:
        fs_khz = st.number_input("开关频率 fs (kHz)", min_value=0.0, value=50.0, step=1.0)
    
    # 新增Vpeak输入
    v_peak = st.number_input("峰值电压 Vpeak (V)", min_value=0.0, value=200.0, step=1.0)
    
    # 转换单位
    fr1 = fr1_mhz * 1e6  # MHz 转 Hz
    fr2 = fr2_mhz * 1e6  # MHz 转 Hz
    c_add = c_add_pf * 1e-12  # pF 转 F
    fs = fs_khz * 1e3  # kHz 转 Hz
    
    # 计算RC值
    with st.spinner("计算中..."):
        # 计算特征阻抗 R
        r = (1 / (2 * np.pi * c_add * fr1)) * ((fr1**2 / fr2**2) - 1)
        
        # 估算电容 C
        c = 2 / (np.pi * fr1 * r)
        
        # 计算RC时间常数
        tau = r * c
        
        # 估算寄生电感 Lpar
        l_par = 1 / ((2 * np.pi * fr1) ** 2 * c)
        
        # 估算分布电容 Cpar
        c_par = 1 / ((2 * np.pi * fr1) ** 2 * l_par)
        
        # 计算功率
        p = fs * c * v_peak ** 2
    
    # 显示计算结果 - 水平布局
    st.header("计算结果")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("寄生电感 Lpar", f"{format_value(l_par)}H")
    with col2:
        st.metric("分布电容 Cpar", f"{format_value(c_par)}F")
    with col3:
        st.metric("特征阻抗 Z", f"{format_value(r)}Ω")
    with col4:
        st.metric("电阻 R", f"{format_value(r)}Ω")
    with col5:
        st.metric("电容 C", f"{format_value(c)}F")
    with col6:
        st.metric("电阻功率", f"{format_value(p)}W")

# 可视化振荡波形
st.header("波形模拟")

# 生成时间序列
t = np.linspace(0, 5/fr1, 1000)  # 显示5个振荡周期

# 根据不同方法设置阻尼系数
if method == "LCR测分布电容":
    damping_factor = 1/(2*r*c_min)
else:
    damping_factor = 1/(2*r*c)

# 模拟LC振荡波形（带阻尼）
lc_oscillation = np.exp(-t*damping_factor) * np.sin(2*np.pi*fr1*t)  # 带阻尼的正弦波

# 模拟RC对LC振荡的衰减效果
if method == "LCR测分布电容":
    # 使用方法1的RC值
    rc_impedance = r / np.sqrt(1 + (2*np.pi*fr1*r*c_min)**2)
    attenuation_factor = rc_impedance / r
    rc_time_constant = r * c_min
else:
    # 使用方法2的RC值
    rc_impedance = r / np.sqrt(1 + (2*np.pi*fr1*r*c)**2)
    attenuation_factor = rc_impedance / r
    rc_time_constant = r * c

# 计算LC振荡通过RC后的衰减波形
decayed_oscillation = lc_oscillation * np.exp(-t/rc_time_constant) * attenuation_factor

# 创建图表
fig, ax = plt.subplots(figsize=(12, 5))

# 绘制波形
ax.plot(t*1e6, lc_oscillation, 'b-', label='LC Oscillation (No RC)')
ax.plot(t*1e6, decayed_oscillation, 'r--', label='LC Oscillation with RC Snubber')
ax.set_title("Effect of RC Snubber on LC Oscillation")
ax.set_xlabel("Time (μs)")
ax.set_ylabel("Normalized Amplitude")
ax.grid(True)
ax.legend()

# 显示图表
st.pyplot(fig)

# 绘制RC网络的Bode图
st.header("RC网络Bode图")

# 创建频率点（对数尺度），单位转换为MHz
freq_mhz = np.logspace(-3, 3, 1000)  # 从1kHz到1GHz，单位为MHz
freq_hz = freq_mhz * 1e6  # 转换为Hz
omega = 2 * np.pi * freq_hz

# 计算RC网络的传递函数
def calculate_rc_response(r, c, omega):
    # RC低通滤波器传递函数
    h = 1 / (1 + 1j * omega * r * c)
    magnitude = 20 * np.log10(np.abs(h))  # 转换为dB
    phase = np.degrees(np.angle(h))  # 转换为度
    return magnitude, phase

# 开关频率（转换为MHz）
fs_mhz = fs_khz / 1000

# 根据选择的方法使用不同的RC值
if method == "LCR测分布电容":
    # 使用方法1的RC值（范围值）
    magnitude_min, phase_min = calculate_rc_response(r, c_min, omega)
    magnitude_max, phase_max = calculate_rc_response(r, c_max, omega)
    
    # 创建Bode图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # 幅度响应
    ax1.semilogx(freq_mhz, magnitude_min, 'b-', label=f'C = {format_value(c_min)}F')
    ax1.semilogx(freq_mhz, magnitude_max, 'r--', label=f'C = {format_value(c_max)}F')
    ax1.axvline(x=fr1_mhz, color='g', linestyle=':', label=f'fr1 = {format_value(fr1_mhz)}MHz')
    ax1.axvline(x=fs_mhz, color='m', linestyle='--', label=f'fs = {format_value(fs_mhz)}MHz')
    ax1.set_title('Magnitude Response')
    ax1.set_ylabel('Gain (dB)')
    ax1.grid(True, which="both", ls="-")
    ax1.legend()
    
    # 相位响应
    ax2.semilogx(freq_mhz, phase_min, 'b-', label=f'C = {format_value(c_min)}F')
    ax2.semilogx(freq_mhz, phase_max, 'r--', label=f'C = {format_value(c_max)}F')
    ax2.axvline(x=fr1_mhz, color='g', linestyle=':', label=f'fr1 = {format_value(fr1_mhz)}MHz')
    ax2.axvline(x=fs_mhz, color='m', linestyle='--', label=f'fs = {format_value(fs_mhz)}MHz')
    ax2.set_title('Phase Response')
    ax2.set_xlabel('Frequency (MHz)')
    ax2.set_ylabel('Phase (degrees)')
    ax2.grid(True, which="both", ls="-")
    ax2.legend()
else:
    # 使用方法2的RC值（单一值）
    magnitude, phase = calculate_rc_response(r, c, omega)
    
    # 创建Bode图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # 幅度响应
    ax1.semilogx(freq_mhz, magnitude, 'b-', label=f'C = {format_value(c)}F')
    ax1.axvline(x=fr1_mhz, color='g', linestyle=':', label=f'fr1 = {format_value(fr1_mhz)}MHz')
    ax1.axvline(x=fs_mhz, color='m', linestyle='--', label=f'fs = {format_value(fs_mhz)}MHz')
    ax1.set_title('Magnitude Response')
    ax1.set_ylabel('Gain (dB)')
    ax1.grid(True, which="both", ls="-")
    ax1.legend()
    
    # 相位响应
    ax2.semilogx(freq_mhz, phase, 'b-', label=f'C = {format_value(c)}F')
    ax2.axvline(x=fr1_mhz, color='g', linestyle=':', label=f'fr1 = {format_value(fr1_mhz)}MHz')
    ax2.axvline(x=fs_mhz, color='m', linestyle='--', label=f'fs = {format_value(fs_mhz)}MHz')
    ax2.set_title('Phase Response')
    ax2.set_xlabel('Frequency (MHz)')
    ax2.set_ylabel('Phase (degrees)')
    ax2.grid(True, which="both", ls="-")
    ax2.legend()

# 优化x轴标签显示
for ax in [ax1, ax2]:
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.xaxis.set_minor_formatter(NullFormatter())

# 显示Bode图
st.pyplot(fig)

# 精简设计建议
st.header("设计建议")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**电阻选型**：\n- 低感电阻\n- 功率降额70%\n- 合适封装")

with col2:
    st.markdown("**电容选型**：\n- 陶瓷/薄膜电容\n- 耐压>1.5×Vpeak\n- 从计算值开始调整")

with col3:
    st.markdown("**PCB布局**：\n- 靠近MOS管\n- 短粗连接线\n- 减少寄生参数")
