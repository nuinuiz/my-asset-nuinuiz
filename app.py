import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(page_title="My Asset & Dividend Dashboard", layout="wide", page_icon="💰")

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

# --- 2. การแสดงผล ---
if not df.empty:
    st.title("💰 ระบบติดตามสินทรัพย์และเงินปันผล")
    
    # Metrics สรุปยอดด้านบน
    c1, c2, c3 = st.columns(3)
    total_val = df['มูลค่าปัจจุบัน'].sum()
    total_pnl = df['กำไร/ขาดทุน'].sum()
    total_div = df['ปันผลรวม'].sum()
    
    c1.metric("มูลค่าพอร์ตสุทธิ", f"{total_val:,.2f} บาท")
    c2.metric("กำไร/ขาดทุนรวม", f"{total_pnl:,.2f} บาท", delta=f"{(total_pnl/df['มูลค่าต้นทุน'].sum()*100):.2f}%")
    c3.metric("เงินปันผลรับรวม/ปี", f"{total_div:,.2f} บาท")
    
    st.divider()

    # --- 3. ส่วนของกราฟ (แบ่งเป็น 2 คอลัมน์) ---
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📈 มูลค่าสินทรัพย์รายตัว")
        fig_val = px.bar(df, x='ชื่อ', y='มูลค่าปัจจุบัน', color='ประเภท', 
                         text_auto='.2s', title="เปรียบเทียบขนาดสินทรัพย์")
        st.plotly_chart(fig_val, use_container_width=True)
        
    with col_chart2:
        st.subheader("💸 เงินปันผลคาดการณ์รายตัว")
        # กราฟแสดงปันผลที่คุณต้องการ
        fig_div = px.bar(df, x='ชื่อ', y='ปันผลรวม', 
                         color_discrete_sequence=['#00CC96'], # สีเขียวเหนี่ยวทรัพย์
                         text_auto='.2s', title="ปันผลที่จะได้รับ (บาท/ปี)")
        fig_div.update_layout(xaxis_title="ชื่อหุ้น/สหกรณ์", yaxis_title="ปันผล (บาท)")
        st.plotly_chart(fig_div, use_container_width=True)

    st.divider()

    # --- 4. ตารางข้อมูลแบบ Fit หน้าจอ ---
    st.subheader("📋 รายละเอียดข้อมูลแบบตาราง")
    
    # ปรับแต่งตารางให้สวยและอ่านง่าย
    display_df = df[['ประเภท', 'ชื่อ', 'จำนวน', 'ราคาซื้อ', 'ราคาปัจจุบัน', 'กำไร/ขาดทุน', 'ปันผลรวม']]
    
    st.dataframe(
        display_df.style.format({
            'จำนวน': '{:,.0f}',
            'ราคาซื้อ': '{:,.2f}',
            'ราคาปัจจุบัน': '{:,.2f}',
            'กำไร/ขาดทุน': '{:,.2f}',
            'ปันผลรวม': '{:,.2f}'
        }),
        use_container_width=True, # ทำให้ตารางขยายเต็มหน้าจอ
        height=400 # กำหนดความสูงให้พอดี
    )

else:
    st.info("ระบบกำลังเตรียมข้อมูล...")
