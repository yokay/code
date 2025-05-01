import streamlit as st
import sudokum
import numpy as np

def generate_sudoku(difficulty):
    # 设置难度级别对应的挖空比例
    difficulty_map = {
        "简单": 0.3,  # 保留70%数字
        "中等": 0.5,  # 保留50%数字
        "困难": 0.65  # 保留35%数字
    }
    
    # 生成标准数独（保证唯一解）
    matrix = sudokum.generate(3)  # 3表示标准9x9数独
    solution = matrix.copy()
    
    # 按难度挖空（保持唯一解）
    sudokum.mask(matrix, difficulty_map[difficulty])
    
    return matrix, solution

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
