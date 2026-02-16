import streamlit as st
import json
from datetime import datetime
import pandas as pd

# 页面设置
st.set_page_config(page_title="NutriWave", page_icon="🌱", layout="wide")

# 语言切换 (前端客户可见)
languages = {"中文": "zh", "English": "en"}
language = st.sidebar.selectbox("🌍 语言 / Language", list(languages.keys()), index=0)
lang = languages[language]

# 双语文本 (前端)
texts = {
    "title": {"zh": "🌱 NutriWave: 从想法到配方", "en": "🌱 NutriWave: From Idea to Recipe"},
    "subtitle": {"zh": "5分钟生成可投产植物基发酵配方", "en": "5 Minutes to Scalable Plant-Based Fermented Recipes"},
    "new_recipe": {"zh": "✨ 生成新配方", "en": "✨ Generate New Recipe"},
    "input_label": {"zh": "输入酸奶类型 (e.g. 大豆酸奶，去豆腥，甜豆浆，柔和口感)", "en": "Enter Yogurt Type (e.g. Soy yogurt, remove beany, sweet soymilk, soft texture)"},
    "base": {"zh": "基质", "en": "Base"},
    "texture": {"zh": "口感", "en": "Texture"},
    "generate_btn": {"zh": "🚀 AI生成配方", "en": "🚀 AI Generate Recipe"},
    "success": {"zh": "✅ 配方生成成功！", "en": "✅ Recipe Generated!"},
    "download": {"zh": "📥 下载配方", "en": "📥 Download Recipe"},
}

# 加载数据库 (后端)
@st.cache_data
def load_data():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

data = load_data()

# 管理员模式 (数据库密码保护)
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

admin_password = st.sidebar.text_input("🔒 管理员密码 (团队专用)", type="password")
if admin_password == "nutriwave2026":  # 已改成NutriWave风格密码
    st.session_state.admin_logged_in = True
    st.sidebar.success("✅ 管理员登录成功！")

# 侧边栏菜单 (前端客户看不到数据库)
menu_options = ["🏠 首页 / Home", "✨ 新配方 / New Recipe"]
if st.session_state.admin_logged_in:
    menu_options.append("🧬 数据库 / Database")

menu = st.sidebar.radio("导航 / Navigation", menu_options)

# 首页 (前端)
if menu.startswith("🏠"):
    st.title(texts["title"][lang])
    st.subheader(texts["subtitle"][lang])
    st.image("https://via.placeholder.com/800x300/4CAF50/FFFFFF?text=NutriWave+植物基酸奶", use_column_width=True)

# 新配方 (前端客户输入)
elif menu.startswith("✨"):
    st.title(texts["new_recipe"][lang])
    st.markdown(texts["input_label"][lang])
    
    input_text = st.text_area("酸奶类型 / Yogurt Type", 
        "大豆酸奶，要去除豆腥味，喜欢甜豆浆的味道，口感要柔和一点的。" if lang == "zh" else "Soy yogurt, remove beany flavor, sweet soymilk taste, softer texture.",
        height=120)
    
    col1, col2 = st.columns(2)
    with col1:
        base = st.selectbox(texts["base"][lang], ["大豆", "燕麦", "豌豆", "杏仁"] if lang == "zh" else ["Soy", "Oat", "Pea", "Almond"])
    with col2:
        texture = st.selectbox(texts["texture"][lang], ["柔和", "浓稠", "清爽"] if lang == "zh" else ["Soft", "Thick", "Refreshing"])
    
    if st.button(texts["generate_btn"][lang], type="primary", use_container_width=True):
        with st.spinner("正在生成配方..." if lang == "zh" else "Generating Recipe..."):
            # 前端生成 (用数据库)
            selected_strains = data['strains'][:2]
            struct = data['structure_params']['soft_zh'] if lang == "zh" else data['structure_params']['soft_en']
            
            recipe = {
                "产品 / Product": f"{base}柔和甜酸奶" if lang == "zh" else f"{base} Soft Sweet Yogurt",
                "描述 / Description": f"Clean label: 去除豆腥，甜豆浆风味，{texture}口感。" if lang == "zh" else f"Clean label: Beany removed, sweet soymilk, {texture} texture.",
                "配方 (100kg) / Recipe (100kg)": [
                    "水 85kg",
                    f"{base}蛋白 10kg ({data['suppliers']['proteins_zh'] if lang == 'zh' else data['suppliers']['proteins_en']})",
                    f"甜味剂 0.5kg ({data['suppliers']['sweeteners_zh'] if lang == 'zh' else data['suppliers']['sweeteners_en']})",
                    f"稳定剂 0.3kg ({data['suppliers']['stabilizers_zh'] if lang == 'zh' else data['suppliers']['stabilizers_en']})",
                    f"菌株 / Strains: {', '.join([s['name_zh' if lang == 'zh' else 'name_en'] for s in selected_strains])}"
                ],
                "结构参数 / Structure": struct,
                "发酵路径 / Path": "42°C 8h → pH 4.4"
            }
            
            st.success(texts["success"][lang])
            st.json(recipe)
            st.download_button(texts["download"][lang], json.dumps(recipe, ensure_ascii=False), f"recipe_{datetime.now().strftime('%Y%m%d')}.json")

# 数据库页 (后端，只有我们能见)
elif menu.startswith("🧬"):
    st.title("🧬 内部数据库 / Internal Database (NutriWave)")
    st.markdown("**客户不可见，仅团队使用**")
    
    db_lang = st.selectbox("数据库语言 / DB Language", ["中文", "English"])
    db_lang_code = "zh" if db_lang == "中文" else "en"
    
    st.subheader("菌株库 / Strains")
    strains_df = pd.DataFrame([
        {"名称 / Name": s[f'name_{db_lang_code}'], "益处 / Benefits": ', '.join(s[f'benefits_{db_lang_code}']), "供应商 / Sup": s['uk_sup']}
        for s in data['strains']
    ])
    st.dataframe(strains_df)
    
    st.subheader("结构参数 / Structure Params")
    st.json(data['structure_params'][f'soft_{db_lang_code}'])
    
    st.subheader("供应商 / Suppliers")
    st.json(data['suppliers'])

st.sidebar.markdown("---")
st.sidebar.info("NutriWave MVP v0.4 | 前端客户可见 • 后端团队专用")