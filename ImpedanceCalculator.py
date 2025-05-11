import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
import plotly.graph_objects as go
import pandas as pd

# 设置中文字体支持
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False  # 正确显示负号

# 应用布局设置
st.set_page_config(
    page_title="阻抗计算器",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 格式化数值显示的辅助函数
def format_value(value, unit="", engineering=True, precision=3, special_freq=False):
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
        return float('inf') if f != 0 else 0
    capacitive_reactance = 1 / (2 * np.pi * f * C)
    return complex(ESR, -capacitive_reactance)

def impedance_inductor(L, DCR, f):
    """计算电感的阻抗，包括DCR"""
    if L == 0:
        return 0
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

# 页面标题和介绍
st.title("电容和电感阻抗计算器")
st.markdown("""
这是一个专业的阻抗计算器，可以计算电容和电感在不同频率下的阻抗特性，并以图形方式直观展示。
支持串联和并联两种连接方式，同时考虑了电容ESR和电感DCR的影响，提供更准确的计算结果。
""")

# 侧边栏参数设置
with st.sidebar:
    st.header("参数设置")
    
    # 使用选项卡组织输入参数
    tab1, tab2, tab3 = st.tabs(["元件参数", "频率范围", "显示设置"])
    
    with tab1:
        # 电容值输入，支持单位选择
        col1, col2 = st.columns([3, 2])
        with col1:
            cap_value = st.number_input(
                '电容值', 
                min_value=0.0, 
                max_value=1e9, 
                value=1.0, 
                format="%f",
                help="输入电容值的数值部分"
            )
        with col2:
            cap_unit = st.selectbox(
                '单位',
                ['F', 'mF', 'μF', 'nF', 'pF'],
                index=2,  # 默认μF
                help="选择电容值的单位"
            )
        
        # 电容ESR输入
        col3, col4 = st.columns([3, 2])
        with col3:
            esr_value = st.number_input(
                '电容ESR', 
                min_value=0.0, 
                max_value=1e9, 
                value=0.1, 
                format="%f",
                help="输入电容等效串联电阻的数值部分"
            )
        with col4:
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
        
        # 电感值输入，支持单位选择
        col5, col6 = st.columns([3, 2])
        with col5:
            ind_value = st.number_input(
                '电感值', 
                min_value=0.0, 
                max_value=1e9, 
                value=1.0, 
                format="%f",
                help="输入电感值的数值部分"
            )
        with col6:
            ind_unit = st.selectbox(
                '单位',
                ['H', 'mH', 'μH', 'nH', 'pH'],
                index=2,  # 默认μH
                help="选择电感值的单位"
            )
        
        # 电感DCR输入
        col7, col8 = st.columns([3, 2])
        with col7:
            dcr_value = st.number_input(
                '电感DCR', 
                min_value=0.0, 
                max_value=1e9, 
                value=0.1, 
                format="%f",
                help="输入电感直流电阻的数值部分"
            )
        with col8:
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
    
    with tab2:
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
    
    with tab3:
        # 显示设置
        connection_type = st.selectbox(
            '连接方式', 
            ['串联', '并联'],
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

# 处理频率范围包含0的情况
if f_min == 0:
    # 创建一个包含0的特殊频率数组
    frequencies = np.linspace(0, f_max, 1000)
else:
    # 正常对数分布
    frequencies = np.logspace(np.log10(f_min), np.log10(f_max), 1000)

# 计算阻抗，考虑ESR和DCR
Z_C = np.array([impedance_capacitor(C, ESR, f) for f in frequencies])
Z_L = np.array([impedance_inductor(L, DCR, f) for f in frequencies])

# 计算组合阻抗
if connection_type == '串联':
    Z_combined = series_impedance(Z_C, Z_L)
else:
    Z_combined = parallel_impedance(Z_C, Z_L)

# 计算典型频率下的阻抗
Z_C_typical = np.array([impedance_capacitor(C, ESR, f) for f in typical_frequencies])
Z_L_typical = np.array([impedance_inductor(L, DCR, f) for f in typical_frequencies])
if connection_type == '串联':
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

# 计算阻抗的实部和虚部
real_Z_combined = np.real(Z_combined)
imag_Z_combined = np.imag(Z_combined)

# 计算导纳的实部和虚部
real_Y_combined = np.real(Y_combined)
imag_Y_combined = np.imag(Y_combined)

# 找出谐振频率（如果存在）
if connection_type == '串联':
    # 串联谐振：阻抗虚部为0，阻抗最小
    if 0 in frequencies:
        # 如果频率范围包含0，检查0频率处的阻抗
        zero_freq_idx = np.where(frequencies == 0)[0][0]
        if abs(imag_Z_combined[zero_freq_idx]) < 1e-10:
            resonance_idx = zero_freq_idx
        else:
            # 找到最接近0虚部的点
            resonance_idx = np.argmin(np.abs(imag_Z_combined))
    else:
        resonance_idx = np.argmin(np.abs(imag_Z_combined))
else:
    # 并联谐振：导纳虚部为0，阻抗最大
    if 0 in frequencies:
        zero_freq_idx = np.where(frequencies == 0)[0][0]
        if abs(imag_Y_combined[zero_freq_idx]) < 1e-10:
            resonance_idx = zero_freq_idx
        else:
            resonance_idx = np.argmax(np.abs(real_Z_combined))
    else:
        resonance_idx = np.argmax(np.abs(real_Z_combined))
    
resonance_freq = frequencies[resonance_idx]
resonance_impedance = Z_combined[resonance_idx]

# 计算Q因子（品质因数）
if connection_type == '串联':
    # 串联谐振Q因子：X_L/R或X_C/R（在谐振点两者相等）
    R = np.real(resonance_impedance)
    X_L = np.imag(impedance_inductor(L, DCR, resonance_freq))
    
    if R == 0:
        Q_factor = float('inf') if X_L != 0 else 0
    else:
        Q_factor = np.abs(X_L) / R
else:
    # 并联谐振Q因子：R/X_L或R/X_C（在谐振点两者相等）
    R = np.real(resonance_impedance)
    X_L = np.imag(impedance_inductor(L, DCR, resonance_freq))
    
    if R == 0:
        Q_factor = 0
    else:
        if X_L == 0:
            Q_factor = float('inf')
        else:
            Q_factor = R / np.abs(X_L)

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
    
with col2:
    st.markdown(f"**谐振频率**: {format_value(resonance_freq, 'Hz', special_freq=True)}")
    st.markdown(f"**谐振阻抗**: {format_value(np.abs(resonance_impedance), 'Ω')}")
    st.markdown(f"**谐振电阻**: {format_value(np.real(resonance_impedance), 'Ω')}")
    st.markdown(f"**品质因数Q**: {Q_factor:.3f}")

# 显示典型频率下的阻抗值表格
if typical_frequencies:
    st.subheader(f"典型频率 ({freq_scale}) 下的阻抗值")
    
    # 创建数据框
    data = []
    for f, z, y, gamma, phase in zip(
        typical_frequencies, 
        Z_combined_typical, 
        Y_combined_typical,
        gamma_combined_typical,
        phase_combined_typical
    ):
        data.append({
            "频率": format_value(f, 'Hz', special_freq=True),
            "阻抗实部 (Ω)": format_value(np.real(z), 'Ω'),
            "阻抗虚部 (Ω)": format_value(np.imag(z), 'Ω'),
            "阻抗模 (Ω)": format_value(np.abs(z), 'Ω'),
            "阻抗角 (°)": f"{phase:.2f}",
            "导纳实部 (S)": format_value(np.real(y), 'S'),
            "导纳虚部 (S)": format_value(np.imag(y), 'S'),
            "反射系数实部": f"{np.real(gamma):.6f}",
            "反射系数虚部": f"{np.imag(gamma):.6f}",
            "反射系数模": f"{np.abs(gamma):.6f}",
            "反射系数角 (°)": f"{np.angle(gamma, deg=True):.2f}"
        })
    
    # 显示表格
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

# 图表显示区域
st.subheader("图表分析")

# 使用选项卡组织不同类型的图表
tab1, tab2, tab3, tab4 = st.tabs(["阻抗图", "导纳图", "相位图", "史密斯圆图"])

with tab1:
    if show_impedance_plot:
        # 创建阻抗图
        fig1 = go.Figure()
        
        # 处理阻抗为无穷大的情况
        impedance_magnitudes = np.array([np.abs(z) if z != float('inf') else 1e10 for z in Z_combined])
        
        # 添加阻抗模和相位轨迹
        fig1.add_trace(go.Scatter(
            x=frequencies/unit_factor, 
            y=impedance_magnitudes,
            mode='lines',
            name='阻抗模 (Ω)',
            line=dict(width=2)
        ))
        
        # 添加典型频率点
        fig1.add_trace(go.Scatter(
            x=np.array(typical_frequencies)/unit_factor, 
            y=[np.abs(z) if z != float('inf') else 1e10 for z in Z_combined_typical],
            mode='markers',
            name='典型频率点',
            marker=dict(size=8, color='red', symbol='circle')
        ))
        
        # 添加谐振点
        fig1.add_trace(go.Scatter(
            x=[resonance_freq/unit_factor], 
            y=[np.abs(resonance_impedance) if resonance_impedance != float('inf') else 1e10],
            mode='markers+text',
            name='谐振点',
            marker=dict(size=10, color='green', symbol='diamond'),
            text=[f"谐振: {format_value(np.abs(resonance_impedance), 'Ω')}"],
            textposition='top center'
        ))
        
        # 设置图表布局
        fig1.update_layout(
            title=f'阻抗模 vs 频率 ({connection_type})',
            xaxis_title=f'频率 ({freq_scale})',
            yaxis_title='阻抗 (Ω)',
            xaxis=dict(type='log' if f_min > 0 else 'linear'),
            yaxis=dict(type='log'),
            hovermode='x unified',
            template='plotly_dark' if plot_theme == "暗色" else 'plotly_white',
            height=500
        )
        
        # 显示阻抗图
        st.plotly_chart(fig1, use_container_width=True)

with tab2:
    if show_admittance_plot:
        # 创建导纳图
        fig2 = go.Figure()
        
        # 处理导纳为无穷大的情况
        admittance_magnitudes = np.array([np.abs(y) if y != float('inf') else 1e10 for y in Y_combined])
        
        # 添加导纳模轨迹
        fig2.add_trace(go.Scatter(
            x=frequencies/unit_factor, 
            y=admittance_magnitudes,
            mode='lines',
            name='导纳模 (S)',
            line=dict(width=2)
        ))
        
        # 添加典型频率点
        fig2.add_trace(go.Scatter(
            x=np.array(typical_frequencies)/unit_factor, 
            y=[np.abs(y) if y != float('inf') else 1e10 for y in Y_combined_typical],
            mode='markers',
            name='典型频率点',
            marker=dict(size=8, color='red', symbol='circle')
        ))
        
        # 设置图表布局
        fig2.update_layout(
            title=f'导纳模 vs 频率 ({connection_type})',
            xaxis_title=f'频率 ({freq_scale})',
            yaxis_title='导纳 (S)',
            xaxis=dict(type='log' if f_min > 0 else 'linear'),
            yaxis=dict(type='log'),
            hovermode='x unified',
            template='plotly_dark' if plot_theme == "暗色" else 'plotly_white',
            height=500
        )
        
        # 显示导纳图
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    if show_phase_plot:
        # 创建相位图
        fig3 = go.Figure()
        
        # 添加相位轨迹
        fig3.add_trace(go.Scatter(
            x=frequencies/unit_factor, 
            y=phase_combined,
            mode='lines',
            name='相位角 (°)',
            line=dict(width=2)
        ))
        
        # 添加典型频率点
        fig3.add_trace(go.Scatter(
            x=np.array(typical_frequencies)/unit_factor, 
            y=phase_combined_typical,
            mode='markers',
            name='典型频率点',
            marker=dict(size=8, color='red', symbol='circle')
        ))
        
        # 添加谐振点
        fig3.add_trace(go.Scatter(
            x=[resonance_freq/unit_factor], 
            y=[phase_combined[resonance_idx]],
            mode='markers+text',
            name='谐振点',
            marker=dict(size=10, color='green', symbol='diamond'),
            text=[f"相位: {phase_combined[resonance_idx]:.2f}°"],
            textposition='top center'
        ))
        
        # 设置图表布局
        fig3.update_layout(
            title=f'相位角 vs 频率 ({connection_type})',
            xaxis_title=f'频率 ({freq_scale})',
            yaxis_title='相位角 (°)',
            xaxis=dict(type='log' if f_min > 0 else 'linear'),
            hovermode='x unified',
            template='plotly_dark' if plot_theme == "暗色" else 'plotly_white',
            height=500
        )
        
        # 显示相位图
        st.plotly_chart(fig3, use_container_width=True)

with tab4:
    if show_smith_chart:
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
            circle = plt.Circle((center, 0), radius, color='gray', fill=False, lw=0.5)
            ax4.add_artist(circle)
        
        # 恒定电抗弧
        x_values = np.array([0.2, 0.5, 1, 2, 5, 10])
        for x in x_values:
            center = 1
            radius = 1 / x
            theta = np.linspace(0, np.pi/2, 100)
            ax4.plot(np.cos(theta) * radius + center, np.sin(theta) * radius, 'gray', lw=0.5)
            ax4.plot(np.cos(theta) * radius + center, -np.sin(theta) * radius, 'gray', lw=0.5)
        
        # 绘制阻抗轨迹
        ax4.plot(np.real(valid_gamma), np.imag(valid_gamma), 
                 label='Impedance Locus', color='blue', lw=2)
        
        # 标记典型频率点
        valid_typical_indices = []
        valid_typical_gamma = []
        valid_typical_frequencies = []
        
        for i, (f, gamma) in enumerate(zip(typical_frequencies, gamma_combined_typical)):
            if abs(gamma) <= 1:
                valid_typical_indices.append(i)
                valid_typical_gamma.append(gamma)
                valid_typical_frequencies.append(f)
        
        if valid_typical_gamma:
            ax4.scatter(np.real(valid_typical_gamma), np.imag(valid_typical_gamma), 
                        color='red', zorder=5, label='Typical Frequencies')
            
            # 添加频率标签到典型点
            for i, (f, gamma) in enumerate(zip(valid_typical_frequencies, valid_typical_gamma)):
                ax4.annotate(f'{format_value(f, "Hz", special_freq=True)}', 
                            (np.real(gamma), np.imag(gamma)),
                            textcoords="offset points",
                            xytext=(0,10),
                            ha='center',
                            fontsize=8)
        
        # 标记谐振点
        gamma_resonance = impedance_to_gamma(resonance_impedance)
        if abs(gamma_resonance) <= 1:
            ax4.scatter(np.real(gamma_resonance), np.imag(gamma_resonance), 
                        color='green', s=100, zorder=6, label='Resonant Point')
        
        # 设置图表属性 - 保留英文标题和标签
        ax4.set_xlim(-1, 1)
        ax4.set_ylim(-1, 1)
        ax4.set_aspect('equal')
        ax4.set_title(f'Smith Chart ({connection_type})')  # 英文标题
        ax4.legend()
        ax4.grid(False)
        
        # 显示史密斯圆图
        st.pyplot(fig4)

# 帮助和说明
with st.expander("查看帮助说明"):
    st.markdown("""
    ### 使用指南
    
    **参数设置**:
    - 输入电容值和电感值（支持普通小数格式）
    - 设置电容ESR（等效串联电阻）和电感DCR（直流电阻）
    - 设置频率范围和典型频率点
    - 选择元件连接方式（串联或并联）
    
    **图表分析**:
    - 阻抗图：显示阻抗模随频率的变化
    - 导纳图：显示导纳模随频率的变化
    - 相位图：显示阻抗相位角随频率的变化
    - 史密斯圆图：以图形方式表示阻抗匹配情况
    
    **计算结果**:
    - 谐振频率：系统发生谐振的频率点
    - 谐振阻抗：谐振频率下的阻抗值
    - 谐振电阻：谐振频率下阻抗的实部
    - 品质因数Q：衡量谐振电路性能的指标，基于实际阻抗计算
    
    ### 关于阻抗计算
    
    - 电容阻抗: Zc = ESR - j/(ωC)
    - 电感阻抗: Zl = DCR + jωL
    - 串联总阻抗: Z = Zc + Zl
    - 并联总阻抗: Z = (Zc × Zl)/(Zc + Zl)
    - 反射系数: Γ = (Z - Z0)/(Z + Z0)，其中Z0通常为50Ω
    
    """)

# 页脚
st.markdown("---")
st.caption("阻抗计算器 | 专业电子工程工具")
