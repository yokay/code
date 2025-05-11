import streamlit as st
import time
import math
from datetime import datetime, timedelta

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
if 'timer_placeholder' not in st.session_state:
    st.session_state.timer_placeholder = None
if 'best_time' not in st.session_state:
    st.session_state.best_time = float('inf')
if 'attempts' not in st.session_state:
    st.session_state.attempts = 0
if 'completed_attempts' not in st.session_state:
    st.session_state.completed_attempts = 0
if 'total_time' not in st.session_state:
    st.session_state.total_time = 0
if 'average_time' not in st.session_state:
    st.session_state.average_time = 0
if 'last_attempt_time' not in st.session_state:
    st.session_state.last_attempt_time = 0

# 添加 CSS 样式来调整按钮间距和响应式布局
st.markdown(
    """
    <style>
    /* 主容器样式 */
    .main .block-container {
        max-width: 100%;
        padding: 0rem 1rem;
    }
    
    /* 计时器样式 */
    .timer-container {
        display: flex;
        justify-content: center;
        margin: 0.5rem 0;
        padding: 0.5rem;
        border-radius: 0.5rem;
        background-color: rgba(240, 240, 240, 0.8);
        font-family: monospace;
        font-size: 2rem;
        font-weight: bold;
        color: #333;
    }
    
    /* 按钮容器 */
    .button-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
        gap: 0.3rem;
        margin: 1rem 0;
    }
    
    /* 通用按钮样式 */
    .stButton>button {
        aspect-ratio: 1/1 !important;
        width: 100% !important;
        height: 100% !important;
        margin: 0;
        padding: 0;
        font-size: clamp(1rem, 4vw, 2.5rem) !important;
        font-family: Arial, sans-serif !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
        border-radius: 0.5rem !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }
    
    /* 按钮状态样式 */
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    }
    
    .stButton>button:active {
        transform: translateY(0) !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }
    
    /* 正确点击的按钮 */
    .stButton>button.success {
        background-color: #4CAF50 !important;
        color: white !important;
    }
    
    /* 错误点击效果 */
    .stButton>button.error {
        background-color: #ff4444 !important;
        animation: shake 0.5s !important;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        50% { transform: translateX(5px); }
        75% { transform: translateX(-3px); }
    }
    
    /* 游戏统计卡片 */
    .stats-card {
        background-color: rgba(245, 245, 245, 0.8);
        border-radius: 0.75rem;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stats-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .stats-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1E40AF;
    }
    
    /* 游戏难度指示器 */
    .difficulty-indicator {
        display: flex;
        justify-content: center;
        margin: 0.5rem 0;
    }
    
    .difficulty-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin: 0 2px;
        transition: all 0.3s ease;
    }
    
    /* 移动设备优化 */
    @media (max-width: 768px) {
        .timer-container {
            font-size: 1.5rem;
        }
        
        .stButton>button {
            font-size: clamp(0.8rem, 5vw, 1.5rem) !important;
        }
        
        .stats-card {
            padding: 0.75rem;
        }
        
        .stats-title {
            font-size: 1rem;
        }
        
        .stats-value {
            font-size: 1.2rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 自定义伪随机数生成器
class SimpleRandom:
    def __init__(self, seed=None):
        if seed is None:
            # 使用当前时间戳作为种子
            seed = int(time.time() * 1000) % 1000000
        self.seed = seed
        self.state = seed
    
    def randint(self, a, b):
        """生成[a, b]范围内的伪随机整数"""
        # 简单的线性同余生成器
        self.state = (1664525 * self.state + 1013904223) % (2**32)
        return a + (self.state % (b - a + 1))
    
    def shuffle(self, array):
        """实现Fisher-Yates洗牌算法"""
        n = len(array)
        for i in range(n-1, 0, -1):
            j = self.randint(0, i)
            array[i], array[j] = array[j], array[i]
        return array

# 开始新游戏按钮
def reset_game():
    st.session_state.current_number = 1
    st.session_state.start_time = None
    st.session_state.end_time = None
    st.session_state.game_over = False
    st.session_state.elapsed_time = 0
    
    # 增加尝试次数
    st.session_state.attempts += 1
    
    # 生成随机数填充方格（不使用random库）
    rng = SimpleRandom()
    numbers = list(range(1, st.session_state.grid_size ** 2 + 1))
    shuffled_numbers = rng.shuffle(numbers)
    st.session_state.grid = [shuffled_numbers[i:i+st.session_state.grid_size] for i in range(0, len(shuffled_numbers), st.session_state.grid_size)]
    
    # 清除计时器占位符
    if st.session_state.timer_placeholder:
        st.session_state.timer_placeholder.empty()
    
    st.rerun()  # 刷新整个界面

# 更新计时器显示
def update_timer():
    if st.session_state.start_time and not st.session_state.game_over:
        elapsed = time.time() - st.session_state.start_time
        st.session_state.elapsed_time = elapsed
        
        # 格式化时间显示 (分钟:秒.毫秒)
        minutes, seconds = divmod(elapsed, 60)
        time_display = f"{int(minutes):02}:{seconds:05.2f}"
        
        # 更新计时器显示
        if st.session_state.timer_placeholder:
            st.session_state.timer_placeholder.markdown(f'<div class="timer-container">{time_display}</div>', unsafe_allow_html=True)
        
        # 每秒更新一次
        time.sleep(0.1)
        st.experimental_rerun()

# 显示游戏难度指示器
def show_difficulty_indicator():
    difficulty_level = st.session_state.grid_size - 3  # 4x4 为初级，9x9 为极难
    max_difficulty = 6  # 对应 9x9
    
    dots = []
    for i in range(1, max_difficulty + 1):
        if i <= difficulty_level:
            dots.append(f'<div class="difficulty-dot" style="background-color: #1E40AF;"></div>')
        else:
            dots.append(f'<div class="difficulty-dot" style="background-color: #CBD5E1;"></div>')
    
    st.markdown(f'<div class="difficulty-indicator">{"".join(dots)}</div>', unsafe_allow_html=True)

# 游戏主界面
st.title("✨ 舒尔特方格训练游戏")
st.markdown("点击数字从 1 到 **" + str(st.session_state.grid_size ** 2) + "**，训练你的注意力和反应速度！")

# 显示难度指示器
show_difficulty_indicator()

# 显示当前需要点击的数字
if not st.session_state.game_over:
    st.markdown(f'<div class="text-center text-lg font-bold mb-2">当前目标: <span class="text-blue-600 text-2xl">{st.session_state.current_number}</span></div>', unsafe_allow_html=True)

# 创建计时器占位符
if st.session_state.timer_placeholder is None:
    st.session_state.timer_placeholder = st.empty()

# 更新计时器
update_timer()

# 显示方格
if st.session_state.grid:
    # 使用 CSS Grid 布局
    st.markdown('<div class="button-grid">', unsafe_allow_html=True)
    
    cols = st.columns(st.session_state.grid_size)
    for i in range(st.session_state.grid_size):
        for j in range(st.session_state.grid_size):
            with cols[j]:
                number = st.session_state.grid[i][j]
                # 游戏结束后禁用所有按钮
                disabled = st.session_state.game_over or number < st.session_state.current_number
                
                # 已点击的数字显示为成功状态
                button_class = "success" if number < st.session_state.current_number else ""
                
                # 点击按钮
                if st.button(str(number), key=f"button_{i}_{j}", disabled=disabled):
                    if not st.session_state.game_over:
                        # 点击数字 1 时开始计时
                        if number == 1 and st.session_state.current_number == 1 and st.session_state.start_time is None:
                            st.session_state.start_time = time.time()
                        
                        # 检查点击是否正确
                        if number == st.session_state.current_number:
                            # 正确点击
                            if number == st.session_state.grid_size ** 2:
                                # 游戏完成
                                st.session_state.end_time = time.time()
                                st.session_state.game_over = True
                                
                                # 计算用时
                                total_time = st.session_state.end_time - st.session_state.start_time
                                st.session_state.last_attempt_time = total_time
                                
                                # 更新统计数据
                                st.session_state.completed_attempts += 1
                                st.session_state.total_time += total_time
                                st.session_state.average_time = st.session_state.total_time / st.session_state.completed_attempts
                                
                                # 更新最佳时间
                                if total_time < st.session_state.best_time:
                                    st.session_state.best_time = total_time
                            else:
                                st.session_state.current_number += 1
                        else:
                            # 错误点击
                            st.markdown("""
                            <script>
                            setTimeout(() => {
                                const errorBtn = document.querySelector('button[data-testid="baseButton-secondary"]:not([disabled])');
                                errorBtn.classList.add('error');
                                setTimeout(() => errorBtn.classList.remove('error'), 500);
                            }, 10);
                            </script>
                            """, unsafe_allow_html=True)
                            st.error("点击错误！请重新开始。")
                            st.session_state.game_over = True
    
    st.markdown('</div>', unsafe_allow_html=True)

# 游戏结束后显示结果
if st.session_state.game_over and st.session_state.end_time:
    total_time = st.session_state.end_time - st.session_state.start_time
    
    # 显示结果卡片
    st.markdown('<div class="stats-card">', unsafe_allow_html=True)
    st.markdown('<div class="stats-title">游戏完成！</div>', unsafe_allow_html=True)
    
    # 格式化时间
    minutes, seconds = divmod(total_time, 60)
    time_display = f"{int(minutes):02}:{seconds:05.2f}"
    
    st.markdown(f'<div class="stats-value">用时: {time_display}</div>', unsafe_allow_html=True)
    
    # 显示评分
    if st.session_state.grid_size == 5:  # 标准5x5评分
        if total_time < 26:
            st.markdown('<div class="text-green-600 font-bold">评分: 优秀 🎉</div>', unsafe_allow_html=True)
        elif total_time < 42:
            st.markdown('<div class="text-blue-600 font-bold">评分: 中等水平 👍</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="text-orange-600 font-bold">评分: 用时较长，继续加油 ⏱️</div>', unsafe_allow_html=True)
    else:
        # 根据方格大小调整评分标准
        expected_time = 26 * (st.session_state.grid_size / 5) ** 2
        if total_time < expected_time * 0.7:
            st.markdown('<div class="text-green-600 font-bold">评分: 优秀 🎉</div>', unsafe_allow_html=True)
        elif total_time < expected_time * 1.3:
            st.markdown('<div class="text-blue-600 font-bold">评分: 中等水平 👍</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="text-orange-600 font-bold">评分: 用时较长，继续加油 ⏱️</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 显示统计数据
    st.subheader("📊 游戏统计")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.markdown('<div class="stats-title">最佳时间</div>', unsafe_allow_html=True)
        if st.session_state.best_time < float('inf'):
            best_min, best_sec = divmod(st.session_state.best_time, 60)
            st.markdown(f'<div class="stats-value">{int(best_min):02}:{best_sec:05.2f}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="stats-value">-</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.markdown('<div class="stats-title">平均时间</div>', unsafe_allow_html=True)
        if st.session_state.completed_attempts > 0:
            avg_min, avg_sec = divmod(st.session_state.average_time, 60)
            st.markdown(f'<div class="stats-value">{int(avg_min):02}:{avg_sec:05.2f}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="stats-value">-</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.markdown('<div class="stats-title">完成次数</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stats-value">{st.session_state.completed_attempts}/{st.session_state.attempts}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 显示庆祝动画
    st.balloons()

# 将控制面板移动到侧边栏
with st.sidebar:
    st.header("⚙️ 游戏设置")
    
    st.session_state.grid_size = st.select_slider(
        "选择方格大小", 
        options=[4, 5, 6, 7, 8, 9], 
        value=5,
        format_func=lambda x: f"{x}x{x} ({x**2}个数字)"
    )
    
    st.markdown("""
    **难度说明：**
    - 4x4: 简单 (适合初学者)
    - 5x5: 标准 (适合大多数人)
    - 6x6: 较难
    - 7x7+: 挑战极限
    """)
    
    st.divider()
    
    if st.button("🎮 开始新游戏", 
                use_container_width=True,
                help="点击开始新的游戏"):
        reset_game()
    
    st.divider()
    
    st.subheader("ℹ️ 游戏说明")
    st.markdown("""
    舒尔特训练法是世界公认的提高注意力的有效方法。
    - 点击数字从 1 开始，按顺序点击到最后一个数字
    - 方格越小，难度越低，用时越短说明注意力越集中
    - 记录你的最佳时间，挑战自我！
    """)    
