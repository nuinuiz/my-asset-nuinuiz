import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(page_title="My Asset Dashboard", layout="wide", page_icon="📊")

# --- 1. เชื่อมต่อข้อมูล ---
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
                    price = stock.fast_info['last_price']
                    current_prices.append(price)
                except:
                    current_prices.append(row['ราคาปัจจุบัน'])
            else:
                current_prices.append(row['ราคาปัจจุบัน'])
        
        df['ราคาปัจจุบัน'] = current_prices
        df['มูลค่าต้นทุน'] = df['จำนวน'] * df['ราคาซื้อ']
        df['มูลค่าปัจจุบัน'] = df['จำนวน'] * df['ราคาปัจจุบัน']
        df['กำไร/ขาดทุน'] = df['มูลค่าปัจจุบัน'] - df['มูลค่าต้นทุน']
        df['ปันผลรวม'] = df['จำนวน'] * df['ปันผลต่อหุ้น']
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = get_data()

# --- 2. แสดงผล ---
if not df.empty:
    st.title("📊 สรุปพอร์ตสินทรัพย์ (Real-time)")
    
    # สรุปยอดด้านบน
    c1, c2, c3 = st.columns(3)
    c1.metric("มูลค่าปัจจุบันรวม", f"{df['มูลค่าปัจจุบัน'].sum():,.2f} บาท")
    c2.metric("กำไร/ขาดทุนรวม", f"{df['กำไร/ขาดทุน'].sum():,.2f} บาท")
    c3.metric("ปันผลที่จะได้รับ/ปี", f"{df['ปันผลรวม'].sum():,.2f} บาท")
    
    st.divider()

    # --- ส่วนกราฟแท่งที่แก้ไขแล้ว ---
    st.subheader("📈 มูลค่าสินทรัพย์รายตัว")
    # แก้จาก TICKER เป็น 'ชื่อ' เพื่อให้ตรงกับ Google Sheets
    fig_bar = px.bar(
        df, 
        x='ชื่อ', 
        y='มูลค่าปัจจุบัน', 
        color='ประเภท', # แยกสีตามประเภท (SET หรือ สหกรณ์)
        text_auto='.2s', # โชว์ตัวเลขบนแท่งกราฟแบบย่อ
        title='เปรียบเทียบมูลค่าปัจจุบันแต่ละบริษัท/สหกรณ์'
    )
    fig_bar.update_layout(xaxis_title="รายชื่อสินทรัพย์", yaxis_title="มูลค่า (บาท)")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # ตารางข้อมูล
    st.subheader("📋 รายละเอียดข้อมูลทั้งหมด")
    st.dataframe(df.style.format({
        'จำนวน': '{:,.0f}', 'ราคาซื้อ': '{:,.2f}', 'ราคาปัจจุบัน': '{:,.2f}',
        'มูลค่าต้นทุน': '{:,.2f}', 'มูลค่าปัจจุบัน': '{:,.2f}',
        'กำไร/ขาดทุน': '{:,.2f}', 'ปันผลรวม': '{:,.2f}'
    }), use_container_width=True)
else:
    st.info("กำลังรอข้อมูล...")
