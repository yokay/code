import streamlit as st

# 重新组织单位结构，按物理量分组
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
    "重量/质量": {
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
    },
    "电学": {
        "电流": {
            "安培(A)": 1,
            "毫安培(mA)": 0.001,
            "微安培(μA)": 1e-6,
            "千安培(kA)": 1000
        },
        "电压": {
            "伏特(V)": 1,
            "毫伏(mV)": 0.001,
            "微伏(μV)": 1e-6,
            "千伏(kV)": 1000
        },
        "电阻": {
            "欧姆(Ω)": 1,
            "千欧(kΩ)": 1000,
            "兆欧(MΩ)": 1000000
        },
        "电导": {
            "西门子(S)": 1,
            "毫西门子(mS)": 0.001,
            "微西门子(μS)": 1e-6
        },
        "功率": {
            "瓦特(W)": 1,
            "千瓦(kW)": 1000,
            "兆瓦(MW)": 1000000,
            "毫瓦(mW)": 0.001,
            "微瓦(μW)": 1e-6
        },
        "能量": {
            "焦耳(J)": 1,
            "千焦(kJ)": 1000,
            "兆焦(MJ)": 1000000,
            "千瓦时(kWh)": 3600000
        },
        "电荷量": {
            "库仑(C)": 1,
            "微库仑(μC)": 1e-6,
            "毫库仑(mC)": 0.001,
            "安培小时(Ah)": 3600
        }
    },
    "电磁学": {
        "磁通量密度": {
            "特斯拉(T)": 1,
            "毫特斯拉(mT)": 0.001,
            "微特斯拉(μT)": 1e-6,
            "高斯(G)": 1e-4
        },
        "磁通量": {
            "韦伯(Wb)": 1,
            "毫韦伯(mWb)": 0.001,
            "微韦伯(μWb)": 1e-6
        },
        "电感": {
            "亨利(H)": 1,
            "毫亨利(mH)": 0.001,
            "微亨利(μH)": 1e-6
        },
        "电容": {
            "法拉(F)": 1,
            "毫法(mF)": 0.001,
            "微法(μF)": 1e-6,
            "纳法(nF)": 1e-9,
            "皮法(pF)": 1e-12
        },
        "电磁常数": {
            "亨利/米(H/m)": 1,
            "法拉/米(F/m)": 1
        }
    },
    "声学": {
        "频率": {
            "赫兹(Hz)": 1,
            "千赫兹(kHz)": 1000,
            "兆赫兹(MHz)": 1000000,
            "吉赫兹(GHz)": 1000000000
        },
        "声级": {
            "分贝(dB)": 1,
            "贝尔(B)": 0.1
        },
        "声压": {
            "帕斯卡(Pa)": 1,
            "毫帕斯卡(mPa)": 0.001,
            "微帕斯卡(μPa)": 1e-6
        },
        "声速": {
            "米/秒(m/s)": 1,
            "千米/小时(km/h)": 0.277778,
            "英尺/秒(ft/s)": 0.3048,
            "马赫(Mach)": 340.29
        }
    },
    "光学": {
        "长度": {
            "米(m)": 1,
            "千米(km)": 1000,
            "厘米(cm)": 0.01,
            "毫米(mm)": 0.001,
            "微米(μm)": 1e-6,
            "纳米(nm)": 1e-9,
            "埃(Å)": 1e-10
        },
        "频率": {
            "赫兹(Hz)": 1,
            "千赫兹(kHz)": 1000,
            "兆赫兹(MHz)": 1000000,
            "吉赫兹(GHz)": 1000000000,
            "太赫兹(THz)": 1000000000000
        },
        "能量": {
            "焦耳(J)": 1,
            "电子伏特(eV)": 1.60218e-19
        },
        "光通量": {
            "流明(lm)": 1
        },
        "发光强度": {
            "坎德拉(cd)": 1
        },
        "光照度": {
            "勒克斯(lx)": 1
        },
        "亮度": {
            "尼特(cd/m²)": 1
        },
        "发光效率": {
            "流明/瓦(lm/W)": 1
        },
        "光功率": {
            "瓦特(W)": 1,
            "毫瓦(mW)": 0.001,
            "微瓦(μW)": 1e-6,
            "千瓦(kW)": 1000
        }
    },
    "热力学": {
        "温度": {
            "开尔文(K)": 1,  # 特殊处理，见convert_temperature函数
            "摄氏度(°C)": 1,  # 特殊处理，见convert_temperature函数
            "华氏度(°F)": 1,  # 特殊处理，见convert_temperature函数
            "兰金(R)": 1     # 特殊处理，见convert_temperature函数
        },
        "能量": {
            "焦耳(J)": 1,
            "卡路里(cal)": 4.184,
            "千卡(kcal)": 4184,
            "英热单位(BTU)": 1055.06
        },
        "功率": {
            "瓦特(W)": 1,
            "千瓦(kW)": 1000,
            "马力(HP)": 745.7,
            "千瓦小时(kWh)": 3600000
        },
        "热流率": {
            "卡/秒(cal/s)": 4.184,
            "千卡/小时(kcal/h)": 1.16222,
            "英热单位/小时(BTU/h)": 0.293071
        },
        "热导率": {
            "瓦/米·开尔文(W/(m·K))": 1,
            "英热单位·英尺/(小时·平方英尺·°F)(BTU·ft/(h·ft²·°F))": 1.73073
        }
    },
    "力学": {
        "力": {
            "牛顿(N)": 1,
            "千克力(kgf)": 9.80665,
            "磅力(lbf)": 4.44822,
            "达因(dyn)": 1e-5
        },
        "能量/功": {
            "焦耳(J)": 1,
            "牛顿·米(N·m)": 1,
            "千克力·米(kgf·m)": 9.80665,
            "英尺·磅力(ft·lbf)": 1.35582,
            "尔格(erg)": 1e-7
        },
        "功率": {
            "瓦特(W)": 1,
            "焦耳/秒(J/s)": 1,
            "千克力·米/秒(kgf·m/s)": 9.80665,
            "英尺·磅力/秒(ft·lbf/s)": 1.35582,
            "马力(HP)": 745.7
        },
        "压力": {
            "帕斯卡(Pa)": 1,
            "千帕(kPa)": 1000,
            "兆帕(MPa)": 1000000,
            "巴(bar)": 100000,
            "标准大气压(atm)": 101325,
            "托(Torr)": 133.322,
            "毫米汞柱(mmHg)": 133.322,
            "磅力/平方英寸(psi)": 6894.76,
            "千克力/平方厘米(kgf/cm²)": 98066.5
        },
        "速度": {
            "米/秒(m/s)": 1,
            "千米/小时(km/h)": 0.277778,
            "英里/小时(mph)": 0.44704,
            "节(knot)": 0.514444,
            "英尺/秒(ft/s)": 0.3048
        },
        "加速度": {
            "加速度(m/s²)": 1,
            "重力加速度(g)": 9.80665
        },
        "角速度": {
            "弧度/秒(rad/s)": 1,
            "转/分钟(RPM)": 0.10472
        },
        "质量": {
            "千克(kg)": 1,
            "克(g)": 0.001,
            "毫克(mg)": 1e-6,
            "吨(t)": 1000,
            "磅(lb)": 0.453592,
            "盎司(oz)": 0.0283495
        },
        "体积": {
            "立方米(m³)": 1,
            "升(L)": 0.001,
            "毫升(mL)": 1e-6,
            "立方厘米(cm³)": 1e-6,
            "加仑(美制,gal)": 0.00378541,
            "加仑(英制,gal)": 0.00454609
        },
        "流量": {
            "升/秒(L/s)": 0.001,
            "立方米/小时(m³/h)": 0.000277778,
            "加仑/分钟(GPM)": 6.30902e-5
        },
        "粘度": {
            "帕斯卡·秒(Pa·s)": 1,
            "泊(P)": 0.1,
            "厘泊(cP)": 0.001
        }
    },
    "化学": {
        "物质的量": {
            "摩尔(mol)": 1,
            "毫摩尔(mmol)": 0.001,
            "微摩尔(μmol)": 1e-6,
            "纳摩尔(nmol)": 1e-9,
            "皮摩尔(pmol)": 1e-12
        },
        "质量": {
            "千克(kg)": 1,
            "克(g)": 0.001,
            "毫克(mg)": 1e-6,
            "微克(μg)": 1e-9,
            "纳克(ng)": 1e-12,
            "皮克(pg)": 1e-15
        },
        "体积": {
            "升(L)": 1,
            "毫升(mL)": 0.001,
            "微升(μL)": 1e-6,
            "纳升(nL)": 1e-9,
            "皮升(pL)": 1e-12
        },
        "浓度": {
            "摩尔/升(M)": 1,
            "毫摩尔/升(mM)": 0.001,
            "微摩尔/升(μM)": 1e-6,
            "纳摩尔/升(nM)": 1e-9,
            "皮摩尔/升(pM)": 1e-12
        },
        "质量浓度": {
            "质量浓度(g/L)": 1,
            "质量浓度(mg/mL)": 1,
            "质量浓度(μg/μL)": 1
        },
        "比例": {
            "ppm": 1,  # 百万分之一 (part per million)
            "ppb": 0.001,  # 十亿分之一 (part per billion)
            "ppt": 0.000001  # 万亿分之一 (part per trillion)
        },
        "密度": {
            "密度(g/cm³)": 1,
            "密度(kg/m³)": 0.001,
            "密度(lb/ft³)": 0.0160185
        },
        "渗透压": {
            "渗透压(Pa)": 1,
            "渗透压(atm)": 9.86923e-6
        }
    }
}

def convert(value, from_unit, to_unit, units):
    """将值从一个单位转换为另一个单位"""
    # 特殊处理温度单位转换
    if isinstance(units, dict) and "温度" in units:
        if from_unit in ["摄氏度(°C)", "华氏度(°F)", "开尔文(K)", "兰金(R)"] and to_unit in ["摄氏度(°C)", "华氏度(°F)", "开尔文(K)", "兰金(R)"]:
            return convert_temperature(value, from_unit, to_unit)
    
    # 检查单位是否在当前单位组中
    if from_unit not in units or to_unit not in units:
        return "错误：单位不匹配"
    
    base_value = value * units[from_unit]
    return base_value / units[to_unit]

def convert_temperature(value, from_unit, to_unit):
    """特殊处理温度单位转换"""
    if from_unit == "摄氏度(°C)":
        if to_unit == "华氏度(°F)":
            return value * 9/5 + 32
        elif to_unit == "开尔文(K)":
            return value + 273.15
        elif to_unit == "兰金(R)":
            return (value + 273.15) * 9/5
    elif from_unit == "华氏度(°F)":
        if to_unit == "摄氏度(°C)":
            return (value - 32) * 5/9
        elif to_unit == "开尔文(K)":
            return (value + 459.67) * 5/9
        elif to_unit == "兰金(R)":
            return value + 459.67
    elif from_unit == "开尔文(K)":
        if to_unit == "摄氏度(°C)":
            return value - 273.15
        elif to_unit == "华氏度(°F)":
            return value * 9/5 - 459.67
        elif to_unit == "兰金(R)":
            return value * 9/5
    elif from_unit == "兰金(R)":
        if to_unit == "摄氏度(°C)":
            return (value - 491.67) * 5/9
        elif to_unit == "华氏度(°F)":
            return value - 459.67
        elif to_unit == "开尔文(K)":
            return value * 5/9
    
    return value  # 默认返回原值

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

def format_number(value, precision_mode, scientific_threshold=1e-4):
    """格式化数字，根据值的大小和精度模式选择合适的显示格式"""
    # 检查是否为整数
    if value == int(value):
        return f"{int(value):,}"
    
    # 检查是否需要科学计数法
    if abs(value) < scientific_threshold and value != 0:
        return f"{value:.4e}"
    
    # 根据精度模式格式化
    if precision_mode == "整数":
        return f"{round(value):,}"
    else:
        # 小数模式，保留4位小数
        return f"{value:.4f}"

# 应用标题和描述
st.title("单位换算器")
st.markdown("这是一个多功能单位换算器，支持多种单位类型的换算以及时间格式的转换。")

# 选择换算类别
category = st.selectbox("选择换算类别", list(unit_groups.keys()))

# 根据选择的类别进行不同的处理
if "格式" in category:
    # 时间格式转换
    units = unit_groups[category]
    
    # 时间格式选择
    from_unit = st.selectbox("从", options=list(units.keys()))
    to_unit = st.selectbox("到", options=list(units.keys()))
    
    # 时间输入
    hour = st.number_input("时", 0, 23 if from_unit.startswith("24") else 12, step=1)
    minute = st.number_input("分", 0, 59, 0)
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
    # 检查是否是复合类别（如电学、电磁学等）
    if any(isinstance(sub_units, dict) for sub_units in unit_groups[category].values()):
        # 复合类别，先选择物理量类型
        physical_quantity = st.selectbox("选择物理量", list(unit_groups[category].keys()))
        units = unit_groups[category][physical_quantity]
    else:
        # 简单类别，直接使用单位组
        units = unit_groups[category]
    
    # 单位选择
    from_unit = st.selectbox("从", options=list(units.keys()))
    to_unit = st.selectbox("到", options=list(units.keys()))
    
    # 输入要转换的值
    value = st.number_input("输入数值", value=1.0, step=0.1, format="%.6g")
    
    # 选择结果显示精度
    precision_mode = st.radio("显示精度", ["小数", "整数", "科学计数法"], horizontal=True)
    
    # 执行转换
    result = convert(value, from_unit, to_unit, units)
    
    # 检查是否为错误信息
    if isinstance(result, str):
        st.error(result)
    else:
        # 根据精度模式格式化结果
        if precision_mode == "科学计数法":
            result_str = f"{result:.4e}"
        else:
            result_str = format_number(result, precision_mode)
        
        # 显示结果
        st.success(f"换算结果: {value:.6g} {from_unit} = {result_str} {to_unit}")

# 页脚信息
st.markdown("---")
st.markdown("© 2025 单位换算器 | 设计与开发")
