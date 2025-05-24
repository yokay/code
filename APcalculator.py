import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 自定义CSS样式
st.markdown("""
<style>
   .title {text-align:center;color:#1E88E5;margin-bottom:20px;}
   .formula-box {background:#f5f7fa;border-radius:8px;padding:15px;margin:20px 0;box-shadow:0 2px 5px rgba(0,0,0,0.1);}
   .result-box {background:#e8f5e9;border-radius:8px;padding:20px;margin:20px 0;text-align:center;font-size:1.2em;font-weight:bold;}
   .sidebar-title {color:#1E88E5;font-size:1.2em;margin-top:20px;}
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

# 创建两列布局（避免嵌套）
col1, col2 = st.columns(2)

with col1:
    st.subheader("功率与效率参数")
    
    # 输出功率（使用两个独立组件，避免嵌套列）
    power_value = st.number_input('输出功率值', value=3.0, step=0.1, key="power_value")
    power_unit = st.selectbox("输出功率单位", ["W", "mW", "kW"], key="power_unit", index=0)
    
    power_units = {"W": 1, "mW": 1e-3, "kW": 1e3}
    p_out = power_value * power_units[power_unit]
    
    # 效率输入
    efficiency_method = st.radio("输入效率方式", ["百分比 (%)", "小数"], key="eff_method")
    if efficiency_method == "百分比 (%)":
        efficiency = st.slider('变换器效率 (%)', 1, 100, 80) / 100.0
    else:
        efficiency = st.slider('变换器效率 (小数)', 0.01, 1.0, 0.8, step=0.01)

with col2:
    st.subheader("磁芯与频率参数")
    
    # 磁通密度（使用两个独立组件，避免嵌套列）
    flux_value = st.number_input('磁芯工作磁通密度值', value=0.2, step=0.01, key="flux_value")
    flux_unit = st.selectbox("磁通密度单位", ["T", "mT", "G"], key="flux_unit", index=0)
    
    flux_units = {"T": 1, "mT": 1e-3, "G": 1e-4}
    b_w = flux_value * flux_units[flux_unit]
    
    # 频率（使用两个独立组件，避免嵌套列）
    freq_value = st.number_input('开关频率值', value=1.0, step=0.1, key="freq_value")
    freq_unit = st.selectbox("频率单位", ["Hz", "kHz", "MHz"], key="freq_unit", index=2)
    
    freq_units = {"Hz": 1, "kHz": 1e3, "MHz": 1e6}
    f = freq_value * freq_units[freq_unit]

# 计算AP值的函数
def calculate_ap(p_out, efficiency, b_w, f):
    return (p_out / efficiency) / (b_w * f) * 1e4  # 转换为cm⁴

# 创建图表的函数 - 英文文本
def create_sensitivity_chart(x, y, current_x, x_label, title, color='blue'):
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(x, y, color=color, linewidth=2)
    ax.axvline(current_x, color='red', linestyle='--', linewidth=1.5)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel('AP Value (cm⁴)')  # 英文标签
    if 'Hz' in x_label:
        ax.set_xscale('log')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.xaxis.set_major_formatter(EngFormatter())
    ax.annotate('Current: %.4g' % current_x, xy=(current_x, max(y)*0.8), 
                xytext=(current_x*1.1, max(y)*0.9), 
                arrowprops=dict(facecolor='red', shrink=0.05))
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
        
        # 单栏显示图表（避免嵌套列）
        st.pyplot(create_sensitivity_chart(
            p_values, ap_p, p_out, f"Output Power ({power_unit})", "Effect of Output Power on AP Value", '#1f77b4'
        ))
        
        st.pyplot(create_sensitivity_chart(
            eff_values, ap_eff, efficiency, "Efficiency", "Effect of Efficiency on AP Value", '#ff7f0e'
        ))
        
        st.pyplot(create_sensitivity_chart(
            bw_values, ap_bw, b_w, f"Flux Density ({flux_unit})", "Effect of Flux Density on AP Value", '#2ca02c'
        ))
        
        st.pyplot(create_sensitivity_chart(
            freq_values, ap_freq, f, f"Frequency ({freq_unit})", "Effect of Frequency on AP Value", '#d62728'
        ))
        
        # 磁芯选型建议
        st.subheader("磁芯选型建议")
        st.markdown("""
        | AP值范围 (cm⁴) | 磁芯尺寸建议       | 适用功率范围 |
        |---|---|---|
        | 0-1             | E13, E16, E19     | 1-10W        |
        | 1-5             | E25, E30, E35     | 10-50W       |
        | 5-15            | E40, E55, E65     | 50-200W      |
        | 15-30           | E75, E85, E100    | 200-500W     |
        | >30             | UI型、罐型等大型磁芯 | 500W以上 |
        """)
            
    except Exception as e:
        st.error("计算出错: %s" % str(e), icon="🚨")

# 侧边栏
with st.sidebar:
    # 使用 markdown 替代 header，应用 CSS 类
    st.markdown('<h3 class="sidebar-title">磁芯材料参考</h3>', unsafe_allow_html=True)
    st.markdown("""
    | 材料类型   | 工作磁通密度范围 (T) | 推荐频率范围   |
    |---|---|---|
    | 铁氧体 (MnZn) | 0.2-0.4            | 10kHz-1MHz     |
    | 铁氧体 (NiZn) | 0.1-0.3            | 1MHz-10MHz     |
    | 铁粉芯     | 0.3-0.6            | 50kHz-500kHz   |
    | 铁硅铝     | 0.5-0.8            | 20kHz-200kHz   |
    | 铁硅       | 0.8-1.5            | 50Hz-20kHz     |
    | 坡莫合金   | 0.6-1.0            | 1kHz-100kHz    |
    """)
    
    # 使用 markdown 替代 header，应用 CSS 类
    st.markdown('<h3 class="sidebar-title">关于AP值</h3>', unsafe_allow_html=True)
    st.markdown("AP值是磁芯截面积与窗口面积的乘积，反映磁芯功率处理能力，值越大需磁芯尺寸越大。")
    
    # 使用 markdown 替代 header，应用 CSS 类
    st.markdown('<h3 class="sidebar-title">关于本工具</h3>', unsafe_allow_html=True)
    st.info("版本: 1.0.3\n适用于推挽变压器初步设计，实际选型需考虑温升、窗口系数等因素。")

# 页脚
st.markdown("---")
st.markdown("© 2025 变压器设计助手 | 基于Streamlit 1.10.0开发")
