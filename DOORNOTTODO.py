import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import ScalarMappable

# 设置页面标题
st.title('DO OR NOT TO DO')

# 定义检查项字典及权重
check_items = {
    '是否有意义': {
        '是否心血来潮，一时兴起': 0.05,
        '是否经过2~3天冷静期思考': 0.07,
        '是否有在网络上查询过': 0.04,
        '是否会后悔': 0.10,
        '是否在年度计划内': 0.06,
        '是否可以不做': 0.03
    },
    '是否有价值': {
        '是否对健康有帮助': 0.12,
        '是否产生财务增值': 0.09,    # 计算每个类别的得分
        '是否获取新的知识': 0.09,
        '是否对工作有用': 0.06,
        '是否开心': 0.06,
        '是否对家庭有帮助': 0.03
    },
    '付出什么代价': {
        '是否需要花一个月时间': 0.12,
        '是否需要花1000元以上': 0.08
    }
}

# 创建空字典来存储用户输入的评分
user_scores = {}
total_score = 0.0
category_scores = {}
# 遍历每个类别及其对应的检查项
for category, items in check_items.items():
    st.subheader(category)
    user_scores[category] = {}
    for item, weight in items.items():
        # 获取用户对检查项的评分（1 - 5 分）
        user_scores[category][item] = st.slider(
            f'{item}', 
            1, 5,  
            key=f'{category}_{item}_score'
        )

        
# 计算每个类别的得分
for category, items in check_items.items():
    category_weight = sum(items.values())
    category_score = 0.0
    
    for item, weight in items.items():
        score = user_scores[category][item]
        weighted_score = score * weight
        total_score += weighted_score  # 累加到总分
        category_score += weighted_score  # 累加到类别分
    
    category_scores[category] = category_score

st.write('---')
# 显示总分
st.header(f'**最终得分**: {total_score:.2f} / 5.00')

# 根据总分给出建议
if total_score >= 4.0:
    st.success('**强烈建议去做！** 各方面评估都很积极，值得优先考虑。')
elif total_score >= 3.0:
    st.warning('**可以考虑去做。** 总体评估不错，但某些方面可能需要再斟酌。')
elif total_score >= 2.0:
    st.warning('**建议谨慎考虑。** 存在一些明显的负面因素，需要权衡利弊。')
else:
    st.error('**不建议去做。** 各方面评估都不理想，可能需要重新考虑。')


# 修改后的三维热力图可视化
st.header('三维热力矩阵')
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

    
# 获取三维评分数据
x = category_scores['是否有意义']
y = category_scores['是否有价值']
z = category_scores['付出什么代价']

# 获取各轴最大值
max_x = sum(check_items['是否有意义'].values()) 
max_y = sum(check_items['是否有价值'].values()) 
max_z = sum(check_items['付出什么代价'].values()) 

# 绘制三维导引线（从实际得分位置向轴延伸）
ax.plot([x, max_x], [y, y], [z, z], color='red', linestyle='-', alpha=0.5)  # X轴延伸线
ax.plot([x, x], [y, max_y], [z, z], color='green', linestyle='-', alpha=0.5)  # Y轴延伸线 
ax.plot([x, x], [y, y], [z, max_z], color='blue', linestyle='-', alpha=0.5)  # Z轴延伸线


points = []  # 收集所有连接线起点
for category, items in check_items.items():
    for item, weight in items.items():
        item_score = user_scores[category][item] * weight
        if category == '是否有意义':
            start_point = [item_score, 0, 0]
            ax.plot([item_score, x], [0, y], [0, z], color='gray', linestyle=':', alpha=0.3)
            max_xx = np.max([x,item_score])
        elif category == '是否有价值':
            start_point = [0, item_score, 0]
            ax.plot([0, x], [item_score, y], [0, z], color='gray', linestyle=':', alpha=0.3)
            max_yy = np.max([y,item_score])
        elif category == '付出什么代价':
            start_point = [0, 0, item_score]
            ax.plot([0, x], [0, y], [item_score, z], color='gray', linestyle=':', alpha=0.3)
            max_zz = np.max([z,item_score])
        points.append(start_point)

# 新增：创建金字塔形封闭曲面
# 使用实际评分作为顶点坐标（替换原坐标轴极值点）
vertices = np.array([
    [max_xx, 0, 0],   # 有意义维度得分
    [0, max_yy, 0],   # 有价值维度得分
    [0, 0, max_zz],   # 代价维度得分
    [x, y, z]    # 总分点
])

# 定义三角面连接方式保持不变
triangles = [
    [0, 1, 3],  
    [1, 2, 3],  
    [2, 0, 3],  
    [0, 1, 2]   
]

ax.plot_trisurf(vertices[:,0], vertices[:,1], vertices[:,2],
               triangles=triangles, color='gold', 
               alpha=0.15, edgecolor='navy')


# 创建颜色映射（根据总得分）
point_color = plt.cm.hot(total_score/5) 

# 修改后的散点图绘制
scatter = ax.scatter(x, y, z, 
                    color=point_color,  # 保持原有颜色逻辑
                    s=500,
                    alpha=0.7,
                    edgecolors='w')

# 设置坐标轴标签
ax.set_xlabel('是否有意义 →', labelpad=15)
ax.set_ylabel('是否有价值 →', labelpad=15)
ax.set_zlabel('付出什么代价 →', labelpad=15)

# 创建标准化范围（0-5）
norm = plt.Normalize(vmin=0, vmax=5)
sm = ScalarMappable(norm=norm, cmap=plt.cm.hot)
sm.set_array([])

cbar = fig.colorbar(sm, ax=ax, shrink=0.6)
cbar.set_label('决策温度', fontproperties='SimHei')

# 设置坐标轴范围
max_values = [
    sum(check_items['是否有意义'].values())*5,
    sum(check_items['是否有价值'].values())*5,
    sum(check_items['付出什么代价'].values())*5
]
ax.set_xlim(0, max_values[0])
ax.set_ylim(0, max_values[1])
ax.set_zlim(0, max_values[2])

# 设置观察角度
ax.view_init(elev=25, azim=45)

plt.tight_layout()
st.pyplot(fig)
