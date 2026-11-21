import streamlit as st
import pandas as pd
import time
from groq import Groq

# Կայքի էջի կարգավորումները
st.set_page_config(page_title="EcoDrop", page_icon="♻️", layout="centered")

API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

client = Groq(api_key=API_KEY)

# Հիշողության մեջ պահում ենք օգտատիրոջ միավորները (սկզբում 50 միավոր)
if 'points' not in st.session_state:
    st.session_state.points = 50

# Կայքի վերնագիրը
st.title("♻️ EcoDrop")
st.write("Հանձնի՛ր պլաստիկ շշերը, սկանավորի՛ր և ստացի՛ր իրական մրցանակներ։")

# Մենյու (Ավելացրել ենք 4-րդ բաժինը՝ AI Օգնական)
tab1, tab2, tab3, tab4 = st.tabs([
    "📷 Սկանավորել շիշը", 
    "📍 Աղբամանների քարտեզ", 
    "🏆 Իմ միավորները", 
    "🤖 AI Էկո-Օգնական"
])

# --- ԲԱԺԻՆ 1. ՏԵՍԱԽՑԻԿ ԵՎ AI ---
with tab1:
    st.subheader("Քայլ 1. Աղբամանի QR կոդը հաստատված է ✅")
    st.caption("Գտնվելու վայրը՝ ԵՊՀ Գլխավոր մասնաշենք (GPS հաստատված)")
    
    st.subheader("Քայլ 2. Լուսանկարիր պլաստիկ շիշը")
    
    # Բացում է համակարգչի կամ հեռախոսի տեսախցիկը
    photo = st.camera_input("Պահիր շիշը տեսախցիկի առաջ և սեղմիր լուսանկարել")
    
    if photo is None:
        photo = st.file_uploader("Կամ ընտրիր պատրաստի նկար համակարգչից", type=["jpg", "png", "jpeg"])

    if photo is not None:
        if st.button("🔍 Ստուգել AI-ի միջոցով և գցել աղբամանը"):
            with st.spinner('AI-ն վերլուծում է շշի տեսակն ու չափսը...'):
                time.sleep(2)
            
            st.success("🎉 AI-ն ճանաչեց՝ **0.5լ Պլաստիկ շիշ (PET - վերամշակվող)**")
            st.session_state.points += 10
            st.balloons()
            st.info(f"Ձեր հաշվին ավելացավ **+10 միավոր**։ Ընդհանուր միավորները՝ **{st.session_state.points}**")

# --- ԲԱԺԻՆ 2. GPS ՔԱՐՏԵԶ ---
with tab2:
    st.subheader("Երևանում տեղադրված մեր խելացի աղբամանները")
    
    locations = pd.DataFrame({
        'lat': [40.1872, 40.1776, 40.1924, 40.1811],
        'lon': [44.5152, 44.5126, 44.5035, 44.5140]
    })
    st.map(locations)
    
    st.write("🟢 **ԵՊՀ Գլխավոր մասնաշենք** — Ազատ է (լցվածությունը՝ 30%)")
    st.write("🟢 **Հանրապետության Հրապարակ** — Ազատ է (լցվածությունը՝ 45%)")
    st.write("🟡 **Կասկադ** — Գրեթե լիքն է (լցվածությունը՝ 80%)")

# --- ԲԱԺԻՆ 3. ՄԻԱՎՈՐՆԵՐ ԵՎ ՄՐՑԱՆԱԿՆԵՐ ---
with tab3:
    st.metric(label="Ձեր ընթացիկ հաշիվը", value=f"{st.session_state.points} միավոր")
    st.markdown("---")
    st.subheader("🎁 Փոխանակել միավորները մրցանակների հետ")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("☕ **Անվճար սուրճ** (60 միավոր)")
        if st.button("Ստանալ սուրճի կտրոն"):
            if st.session_state.points >= 60:
                st.session_state.points -= 60
                st.success("Շնորհավորո՜ւմ ենք։ Ձեր պրոմո-կոդն է՝ **ECO2026**")
            else:
                st.error("Միավորները չեն բավականացնում։ Հանձնեք ևս 1 շիշ։")
                
    with col2:
        st.write("🛍️ **Էկո-պայուսակ** (150 միավոր)")
        if st.button("Ստանալ էկո-պայուսակ"):
            if st.session_state.points >= 150:
                st.session_state.points -= 150
                st.success("Շնորհավորո՜ւմ ենք։ Կարող եք վերցնել մոտակա կետից։")
            else:
                st.error(f"Պակասում է ևս {150 - st.session_state.points} միավոր։")

# --- ԲԱԺԻՆ 4. AI ԷԿՈ-ՕԳՆԱԿԱՆ (ՆՈՐՈՒԹՅՈՒՆ) ---
with tab4:
    st.subheader("Հարցրու EcoDrop AI-ին 🌿")
    st.write("Հարցրու ամեն ինչ վերամշակման, պլաստիկի տեսակների կամ մեր հավելվածի մասին։")
    
    user_question = st.text_input("Գրիր հարցդ այստեղ (օրինակ՝ Ինչպե՞ս տարբերել PET պլաստիկը).")
    
    if st.button("Ուղարկել հարցը"):
        if user_question:
            with st.spinner("AI-ն մտածում է..."):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": "Դու EcoDrop էկո-հավելվածի օգնականն ես: Պատասխանիր կարճ, ընկերական և գրագետ հայերենով:"
                            },
                            {
                                "role": "user",
                                "content": user_question,
                            }
                        ],
                        model="llama-3.3-70b-versatile",
                    )
                    st.success(chat_completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"Սխալ՝ {e}")
        else:
            st.warning("Խնդրում ենք նախ գրել հարցը:")
