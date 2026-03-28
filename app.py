import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="My Asset Bar Dashboard", layout="wide", page_icon="📊")

st.title("📊 สรุปพอร์ตสินทรัพย์แบบกราฟแท่ง")
st.markdown("---")

# --- 2. เชื่อมต่อข้อมูลจาก Google Sheets ---
# อย่าลืมเปลี่ยนลิงก์ CSV ตรงนี้เป็นลิงก์ของคุณนะครับ
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ9PsXhJc-U5S2_KkWxareZt2uQpHAkcvRSecBnE0GgJ5bBZ0BQ8AdG5uXdIXi8Y3zkp7u_OyhFE4j_/pub?gid=138264559&single=true&output=csv"

@st.cache_data(ttl=300) # อัปเดตข้อมูลทุก 5 นาที
def get_data():
    try:
        # ดึงข้อมูลและจัดการค่าว่าง (Fill NaN with 0)
        df = pd.read_csv(SHEET_CSV_URL).fillna(0)
        
        # จัดการชื่อประเภทให้ตรงกัน (SET vs หุ้นตลาดหลักทรัพย์)
        df['ประเภท'] = df['ประเภท'].replace('SET', 'หุ้นตลาดหลักทรัพย์')
        
        current_prices = []
        for index, row in df.iterrows():
            if row['ประเภท'] == 'หุ้นตลาดหลักทรัพย์':
                try:
                    # ดึงราคา Real-time (ต้องเติม .BK)
                    ticker = f"{str(row['ชื่อ']).strip()}.BK"
                    stock = yf.Ticker(ticker)
                    price = stock.fast_info['last_price']
                    current_prices.append(price)
                except:
                    # ถ้าดึงไม่ได้ใช้ราคาเดิมจาก Sheets
                    current_prices.append(row['ราคาปัจจุบัน'])
            else:
                # ถ้าเป็นหุ้นสหกรณ์ ให้ใช้ราคาปัจจุบันจาก Sheets
                current_prices.append(row['ราคาปัจจุบัน'])
        
        df['ราคาปัจจุบัน'] = current_prices
        
        # สูตรคำนวณยอดต่างๆ
        df['มูลค่าต้นทุน'] = df['จำนวน'] * df['ราคาซื้อ']
        df['มูลค่าปัจจุบัน'] = df['จำนวน'] * df['ราคาปัจจุบัน']
        df['กำไร/ขาดทุน'] = df['มูลค่าปัจจุบัน'] - df['มูลค่าต้นทุน']
        df['ปันผลรวม'] = df['จำนวน'] * df['ปันผลต่อหุ้น']
        df['% กำไร/ขาดทุน'] = (df['กำไร/ขาดทุน'] / df['มูลค่าต้นทุน']) * 100
        
        return df
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        return pd.DataFrame()

df = get_data()

# --- 3. แสดงผล Dashboard ---
if not df.empty:
    # 3.1 Metrics สรุปยอดด้านบน
    c1, c2, c3, c4 = st.columns(4)
    total_cost = df['มูลค่าต้นทุน'].sum()
    total_val = df['มูลค่าปัจจุบัน'].sum()
    total_profit = df['กำไร/ขาดทุน'].sum()
    total_div = df['ปันผลรวม'].sum()
    
    c1.metric("มูลค่าทุนรวม", f"{total_cost:,.2f} บาท")
    c2.metric("มูลค่าปัจจุบันรวม", f"{total_val:,.2f} บาท", delta=f"{total_profit:,.2f} บาท ({(total_profit/total_cost)*100:.2f}%)")
    c3.metric("ปันผลที่จะได้รับ/ปี", f"{total_div:,.2f} บาท")
    
    # คำนวณจำนวนบริษัทที่ถือ
    c4.metric("จำนวนบริษัทที่ถือ", f"{len(df)} บริษัท")
    
    st.divider()
    
    # 3.2 กราฟแท่งสวยๆ แทนกราฟวงกลม
    st.subheader("🎡 สัดส่วนพอร์ต (Donut Chart)")
    
    # สร้างกราฟวงกลมแสดงสัดส่วนมูลค่าปัจจุบันของหุ้นแต่ละตัว
    fig_bar = px.bar(
        df, 
        x='TICKER', 
        y='มูลค่าปัจจุบัน', 
        color='TICKER', # ใช้สีแยกตามบริษัท
        title='มูลค่าปัจจุบันของหุ้นแต่ละตัวในพอร์ต',
        # ปรับแต่งให้สวยงาม
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Plotly # ใช้ชุดสีที่สวยงาม
    )
    
    # ปรับแต่งกราฟเล็กน้อย
    fig_bar.update_layout(xaxis_title="บริษัท", yaxis_title="มูลค่าปัจจุบัน (บาท)", showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
    
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    
    # 3.3 ตารางรายละเอียดสินทรัพย์
    st.subheader("📋 รายละเอียดสินทรัพย์แยกรายตัว")
    
    # จัดรูปแบบการแสดงผลตัวเลขในตารางให้สวยงาม
    formatted_df = df.style.format({
        'จำนวน': '{:,.0f}',
        'ราคาซื้อ': '{:,.2f}',
        'ราคาปัจจุบัน': '{:,.2f}',
        'มูลค่าต้นทุน': '{:,.2f}',
        'มูลค่าปัจจุบัน': '{:,.2f}',
        'กำไร/ขาดทุน': '{:,.2f}',
        '% กำไร/ขาดทุน': '{:.2f}%',
        'ปันผลรวม': '{:,.2f}'
    })
    
    # แสดงตารางแบบ Interactive (เรียงลำดับได้)
    st.dataframe(formatted_df, use_container_width=True)

else:
    st.warning("กำลังโหลดข้อมูลจาก Google Sheets... หรือตรวจสอบว่าได้ใส่ลิงก์ CSV ที่ถูกต้องและมีข้อมูลแล้ว")
