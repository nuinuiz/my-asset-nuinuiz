import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(page_title="Professional Asset Dashboard", layout="wide")

# --- 1. Custom CSS เพื่อทำให้ Metrics ดูเหมือนรูปที่คุณส่งมา ---
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 32px; color: #1f77b4; }
    .main-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #1f77b4;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. การโหลดข้อมูล (ใช้ลิงก์เดิมของคุณ) ---
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ9PsXhJc-U5S2_KkWxareZt2uQpHAkcvRSecBnE0GgJ5bBZ0BQ8AdG5uXdIXi8Y3zkp7u_OyhFE4j_/pub?gid=138264559&single=true&output=csv"

@st.cache_data(ttl=60)
def get_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL).fillna(0)
        df['ประเภท'] = df['ประเภท'].replace('SET', 'หุ้นตลาดหลักทรัพย์')
        current_prices = []
        for index, row in df.iterrows():
            if row['ประเภท'] == 'หุ้นตลาดหลักทรัพย์':
                try:
                    ticker = f"{str(row['ชื่อ']).strip()}.BK"
                    stock = yf.Ticker(ticker)
                    current_prices.append(stock.fast_info['last_price'])
                except: current_prices.append(row['ราคาปัจจุบัน'])
            else: current_prices.append(row['ราคาปัจจุบัน'])
        
        df['ราคาปัจจุบัน'] = current_prices
        df['มูลค่าต้นทุน'] = df['จำนวน'] * df['ราคาซื้อ']
        df['มูลค่าปัจจุบัน'] = df['จำนวน'] * df['ราคาปัจจุบัน']
        df['กำไร/ขาดทุน'] = df['มูลค่าปัจจุบัน'] - df['มูลค่าต้นทุน']
        df['ปันผลรวม'] = df['จำนวน'] * df['ปันผลต่อหุ้น']
        return df
    except: return pd.DataFrame()

df = get_data()

if not df.empty:
    st.title("📈 Asset & Dividend Dashboard")

    # --- 3. ส่วน Metrics แบบสวยงาม (ตามรูปที่อยากได้) ---
    t_val = df['มูลค่าปัจจุบัน'].sum()
    t_pnl = df['กำไร/ขาดทุน'].sum()
    t_div = df['ปันผลรวม'].sum()
    t_yield = (t_div / df['มูลค่าต้นทุน'].sum()) * 100

    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("Portfolio Value", f"฿{t_val:,.0f}", delta=f"{t_pnl:,.0f} BHT")
    with m2:
        # แสดงกำไรเป็น %
        st.metric("Total Profit", f"฿{t_pnl:,.0f}", delta=f"{(t_pnl/df['มูลค่าต้นทุน'].sum()*100):.2f}%")
    with m3:
        st.metric("Annual Dividend", f"฿{t_div:,.0f}", delta="Expected Yearly")
    with m4:
        st.metric("Monthly Passive Income", f"฿{(t_div/12):,.0f}", delta=f"Yield {t_yield:.2f}%")

    st.divider()

    # --- 4. ส่วนกราฟ (เน้นปันผลและสัดส่วน) ---
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📊 มูลค่าสินทรัพย์แยกตามตัว")
        fig1 = px.bar(df, x='ชื่อ', y='มูลค่าปัจจุบัน', color='ประเภท', text_auto='.2s')
        st.plotly_chart(fig1, use_container_width=True)
    
    with c2:
        st.subheader("💸 เงินปันผลที่จะได้รับ (บาท/ปี)")
        fig2 = px.bar(df, x='ชื่อ', y='ปันผลรวม', color_discrete_sequence=['#2ca02c'], text_auto='.2s')
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # --- 5. ตารางแบบ Fit หน้าจอ (Full Width) ---
    st.subheader("📋 รายละเอียดพอร์ตโฟลิโอ")
    
    # เลือกคอลัมน์และจัดลำดับใหม่
    display_df = df[['ประเภท', 'ชื่อ', 'จำนวน', 'ราคาซื้อ', 'ราคาปัจจุบัน', 'กำไร/ขาดทุน', 'ปันผลรวม']]
    
    st.dataframe(
        display_df.style.format({
            'จำนวน': '{:,.0f}', 'ราคาซื้อ': '{:,.2f}', 'ราคาปัจจุบัน': '{:,.2f}',
            'กำไร/ขาดทุน': '{:,.2f}', 'ปันผลรวม': '{:,.2f}'
        }).set_properties(**{'background-color': '#ffffff', 'color': '#333'}),
        use_container_width=True # ทำให้ตารางขยาย Fit หน้าจอ
    )

else:
    st.info("กำลังดึงข้อมูลล่าสุด...")
