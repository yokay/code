import streamlit as st

pg = st.navigation([st.Page("./pages/homepage.py", title="Home", icon="🏠")])

# 假设这是 calculate_ap 函数，你需要根据实际情况替换
def calculate_ap(p_out, efficiency, b_w, f):
    # 这里只是示例实现，你需要替换为真实的计算逻辑
    return (p_out * (1 / efficiency)) / (b_w * f)

st.title('推挽变压器 AP 值计算')

# 创建输入组件
p_out = st.number_input('输出功率 (W)', value=3)
efficiency = st.number_input('变换器效率', min_value=0.01, max_value=1.0, value=0.2)
b_w = st.number_input('磁芯材料工作磁通密度 (T)', value=0.01)
f = st.number_input('开关频率 (Hz)', value=1e6)

# 计算并显示结果
if st.button('计算'):
    ap_result = calculate_ap(p_out, efficiency, b_w, f)
    st.write(f"计算得到的 AP 值为: {ap_result} cm⁴")

st.write(
    "Copyright © 2025 by [MYTHBIRD](https://www.mythbird.com)"
)

pg.run()
