import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 检查项和权重配置
check_items = {
    '是否有意义': {
        '是否心血来潮，一时兴起': {'weight': 0.06, 'positive': False},
        '是否经过2~3天冷静期思考': {'weight': 0.08, 'positive': True},
        '是否有在网络上查询过': {'weight': 0.05, 'positive': True},
        '是否会后悔': {'weight': 0.10, 'positive': False},
        '是否在年度计划内': {'weight': 0.07, 'positive': True},
        '是否可以不做': {'weight': 0.04, 'positive': False}
    },
    '是否有价值': {
        '是否对健康有帮助': {'weight': 0.10, 'positive': True},
        '是否产生财务增值': {'weight': 0.10, 'positive': True},
        '是否获取新的知识': {'weight': 0.10, 'positive': True},
        '是否对工作有用': {'weight': 0.07, 'positive': True},
        '是否开心': {'weight': 0.07, 'positive': True},
        '是否对家庭有帮助': {'weight': 0.05, 'positive': True}
    },
    '付出什么代价': {
        '是否需要花一个月时间': {'weight': 0.09, 'positive': False},
        '是否需要花1000元以上': {'weight': 0.07, 'positive': False}
    }
}

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
for category, items in check_items.items():
    st.subheader(f"📊 {category}")
    user_scores[category] = {}
    
    items_list = list(items.items())
    items_per_row = 2  # 每行显示2个评估项
    rows_needed = (len(items_list) + items_per_row - 1) // items_per_row
    
    for row in range(rows_needed):
        start_idx = row * items_per_row
        end_idx = min(start_idx + items_per_row, len(items_list))
        current_items = items_list[start_idx:end_idx]
        
        cols = st.columns(len(current_items))
        
        for i, (item, params) in enumerate(current_items):
            with cols[i]:
                user_scores[category][item] = st.slider(
                    f'{item}', 
                    1, 5,  
                    key=f'{category}_{item}_score',
                    format="%d分"
                )

# 计算每个类别的得分
for category, items in check_items.items():
    category_score = 0.0
    for item, params in items.items():
        score = user_scores[category][item]
        if not params['positive']:
            score = 6 - score  # 负向评估项转换分数
        weighted_score = score * params['weight']
        total_score += weighted_score
        category_score += weighted_score
    category_scores[category] = category_score

# 显示总分和建议
st.write('---')
st.header(f'**最终得分**: {total_score:.2f} / 5.00')

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
    st.dataframe(history_df)
    
    selected_history = st.selectbox(
        "选择历史记录查看详情",
        [h["name"] for h in st.session_state.history],
        format_func=lambda x: f"{x} ({next(h['date'] for h in st.session_state.history if h['name'] == x)})"
    )
    
    if selected_history:
        hist = next(h for h in st.session_state.history if h["name"] == selected_history)
        st.write(f"**{selected_history}** - {hist['date']}")
        st.write(f"最终得分: {hist['total_score']:.2f}")
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
    data = []
    for category, items in user_scores.items():
        for item, score in items.items():
            params = check_items[category][item]
            transformed_score = score if params['positive'] else (6 - score)
            weighted_score = transformed_score * params['weight']
            # 直接将数值转换为字符串，缺失值用'-'表示
            data.append({
                "类别": category,
                "评估项": item,
                "原始评分": str(score),
                "转换后评分": str(transformed_score),
                "权重": f"{params['weight']:.2f}",
                "加权得分": f"{weighted_score:.2f}"
            })
    
    df = pd.DataFrame(data)
    
    # 添加类别汇总行（统一用字符串类型）
    for category in df['类别'].unique():
        cat_total = sum(float(row['加权得分']) for _, row in df[df['类别'] == category].iterrows())
        df = pd.concat([
            df,
            pd.DataFrame({
                "类别": [f"**{category} 总分**"],
                "评估项": ["-"],
                "原始评分": ["-"],
                "转换后评分": ["-"],
                "权重": ["-"],
                "加权得分": [f"{cat_total:.2f}"]
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
            "加权得分": [f"{total_score:.2f}"]
        })
    ], ignore_index=True)
    
    # 使用st.table显示字符串类型数据
    st.table(df)

# 显示类别得分图表（翻译类别名称为英文）
if show_details:
    st.subheader("📊 类别得分分布")
    
    # 将中文类别名称映射为英文
    category_translation = {
        '是否有意义': 'Meaningfulness',
        '是否有价值': 'Value',
        '付出什么代价': 'Cost'
    }
    
    # 使用英文类别名称
    categories = [category_translation.get(cat, cat) for cat in category_scores.keys()]
    scores = [float(score) for score in category_scores.values()]  # 确保为数值类型
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categories, scores, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    
    # 图表英文配置
    ax.set_ylabel('Score', fontsize=12)  # Y轴标签（英文）
    ax.set_title('Category Scores', fontsize=14, pad=20)  # 图表标题（英文）
    ax.set_xlabel('Categories', fontsize=12)  # X轴标签（英文）
    
    # 旋转X轴标签
    plt.xticks(rotation=45)
    
    # 数据标签（英文格式）
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.2f}', ha='center', va='bottom', fontsize=10)
    
    # 调整布局，避免标签被截断
    plt.tight_layout()
    
    st.pyplot(fig)

# 页脚
st.write("---")
st.caption("© 2025 DO OR NOT TO DO 决策评估系统 | 设计用于帮助您做出更明智的决策")
