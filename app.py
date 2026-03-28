import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="My Asset Dashboard", layout="wide")

# --- 1. เชื่อมต่อข้อมูล ---
# วางลิงก์ CSV ที่ก๊อปปี้มาจาก Google Sheets ในเครื่องหมายอัญประกาศข้างล่างนี้
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ9PsXhJc-U5S2_KkWxareZt2uQpHAkcvRSecBnE0GgJ5bBZ0BQ8AdG5uXdIXi8Y3zkp7u_OyhFE4j_/pub?gid=138264559&single=true&output=csv"

@st.cache_data(ttl=60) # อัปเดตข้อมูลทุก 1 นาที
def get_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        # คำนวณยอดต่างๆ
        df['มูลค่าต้นทุน'] = df['จำนวน'] * df['ราคาซื้อ']
        df['มูลค่าปัจจุบัน'] = df['จำนวน'] * df['ราคาปัจจุบัน']
        df['กำไร/ขาดทุน'] = df['มูลค่าปัจจุบัน'] - df['มูลค่าต้นทุน']
        df['ปันผลรวม'] = df['จำนวน'] * df['ปันผลต่อหุ้น']
        return df
    except Exception as e:
        st.error(f"เชื่อมต่อข้อมูลไม่ได้: {e}")
        return pd.DataFrame()

df = get_data()

# --- 2. แสดงผล Dashboard ---
if not df.empty:
    st.title("💰 พอร์ตสินทรัพย์รวม")
    
    # สรุปยอดด้านบน
    c1, c2, c3 = st.columns(3)
    c1.metric("มูลค่าปัจจุบันรวม", f"{df['มูลค่าปัจจุบัน'].sum():,.2f} บาท")
    c2.metric("กำไร/ขาดทุนรวม", f"{df['กำไร/ขาดทุน'].sum():,.2f} บาท")
    c3.metric("ปันผลที่จะได้รับ", f"{df['ปันผลรวม'].sum():,.2f} บาท")
    
    st.divider()
    
    # ตารางและกราฟ
    col_t, col_g = st.columns([2, 1])
    with col_t:
        st.subheader("รายละเอียดสินทรัพย์")
        st.dataframe(df, use_container_width=True)
        
    with col_g:
        st.subheader("สัดส่วนพอร์ต")
        fig = px.pie(df, values='มูลค่าปัจจุบัน', names='ชื่อ', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("กำลังรอข้อมูลจาก Google Sheets... ตรวจสอบว่าใส่ลิงก์ถูกต้องและมีข้อมูลใน Sheets หรือยัง")
