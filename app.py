import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(page_title="My Asset & Dividend Dashboard", layout="wide", page_icon="💰")

# --- 1. การกำหนดสีมาตรฐาน (เพื่อให้สัมพันธ์กันทั้งแอป) ---
COLOR_MAP = {
    'หุ้นตลาดหลักทรัพย์': '#1f77b4',  # สีน้ำเงิน
    'สหกรณ์': '#2ca02c',            # สีเขียว
    'อื่นๆ': '#9467bd'                # สีม่วง
}

# --- 2. ฟังก์ชันดึงและเตรียมข้อมูล ---
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ9PsXhJc-U5S2_KkWxareZt2uQpHAkcvRSecBnE0GgJ5bBZ0BQ8AdG5uXdIXi8Y3zkp7u_OyhFE4j_/pub?gid=138264559&single=true&output=csv"

@st.cache_data(ttl=300)
def get_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL).fillna('-')
        
        # ปรับชื่อประเภทให้เป็นมาตรฐาน
        df['ประเภท'] = df['ประเภท'].replace('SET', 'หุ้นตลาดหลักทรัพย์')
        
        current_prices = []
        auto_div_dates = []
        
        for index, row in df.iterrows():
            if row['ประเภท'] == 'หุ้นตลาดหลักทรัพย์':
                try:
                    ticker = f"{str(row['ชื่อ']).strip()}.BK"
                    stock = yf.Ticker(ticker)
                    # ดึงราคาล่าสุด
                    current_prices.append(stock.fast_info['last_price'])
                    
                    # ลองดึงวันจ่ายปันผลจากระบบ (ถ้าใน sheet ไม่ได้ระบุไว้)
                    if row.get('วันจ่ายปันผล', '-') == '-':
                        cal = stock.calendar
                        if 'Dividend Date' in cal:
                            auto_div_dates.append(cal['Dividend Date'].strftime('%d/%m/%Y'))
                        else:
                            auto_div_dates.append('รอประกาศ')
                    else:
                        auto_div_dates.append(row['วันจ่ายปันผล'])
                except:
                    current_prices.append(float(row['ราคาปัจจุบัน']) if row['ราคาปัจจุบัน'] != '-' else 0)
                    auto_div_dates.append(row.get('วันจ่ายปันผล', 'ไม่พบข้อมูล'))
            else:
                current_prices.append(float(row['ราคาปัจจุบัน']) if row['ราคาปัจจุบัน'] != '-' else 0)
                auto_div_dates.append(row.get('วันจ่ายปันผล', '-'))
        
        df['ราคาปัจจุบัน'] = current_prices
        df['วันจ่ายปันผล'] = auto_div_dates
        
        # แปลงค่าตัวเลขเพื่อคำนวณ
        df['จำนวน'] = pd.to_numeric(df['จำนวน'], errors='coerce').fillna(0)
        df['ราคาซื้อ'] = pd.to_numeric(df['ราคาซื้อ'], errors='coerce').fillna(0)
        df['ปันผลต่อหุ้น'] = pd.to_numeric(df['ปันผลต่อหุ้น'], errors='coerce').fillna(0)
        
        df['มูลค่าต้นทุน'] = df['จำนวน'] * df['ราคาซื้อ']
        df['มูลค่าปัจจุบัน'] = df['จำนวน'] * df['ราคาปัจจุบัน']
        df['ปันผลรวม'] = df['จำนวน'] * df['ปันผลต่อหุ้น']
        df['กำไร/ขาดทุน'] = df['มูลค่าปัจจุบัน'] - df['มูลค่าต้นทุน']
        
        return df
    except Exception as e:
        st.error(f"การดึงข้อมูลผิดพลาด: {e}")
        return pd.DataFrame()

df = get_data()

# --- 3. ส่วนการแสดงผล (UI) ---
if not df.empty:
    st.title("💰 ระบบติดตามพอร์ตและปันผลอัจฉริยะ")

    # --- 3.1 Metrics สรุปยอด (สีสัมพันธ์กับประเภท) ---
    t_val = df['มูลค่าปัจจุบัน'].sum()
    t_div_year = df['ปันผลรวม'].sum()
    t_div_month = t_div_year / 12
    
    # คำนวณแยกประเภทเพื่อโชว์ใน Delta
    set_div = df[df['ประเภท'] == 'หุ้นตลาดหลักทรัพย์']['ปันผลรวม'].sum()
    coop_div = df[df['ประเภท'] == 'สหกรณ์']['ปันผลรวม'].sum()

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("มูลค่าพอร์ตสุทธิ", f"฿{t_val:,.2f}", delta="ราคาตลาดปัจจุบัน")
    with m2:
        st.metric("ปันผลรับรวม (รายปี)", f"฿{t_div_year:,.2f}", 
                  delta=f"หุ้น: {set_div:,.0f} | สหกรณ์: {coop_div:,.0f}")
    with m3:
        st.metric("รายได้เฉลี่ย (รายเดือน)", f"฿{t_div_month:,.2f}", delta="Passive Income")

    st.divider()

    # --- 3.2 กราฟแท่ง (ใช้สีตามที่กำหนดไว้ใน COLOR_MAP) ---
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📈 สัดส่วนมูลค่าสินทรัพย์")
        fig_val = px.bar(df, x='ชื่อ', y='มูลค่าปัจจุบัน', color='ประเภท',
                         color_discrete_map=COLOR_MAP, text_auto='.2s')
        st.plotly_chart(fig_val, use_container_width=True)
        
    with col_chart2:
        st.subheader("💸 ปันผลรายปีแยกตามตัว")
        fig_div = px.bar(df, x='ชื่อ', y='ปันผลรวม', color='ประเภท',
                         color_discrete_map=COLOR_MAP, text_auto='.2s')
        st.plotly_chart(fig_div, use_container_width=True)

    st.divider()

    # --- 3.3 ตารางรายละเอียดแบบ Fit หน้าจอ ---
    st.subheader("📋 รายละเอียดพอร์ตและวันจ่ายปันผล")
    
    # เลือกคอลัมน์ที่ต้องการแสดง
    display_df = df[['ประเภท', 'ชื่อ', 'จำนวน', 'ราคาปัจจุบัน', 'มูลค่าปัจจุบัน', 'ปันผลรวม', 'วันจ่ายปันผล']]
    
    st.dataframe(
        display_df.style.format({
            'จำนวน': '{:,.0f}',
            'ราคาปัจจุบัน': '{:,.2f}',
            'มูลค่าปัจจุบัน': '{:,.2f}',
            'ปันผลรวม': '{:,.2f}'
        }),
        use_container_width=True, # ทำให้ตาราง Fit เต็มหน้าจอ
        height=400
    )
    
else:
    st.warning("ไม่สามารถโหลดข้อมูลได้ กรุณาตรวจสอบลิงก์ CSV หรือโครงสร้างไฟล์")
