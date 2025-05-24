import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
import pandas as pd

# 设置中文字体支持
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False  # 正确显示负号
DISPLAY_PRECISION = 3  # 全局显示精度

# 格式化数值显示的辅助函数
def format_value(value, unit="", engineering=True, precision=DISPLAY_PRECISION, special_freq=False):
    """
    格式化数值显示，根据数值大小自动选择合适的单位前缀
    
    Args:
        value: 要格式化的数值
        unit: 单位名称
        engineering: 是否使用工程单位前缀
        precision: 最大小数精度
        special_freq: 是否特殊处理频率单位
    
    Returns:
        格式化后的字符串
    """
    if np.isnan(value) or np.isinf(value):
        return str(value)
    
    if engineering:
        # 使用工程前缀 (p, n, μ, m, k, M, G, T)
        prefixes = {
            1e-12: 'p', 1e-9: 'n', 1e-6: 'μ', 1e-3: 'm',
            1: '', 1e3: 'k', 1e6: 'M', 1e9: 'G', 1e12: 'T'
        }
        
        # 特殊处理频率单位，避免重复的单位前缀
        if special_freq and unit == "Hz":
            if value >= 1e12:
                return f"{value/1e12:.{precision}f} THz"
            elif value >= 1e9:
                return f"{value/1e9:.{precision}f} GHz"
            elif value >= 1e6:
                return f"{value/1e6:.{precision}f} MHz"
            elif value >= 1e3:
                return f"{value/1e3:.{precision}f} kHz"
            else:
                return f"{value:.{precision}f} Hz"
        
        # 找到最接近的工程前缀
        if abs(value) > 0:
            exponent = np.floor(np.log10(abs(value)) // 3) * 3
            magnitude = 10 ** exponent
        else:
            magnitude = 1
        
        # 确保magnitude在定义的前缀范围内
        magnitude = max(min(magnitude, 1e12), 1e-12)
        
        # 找到对应的前缀
        prefix = prefixes[magnitude]
        scaled_value = value / magnitude
        
        # 动态调整精度，避免显示不必要的零
        if abs(scaled_value) >= 100:
            # 整数部分3位或更多，只显示整数
            formatted = f"{scaled_value:.0f}"
        elif abs(scaled_value) >= 10:
            # 整数部分2位，保留1位小数
            formatted = f"{scaled_value:.1f}"
        else:
            # 整数部分1位，保留有效小数位
            # 先按最大精度格式化
            formatted = f"{scaled_value:.{precision}f}"
            
            # 移除末尾的零
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted
        
        return f"{formatted} {prefix}{unit}"
    else:
        # 普通格式化
        formatted = f"{value:.{precision}f}"
        
        # 移除末尾的零
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted
        
        return f"{formatted} {unit}"

# 单位转换函数
def convert_to_base_unit(value, unit_multiplier):
    """将带单位的值转换为基本单位"""
    return value * unit_multiplier

# 定义阻抗计算函数
def impedance_capacitor(C, ESR, f):
    """计算电容的阻抗，包括ESR"""
    if C == 0:
        return float('inf')  # 电容为0时，相当于开路
    capacitive_reactance = 1 / (2 * np.pi * f * C)
    return complex(ESR, -capacitive_reactance)

def impedance_inductor(L, DCR, f):
    """计算电感的阻抗，包括DCR"""
    if L == 0:
        return complex(DCR, 0)  # 电感为0时，相当于纯电阻DCR
    inductive_reactance = 2 * np.pi * f * L
    return complex(DCR, inductive_reactance)

def series_impedance(Z1, Z2):
    """计算两个元件串联的总阻抗"""
    return Z1 + Z2

def parallel_impedance(Z1, Z2):
    """计算两个元件并联的总阻抗"""
    # 处理NumPy数组输入
    if isinstance(Z1, np.ndarray) or isinstance(Z2, np.ndarray):
        Z1 = np.asarray(Z1)
        Z2 = np.asarray(Z2)
        
        # 创建结果数组，初始值为0
        result = np.zeros_like(Z1, dtype=complex)
        
        # 处理Z1为无穷大的情况
        mask1 = np.isinf(Z1)
        result[mask1] = Z2[mask1]
        
        # 处理Z2为无穷大的情况
        mask2 = np.isinf(Z2) & ~mask1
        result[mask2] = Z1[mask2]
        
        # 处理其他情况
        mask3 = ~(mask1 | mask2)
        result[mask3] = (Z1[mask3] * Z2[mask3]) / (Z1[mask3] + Z2[mask3])
        
        return result
    else:
        # 处理标量输入
        if Z1 == float('inf'):
            return Z2
        if Z2 == float('inf'):
            return Z1
        return (Z1 * Z2) / (Z1 + Z2)

def impedance_to_gamma(Z, Z0=50):
    """将阻抗转换为反射系数"""
    if isinstance(Z, np.ndarray):
        return np.where(Z == float('inf'), 1, (Z - Z0) / (Z + Z0))
    else:
        return 1 if Z == float('inf') else (Z - Z0) / (Z + Z0)

def impedance_to_admittance(Z):
    """将阻抗转换为导纳"""
    if isinstance(Z, np.ndarray):
        return np.where(Z == 0, float('inf'), 
                       np.where(Z == float('inf'), 0, 1 / Z))
    else:
        if Z == 0:
            return float('inf')
        if Z == float('inf'):
            return 0
        return 1 / Z

# 复数阻抗格式化函数
def format_complex_impedance(Z, precision=DISPLAY_PRECISION):
    """格式化复数阻抗为 R+jX 形式"""
    if Z == float('inf'):
        return "∞"
    
    real = np.real(Z)
    imag = np.imag(Z)
    
    # 处理实部
    real_str = format_value(real, 'Ω', precision=precision)
    
    # 处理虚部
    if imag >= 0:
        imag_str = f"+j{format_value(imag, 'Ω', precision=precision)}"
    else:
        imag_str = f"-j{format_value(abs(imag), 'Ω', precision=precision)}"
    
    return f"{real_str}{imag_str}"

# 计算LC电路在负载下的传递函数
def calculate_transfer_function(Z_source, Z_load):
    """计算电压传递函数 H = V_out/V_in = Z_load/(Z_source + Z_load)"""
    return Z_load / (Z_source + Z_load)

# 计算Bode图数据
def calculate_bode_data(frequencies, Z_source, Z_load):
    """计算Bode图的幅度和相位数据"""
    H = calculate_transfer_function(Z_source, Z_load)
    
    # 计算幅度响应 (dB)
    magnitude_db = 20 * np.log10(np.abs(H))
    
    # 计算相位响应 (度)
    phase_deg = np.angle(H, deg=True)
    
    return magnitude_db, phase_deg

# 页面标题和介绍
st.title("电容和电感阻抗计算器")
st.markdown("""
这是一个专业的阻抗计算器，可以计算电容和电感在不同频率下的阻抗特性，并以图形方式直观展示。
支持串联和并联两种连接方式，同时考虑了电容ESR和电感DCR的影响，提供更准确的计算结果。
""")

# 侧边栏参数设置
with st.sidebar:
    st.header("参数设置")
    
    # 使用容器替代选项卡组织输入参数
    st.subheader("元件参数")
    
    # 电容值输入
    cap_value = st.number_input(
        '电容值', 
        min_value=0.0, 
        max_value=1e9, 
        value=1.0, 
        format="%f",
        help="输入电容值的数值部分"
    )
    cap_unit = st.selectbox(
        '单位',
        ['F', 'mF', 'μF', 'nF', 'pF'],
        index=2,  # 默认μF
        help="选择电容值的单位"
    )
    
    # 电容ESR输入
    esr_value = st.number_input(
        '电容ESR', 
        min_value=0.0, 
        max_value=1e9, 
        value=0.1, 
        format="%f",
        help="输入电容等效串联电阻的数值部分"
    )
    esr_unit = st.selectbox(
        '单位',
        ['Ω', 'mΩ', 'μΩ'],
        index=0,  # 默认Ω
        help="选择ESR的单位"
    )
    
    # 电容单位转换
    cap_unit_multipliers = {'F': 1, 'mF': 1e-3, 'μF': 1e-6, 'nF': 1e-9, 'pF': 1e-12}
    C = convert_to_base_unit(cap_value, cap_unit_multipliers[cap_unit])
    
    # ESR单位转换
    esr_unit_multipliers = {'Ω': 1, 'mΩ': 1e-3, 'μΩ': 1e-6}
    ESR = convert_to_base_unit(esr_value, esr_unit_multipliers[esr_unit])
    
    # 电感值输入
    ind_value = st.number_input(
        '电感值', 
        min_value=0.0, 
        max_value=1e9, 
        value=1.0, 
        format="%f",
        help="输入电感值的数值部分"
    )
    ind_unit = st.selectbox(
        '单位',
        ['H', 'mH', 'μH', 'nH', 'pH'],
        index=2,  # 默认μH
        help="选择电感值的单位"
    )
    
    # 电感DCR输入
    dcr_value = st.number_input(
        '电感DCR', 
        min_value=0.0, 
        max_value=1e9, 
        value=0.1, 
        format="%f",
        help="输入电感直流电阻的数值部分"
    )
    dcr_unit = st.selectbox(
        '单位',
        ['Ω', 'mΩ', 'μΩ'],
        index=0,  # 默认Ω
        help="选择DCR的单位"
    )
    
    # 电感单位转换
    ind_unit_multipliers = {'H': 1, 'mH': 1e-3, 'μH': 1e-6, 'nH': 1e-9, 'pH': 1e-12}
    L = convert_to_base_unit(ind_value, ind_unit_multipliers[ind_unit])
    
    # DCR单位转换
    dcr_unit_multipliers = {'Ω': 1, 'mΩ': 1e-3, 'μΩ': 1e-6}
    DCR = convert_to_base_unit(dcr_value, dcr_unit_multipliers[dcr_unit])
    
    st.subheader("频率范围")
    
    # 频率范围设置
    freq_scale = st.radio(
        "频率单位", 
        ["Hz", "kHz", "MHz", "GHz"],
        index=2,
        help="选择频率显示的单位"
    )
    
    # 根据选择的频率单位调整输入范围
    freq_units = {"Hz": 1, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9}
    unit_factor = freq_units[freq_scale]
    
    f_min = st.number_input(
        f'最小频率 ({freq_scale})', 
        min_value=0.0, 
        max_value=1e9, 
        value=0.001, 
        format="%f",
        help="输入频率范围的最小值"
    ) * unit_factor  # 转换为Hz
    
    f_max = st.number_input(
        f'最大频率 ({freq_scale})', 
        min_value=0.000001, 
        max_value=1e9, 
        value=1000.0, 
        format="%f",
        help="输入频率范围的最大值"
    ) * unit_factor  # 转换为Hz
    
    # 确保f_max大于f_min
    if f_max <= f_min:
        st.error("最大频率必须大于最小频率")
        st.stop()
    
    st.subheader("显示设置")
    
    # 显示设置
    connection_type = st.selectbox(
        '连接方式', 
        ['Series', 'Parallel'],
        help="选择电容和电感的连接方式"
    )
    
    # 典型频率点设置
    typical_frequencies_input = st.text_input(
        f'典型频率 ({freq_scale}, 用逗号分隔)', 
        value='0.001, 0.01, 0.1, 1, 10, 100',
        help="输入需要特别标记的频率点，用逗号分隔"
    )
    
    # 转换典型频率为Hz
    typical_frequencies = []
    for f_str in typical_frequencies_input.split(','):
        f_str = f_str.strip()
        if f_str:
            try:
                f = float(f_str) * unit_factor  # 转换为Hz
                if f_min <= f <= f_max:
                    typical_frequencies.append(f)
                else:
                    st.warning(f"频率 {f_str} {freq_scale} 超出设置的频率范围，已忽略")
            except ValueError:
                st.warning(f"输入的频率 {f_str} 无效，请使用有效的数字格式")
    
    # 图表类型选择
    show_impedance_plot = st.checkbox("显示阻抗图", value=True)
    show_admittance_plot = st.checkbox("显示导纳图", value=False)
    show_smith_chart = st.checkbox("显示史密斯圆图", value=True)
    show_phase_plot = st.checkbox("显示相位图", value=True)
    show_bode_plot = st.checkbox("显示Bode图", value=True)
    
    # 图表样式设置
    plot_theme = st.selectbox(
        "图表主题", 
        ["亮色", "暗色"],
        index=0
    )
    
    # 设置matplotlib样式
    if plot_theme == "暗色":
        plt.style.use('dark_background')
    else:
        plt.style.use('default')
    
    st.subheader("Bode图参数")
    
    # 负载阻抗设置
    load_impedance = st.number_input(
        '负载阻抗 (Ω)',
        min_value=0.0,
        max_value=1e9,
        value=50.0,
        format="%f",
        help="输入负载阻抗值，单位为欧姆"
    )
    
    # Bode图频率范围扩展
    bode_freq_scale = st.radio(
        "Bode图频率范围",
        ["与主频率范围相同", "扩展10倍", "扩展100倍"],
        index=0,
        help="设置Bode图的频率范围，可选择比主频率范围更宽"
    )
    
    # 计算Bode图频率范围
    if bode_freq_scale == "扩展10倍":
        bode_f_min = f_min / 10
        bode_f_max = f_max * 10
    elif bode_freq_scale == "扩展100倍":
        bode_f_min = f_min / 100
        bode_f_max = f_max * 100
    else:
        bode_f_min = f_min
        bode_f_max = f_max
    
    # Bode图频率点数
    bode_num_points = st.slider(
        "Bode图计算点数",
        min_value=100,
        max_value=5000,
        value=1000,
        step=100,
        help="设置Bode图计算的频率点数，点数越多越精确"
    )
    
    # 创建Bode图频率数组
    if bode_f_min == 0:
        bode_frequencies = np.linspace(0, bode_f_max, bode_num_points)
    else:
        bode_frequencies = np.logspace(np.log10(bode_f_min), np.log10(bode_f_max), bode_num_points)

# 处理频率范围包含0的情况
if f_min == 0:
    # 创建一个包含0的特殊频率数组
    frequencies = np.linspace(0, f_max, 1000)
else:
    # 正常对数分布
    frequencies = np.logspace(np.log10(f_min), np.log10(f_max), 1000)

# 根据电容和电感的值决定计算方式
if C == 0 and L == 0:
    # 电容和电感都为0，表示都没有
    Z_combined = np.full_like(frequencies, float('inf'), dtype=complex)
    Z_C = np.full_like(frequencies, float('inf'), dtype=complex)
    Z_L = np.full_like(frequencies, 0, dtype=complex)
    st.warning("警告：电容和电感均为0，表示电路中没有电容和电感元件")
    
    # 如果没有谐振频率，选择一个典型频率作为代表
    if typical_frequencies:
        resonance_freq = typical_frequencies[len(typical_frequencies)//2]  # 选择中间的典型频率
        st.info(f"已选择典型频率 {format_value(resonance_freq, 'Hz', special_freq=True)} 作为参考频率")
    else:
        resonance_freq = frequencies[len(frequencies)//2]  # 选择频率范围中间的点
        st.info(f"已选择频率范围中点 {format_value(resonance_freq, 'Hz', special_freq=True)} 作为参考频率")
    
    resonance_impedance = Z_combined[np.abs(frequencies - resonance_freq).argmin()]
elif C == 0:
    # 电容为0，表示只有电感
    Z_L = np.array([impedance_inductor(L, DCR, f) for f in frequencies])
    Z_combined = Z_L
    Z_C = np.full_like(frequencies, float('inf'), dtype=complex)
    st.info("提示：电容为0，表示电路中只有电感元件")
    
    # 选择一个典型频率作为谐振频率
    if typical_frequencies:
        resonance_freq = typical_frequencies[len(typical_frequencies)//2]  # 选择中间的典型频率
        st.info(f"已选择典型频率 {format_value(resonance_freq, 'Hz', special_freq=True)} 作为参考频率")
    else:
        resonance_freq = frequencies[len(frequencies)//2]  # 选择频率范围中间的点
        st.info(f"已选择频率范围中点 {format_value(resonance_freq, 'Hz', special_freq=True)} 作为参考频率")
    
    # 确保计算谐振阻抗时使用正确的索引
    resonance_idx = np.abs(frequencies - resonance_freq).argmin()
    resonance_impedance = Z_combined[resonance_idx]
elif L == 0:
    # 电感为0，表示只有电容
    Z_C = np.array([impedance_capacitor(C, ESR, f) for f in frequencies])
    Z_combined = Z_C
    Z_L = np.full_like(frequencies, 0, dtype=complex)
    st.info("提示：电感为0，表示电路中只有电容元件")
    
    # 选择一个典型频率作为谐振频率
    if typical_frequencies:
        resonance_freq = typical_frequencies[len(typical_frequencies)//2]  # 选择中间的典型频率
        st.info(f"已选择典型频率 {format_value(resonance_freq, 'Hz', special_freq=True)} 作为参考频率")
    else:
        resonance_freq = frequencies[len(frequencies)//2]  # 选择频率范围中间的点
        st.info(f"已选择频率范围中点 {format_value(resonance_freq, 'Hz', special_freq=True)} 作为参考频率")
    
    # 确保计算谐振阻抗时使用正确的索引
    resonance_idx = np.abs(frequencies - resonance_freq).argmin()
    resonance_impedance = Z_combined[resonance_idx]
else:
    # 电容和电感都不为0，正常计算
    Z_C = np.array([impedance_capacitor(C, ESR, f) for f in frequencies])
    Z_L = np.array([impedance_inductor(L, DCR, f) for f in frequencies])
    
    # 计算组合阻抗
    if connection_type == 'Series':
        Z_combined = series_impedance(Z_C, Z_L)
    else:
        Z_combined = parallel_impedance(Z_C, Z_L)
    
    # 找出谐振频率（如果存在）
    if connection_type == 'Series':
        # 串联谐振：阻抗虚部为0，阻抗最小
        if 0 in frequencies:
            # 如果频率范围包含0，检查0频率处的阻抗
            zero_freq_idx = np.where(frequencies == 0)[0][0]
            if abs(np.imag(Z_combined[zero_freq_idx])) < 1e-10:
                resonance_idx = zero_freq_idx
            else:
                # 找到最接近0虚部的点
                resonance_idx = np.argmin(np.abs(np.imag(Z_combined)))
        else:
            resonance_idx = np.argmin(np.abs(np.imag(Z_combined)))
    else:
        # 并联谐振：导纳虚部为0，阻抗最大
        Y_combined = impedance_to_admittance(Z_combined)
        if 0 in frequencies:
            zero_freq_idx = np.where(frequencies == 0)[0][0]
            if abs(np.imag(Y_combined[zero_freq_idx])) < 1e-10:
                resonance_idx = zero_freq_idx
            else:
                resonance_idx = np.argmax(np.abs(np.real(Z_combined)))
        else:
            resonance_idx = np.argmax(np.abs(np.real(Z_combined)))
    
    resonance_freq = frequencies[resonance_idx]
    resonance_impedance = Z_combined[resonance_idx]

# 计算典型频率下的阻抗
if C == 0 and L == 0:
    Z_combined_typical = np.full_like(typical_frequencies, float('inf'), dtype=complex)
    Z_C_typical = np.full_like(typical_frequencies, float('inf'), dtype=complex)
    Z_L_typical = np.full_like(typical_frequencies, 0, dtype=complex)
elif C == 0:
    # 确保典型频率下的阻抗计算使用精确频率值
    Z_L_typical = np.array([impedance_inductor(L, DCR, f) for f in typical_frequencies])
    Z_combined_typical = Z_L_typical
    Z_C_typical = np.full_like(typical_frequencies, float('inf'), dtype=complex)
    
    # 确保谐振阻抗使用精确的典型频率值
    if resonance_freq in typical_frequencies:
        idx = typical_frequencies.index(resonance_freq)
        resonance_impedance = Z_combined_typical[idx]
    else:
        # 如果谐振频率不是典型频率之一，使用最近的频率点
        resonance_idx = np.abs(frequencies - resonance_freq).argmin()
        resonance_impedance = Z_combined[resonance_idx]
elif L == 0:
    Z_C_typical = np.array([impedance_capacitor(C, ESR, f) for f in typical_frequencies])
    Z_combined_typical = Z_C_typical
    Z_L_typical = np.full_like(typical_frequencies, 0, dtype=complex)
    
    # 确保谐振阻抗使用精确的典型频率值
    if resonance_freq in typical_frequencies:
        idx = typical_frequencies.index(resonance_freq)
        resonance_impedance = Z_combined_typical[idx]
    else:
        resonance_idx = np.abs(frequencies - resonance_freq).argmin()
        resonance_impedance = Z_combined[resonance_idx]
else:
    Z_C_typical = np.array([impedance_capacitor(C, ESR, f) for f in typical_frequencies])
    Z_L_typical = np.array([impedance_inductor(L, DCR, f) for f in typical_frequencies])
    if connection_type == 'Series':
        Z_combined_typical = series_impedance(Z_C_typical, Z_L_typical)
    else:
        Z_combined_typical = parallel_impedance(Z_C_typical, Z_L_typical)

# 计算导纳
Y_combined = np.array([impedance_to_admittance(z) for z in Z_combined])
Y_combined_typical = np.array([impedance_to_admittance(z) for z in Z_combined_typical])

# 计算反射系数
gamma_combined = np.array([impedance_to_gamma(z) for z in Z_combined])
gamma_combined_typical = np.array([impedance_to_gamma(z) for z in Z_combined_typical])

# 计算相位角
phase_combined = np.array([np.angle(z, deg=True) if z != float('inf') else 90 for z in Z_combined])
phase_combined_typical = np.array([np.angle(z, deg=True) if z != float('inf') else 90 for z in Z_combined_typical])

# 计算电容品质因数
capacitive_reactance_at_resonance = 1 / (2 * np.pi * resonance_freq * C) if C != 0 else float('inf')
if ESR == 0:
    Q_capacitor = float('inf') if capacitive_reactance_at_resonance != 0 else 0
else:
    Q_capacitor = np.abs(capacitive_reactance_at_resonance) / ESR

# 计算电感品质因数
inductive_reactance_at_resonance = 2 * np.pi * resonance_freq * L if L != 0 else 0
if DCR == 0:
    Q_inductor = float('inf') if inductive_reactance_at_resonance != 0 else 0
else:
    Q_inductor = np.abs(inductive_reactance_at_resonance) / DCR

# 计算总品质因数（系统品质因数）
if connection_type == 'Series':
    # 串联谐振Q因子：X_L/R或X_C/R（在谐振点两者相等）
    R_total = ESR + DCR
    if R_total == 0:
        Q_total = float('inf') if inductive_reactance_at_resonance != 0 else 0
    else:
        Q_total = np.abs(inductive_reactance_at_resonance) / R_total
else:
    # 并联谐振Q因子：R/X_L或R/X_C（在谐振点两者相等）
    # 对于并联谐振，总阻抗接近无穷大，所以Q因子是R/X
    R_parallel = np.real(resonance_impedance)
    if R_parallel == 0:
        Q_total = 0
    else:
        if inductive_reactance_at_resonance == 0:
            Q_total = float('inf')
        else:
            Q_total = R_parallel / np.abs(inductive_reactance_at_resonance)

# 计算Bode图数据
if C == 0 and L == 0:
    Z_source_bode = np.full_like(bode_frequencies, float('inf'), dtype=complex)
elif C == 0:
    Z_source_bode = np.array([impedance_inductor(L, DCR, f) for f in bode_frequencies])
elif L == 0:
    Z_source_bode = np.array([impedance_capacitor(C, ESR, f) for f in bode_frequencies])
else:
    Z_C_bode = np.array([impedance_capacitor(C, ESR, f) for f in bode_frequencies])
    Z_L_bode = np.array([impedance_inductor(L, DCR, f) for f in bode_frequencies])
    
    if connection_type == 'Series':
        Z_source_bode = series_impedance(Z_C_bode, Z_L_bode)
    else:
        Z_source_bode = parallel_impedance(Z_C_bode, Z_L_bode)

Z_load_bode = load_impedance  # 负载阻抗是常数
magnitude_db, phase_deg = calculate_bode_data(bode_frequencies, Z_source_bode, Z_load_bode)

# 计算典型频率点的Bode图数据
magnitude_db_typical = []
phase_deg_typical = []

for f in typical_frequencies:
    if C == 0 and L == 0:
        Z_source_t = float('inf')
    elif C == 0:
        Z_source_t = impedance_inductor(L, DCR, f)
    elif L == 0:
        Z_source_t = impedance_capacitor(C, ESR, f)
    else:
        Z_C_t = impedance_capacitor(C, ESR, f)
        Z_L_t = impedance_inductor(L, DCR, f)
        
        if connection_type == 'Series':
            Z_source_t = series_impedance(Z_C_t, Z_L_t)
        else:
            Z_source_t = parallel_impedance(Z_C_t, Z_L_t)
    
    H_t = calculate_transfer_function(Z_source_t, Z_load_bode)
    magnitude_db_typical.append(20 * np.log10(np.abs(H_t)))
    phase_deg_typical.append(np.angle(H_t, deg=True))

# 显示基本信息和计算结果
st.subheader("计算结果")

# 使用两列布局显示结果
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"**电容值**: {format_value(C, 'F')}")
    st.markdown(f"**电感值**: {format_value(L, 'H')}")
    st.markdown(f"**电容ESR**: {format_value(ESR, 'Ω')}")
    st.markdown(f"**电感DCR**: {format_value(DCR, 'Ω')}")
    st.markdown(f"**连接方式**: {connection_type}")
    st.markdown(f"**负载阻抗**: {format_value(load_impedance, 'Ω')}")
    
with col2:
    st.markdown(f"**参考频率**: {format_value(resonance_freq, 'Hz', special_freq=True)}")
    st.markdown(f"**电容品质因数Qc**: {Q_capacitor:.3f}")
    st.markdown(f"**电感品质因数Ql**: {Q_inductor:.3f}")
    st.markdown(f"**总品质因数Q**: {Q_total:.3f}")
    st.markdown(f"**复数阻抗**: {format_complex_impedance(resonance_impedance, 3)}")

# 显示典型频率下的阻抗值表格
if typical_frequencies:
    st.subheader(f"典型频率 ({freq_scale}) 下的阻抗值")
    
    # 创建数据框
    data = []
    for f, z, y, gamma, phase, mag_db, phase_d in zip(
        typical_frequencies, 
        Z_combined_typical, 
        Y_combined_typical,
        gamma_combined_typical,
        phase_combined_typical,
        magnitude_db_typical,
        phase_deg_typical
    ):
        # 计算当前频率下的电容和电感品质因数
        X_C = 1 / (2 * np.pi * f * C) if C != 0 else float('inf')
        X_L = 2 * np.pi * f * L if L != 0 else 0
        Q_c = np.abs(X_C) / ESR if ESR != 0 else float('inf')
        Q_l = np.abs(X_L) / DCR if DCR != 0 else float('inf')
        
        data.append({
            "频率": format_value(f, 'Hz', special_freq=True),
            "阻抗实部 (Ω)": format_value(np.real(z), 'Ω'),
            "阻抗虚部 (Ω)": format_value(np.imag(z), 'Ω'),
            "阻抗模 (Ω)": format_value(np.abs(z), 'Ω'),
            "复数阻抗": format_complex_impedance(z,3),
            "阻抗角 (°)": f"{phase:.2f}",
            "导纳实部 (S)": format_value(np.real(y), 'S'),
            "导纳虚部 (S)": format_value(np.imag(y), 'S'),
            "反射系数实部": f"{np.real(gamma):.6f}",
            "反射系数虚部": f"{np.imag(gamma):.6f}",
            "反射系数模": f"{np.abs(gamma):.6f}",
            "反射系数角 (°)": f"{np.angle(gamma, deg=True):.2f}",
            "增益 (dB)": f"{mag_db:.2f}",
            "相位 (°)": f"{phase_d:.2f}",
            "电容Qc": f"{Q_c:.3f}",
            "电感Ql": f"{Q_l:.3f}"
        })
    
    # 显示表格 - 移除 use_container_width 参数，改用表格组件
    df = pd.DataFrame(data)
    
    # 使用表格组件替代 data frame 显示
    st.table(df)
    
    # 如果需要交互式表格，可以使用以下替代方案
    # st.dataframe(df.style.format(precision=3))

# 图表显示区域
st.subheader("图表分析")

# 使用容器替代选项卡组织不同类型的图表
if show_impedance_plot:
    st.subheader("Impedance Plot")
    
    # 创建阻抗图
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    
    # 处理阻抗为无穷大的情况
    impedance_magnitudes = np.array([np.abs(z) if z != float('inf') else 1e10 for z in Z_combined])
    
    # 添加阻抗模轨迹
    ax1.semilogx(frequencies/unit_factor, impedance_magnitudes, 'b-', linewidth=2, label='Impedance Magnitude (Ω)')
    
    # 添加典型频率点
    ax1.plot(
        np.array(typical_frequencies)/unit_factor, 
        [np.abs(z) if z != float('inf') else 1e10 for z in Z_combined_typical],
        'ro', markersize=6, label='Typical Frequencies'
    )
    
    # 添加谐振点
    ax1.plot(
        resonance_freq/unit_factor, 
        np.abs(resonance_impedance) if resonance_impedance != float('inf') else 1e10,
        'gD', markersize=8, label='Resonant Point'
    )
    
    # 添加谐振点标注
    ax1.annotate(
        f"Resonance: {format_value(np.abs(resonance_impedance), 'Ω')}",
        xy=(resonance_freq/unit_factor, np.abs(resonance_impedance)),
        xytext=(10, 10),
        textcoords='offset points',
        arrowprops=dict(arrowstyle='->', color='green')
    )
    
    # 设置坐标轴和标题
    ax1.set_title(f'Impedance Magnitude vs Frequency ({connection_type})')
    ax1.set_xlabel(f'Frequency ({freq_scale})')
    ax1.set_ylabel('Impedance (Ω)')
    ax1.set_yscale('log')
    ax1.grid(True, which='both', linestyle='--', alpha=0.5)
    ax1.legend()
    
    # 显示阻抗图
    st.pyplot(fig1)

if show_admittance_plot:
    st.subheader("Admittance Plot")
    
    # 创建导纳图
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    
    # 处理导纳为无穷大的情况
    admittance_magnitudes = np.array([np.abs(y) if y != float('inf') else 1e10 for y in Y_combined])
    
    # 添加导纳模轨迹
    ax2.semilogx(frequencies/unit_factor, admittance_magnitudes, 'b-', linewidth=2, label='Admittance Magnitude (S)')
    
    # 添加典型频率点
    ax2.plot(
        np.array(typical_frequencies)/unit_factor, 
        [np.abs(y) if y != float('inf') else 1e10 for y in Y_combined_typical],
        'ro', markersize=6, label='Typical Frequencies'
    )
    
    # 设置坐标轴和标题
    ax2.set_title(f'Admittance Magnitude vs Frequency ({connection_type})')
    ax2.set_xlabel(f'Frequency ({freq_scale})')
    ax2.set_ylabel('Admittance (S)')
    ax2.set_yscale('log')
    ax2.grid(True, which='both', linestyle='--', alpha=0.5)
    ax2.legend()
    
    # 显示导纳图
    st.pyplot(fig2)

if show_phase_plot:
    st.subheader("Phase Plot")
    
    # 创建相位图
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    
    # 添加相位轨迹
    ax3.semilogx(frequencies/unit_factor, phase_combined, 'b-', linewidth=2, label='Phase Angle (°)')
    
    # 添加典型频率点
    ax3.plot(
        np.array(typical_frequencies)/unit_factor, 
        phase_combined_typical,
        'ro', markersize=6, label='Typical Frequencies'
    )
    
    # 添加谐振点
    ax3.plot(
        resonance_freq/unit_factor, 
        phase_combined[np.abs(frequencies - resonance_freq).argmin()],
        'gD', markersize=8, label='Resonant Point'
    )
    
    # 添加谐振点标注
    ax3.annotate(
        f"Phase: {phase_combined[np.abs(frequencies - resonance_freq).argmin()]:.2f}°",
        xy=(resonance_freq/unit_factor, phase_combined[np.abs(frequencies - resonance_freq).argmin()]),
        xytext=(10, 10),
        textcoords='offset points',
        arrowprops=dict(arrowstyle='->', color='green')
    )
    
    # 设置坐标轴和标题
    ax3.set_title(f'Phase Angle vs Frequency ({connection_type})')
    ax3.set_xlabel(f'Frequency ({freq_scale})')
    ax3.set_ylabel('Phase Angle (°)')
    ax3.grid(True, which='both', linestyle='--', alpha=0.5)
    ax3.legend()
    
    # 显示相位图
    st.pyplot(fig3)

if show_smith_chart:
    st.subheader("Smith Chart")
    
    # 创建史密斯圆图
    fig4, ax4 = plt.subplots(figsize=(8, 8))
    
    # 过滤掉无穷大的反射系数值
    valid_indices = [i for i, g in enumerate(gamma_combined) if abs(g) <= 1]
    valid_gamma = [gamma_combined[i] for i in valid_indices]
    valid_frequencies = [frequencies[i] for i in valid_indices]
    
    # 绘制史密斯圆图网格
    # 恒定电阻圆
    r_values = np.array([0, 0.2, 0.5, 1, 2, 5, 10])
    for r in r_values:
        center = r / (1 + r)
        radius = 1 / (1 + r)
        circle = plt.Circle((center, 0), radius, fill=False, color='gray', linestyle='--', alpha=0.5)
        ax4.add_artist(circle)
    
    # 恒定电抗圆
    x_values = np.array([0.2, 0.5, 1, 2, 5, 10, -0.2, -0.5, -1, -2, -5, -10])
    for x in x_values:
        if x == 0:
            continue
        center_x = 1
        center_y = 1/x
        radius = 1/abs(x)
        circle = plt.Circle((center_x, center_y), radius, fill=False, color='gray', linestyle='--', alpha=0.5)
        ax4.add_artist(circle)
    
    # 绘制阻抗轨迹
    real_part = np.real(valid_gamma)
    imag_part = np.imag(valid_gamma)
    ax4.plot(real_part, imag_part, 'b-', linewidth=2, label='Impedance Locus')
    
    # 绘制典型频率点
    valid_typical_indices = []
    for i, f in enumerate(typical_frequencies):
        if f in valid_frequencies:
            idx = valid_frequencies.index(f)
            valid_typical_indices.append(idx)
            ax4.plot(real_part[idx], imag_part[idx], 'ro', markersize=6)
            ax4.annotate(
                format_value(f, 'Hz', special_freq=True),
                xy=(real_part[idx], imag_part[idx]),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=8
            )
    
    # 绘制谐振点
    if resonance_freq in valid_frequencies:
        res_idx = valid_frequencies.index(resonance_freq)
        ax4.plot(real_part[res_idx], imag_part[res_idx], 'gD', markersize=8, label='Resonant Point')
    
    # 设置坐标轴范围和标题
    ax4.set_xlim(-1, 1)
    ax4.set_ylim(-1, 1)
    ax4.set_aspect('equal')
    ax4.set_title('Smith Chart')
    ax4.set_xlabel('Real part of Γ')
    ax4.set_ylabel('Imaginary part of Γ')
    ax4.grid(True, linestyle='--', alpha=0.7)
    ax4.legend()
    
    # 绘制单位圆
    circle = plt.Circle((0, 0), 1, fill=False, color='black', linestyle='-', alpha=0.7)
    ax4.add_artist(circle)
    
    # 显示史密斯圆图
    st.pyplot(fig4)

if show_bode_plot:
    st.subheader("Bode Plot")
    
    # 创建Bode图
    fig5, (ax5a, ax5b) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
    
    # 绘制幅频响应
    ax5a.semilogx(bode_frequencies/unit_factor, magnitude_db, 'b-', linewidth=2, label='Magnitude (dB)')
    
    # 添加典型频率点
    ax5a.plot(
        np.array(typical_frequencies)/unit_factor, 
        magnitude_db_typical,
        'ro', markersize=6, label='Typical Frequencies'
    )
    
    # 添加谐振点
    if resonance_freq in bode_frequencies:
        res_idx = np.where(bode_frequencies == resonance_freq)[0][0]
        ax5a.plot(
            resonance_freq/unit_factor, 
            magnitude_db[res_idx],
            'gD', markersize=8, label='Resonant Point'
        )
        ax5a.annotate(
            f"{magnitude_db[res_idx]:.2f} dB",
            xy=(resonance_freq/unit_factor, magnitude_db[res_idx]),
            xytext=(10, 10),
            textcoords='offset points',
            arrowprops=dict(arrowstyle='->', color='green')
        )
    
    # 设置幅频响应图属性
    ax5a.set_title('Bode Plot - Magnitude Response')
    ax5a.set_ylabel('Magnitude (dB)')
    ax5a.grid(True, which='both', linestyle='--', alpha=0.5)
    ax5a.legend()
    
    # 绘制相频响应
    ax5b.semilogx(bode_frequencies/unit_factor, phase_deg, 'r-', linewidth=2, label='Phase (deg)')
    
    # 添加典型频率点
    ax5b.plot(
        np.array(typical_frequencies)/unit_factor, 
        phase_deg_typical,
        'bo', markersize=6, label='Typical Frequencies'
    )
    
    # 添加谐振点
    if resonance_freq in bode_frequencies:
        res_idx = np.where(bode_frequencies == resonance_freq)[0][0]
        ax5b.plot(
            resonance_freq/unit_factor, 
            phase_deg[res_idx],
            'gD', markersize=8, label='Resonant Point'
        )
        ax5b.annotate(
            f"{phase_deg[res_idx]:.2f}°",
            xy=(resonance_freq/unit_factor, phase_deg[res_idx]),
            xytext=(10, 10),
            textcoords='offset points',
            arrowprops=dict(arrowstyle='->', color='green')
        )
    
    # 设置相频响应图属性
    ax5b.set_title('Bode Plot - Phase Response')
    ax5b.set_xlabel(f'Frequency ({freq_scale})')
    ax5b.set_ylabel('Phase (deg)')
    ax5b.grid(True, which='both', linestyle='--', alpha=0.5)
    ax5b.legend()
    
    # 调整布局
    plt.tight_layout()
    
    # 显示Bode图
    st.pyplot(fig5)

