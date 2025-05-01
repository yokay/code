import streamlit as st
from sudoku import Sudoku
import numpy as np

def generate_sudoku(difficulty):
    # 映射难度级别
    difficulty_map = {
        "简单": 0.3,  # 对应easy
        "中等": 0.5,  # 对应medium
        "困难": 0.7   # 对应hard
    }
    
    # 创建数独实例
    puzzle = Sudoku(3, 3).difficulty(difficulty_map[difficulty])
    
    # 获取题目和答案
    question = np.array(puzzle.board)
    answer = np.array(puzzle.solve().board)
    
    return question, answer

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
            
            num = ""
            if sudoku[i][j] != 0:
                num = str(sudoku[i][j])
            elif answer is not None:
                num = f"<span style='color:red'>{answer[i][j]}</span>"
            
            html += f"<td style='width:40px;height:40px;text-align:center;" \
                    f"font-size:24px;font-family:Arial,sans-serif;{';'.join(border)}'>" \
                    f"{num}</td>"
        html += "</tr>"
    html += "</table>"
    return html

# 页面设置
st.set_page_config(layout="centered")

# 侧边栏控件
with st.sidebar:
    st.header("设置选项")
    difficulty = st.selectbox("选择难度", ["简单", "中等", "困难"])
    col1, col2 = st.columns(2)
    with col1:
        generate_clicked = st.button("生成新数独")
    with col2:
        show_answer = st.button("显示答案")

# 生成数独
if generate_clicked:
    st.session_state.puzzles = []
    st.session_state.answers = []
    for _ in range(2):
        puzzle, solution = generate_sudoku(difficulty)
        st.session_state.puzzles.append(puzzle)
        st.session_state.answers.append(solution)

# 显示数独
if 'puzzles' in st.session_state:
    use_answer = st.session_state.answers if show_answer else [None]*2
    for i in range(2):
        with st.container():
            if i < len(st.session_state.puzzles):
                st.markdown(display_sudoku(
                    st.session_state.puzzles[i],
                    use_answer[i] if i < len(use_answer) else None
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
