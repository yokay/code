import streamlit as st
import random
import time

# 初始化会话状态
if 'grid_size' not in st.session_state:
    st.session_state.grid_size = 5
if 'grid' not in st.session_state:
    st.session_state.grid = []
if 'current_number' not in st.session_state:
    st.session_state.current_number = 1
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'end_time' not in st.session_state:
    st.session_state.end_time = None
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0

# 侧边栏选择方格大小
st.sidebar.title("舒尔特方格设置")
st.session_state.grid_size = st.sidebar.selectbox("选择方格大小", [4, 5, 6, 7, 8, 9], index=1)

# 添加 CSS 样式来调整按钮间距
st.markdown(
    """
    <style>
    .stButton>button {
        margin: 0px;
        padding: 10px;
        width: 100%;
    }
    .css-12w0qpk {
        gap: 0rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 开始新游戏按钮
def reset_game():
    st.session_state.current_number = 1
    st.session_state.start_time = None
    st.session_state.end_time = None
    st.session_state.game_over = False
    st.session_state.elapsed_time = 0
    numbers = list(range(1, st.session_state.grid_size ** 2 + 1))
    random.shuffle(numbers)
    st.session_state.grid = [numbers[i:i+st.session_state.grid_size] for i in range(0, len(numbers), st.session_state.grid_size)]

if st.sidebar.button("开始新游戏"):
    reset_game()

# 显示计时时间
if st.session_state.start_time and not st.session_state.game_over:
    st.session_state.elapsed_time = time.time() - st.session_state.start_time
st.markdown(f"已用时: {st.session_state.elapsed_time:.2f} 秒", unsafe_allow_html=True)

# 游戏主界面
if st.session_state.grid:
    st.title("舒尔特方格训练")

    cols = st.columns(st.session_state.grid_size)
    for i in range(st.session_state.grid_size):
        for j in range(st.session_state.grid_size):
            with cols[j]:
                if not st.session_state.game_over:
                    if st.button(str(st.session_state.grid[i][j])):
                        # 点击数字 1 时开始计时
                        if st.session_state.grid[i][j] == 1 and st.session_state.current_number == 1:
                            st.session_state.start_time = time.time()
                        if st.session_state.grid[i][j] == st.session_state.current_number:
                            if st.session_state.current_number == st.session_state.grid_size ** 2:
                                st.session_state.end_time = time.time()
                                st.session_state.game_over = True
                            else:
                                st.session_state.current_number += 1
                        else:
                            st.error("点击错误，游戏结束！")
                            reset_game()
                else:
                    st.button(str(st.session_state.grid[i][j]), disabled=True)

    if st.session_state.game_over and st.session_state.end_time:
        total_time = st.session_state.end_time - st.session_state.start_time
        st.success(f"恭喜完成！用时 {total_time:.2f} 秒")
        # 添加彩虹色字体的 CSS 样式
        rainbow_style = """
        <style>
        .rainbow-text {
            font-size: 32px;
            background: linear-gradient(to right, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #8f00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        </style>
        """
        st.markdown(rainbow_style, unsafe_allow_html=True)
        # 根据 7 - 12 岁年龄组舒尔特方格训练法评分
        if total_time < 26:
            st.markdown('<p class="rainbow-text">优秀 🎉</p>', unsafe_allow_html=True)
        elif total_time < 42:
            st.markdown('<p class="rainbow-text">中等水平 👍</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="rainbow-text">用时较长，继续加油呀 ⏱️</p>', unsafe_allow_html=True)
        st.balloons()
        st.write(f"总用时: {total_time:.2f} 秒")
