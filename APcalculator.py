import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 设置页面配置
st.set_page_config(
    page_title="推挽变压器AP值计算器",
    page_icon="🔌",
    layout="wide"
)

# 自定义CSS样式
st.markdown("""
<style>
   .title {
        text-align: center;
        color: #1E88E5;
        margin-bottom: 20px;
    }
   .formula-box {
        background-color: #f5f7fa;
        border-radius: 8px;
        padding: 15px;
        margin: 20px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
   .result-box {
        background-color: #e8f5e9;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
        font-size: 1.2em;
        font-weight: bold;
    }
   .sidebar-title {
        color: #1E88E5;
        font-size: 1.2em;
        margin-top: 20px;
    }
   .stNumberInput div[class*="stText"] {
        border-radius: 0.375rem 0 0 0.375rem!important;
    }
   .stSelectbox div[class*="stText"] {
        border-radius: 0 0.375rem 0.375rem 0!important;
        border-left: none!important;
    }
   .param-chart {
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 主标题
st.markdown('<h1 class="title">推挽变压器 AP 值计算工具</h1>', unsafe_allow_html=True)

# 公式部分
st.markdown('<div class="formula-box">', unsafe_allow_html=True)
st.latex(r"""
AP = \frac{P_{out}/\eta}{B_{w}\times f} \times 10^4 \quad (\text{单位:} \ cm^4)
""")
st.markdown("""
其中：
- $P_{out}$：输出功率
- $\eta$：变换器效率
- $B_{w}$：磁芯工作磁通密度
- $f$：开关频率
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 创建两列布局
col1, col2 = st.columns(2)

with col1:
    st.subheader("功率与效率参数")
    
    # 输出功率输入 - 使用并列布局，单位在后面
    power_col1, power_col2 = st.columns([4, 1])
    with power_col1:
        power_value = st.number_input('输出功率值', value=3.0, step=0.1, key="power_value")
    with power_col2:
        power_unit = st.selectbox("", ["W", "mW", "kW"], key="power_unit", index=0, 
                                 format_func=lambda x: f"{x}")
    power_units = {"W": 1, "mW": 1e-3, "kW": 1e3}
    p_out = power_value * power_units[power_unit]
    
    # 效率输入
    efficiency_method = st.radio("输入效率方式", ["百分比 (%)", "小数"], key="eff_method")
    if efficiency_method == "百分比 (%)":
        efficiency_percent = st.slider('变换器效率 (%)', min_value=1, max_value=100, value=80)
        efficiency = efficiency_percent / 100.0
    else:
        efficiency = st.slider('变换器效率 (小数)', min_value=0.01, max_value=1.0, value=0.8, step=0.01)

with col2:
    st.subheader("磁芯与频率参数")
    
    # 磁通密度输入 - 使用并列布局，单位在后面
    flux_col1, flux_col2 = st.columns([4, 1])
    with flux_col1:
        flux_value = st.number_input('磁芯工作磁通密度值', value=0.2, step=0.01, key="flux_value")
    with flux_col2:
        flux_unit = st.selectbox("", ["T", "mT", "G"], key="flux_unit", index=0, 
                                format_func=lambda x: f"{x}")
    flux_units = {"T": 1, "mT": 1e-3, "G": 1e-4}
    b_w = flux_value * flux_units[flux_unit]
    
    # 输出功率输入 - 使用并列布局，单位在后面
    freq_col1, freq_col2 = st.columns([4, 1])
    with freq_col1:
        freq_value = st.number_input('开关频率值', value=1.0, step=0.1, key="freq_value")
    with freq_col2:
        freq_unit = st.selectbox("", ["Hz", "kHz", "MHz"], key="freq_unit", index=2, 
                                format_func=lambda x: f"{x}")
    freq_units = {"Hz": 1, "kHz": 1e3, "MHz": 1e6}
    f = freq_value * freq_units[freq_unit]

# 计算AP值的函数
def calculate_ap(p_out, efficiency, b_w, f):
    """计算推挽变压器的AP值"""
    return (p_out / efficiency) / (b_w * f) * 1e4  # 转换为cm⁴

# 创建图表的函数
def create_sensitivity_chart(x, y, current_x, x_label, title, color='blue'):
    """创建参数敏感性分析图表"""
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(x, y, color=color, linewidth=2)
    ax.axvline(x=current_x, color='red', linestyle='--', linewidth=1.5)
    ax.set_title(title, fontsize=12)
    ax.set_xlabel(x_label, fontsize=10)
    ax.set_ylabel('AP value (cm⁴)', fontsize=10)  # 修改为英文
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # 设置科学计数法格式化
    ax.xaxis.set_major_formatter(EngFormatter())
    
    # 添加当前值标记
    ax.annotate(f'Current value: {current_x:.4g}',  # 修改为英文
                xy=(current_x, max(y)*0.8), 
                xytext=(current_x*1.1, max(y)*0.9),
                arrowprops=dict(facecolor='red', shrink=0.05, width=1.5, headwidth=8),
                fontsize=9)
    
    return fig

# 计算并显示结果
if st.button('计算', key="calculate_btn"):
    try:
        ap_result = calculate_ap(p_out, efficiency, b_w, f)
        
        # 结果格式化显示
        st.markdown(f'<div class="result-box">计算得到的 AP 值为: <span style="color:#2E7D32;">{ap_result:.4f} cm⁴</span></div>', unsafe_allow_html=True)
        
        # 结果解释
        if ap_result < 1:
            st.info("✅ AP值较小，适合小型变压器设计")
        elif ap_result < 10:
            st.info("✅ AP值适中，适合中等功率变压器")
        else:
            st.warning("⚠️ AP值较大，适合大功率变压器，可能需要较大磁芯")
        
        # 绘制参数敏感性分析图表
        st.subheader("参数敏感性分析")
        
        # 计算各参数敏感性数据
        p_values = np.linspace(max(p_out*0.5, 0.1), p_out*1.5, 20)
        ap_p = [calculate_ap(p, efficiency, b_w, f) for p in p_values]
        
        eff_values = np.linspace(max(efficiency*0.8, 0.01), min(efficiency*1.2, 0.99), 20)
        ap_eff = [calculate_ap(p_out, e, b_w, f) for e in eff_values]
        
        bw_values = np.linspace(max(b_w*0.5, 0.001), b_w*1.5, 20)
        ap_bw = [calculate_ap(p_out, efficiency, bw, f) for bw in bw_values]
        
        freq_values = np.linspace(max(f*0.5, 100), f*1.5, 20)
        ap_freq = [calculate_ap(p_out, efficiency, b_w, freq) for freq in freq_values]
        
        # 创建四列布局展示独立图表
        chart_col1, chart_col2 = st.columns(2)
        
        # 输出功率敏感性图表
        with chart_col1:
            fig_p = create_sensitivity_chart(
                p_values, ap_p, p_out, 
                f"Output Power ({power_unit})",  # 修改为英文
                "Impact of Output Power on AP value",  # 修改为英文
                color='#1f77b4'
            )
            st.pyplot(fig_p)
        
        # 效率敏感性图表
        with chart_col2:
            fig_eff = create_sensitivity_chart(
                eff_values, ap_eff, efficiency, 
                "Converter Efficiency",  # 修改为英文
                "Impact of Efficiency on AP value",  # 修改为英文
                color='#ff7f0e'
            )
            st.pyplot(fig_eff)
        
        # 磁通密度敏感性图表
        with chart_col1:
            fig_bw = create_sensitivity_chart(
                bw_values, ap_bw, b_w, 
                f"Magnetic Flux Density ({flux_unit})",  # 修改为英文
                "Impact of Magnetic Flux Density on AP value",  # 修改为英文
                color='#2ca02c'
            )
            st.pyplot(fig_bw)
        
        # 频率敏感性图表
        with chart_col2:
            fig_freq = create_sensitivity_chart(
                freq_values, ap_freq, f, 
                f"Switching Frequency ({freq_unit})",  # 修改为英文
                "Impact of Switching Frequency on AP value",  # 修改为英文
                color='#d62728'
            )
            st.pyplot(fig_freq)
        
        # 磁芯选型建议
        st.subheader("磁芯选型建议")
        st.markdown("""
        根据计算得到的AP值，可参考以下磁芯选型范围：
        
        | AP值范围 (cm⁴) | 磁芯尺寸建议 | 适用功率范围 |
        |---|---|---|
        | 0-1 | E13, E16, E19 | 1-10W |
        | 1-5 | E25, E30, E35 | 10-50W |
        | 5-15 | E40, E55, E65 | 50-200W |
        | 15-30 | E75, E85, E100 | 200-500W |
        | >30 | UI型、罐型等大型磁芯 | 500W以上 |
        
        注意：实际选型时还需考虑窗口利用系数、电流密度、温升等因素。
        """)
            
    except Exception as e:
        st.error(f"计算出错: {str(e)}")

# 侧边栏：磁芯材料参考
with st.sidebar:
    st.header("磁芯材料参考")
    st.markdown("""
    | 材料类型 | 工作磁通密度范围 (T) | 推荐频率范围 |
    |---|---|---|
    | 铁氧体 (MnZn) | 0.2-0.4 | 10kHz-1MHz |
    | 铁氧体 (NiZn) | 0.1-0.3 | 1MHz-10MHz |
    | 铁粉芯 | 0.3-0.6 | 50kHz-500kHz |
    | 铁硅铝 | 0.5-0.8 | 20kHz-200kHz |
    | 铁硅 | 0.8-1.5 | 50Hz-20kHz |
    | 坡莫合金 | 0.6-1.0 | 1kHz-100kHz |
    """)
    
    st.header("关于AP值")
    st.markdown("""
    AP值(Area Product)是变压器磁芯截面积(Ae)与窗口面积(Aw)的乘积，单位为cm⁴。
    
    AP值反映了磁芯的功率处理能力，其物理意义为：
    $$ AP = A_e \\times A_w = \\frac{P_{out}/\\eta}{B_{w}\\times f} \\times 10^4 $$
    
    AP值越大，所需磁芯尺寸越大，可处理的功率也越大。
    """)
    
    # 添加关于部分
    st.header("关于本工具")
    st.info("本工具用于快速计算推挽变压器的AP值，帮助工程师选择合适的磁芯。\n\n版本: 1.0.3")

# 添加页脚
st.markdown("""
---
© 2025 变压器设计助手 | 设计参数仅供参考，请结合实际工程经验调整
""")
