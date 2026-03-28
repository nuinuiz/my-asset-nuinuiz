import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(page_title="Unified Color Dashboard", layout="wide", page_icon="🎨")

# --- 1. การโหลดข้อมูลและคำนวณ ---
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ9PsXhJc-U5S2_KkWxareZt2uQpHAkcvRSecBnE0GgJ5bBZ0BQ8AdG5uXdIXi8Y3zkp7u_OyhFE4j_/pub?gid=138264559&single=true&output=csv"

@st.cache_data(ttl=600)
def get_unified_data():
    try:
        # ดึงข้อมูลและจัดการค่าว่าง
        df = pd.read_csv(SHEET_CSV_URL).fillna(0)
        
        # จัดการชื่อประเภทให้ตรงกัน
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
        
        # สูตรคำนวณยอดต่างๆ
        df['มูลค่าต้นทุน'] = df['จำนวน'] * df['ราคาซื้อ']
        df['มูลค่าปัจจุบัน'] = df['จำนวน'] * df['ราคาปัจจุบัน']
        df['ปันผลรวม'] = df['จำนวน'] * df['ปันผลต่อหุ้น']
        df['กำไร/ขาดทุน'] = df['มูลค่าปัจจุบัน'] - df['มูลค่าต้นทุน']
        df['% กำไร/ขาดทุน'] = (df['กำไร/ขาดทุน'] / df['มูลค่าต้นทุน']) * 100
        df['Yield (%)'] = (df['ปันผลรวม'] / df['มูลค่าต้นทุน']) * 100
        
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = get_unified_data()

# --- 2. การกำหนดสี (Unified Colors) ---
# เราจะใช้สีน้ำเงินสำหรับหุ้น SET และสีเขียวสำหรับสหกรณ์
color_map = {
    'หุ้นตลาดหลักทรัพย์': '#1f77b4', # สีน้ำเงิน
    'หุ้นสหกรณ์': '#2ca02c'           # สีเขียว
}

# --- 3. Custom CSS เพื่อทำให้ Metrics มีสีตามประเภท ---
# เราจะสร้าง Class พิเศษสำหรับสีแต่ละประเภท
st.markdown(f"""
<style>
    .set-metric data-testid="stMetricDelta" {{ color: {color_map['หุ้นตลาดหลักทรัพย์']}; }}
    .coop-metric data-testid="stMetricDelta" {{ color: {color_map['หุ้นสหกรณ์']}; }}
    
    [data-testid="stMetricValue"] {{ font-size: 32px; color: #333; }}
</style>
""", unsafe_allow_html=True)

# --- 4. แสดงผล Dashboard ---
if not df.empty:
    st.title("🎨 พอร์ตสินทรัพย์และปันผล (สีสัมพันธ์กัน)")
    
    # คำนวณยอดรวมแยกประเภท
    set_cost = df[df['ประเภท'] == 'หุ้นตลาดหลักทรัพย์']['มูลค่าต้นทุน'].sum()
    set_div = df[df['ประเภท'] == 'หุ้นตลาดหลักทรัพย์']['ปันผลรวม'].sum()
    set_yield = (set_div / set_cost) * 100 if set_cost > 0 else 0
    
    coop_cost = df[df['ประเภท'] == 'หุ้นสหกรณ์']['มูลค่าต้นทุน'].sum()
    coop_div = df[df['ประเภท'] == 'หุ้นสหกรณ์']['ปันผลรวม'].sum()
    coop_yield = (coop_div / coop_cost) * 100 if coop_cost > 0 else 0
    
    total_val = df['มูลค่าปัจจุบัน'].sum()
    total_div = df['ปันผลรวม'].sum()
    
    # --- 4.1 Metrics แบบกำหนดสี ---
    m1, m2, m3, m4 = st.columns(4)
    
    m1.metric("มูลค่าปัจจุบันรวม", f"฿{total_val:,.0f}")
    
    # Metrics สำหรับหุ้น SET (ใช้ Class 'set-metric' เพื่อกำหนดสีน้ำเงิน)
    with m2:
        st.markdown('<div class="set-metric">', unsafe_allow_html=True)
        st.metric("ปันผลรวมรายปี (SET)", f"฿{set_div:,.0f}", delta=f"Yield {set_yield:.2f}%")
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Metrics สำหรับหุ้นสหกรณ์ (ใช้ Class 'coop-metric' เพื่อกำหนดสีเขียว)
    with m3:
        st.markdown('<div class="coop-metric">', unsafe_allow_html=True)
        st.metric("ปันผลรวมรายปี (สหกรณ์)", f"฿{coop_div:,.0f}", delta=f"Yield {coop_yield:.2f}%")
        st.markdown('</div>', unsafe_allow_html=True)
        
    m4.metric("ปันผลเฉลี่ยรายเดือน", f"฿{(total_div/12):,.0f}", delta=f"Yield {((total_div/df['มูลค่าต้นทุน'].sum())*100):.2f}%")

    st.divider()

    # --- 4.2 กราฟแท่งแบบกำหนดสีตามประเภท ---
    st.subheader("📊 มูลค่าสินทรัพย์แยกตามตัว (สีสัมพันธ์กัน)")
    
    # ใช้สีแยกตามประเภท (SET หรือ สหกรณ์)
    fig_bar = px.bar(df, x='ชื่อ', y='มูลค่าปัจจุบัน', color='ประเภท', 
                     color_discrete_map=color_map, # กำหนดสีตามที่เรากำหนดไว้
                     text_auto='.2s', title="เปรียบเทียบขนาดสินทรัพย์")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- 4.3 ตารางข้อมูลแยกตามประเภท ---
    st.subheader("📋 รายละเอียดข้อมูลแบบตาราง (Fit หน้าจอ)")
    
    # เลือกคอลัมน์สำคัญมาโชว์
    display_df = df[['ประเภท', 'ชื่อ', 'จำนวน', 'ราคาซื้อ', 'ราคาปัจจุบัน', 'กำไร/ขาดทุน', 'ปันผลรวม']]
    
    # จัดรูปแบบตารางให้สวยงาม
    formatted_df = display_df.style.format({
        'จำนวน': '{:,.0f}', 'ราคาซื้อ': '{:,.2f}', 'ราคาปัจจุบัน': '{:,.2f}',
        'กำไร/ขาดทุน': '{:,.2f}', 'ปันผลรวม': '{:,.2f}'
    })
    
    st.dataframe(formatted_df, use_container_width=True)

else:
    st.info("กรุณาตรวจสอบการเชื่อมต่อ Google Sheets")
