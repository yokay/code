import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.transforms as transforms
import pandas as pd

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 基本物理常数
Z0 = 50.0  # 特性阻抗
ERROR_TOLERANCE = 1e-2  # 误差容忍度(Ω)
MAX_ITERATIONS = 200    # 最大迭代次数
LEARNING_RATE = 0.1     # 学习率
MIN_STEP = 1e-12        # 最小步长
MIN_GRADIENT = 1e-6     # 梯度阈值
PLATEAU_THRESHOLD = 20  # 平台期检测窗口大小

# 单位前缀及其对应的乘数
UNIT_PREFIXES = {
    'p': 1e-12,
    'n': 1e-9,
    'μ': 1e-6,
    'm': 1e-3,
    '': 1.0
}

# 元件类型对应的默认范围和单位选项
COMPONENT_DEFAULTS = {
    '电感': {
        'min': 0.1,
        'max': 1000.0,  # 滑动条最大值调整为1000
        'step': 0.1,
        'prefixes': ['pH', 'nH', 'μH', 'mH', 'H'],
        'prefix_default': 'n',
        'unit': 'H'
    },
    '电容': {
        'min': 0.1,
        'max': 1000.0,  # 滑动条最大值调整为1000
        'step': 0.1,
        'prefixes': ['fF', 'pF', 'nF', 'μF', 'mF'],
        'prefix_default': 'p',
        'unit': 'F'
    }
}

def complex_input(label, default_real=50.0, default_imag=0.0):
    """创建复数输入组件"""
    col1, col2 = st.columns(2)
    with col1:
        real_part = st.number_input(f"{label} - 实部 (Ω)", value=default_real, format="%f")
    with col2:
        imag_part = st.number_input(f"{label} - 虚部 (Ω)", value=default_imag, format="%f")
    return complex(real_part, imag_part)

def calculate_gamma(Z, Z_ref=Z0):
    """计算反射系数"""
    return (Z - Z_ref) / (Z + Z_ref)

def calculate_vswr(gamma):
    """计算电压驻波比"""
    if abs(gamma) >= 1:
        return float('inf')
    return (1 + abs(gamma)) / (1 - abs(gamma))

def calculate_smith_distance(Z1, Z2, Z_ref=Z0):
    """计算两个阻抗在Smith图上的距离"""
    gamma1 = calculate_gamma(Z1, Z_ref)
    gamma2 = calculate_gamma(Z2, Z_ref)
    return abs(gamma1 - gamma2)

def calculate_euclidean_distance(Z1, Z2):
    """计算两个复数阻抗的欧拉距离"""
    return abs(Z1 - Z2)

def plot_smith_chart(ax, impedances=None, annotations=None, plot_curve=False, Z_ref=Z0, target_impedance=None):
    """绘制Smith圆图，以目标阻抗为中心"""
    ax.set_aspect('equal')
    
    # 如果有目标阻抗，调整视图范围以目标阻抗为中心
    if target_impedance:
        gamma_target = calculate_gamma(target_impedance, Z_ref)
        # 设置视图范围，确保目标阻抗在中心附近
        view_size = 0.5  # 可视区域大小
        ax.set_xlim(gamma_target.real - view_size, gamma_target.real + view_size)
        ax.set_ylim(gamma_target.imag - view_size, gamma_target.imag + view_size)
    else:
        # 默认视图
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-1.1, 1.1)
    
    # 绘制等电阻圆
    r_values = [0, 0.2, 0.5, 1, 2, 5, 10]
    for r in r_values:
        center = (r / (1 + r), 0)
        radius = 1 / (1 + r)
        circle = Circle(center, radius, fill=False, color='gray', linestyle='-', linewidth=0.5)
        ax.add_patch(circle)

    r_values = [0, 0.2, 0.5, 1, 2, 5, 10]
    for r in r_values:
        center = (-r / (1 + r), 0)
        radius = 1 / (1 + r)
        circle = Circle(center, radius, fill=False, color='gray', linestyle='-', linewidth=0.5)
        ax.add_patch(circle)   
    # # 绘制等电导圆（归一化导纳圆）
    # g_values = [0, 0.2, 0.5, 1, 2, 5, 10]
    # for g in g_values:
    #     if g == 0:
    #         center = (-1, 0)
    #         radius = 1
    #     elif g == 1:
    #         # 电导为1时，圆退化为垂直线x=1
    #         ax.axvline(x=1, color='gray', linestyle='-', linewidth=0.5)
    #         continue
    #     else:
    #         center = (g / (g - 1), 0)
    #         radius = 1 / abs(g - 1)
    #     circle = Circle(center, radius, fill=False, color='gray', linestyle='-', linewidth=0.5)
    #     ax.add_patch(circle)
    
    # 绘制单位圆
    circle = Circle((0, 0), 1, fill=False, color='black', linestyle='-', linewidth=1)
    ax.add_patch(circle)
    
    # 标记原点(匹配点)和开路、短路点
    ax.plot(0, 0, 'ro', markersize=8)
    ax.annotate(f'match point ({Z_ref:.1f},0)', (0, 0), textcoords="offset points", 
                xytext=(0,15), ha='center', fontsize=10)
    ax.plot(1, 0, 'go', markersize=8)
    ax.annotate('OPEN (∞)', (1, 0), textcoords="offset points", 
                xytext=(0,15), ha='center', fontsize=10)
    ax.plot(-1, 0, 'bo', markersize=8)
    ax.annotate('CLOSE (0)', (-1, 0), textcoords="offset points", 
                xytext=(0,15), ha='center', fontsize=10)
    
    # 绘制阻抗点和匹配曲线
    if impedances:
        # 绘制源阻抗
        source_impedance = impedances[0]
        gamma_source = calculate_gamma(source_impedance, Z_ref)
        ax.plot(gamma_source.real, gamma_source.imag, 'o', color='blue', markersize=10)
        ax.annotate(f"RL: {source_impedance.real:.1f}+j{source_impedance.imag:.1f}Ω", 
                    (gamma_source.real, gamma_source.imag), 
                    textcoords="offset points", xytext=(0,20), ha='center', fontsize=10)
        
        # 绘制目标阻抗
        if target_impedance:
            gamma_target = calculate_gamma(target_impedance, Z_ref)
            ax.plot(gamma_target.real, gamma_target.imag, 'o', color='purple', markersize=10)
            ax.annotate(f"Target: {target_impedance.real:.1f}+j{target_impedance.imag:.1f}Ω", 
                        (gamma_target.real, gamma_target.imag), 
                        textcoords="offset points", xytext=(0,-20), ha='center', fontsize=10)
        
        # 绘制匹配后的阻抗
        if len(impedances) > 1:
            matched_impedance = impedances[-2]
            gamma_matched = calculate_gamma(matched_impedance, Z_ref)
            ax.plot(gamma_matched.real, gamma_matched.imag, 'o', color='green', markersize=10)
            ax.annotate(f"After match: {matched_impedance.real:.1f}+j{matched_impedance.imag:.1f}Ω", 
                        (gamma_matched.real, gamma_matched.imag), 
                        textcoords="offset points", xytext=(0,20), ha='center', fontsize=10)
        
        # 绘制Smith图上的距离
        if len(impedances) > 1 and target_impedance:
            ax.plot([gamma_matched.real, gamma_target.real], 
                    [gamma_matched.imag, gamma_target.imag], 
                    'k--', linewidth=1.5, alpha=0.7)
            distance = calculate_smith_distance(matched_impedance, target_impedance, Z_ref)
            mid_x = (gamma_matched.real + gamma_target.real) / 2
            mid_y = (gamma_matched.imag + gamma_target.imag) / 2
            ax.annotate(f"Distance: {distance:.6f}", (mid_x, mid_y), 
                        textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)
        
        # 绘制匹配曲线
        if plot_curve and len(impedances) > 1:
            gamma_points = [calculate_gamma(Z, Z_ref) for Z in impedances]
            real_part = [g.real for g in gamma_points]
            imag_part = [g.imag for g in gamma_points]
            ax.plot(real_part, imag_part, 'r-', linewidth=2, alpha=0.7)
            
            # 为每个中间点添加标记
            for i, Z in enumerate(impedances):
                if i == 0 or i == len(impedances) - 1:  # 跳过已标记的负载和目标
                    continue
                gamma = calculate_gamma(Z, Z_ref)
                ax.plot(gamma.real, gamma.imag, 'o', color='orange', markersize=6)
                ax.annotate(f"Index {i}", (gamma.real, gamma.imag),
                            textcoords="offset points", xytext=(0, 10), ha='center', fontsize=9)
    
    ax.set_title(f'Smith Chart (REF RL Z0 = {Z_ref}Ω)')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_xlabel('RL real')
    ax.set_ylabel('RL img')
    
    return ax

def format_value(value, unit_type, prefix):
    """格式化元件值和单位，使用指定的单位前缀"""
    prefixes = {
        'L': {'p': 'pH', 'n': 'nH', 'μ': 'μH', 'm': 'mH', '': 'H'},
        'C': {'f': 'fF', 'p': 'pF', 'n': 'nF', 'μ': 'μF', 'm': 'mF'}
    }
    
    if prefix in prefixes[unit_type]:
        factor = UNIT_PREFIXES[prefix]
        return f"{value/factor:.3f} {prefixes[unit_type][prefix]}"
    
    # 如果前缀无效，尝试自动选择合适的单位
    factors = [1e-12, 1e-9, 1e-6, 1e-3, 1]  # 对应前缀的因数
    for i, factor in enumerate(factors):
        if value >= factor:
            return f"{value/factor:.3f} {prefixes[unit_type][list(prefixes[unit_type].keys())[i]]}"
    
    # 如果非常小，使用最小单位
    return f"{value/factors[0]:.3f} {prefixes[unit_type][list(prefixes[unit_type].keys())[0]]}"

def add_component(Z, component, frequency):
    """添加单个元件到阻抗"""
    if component['connection'] == "串联":
        if component['type'] == "电感":
            # 串联电感的阻抗: jωL
            X = 2 * np.pi * frequency * component['value']
            return Z + complex(0, X)
        elif component['type'] == "电容":
            # 串联电容的阻抗: -j/(ωC)
            if component['value'] == 0:
                return Z
            X = -1 / (2 * np.pi * frequency * component['value'])
            return Z + complex(0, X)
    elif component['connection'] == "并联":
        if component['type'] == "电感":
            # 并联电感的导纳: 1/(jωL)
            if component['value'] == 0:
                return Z
            B = -1 / (2 * np.pi * frequency * component['value'])
            Y = 1/Z + complex(0, B)
            return 1/Y if Y != 0 else complex(float('inf'), 0)
        elif component['type'] == "电容":
            # 并联电容的导纳: jωC
            B = 2 * np.pi * frequency * component['value']
            Y = 1/Z + complex(0, B)
            return 1/Y if Y != 0 else complex(float('inf'), 0)
    return Z

def calculate_impedance(Z_load, components, frequency):
    """计算给定负载和元件的最终阻抗"""
    Z_current = Z_load
    for component in components:
        Z_current = add_component(Z_current, component, frequency)
    return Z_current

def create_slider_with_input(label, min_value, max_value, value, step, key, prefixes, default_prefix):
    """创建带输入框的滑动条组件"""
    # 初始化会话状态
    if f"{key}_value" not in st.session_state:
        st.session_state[f"{key}_value"] = value
    
    # 定义回调函数
    def update_slider():
        st.session_state[f"{key}_value"] = st.session_state[f"{key}_input"]
    
    def update_input():
        st.session_state[f"{key}_value"] = st.session_state[f"{key}_slider"]
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        slider_value = st.slider(
            label,
            min_value=min_value,
            max_value=max_value,
            value=st.session_state[f"{key}_value"],
            step=step,
            key=f"{key}_slider",
            on_change=update_input
        )
    
    with col2:
        input_value = st.number_input(
            "",
            min_value=min_value,
            max_value=max_value,
            value=st.session_state[f"{key}_value"],
            step=step,
            key=f"{key}_input",
            on_change=update_slider
        )
    
    with col3:
        prefix = st.selectbox(
            "",
            prefixes,
            prefixes.index(default_prefix),
            key=f"{key}_prefix"
        )
        prefix = prefix[0]  # 提取前缀字符（如"n"从"nH"中提取）
    
    return st.session_state[f"{key}_value"], prefix

def main():
    st.title("阻抗匹配Smith圆图工具")
    
    # 侧边栏参数设置
    st.sidebar.header("参数设置")
    Z0 = st.sidebar.number_input("参考阻抗 Z0 (Ω)", value=50.0, min_value=1.0, max_value=1000.0, step=1.0, format="%f")
    frequency = st.sidebar.number_input("工作频率 (MHz)", value=100.0, min_value=0.1, max_value=10000.0, step=0.1, format="%f")
    frequency_hz = frequency * 1e6  # 转换为Hz
    
    # 输入阻抗
    st.header("输入阻抗")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("负载阻抗")
        Z_load = complex_input("负载阻抗", 50.0, 50.0)
    
    with col2:
        st.subheader("目标阻抗")
        Z_target = complex_input("目标阻抗", Z0, 0.0)  # 默认就是自定义，默认值为50
    
    st.info(f"当前显示的是目标阻抗 {Z_target.real:.1f} + j{Z_target.imag:.1f} Ω 的Smith圆图")
    
    # 计算并显示归一化阻抗和导纳
    st.subheader("归一化值")
    z_load = Z_load / Z0
    z_target = Z_target / Z0
    y_target = 1 / z_target
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"归一化负载阻抗: {z_load.real:.4f} + j{z_load.imag:.4f}")
    with col2:
        st.write(f"归一化目标阻抗: {z_target.real:.4f} + j{z_target.imag:.4f}")
        st.write(f"归一化目标导纳: {y_target.real:.4f} + j{y_target.imag:.4f}")
    
    # 手动匹配控件
    st.header("手动匹配")
    
    # 选择匹配拓扑结构
    topology = st.selectbox("匹配拓扑结构", ["串电感并电容", "串电容并电感", "并电感串电容", "并电容串电感"])
    
    # 解析拓扑结构
    if topology == "串电感并电容":
        components = [
            {'connection': '串联', 'type': '电感'},
            {'connection': '并联', 'type': '电容'}
        ]
    elif topology == "串电容并电感":
        components = [
            {'connection': '串联', 'type': '电容'},
            {'connection': '并联', 'type': '电感'}
        ]
    elif topology == "并电感串电容":
        components = [
            {'connection': '并联', 'type': '电感'},
            {'connection': '串联', 'type': '电容'}
        ]
    else:  # 并电容串电感
        components = [
            {'connection': '并联', 'type': '电容'},
            {'connection': '串联', 'type': '电感'}
        ]
    
    # 滑动条上面的标题只写电感、电容
    st.subheader("电感")
    inductor_defaults = COMPONENT_DEFAULTS['电感']
    inductor_value, inductor_prefix = create_slider_with_input(
        "电感值",
        min_value=inductor_defaults['min'],
        max_value=inductor_defaults['max'],
        value=10.0,
        step=inductor_defaults['step'],
        key="inductor",
        prefixes=inductor_defaults['prefixes'],
        default_prefix=inductor_defaults['prefix_default'] + inductor_defaults['unit']
    )
    inductor_value = inductor_value * UNIT_PREFIXES[inductor_prefix]
    
    st.subheader("电容")
    capacitor_defaults = COMPONENT_DEFAULTS['电容']
    capacitor_value, capacitor_prefix = create_slider_with_input(
        "电容值",
        min_value=capacitor_defaults['min'],
        max_value=capacitor_defaults['max'],
        value=10.0,
        step=capacitor_defaults['step'],
        key="capacitor",
        prefixes=capacitor_defaults['prefixes'],
        default_prefix=capacitor_defaults['prefix_default'] + capacitor_defaults['unit']
    )
    capacitor_value = capacitor_value * UNIT_PREFIXES[capacitor_prefix]
    
    # 更新组件值
    for i, comp in enumerate(components):
        if comp['type'] == '电感':
            components[i]['value'] = inductor_value
        else:
            components[i]['value'] = capacitor_value
    
    # 匹配过程Smith圆图标题
    st.header("匹配过程Smith圆图")

    # 计算添加元件后的阻抗
    Z_after_first = calculate_impedance(Z_load, [components[0]], frequency_hz)
    Z_final = calculate_impedance(Z_load, components, frequency_hz)
    
    # 计算反射系数和VSWR
    gamma_load = calculate_gamma(Z_load, Z0)
    gamma_after_first = calculate_gamma(Z_after_first, Z0)
    gamma_final = calculate_gamma(Z_final, Z0)
    
    vswr_load = calculate_vswr(gamma_load)
    vswr_after_first = calculate_vswr(gamma_after_first)
    vswr_final = calculate_vswr(gamma_final)
    
    # 显示匹配结果
    st.header("匹配结果")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**负载阻抗**")
        st.write(f"{Z_load.real:.4f} + j{Z_load.imag:.4f} Ω")
        st.write(f"VSWR: {vswr_load:.4f}")
    with col2:
        st.write("**添加第一个元件后**")
        st.write(f"{components[0]['connection']}{components[0]['type']}: " 
                 f"{format_value(components[0]['value'], 'L' if components[0]['type'] == '电感' else 'C', inductor_prefix if components[0]['type'] == '电感' else capacitor_prefix)}")
        st.write(f"{Z_after_first.real:.4f} + j{Z_after_first.imag:.4f} Ω")
        st.write(f"VSWR: {vswr_after_first:.4f}")
    with col3:
        st.write("**添加第二个元件后**")
        st.write(f"{components[1]['connection']}{components[1]['type']}: " 
                 f"{format_value(components[1]['value'], 'L' if components[1]['type'] == '电感' else 'C', inductor_prefix if components[1]['type'] == '电感' else capacitor_prefix)}")
        st.write(f"{Z_final.real:.4f} + j{Z_final.imag:.4f} Ω")
        st.write(f"VSWR: {vswr_final:.4f}")
    
    # 计算与目标的误差
    error = calculate_euclidean_distance(Z_final, Z_target)
    st.write(f"与目标阻抗的欧拉距离误差: {error:.8f} Ω")
    
    # 构建完整的阻抗点列表用于绘制匹配路径
    impedance_points = [Z_load, Z_after_first, Z_final, Z_target]
    
    # 绘制匹配过程的Smith圆图
    fig, ax = plt.subplots(figsize=(10, 10))
    plot_smith_chart(ax, impedance_points, plot_curve=True, Z_ref=Z0)
    st.pyplot(fig)
    
if __name__ == "__main__":
    main()    
