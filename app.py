import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(page_title="Real-time Asset Tracker", layout="wide")

# --- 1. เชื่อมต่อข้อมูลจาก Google Sheets ---
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ9PsXhJc-U5S2_KkWxareZt2uQpHAkcvRSecBnE0GgJ5bBZ0BQ8AdG5uXdIXi8Y3zkp7u_OyhFE4j_/pub?gid=138264559&single=true&output=csv"

@st.cache_data(ttl=300) # อัปเดตทุก 5 นาทีเพื่อไม่ให้โดนแบนการดึงข้อมูล
def get_live_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        
        # สร้าง List สำหรับเก็บราคาล่าสุด
        current_prices = []
        
        for index, row in df.iterrows():
            if row['ประเภท'] == 'หุ้นตลาดหลักทรัพย์':
                # ดึงราคาจาก Yahoo Finance (ต้องเติม .BK)
                ticker_symbol = f"{row['ชื่อ']}.BK"
                stock = yf.Ticker(ticker_symbol)
                # ดึงราคาสุดท้าย (Fast info)
                price = stock.fast_info['last_price']
                current_prices.append(price)
            else:
                # ถ้าเป็นหุ้นสหกรณ์ ให้ใช้ราคาปัจจุบันจาก Sheets (ซึ่งปกติคือ 10)
                current_prices.append(row['ราคาปัจจุบัน'])
        
        df['ราคาปัจจุบัน'] = current_prices
        
        # คำนวณยอดต่างๆ
        df['มูลค่าต้นทุน'] = df['จำนวน'] * df['ราคาซื้อ']
        df['มูลค่าปัจจุบัน'] = df['จำนวน'] * df['ราคาปัจจุบัน']
        df['กำไร/ขาดทุน'] = df['มูลค่าปัจจุบัน'] - df['มูลค่าต้นทุน']
        df['ปันผลรวม'] = df['จำนวน'] * df['ปันผลต่อหุ้น']
        return df
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
        return pd.DataFrame()

st.title("📈 พอร์ตสินทรัพย์ Real-time")
df = get_live_data()

if not df.empty:
    # --- ส่วนแสดงผล Metrics ---
    c1, c2, c3, c4 = st.columns(4)
    total_val = df['มูลค่าปัจจุบัน'].sum()
    total_profit = df['กำไร/ขาดทุน'].sum()
    
    c1.metric("มูลค่าพอร์ตสุทธิ", f"{total_val:,.2f} บาท")
    c2.metric("กำไร/ขาดทุนรวม", f"{total_profit:,.2f} บาท", delta=f"{(total_profit/df['มูลค่าต้นทุน'].sum())*100:.2f}%")
    c3.metric("ปันผลคาดการณ์/ปี", f"{df['ปันผลรวม'].sum():,.2f} บาท")
    c4.button("🔄 กดเพื่ออัปเดตราคา") # กด Refresh หน้าเว็บเพื่อดึงราคาใหม่

    st.divider()

    # ตารางข้อมูล
    st.subheader("📋 รายละเอียดสินทรัพย์ (ราคาหุ้น SET อัปเดตอัตโนมัติ)")
    st.dataframe(df.style.format({
        'ราคาซื้อ': '{:,.2f}',
        'ราคาปัจจุบัน': '{:,.2f}',
        'มูลค่าต้นทุน': '{:,.2f}',
        'มูลค่าปัจจุบัน': '{:,.2f}',
        'กำไร/ขาดทุน': '{:,.2f}',
        'ปันผลรวม': '{:,.2f}'
    }), use_container_width=True)

    # กราฟสัดส่วน
    fig = px.pie(df, values='มูลค่าปัจจุบัน', names='ชื่อ', title="สัดส่วนการถือครอง")
    st.plotly_chart(fig)
