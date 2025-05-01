import streamlit as st
from sudoku import Sudoku
import numpy as np

# 修改生成逻辑确保答案同步生成
def generate_sudoku(difficulty):
    # 映射难度级别
    difficulty_map = {
        "简单": 0.3,  # 对应easy
        "中等": 0.5,  # 对应medium
        "困难": 0.7   # 对应hard
    }
    
    # 创建数独实例并同步生成答案
    puzzle = Sudoku(3, 3).difficulty(difficulty_map[difficulty])
    solution = puzzle.solve()
    
    # 转换时直接将0替换为空字符串
    question = np.where(np.array(puzzle.board) == 0, '', np.array(puzzle.board))
    solution = np.array(solution.board)
    
    return question, solution

def display_sudoku(sudoku, answer=None):
    html = """<table cellspacing='0' cellpadding='1' style='
        border:2px solid #000;
        margin:5px auto;
        width: 360px;'>"""
    for i in range(9):
        html += "<tr>"
        for j in range(9):
            border = []
            if i % 3 == 0: border.append("border-top:2px solid #000")
            if j % 3 == 0: border.append("border-left:2px solid #000")
            
            # 直接使用单元格内容
            num = str(sudoku[i][j]) if sudoku[i][j] != '' else ''
            if answer is not None and sudoku[i][j] == '':
                num = f"<span style='color:red'>{answer[i][j]}</span>"
            
            html += f"<td style='width:40px;height:40px;text-align:center;" \
                    f"font-size:24px;font-family:Arial,sans-serif;{';'.join(border)}'>" \
                    f"{num}</td>"
        html += "</tr>"
    html += "</table>"
    return html

# 页面设置
st.set_page_config(layout="centered")

# 在侧边栏设置部分修改按钮逻辑
with st.sidebar:
    st.header("设置选项")
    difficulty = st.selectbox("选择难度", ["简单", "中等", "困难"])
    col1, col2 = st.columns(2)
    with col1:
        if st.button("生成新数独"):
            st.session_state.generate_clicked = True
    with col2:
        if st.button("显示答案"):
            st.session_state.show_answer = not getattr(st.session_state, 'show_answer', False)

# 生成数独
if st.session_state.generate_clicked :
    st.session_state.puzzles = []
    st.session_state.answers = []
    for _ in range(2):
        puzzle, solution = generate_sudoku(difficulty)
        st.session_state.puzzles.append(puzzle)
        st.session_state.answers.append(solution)

# 在显示部分修改状态判断
if 'puzzles' in st.session_state:
    # 获取持久化的显示答案状态
    show_answer = getattr(st.session_state, 'show_answer', False)
    for i in range(2):
        with st.container():
            # 确保传递完整的答案数据
            answer = st.session_state.answers[i] if show_answer and i < len(st.session_state.answers) else None
            st.markdown(display_sudoku(
                st.session_state.puzzles[i], 
                answer
            ), unsafe_allow_html=True)
            st.write("")

# 打印样式
st.markdown("""
<style>
    @media print {
        .sidebar, header, .stButton { 
            display: none !important; 
        }
        .main .block-container { 
            max-width: 100% !important;
            padding: 5mm !important;
        }
        table {
            margin: 10mm auto !important;
            page-break-inside: avoid;
        }
    }
</style>
""", unsafe_allow_html=True)
