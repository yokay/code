import streamlit as st
import pandas as pd
import base64


# 设置页面配置
st.set_page_config(
    page_title="DO OR NOT TO DO",
    page_icon="❓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 定义检查项字典及权重，添加正负方向属性（True表示正向，False表示负向）
check_items = {
    '是否有意义': {
        '是否心血来潮，一时兴起': {'weight': 0.05, 'positive': False},
        '是否经过2~3天冷静期思考': {'weight': 0.07, 'positive': True},
        '是否有在网络上查询过': {'weight': 0.04, 'positive': True},
        '是否会后悔': {'weight': 0.10, 'positive': False},
        '是否在年度计划内': {'weight': 0.06, 'positive': True},
        '是否可以不做': {'weight': 0.03, 'positive': False}
    },
    '是否有价值': {
        '是否对健康有帮助': {'weight': 0.12, 'positive': True},
        '是否产生财务增值': {'weight': 0.09, 'positive': True},
        '是否获取新的知识': {'weight': 0.09, 'positive': True},
        '是否对工作有用': {'weight': 0.06, 'positive': True},
        '是否开心': {'weight': 0.06, 'positive': True},
        '是否对家庭有帮助': {'weight': 0.03, 'positive': True}
    },
    '付出什么代价': {
        '是否需要花一个月时间': {'weight': 0.12, 'positive': False},
        '是否需要花1000元以上': {'weight': 0.08, 'positive': False}
    }
}

# 应用标题和介绍
# 应用标题和介绍
st.title('DO OR NOT TO DO 决策评估系统')
with st.expander("ℹ️ 关于这个应用", expanded=False):
    st.markdown("""
    这个决策评估工具可以帮助你通过多维度分析来决定是否应该做某件事情。
    系统会根据你对各个评估项的评分，计算出一个总分并给出建议。
    
    **如何使用：**
    1. 在每个类别下的各个评估项上滑动滑块进行评分（1-5分）
    2. 查看最终得分和系统建议
    
    **评分说明：**
    - 正向评估项：1分（非常负面）→ 5分（非常正面）
    - 负向评估项：1分（非常正面）→ 5分（非常负面）
    """)

# 侧边栏设置
with st.sidebar:
    st.header("⚙️ 设置")
    show_details = st.checkbox("显示详细评分", value=True)
    show_history = st.checkbox("显示历史记录", value=True)
    decision_name = st.text_input("决策名称", "我的重要决策")
    with st.expander("💡 提示", expanded=False):
        st.markdown("""
        - 为了获得更准确的评估结果，请尽可能客观地进行评分
        - 权重值是根据一般决策重要性预先设置的，可以在代码中修改
        - 可以保存多个决策结果进行比较
        """)

# 初始化会话状态
if 'history' not in st.session_state:
    st.session_state.history = []

# 创建空字典来存储用户输入的评分
user_scores = {}
total_score = 0.0
category_scores = {}

# 遍历每个类别及其对应的检查项
col1, col2 = st.columns([1, 1])
with col1:
    for category, items in check_items.items():
        st.subheader(f"📊 {category}")
        user_scores[category] = {}
        for item, params in items.items():
            # 获取用户对检查项的评分（1 - 5 分）
            user_scores[category][item] = st.slider(
                f'{item}', 
                1, 5,  
                key=f'{category}_{item}_score',
                format="%d分"
            )

# 计算每个类别的得分
for category, items in check_items.items():
    category_weight = sum(params['weight'] for params in items.values())
    category_score = 0.0
    
    for item, params in items.items():
        score = user_scores[category][item]
        # 对于负向评估项，转换分数（例如：5分变为1分，4分变为2分，依此类推）
        if not params['positive']:
            score = 6 - score
        weighted_score = score * params['weight']
        total_score += weighted_score  # 累加到总分
        category_score += weighted_score  # 累加到类别分
    
    category_scores[category] = category_score

# 显示总分和建议
st.write('---')
col1, col2 = st.columns([1, 1])
with col1:
    st.header(f'**最终得分**: {total_score:.2f} / 5.00')
    
    # 根据总分给出建议
    if total_score >= 4.0:
        st.success('🔥 **强烈建议去做！** 各方面评估都很积极，值得优先考虑。')
    elif total_score >= 3.0:
        st.warning('👍 **可以考虑去做。** 总体评估不错，但某些方面可能需要再斟酌。')
    elif total_score >= 2.0:
        st.warning('⚠️ **建议谨慎考虑。** 存在一些明显的负面因素，需要权衡利弊。')
    else:
        st.error('🚫 **不建议去做。** 各方面评估都不理想，可能需要重新考虑。')
    
    # 保存结果按钮
    if st.button("💾 保存本次评估结果"):
        result = {
            "name": decision_name,
            "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            "total_score": total_score,
            "category_scores": category_scores,
            "user_scores": user_scores
        }
        st.session_state.history.append(result)
        st.success(f"已保存评估结果: {decision_name}")

# 显示历史记录
with col2:
    if show_history and st.session_state.history:
        st.subheader("📜 历史评估记录")
        history_df = pd.DataFrame([
            {
                "名称": h["name"],
                "日期": h["date"],
                "得分": h["total_score"],
                "建议": "🔥 强烈建议去做" if h["total_score"] >= 4.0 
                      else "👍 可以考虑" if h["total_score"] >= 3.0 
                      else "⚠️ 谨慎考虑" if h["total_score"] >= 2.0 
                      else "🚫 不建议"
            } for h in st.session_state.history
        ])
        st.dataframe(history_df, use_container_width=True)
        
        # 选择历史记录查看详情
        selected_history = st.selectbox(
            "选择历史记录查看详情",
            [h["name"] for h in st.session_state.history],
            format_func=lambda x: f"{x} ({next(h['date'] for h in st.session_state.history if h['name'] == x)})"
        )
        
        # 在历史记录详情部分添加建议显示        
        if selected_history:
            hist = next(h for h in st.session_state.history if h["name"] == selected_history)
            st.write(f"**{selected_history}** - {hist['date']}")
            st.write(f"最终得分: {hist['total_score']:.2f}")
            
            # 新增建议显示
            if hist["total_score"] >= 4.0:
                st.success('🔥 **强烈建议去做**')
            elif hist["total_score"] >= 3.0:
                st.warning('👍 **可以考虑去做**')
            elif hist["total_score"] >= 2.0:
                st.warning('⚠️ **建议谨慎考虑**')
            else:
                st.error('🚫 **不建议去做**')

# 详细评分展示
if show_details:
    st.subheader("📋 详细评分")
    # 创建评分表格
    data = []
    for category, items in user_scores.items():
        for item, score in items.items():
            params = check_items[category][item]
            # 计算转换后的分数
            transformed_score = score if params['positive'] else (6 - score)
            weighted_score = transformed_score * params['weight']
            data.append({
                "类别": category,
                "评估项": item,
                "原始评分": score,
                "转换后评分": transformed_score,
                "权重": params['weight'],
                "加权得分": weighted_score
            })
    
    df = pd.DataFrame(data)
    
    # 计算并添加类别汇总行
    for category in df['类别'].unique():
        cat_df = df[df['类别'] == category]
        cat_total = cat_df['加权得分'].sum()
        df = pd.concat([
            df,
            pd.DataFrame({
                "类别": [f"**{category} 总分**"],
                "评估项": ["-"],
                "原始评分": ["-"],
                "转换后评分": ["-"],
                "权重": ["-"],
                "加权得分": [cat_total]
            })
        ], ignore_index=True)
    
    # 添加总分行
    df = pd.concat([
        df,
        pd.DataFrame({
            "类别": ["**最终总分**"],
            "评估项": ["-"],
            "原始评分": ["-"],
            "转换后评分": ["-"],
            "权重": ["-"],
            "加权得分": [total_score]
        })
    ], ignore_index=True)
    
    # 显示表格
    st.dataframe(df, use_container_width=True)

# 下载数据按钮
if st.button("📥 下载评估数据"):
    data_dict = {
        "决策名称": decision_name,
        "评估日期": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "总得分": total_score,
        "分类得分": category_scores,
        "详细评分": user_scores
    }
    df = pd.json_normalize(data_dict)
    csv = df.to_csv(sep='\t', na_rep='nan')
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="决策评估_{decision_name}.csv">下载 CSV 文件</a>'
    st.markdown(href, unsafe_allow_html=True)

# 页脚
st.write("---")
st.caption("© 2025 DO OR NOT TO DO 决策评估系统 | 设计用于帮助您做出更明智的决策")
