import streamlit as st

# 单位转换系数（相对于基准单位）
unit_groups = {
    "距离": {
        "千米": 1000,
        "米": 1,
        "厘米": 0.01,
        "毫米": 0.001,
        "英里": 1609.34,
        "码": 0.9144,
        "英尺": 0.3048,
        "英寸": 0.0254
    },
    "重量": {
        "吨": 1000,
        "千克": 1,
        "克": 0.001,
        "磅": 0.453592,
        "盎司": 0.0283495
    },
    "时间": {
        "年": 31536000,
        "月": 2592000,
        "周": 604800,
        "天": 86400,
        "小时": 3600,
        "分钟": 60,
        "秒": 1
    },
    "面积": {
        "平方千米": 1e6,
        "平方米": 1,
        "平方分米": 0.01,
        "平方厘米": 0.0001,
        "平方毫米": 1e-6,
        "公顷": 10000,
        "英亩": 4046.86,
        "平方英里": 2589988,
        "平方英尺": 0.092903,
        "平方英寸": 0.00064516
    },
    "体积": {
        "立方米": 1,
        "升": 0.001,
        "毫升": 1e-6,
        "立方厘米": 1e-6,
        "立方英尺": 0.0283168,
        "立方英寸": 0.0000163871,
        "美制加仑": 0.00378541,
        "英制加仑": 0.00454609
    },
    "时间格式": {
        "24小时制 -> 12小时制": "12",
        "12小时制 -> 24小时制": "24"
    }
}

def convert(value, from_unit, to_unit, units):
    """将值从一个单位转换为另一个单位"""
    base_value = value * units[from_unit]
    return base_value / units[to_unit]

def convert_time(hour, minute, second, am_pm, conversion_type):
    """转换时间格式（24小时制与12小时制之间）"""
    try:
        if conversion_type == "24":
            if am_pm == "PM" and hour != 12:
                hour += 12
            elif am_pm == "AM" and hour == 12:
                hour = 0
            return f"{hour:02d}:{minute:02d}:{second:02d}"
        else:
            period = "AM" if hour < 12 else "PM"
            hour_12 = hour % 12
            hour_12 = 12 if hour_12 == 0 else hour_12
            return f"{hour_12}:{minute:02d}:{second:02d} {period}"
    except:
        return "无效时间"

# 设置页面配置
st.set_page_config(
    page_title="单位换算器",
    page_icon="🔄",
    layout="wide"
)

# 应用标题和描述
st.title("单位换算器")
st.markdown("这是一个多功能单位换算器，支持多种单位类型的换算以及时间格式的转换。")

# 选择换算类别
category = st.selectbox("选择换算类别", list(unit_groups.keys()))

# 根据选择的类别进行不同的处理
if "格式" in category:
    # 时间格式转换
    units = unit_groups[category]
    
    # 使用列布局使界面更美观
    col1, col2 = st.columns(2)
    with col1:
        from_unit = st.selectbox("从", options=list(units.keys()))
    with col2:
        to_unit = st.selectbox("到", options=list(units.keys()))
    
    # 时间输入
    cols = st.columns(3)
    with cols[0]:
        hour = st.number_input("时", 0, 23 if from_unit.startswith("24") else 12, step=1)
    with cols[1]:
        minute = st.number_input("分", 0, 59, 0)
    with cols[2]:
        second = st.number_input("秒", 0, 59, 0)
    
    # 如果是12小时制，需要选择上午/下午
    if from_unit.startswith("12"):
        am_pm = st.selectbox("上午/下午", ["AM", "PM"], index=0)
    else:
        am_pm = ""
    
    # 转换按钮
    if st.button("转换"):
        result = convert_time(hour, minute, second, am_pm, units[from_unit])
        st.success(f"转换结果: {result}")
else:
    # 普通单位换算
    units = unit_groups[category]
    
    # 使用列布局使界面更美观
    col1, col2 = st.columns(2)
    with col1:
        from_unit = st.selectbox("从", options=list(units.keys()))
    with col2:
        to_unit = st.selectbox("到", options=list(units.keys()))
    
    # 输入要转换的值
    value = st.number_input("输入数值", value=1.0, step=0.1, format="%.6g")
    
    # 选择结果显示精度
    precision_mode = st.radio("显示精度", ["小数", "整数"], horizontal=True)
    
    # 执行转换
    result = convert(value, from_unit, to_unit, units)
    
    # 根据精度模式格式化结果
    if precision_mode == "整数":
        result_str = f"{round(result):,}"
    else:
        result_str = f"{result:.4f}"
    
    # 显示结果
    st.success(f"换算结果: {value:.6g} {from_unit} = {result_str} {to_unit}")

# 页脚信息
st.markdown("---")
st.markdown("© 2025 单位换算器 | 设计与开发")    
