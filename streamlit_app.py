import streamlit as st
import importlib.util
import os
import sys

# 获取当前脚本所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 页面配置字典
pages = {
    "Push & Pull Transformer AP Value": "APcalculator.py",
    "Cap and inductor": "ImpedanceCalculator.py",
    "Smith Chart": "smithmatch.py",
    "Snubber": "snubber.py",
    "Unit Calc": "unitCal.py",
    "TO DO OR NOT TO DO": "DOORNOTTODO.py"
}

# 初始化会话状态 - 默认为None（空白页）
if 'current_page' not in st.session_state:
    st.session_state.current_page = None

# 定义页面切换函数
def change_page(page_name):
    st.session_state.current_page = page_name

# 清除缓存函数（兼容Streamlit 1.10.0）
def clear_cache():
    # 使用Streamlit 1.10.0官方支持的缓存清除方法
    try:
        # 尝试使用1.10.0版本的缓存清除方法
        from streamlit.caching import clear_cache
        clear_cache()
    except ImportError:
        # 如果无法导入，尝试使用内部API
        try:
            from streamlit.caching import _clear_cached_funcs
            _clear_cached_funcs()
        except ImportError:
            st.warning("无法清除缓存，请刷新页面")

# 加载并运行选定的页面
def load_page(page_name):
    script_name = pages[page_name]
    script_path = os.path.join(BASE_DIR, script_name)
    
    if not os.path.exists(script_path):
        st.error(f"找不到脚本文件: {script_path}")
        st.info(f"请确保 {script_name} 文件存在于 {BASE_DIR} 目录下")
        return
    
    try:
        sys.path.append(BASE_DIR)
        spec = importlib.util.spec_from_file_location(page_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        st.error(f"加载页面时出错: {e}")
        import traceback
        st.text(traceback.format_exc())

# 设置CSS样式，使按钮大小一致且均匀分布
st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    height: 50px;
    font-size: 16px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# 计算需要的行数（每行最多3个按钮）
num_pages = len(pages)
num_rows = (num_pages + 2) // 3  # 向上取整

# 按行创建按钮，确保每行有3列，即使按钮不足3个
for row in range(num_rows):
    cols = st.columns(3)
    
    for i in range(3):
        idx = row * 3 + i
        if idx < num_pages:
            page_name = list(pages.keys())[idx]
            
            # 使用on_click参数绑定回调函数
            cols[i].button(
                page_name, 
                key=f"btn_{page_name}",
                on_click=change_page,
                args=(page_name,)
            )
        else:
            # 空列，保持布局一致
            cols[i].write("")
# 添加刷新按钮
if st.button("Rerun"):
    st.experimental_rerun()
# 显示当前页面内容（初始为空白）
st.markdown("---")

# 清除缓存并初始化
if st.session_state.current_page is None:
    clear_cache()
    st.info("请从上方选择一个工具开始使用")

else:
    st.subheader(st.session_state.current_page)
    load_page(st.session_state.current_page)

# 页脚
st.markdown("---")
st.write(
    "Copyright © 2025 by [MYTHBIRD](https://www.mythbird.com) [粤ICP备15000778号](https://beian.miit.gov.cn/)"
)
