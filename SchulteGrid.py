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

# 添加 CSS 样式来调整按钮间距和响应式布局
st.markdown(
    """
    <style>
    # 修改按钮容器和按钮样式
.css-1v0mbdj {
    gap: 0 !important;  /* 消除列间隙 */
    padding: 0 !important;
}

    /* 通用按钮样式 */
.stButton>button {
    aspect-ratio: 1/1 !important;
    width: 100% !important;
    height: 100%  !important;
    /* 保持原有其他样式 */
    margin: 0;
    padding: 0;
    min-height: 10px;
    min-width: 10px;
    font-size: 2.5rem !important;
    font-family: Arial, sans-serif !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.3s ease !important;
}

/* 手机适配 */
@media (max-width: 768px) {
    .stButton>button {
       font-size: 1.8rem !important;
    }
}
 /* 主容器样式 */
    .css-1v0mbdj {
        gap: 4px !important;
        flex-wrap: nowrap !important;
        width: 100vw !important;
        overflow-x: auto !important;  /* 允许水平滚动 */
        padding: 0 4px !important;
    }

    /* 隐藏水平滚动条 */
    .css-1v0mbdj::-webkit-scrollbar {
        display: none;
    }
    /* 在现有按钮样式中添加 */
    .stButton>button {
        transition: all 0.3s ease !important;
    }
    
    /* 按钮点击效果 */
    .stButton>button:active {
        background-color: #4CAF50 !important;
        transform: scale(0.98);
    }
    
    /* 正确点击效果 */
    .stButton>button:focus:not(:active) {
        background-color: #4CAF50 !important;
    }
    
    /* 错误点击效果 */
    .stButton>button.error-click {
        background-color: #ff4444 !important;
        animation: shake 0.5s;
    }

    @keyframes shake {
        0% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        50% { transform: translateX(5px); }
        75% { transform: translateX(-3px); }
        100% { transform: translateX(0); }
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
    st.text("游戏已重置，当前方格状态：")
    st.text(str(st.session_state.grid))
    st.text("当前需要点击的数字：")
    st.text(str(st.session_state.current_number))
    st.rerun()  # 刷新整个界面

# 游戏主界面
if st.session_state.grid:
    cols = st.columns(st.session_state.grid_size)
    for i in range(st.session_state.grid_size):
        for j in range(st.session_state.grid_size):
            with cols[j]:
                # 游戏结束后禁用所有按钮
                disabled = st.session_state.game_over
                if st.button(str(st.session_state.grid[i][j]), key=f"active_button_{i}_{j}", disabled=disabled):
                    if not st.session_state.game_over:
                        # 点击数字 1 时开始计时
                        if st.session_state.grid[i][j] == 1 and st.session_state.current_number == 1 and st.session_state.start_time is None:
                            st.session_state.start_time = time.time()
                        if st.session_state.grid[i][j] == st.session_state.current_number:
                            if st.session_state.current_number == st.session_state.grid_size ** 2:
                                st.session_state.end_time = time.time()
                                st.session_state.game_over = True
                            else:
                                st.session_state.current_number += 1
                        else:
                            # 添加错误点击效果
                            st.markdown("""
                            <script>
                            setTimeout(() => {
                                const errorBtn = document.querySelector('button[data-testid="baseButton-secondary"]:not([disabled])');
                                errorBtn.classList.add('error-click');
                                setTimeout(() => errorBtn.classList.remove('error-click'), 500);
                            }, 10);
                            </script>
                            """, unsafe_allow_html=True)
                            st.error("点击错误，游戏结束！")
                            st.session_state.game_over = True

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

# 将控制面板移动到侧边栏
with st.sidebar:
    st.header("游戏设置")
    st.session_state.grid_size = st.selectbox(
        "选择方格大小", 
        [4, 5, 6, 7, 8, 9], 
        index=1
    )
    
    if st.button("开始新游戏", 
                key="new_game_button",
                use_container_width=True,
                help="点击开始新的游戏"):
        reset_game()
