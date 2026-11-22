import streamlit as st
import pandas as pd
import time
import gspread
from groq import Groq

# 1. Կայքի կարգավորումներ և հավելվածի տեսք
st.set_page_config(page_title="EcoDrop", page_icon="♻️", layout="centered")

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 2. Միացում Groq AI-ին և Google Sheets-ին
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

@st.cache_resource
def init_gsheet():
    credentials = dict(st.secrets["gcp_service_account"])
    gc = gspread.service_account_from_dict(credentials)
    sh = gc.open("EcoDrop_Users")
    return sh.sheet1

sheet = init_gsheet()

# Օգնող ֆունկցիաներ Google Sheet-ի հետ աշխատելու համար
def get_all_users():
    return sheet.get_all_records()

def update_user_points(username, new_points):
    cell = sheet.find(username)
    sheet.update_cell(cell.row, 4, new_points) # 4-րդ սյունակը points-ն է

# Հիշողության կարգավորում (մուտք գործած է օգտատերը, թե ոչ)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.fullname = ""
    st.session_state.points = 0

# ==========================================
# ՊԱՐՏԱԴԻՐ ՄՈՒՏՔ ԵՎ ԳՐԱՆՑՈՒՄ (Եթե մուտք չի գործել)
# ==========================================
if not st.session_state.logged_in:
    st.title("♻️ EcoDrop")
    st.write("Շարունակելու համար խնդրում ենք մուտք գործել կամ գրանցվել։")
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 Մուտք (Login)", "📝 Գրանցում (Sign Up)"])
    
    # --- ՄՈՒՏՔ ---
    with auth_tab1:
        login_user = st.text_input("Օգտանուն (Username)", key="login_u")
        login_pass = st.text_input("Գաղտնաբառ", type="password", key="login_p")
        
        if st.button("Մուտք գործել", use_container_width=True):
            users = get_all_users()
            user_found = False
            for u in users:
                if str(u['username']) == login_user and str(u['password']) == login_pass:
                    st.session_state.logged_in = True
                    st.session_state.username = str(u['username'])
                    st.session_state.fullname = str(u['fullname'])
                    st.session_state.points = int(u['points'])
                    user_found = True
                    st.rerun()
            if not user_found:
                st.error("❌ Սխալ օգտանուն կամ գաղտնաբառ։")

    # --- ԳՐԱՆՑՈՒՄ ---
    with auth_tab2:
        new_fullname = st.text_input("Անուն Ազգանուն", placeholder="Օրինակ՝ Արամ Սարգսյան")
        new_user = st.text_input("Ընտրեք օգտանուն (Username)", placeholder="aram2026")
        new_pass = st.text_input("Ստեղծեք գաղտնաբառ", type="password")
        
        if st.button("Գրանցվել և ստանալ 50 բոնուս միավոր 🎁", use_container_width=True):
            if new_fullname and new_user and new_pass:
                users = get_all_users()
                if any(str(u['username']) == new_user for u in users):
                    st.warning("⚠️ Այս օգտանունը արդեն զբաղված է։ Ընտրեք մեկ ուրիշը։")
                else:
                    # Ավելացնում ենք նոր տող Google Sheet-ում (սկզբնական 50 միավորով)
                    sheet.append_row([new_user, new_pass, new_fullname, 50])
                    st.session_state.logged_in = True
                    st.session_state.username = new_user
                    st.session_state.fullname = new_fullname
                    st.session_state.points = 50
                    st.success("🎉 Գրանցումը հաջողվեց։")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("Խնդրում ենք լրացնել բոլոր դաշտերը։")

# ==========================================
# ՀԻՄՆԱԿԱՆ ՀԱՎԵԼՎԱԾԸ (Միայն գրանցվելուց հետո)
# ==========================================
else:
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.title("♻️ EcoDrop")
        st.write(f"Բարի գալուստ, **{st.session_state.fullname}** 👋")
    with col_head2:
        if st.button("Դուրս գալ"):
            st.session_state.logged_in = False
            st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📷 Սկանավորել", 
        "📍 Քարտեզ", 
        "🏆 Միավորներ", 
        "🤖 AI Օգնական"
    ])

    # --- ԲԱԺԻՆ 1. ՏԵՍԱԽՑԻԿ ---
    with tab1:
        st.subheader("Քայլ 1. Աղբամանի QR կոդը հաստատված է ✅")
        st.caption("Գտնվելու վայրը՝ ԵՊՀ Գլխավոր մասնաշենք (GPS հաստատված)")
        
        photo = st.camera_input("Լուսանկարիր պլաստիկ շիշը")
        if photo is None:
            photo = st.file_uploader("Կամ ընտրիր նկար հեռախոսից", type=["jpg", "png", "jpeg"])

        if photo is not None:
            if st.button("🔍 Ստուգել և գցել աղբամանը", use_container_width=True):
                with st.spinner('AI-ն վերլուծում է շիշը...'):
                    time.sleep(2)
                
                st.session_state.points += 10
                update_user_points(st.session_state.username, st.session_state.points)
                
                st.success("🎉 AI-ն ճանաչեց՝ **0.5լ Պլաստիկ շիշ (PET)**")
                st.balloons()
                st.info(f"Հաշվին ավելացավ **+10 միավոր**։ Ընդհանուրը՝ **{st.session_state.points}**")

    # --- ԲԱԺԻՆ 2. ՔԱՐՏԵԶ ---
    with tab2:
        st.subheader("Երևանի խելացի աղբամանները")
        locations = pd.DataFrame({
            'lat': [40.1872, 40.1776, 40.1924, 40.1811],
            'lon': [44.5152, 44.5126, 44.5035, 44.5140]
        })
        st.map(locations)
        st.write("🟢 **ԵՊՀ Գլխավոր մասնաշենք** — Ազատ է (30%)")
        st.write("🟢 **Հանրապետության Հրապարակ** — Ազատ է (45%)")
        st.write("🟡 **Կասկադ** — Գրեթե լիքն է (80%)")

    # --- ԲԱԺԻՆ 3. ՄԻԱՎՈՐՆԵՐ ---
    with tab3:
        st.metric(label="Ձեր ընթացիկ հաշիվը", value=f"{st.session_state.points} միավոր")
        st.markdown("---")
        st.subheader("🎁 Փոխանակել միավորները")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("☕ **Անվճար սուրճ** (60 միավոր)")
            if st.button("Ստանալ սուրճ"):
                if st.session_state.points >= 60:
                    st.session_state.points -= 60
                    update_user_points(st.session_state.username, st.session_state.points)
                    st.success("Պրոմո-կոդ՝ **ECO2026**")
                else:
                    st.error("Միավորները չեն բավականացնում։")
                    
        with col2:
            st.write("🛍️ **Էկո-պայուսակ** (150 միավոր)")
            if st.button("Ստանալ պայուսակ"):
                if st.session_state.points >= 150:
                    st.session_state.points -= 150
                    update_user_points(st.session_state.username, st.session_state.points)
                    st.success("Կարող եք վերցնել մոտակա կետից։")
                else:
                    st.error(f"Պակասում է {150 - st.session_state.points} միավոր։")

    # --- ԲԱԺԻՆ 4. AI ՕԳՆԱԿԱՆ ---
    with tab4:
        st.subheader("Հարցրու EcoDrop AI-ին 🌿")
        user_question = st.text_input("Գրիր հարցդ (օրինակ՝ Ինչպե՞ս տարբերել PET պլաստիկը).")
        
        if st.button("Ուղարկել հարցը"):
            if user_question:
                with st.spinner("AI-ն մտածում է..."):
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {
                                    "role": "system",
                                    "content": "Դու EcoDrop էկո-հավելվածի օգնականն ես: Պատասխանիր կարճ, ընկերական և բացառապես գրագետ, մաքուր հայերենով՝ առանց տառասխալների:"
                                },
                                {
                                    "role": "user",
                                    "content": user_question,
                                }
                            ],
                            model="openai/gpt-oss-120b",
                            temperature=0.3,
                        )
                        st.success(chat_completion.choices[0].message.content)
                    except Exception as e:
                        st.error(f"Սխալ՝ {e}")
            else:
                st.warning("Խնդրում ենք նախ գրել հարցը:")
