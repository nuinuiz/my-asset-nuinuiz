import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="My Stock Portfolio", layout="wide", page_icon="📈")

# ส่วนหัวของแอป
st.title("📈 Dashboard ติดตามพอร์ตหุ้นส่วนตัว")
st.markdown("---")

# --- 2. ฟังก์ชันจำลองข้อมูล (ในอนาคตเราจะเปลี่ยนเป็นดึงจาก Google Sheets/Database) ---
@st.cache_data # ช่วยให้แอปโหลดเร็วขึ้น ไม่ต้องคำนวณใหม่ทุกครั้งที่กดปุ่ม
def load_data():
    # สมมติข้อมูลหุ้นในพอร์ตของคุณ
    data = {
        'TICKER': ['AOT', 'CPALL', 'PTT', 'ADVANC'],
        'ชื่อหุ้น': ['ท่าอากาศยานไทย', 'ซีพี ออลล์', 'ปตท.', 'แอดวานซ์ อินโฟร์'],
        'จำนวนหุ้น': [1000, 2000, 5000, 500],
        'ราคาซื้อเฉลี่ย': [65.00, 60.50, 32.25, 210.00],
        # ในแอปจริง ส่วนนี้ต้องดึงราคาปัจจุบันจาก API (เช่น yfinance)
        'ราคาปัจจุบัน': [72.25, 68.75, 34.00, 245.00] 
    }
    df = pd.DataFrame(data)
    
    # คำนวณค่าต่างๆ เพิ่มเติม
    df['มูลค่าทุน'] = df['จำนวนหุ้น'] * df['ราคาซื้อเฉลี่ย']
    df['มูลค่าปัจจุบัน'] = df['จำนวนหุ้น'] * df['ราคาปัจจุบัน']
    df['กำไร/ขาดทุน (บาท)'] = df['มูลค่าปัจจุบัน'] - df['มูลค่าทุน']
    df['% กำไร/ขาดทุน'] = (df['กำไร/ขาดทุน (บาท)'] / df['มูลค่าทุน']) * 100
    
    return df

# โหลดข้อมูลมาใช้งาน
df_portfolio = load_data()

# --- 3. ส่วนแสดงผลตัวเลขสำคัญ (Metrics Cards) ---
st.subheader("📊 สรุปภาพรวมพอร์ต")

# คำนวณยอดรวม
total_cost = df_portfolio['มูลค่าทุน'].sum()
total_value = df_portfolio['มูลค่าปัจจุบัน'].sum()
total_pnl = df_portfolio['กำไร/ขาดทุน (บาท)'].sum()
total_pnl_percent = (total_pnl / total_cost) * 100 if total_cost > 0 else 0

# สร้าง 3 คอลัมน์สำหรับ Card
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="💰 มูลค่าต้นทุนรวม",
        value=f"{total_cost:,.2f} บาท"
    )

with col2:
    st.metric(
        label="🚀 มูลค่าปัจจุบันรวม",
        value=f"{total_value:,.2f} บาท",
        delta=f"{total_pnl:,.2f} บาท ({total_pnl_percent:.2f}%)"
    )

with col3:
    # แสดงจำนวนหุ้นที่มีในพอร์ต
    st.metric(
        label="🏢 จำนวนบริษัทที่ถือ",
        value=f"{len(df_portfolio)} บริษัท"
    )

st.markdown("---")

# --- 4. ส่วนตารางข้อมูลและกราฟ ---
col_table, col_chart = st.columns([2, 1]) # แบ่งสัดส่วนตาราง 2 ส่วน กราฟ 1 ส่วน

with col_table:
    st.subheader("📄 รายละเอียดหุ้นรายตัว")
    
    # จัดรูปแบบการแสดงผลตัวเลขในตารางให้สวยงาม
    formatted_df = df_portfolio.style.format({
        'ราคาซื้อเฉลี่ย': '{:,.2f}',
        'ราคาปัจจุบัน': '{:,.2f}',
        'มูลค่าทุน': '{:,.2f}',
        'มูลค่าปัจจุบัน': '{:,.2f}',
        'กำไร/ขาดทุน (บาท)': '{:,.2f}',
        '% กำไร/ขาดทุน': '{:.2f}%'
    })
    
    # แสดงตารางแบบ Interactive (เรียงลำดับได้)
    st.dataframe(formatted_df, use_container_width=True)

with col_chart:
    st.subheader("🎡 สัดส่วนพอร์ต (Donut Chart)")
    
    # สร้างกราฟวงกลมแสดงสัดส่วนมูลค่าปัจจุบันของหุ้นแต่ละตัว
    fig = px.pie(
        df_portfolio, 
        values='มูลค่าปัจจุบัน', 
        names='TICKER', 
        hole=0.5, # ทำให้เป็นวงแหวน (Donut)
        color_discrete_sequence=px.colors.qualitative.Plotly # ใช้ชุดสีที่สวยงาม
    )
    
    # ปรับแต่งกราฟเล็กน้อย
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- 5. ส่วน Sidebar สำหรับจัดการข้อมูล (ตัวอย่าง) ---
with st.sidebar:
    st.header("⚙️ จัดการพอร์ต")
    st.write("ฟังก์ชันเสริมในอนาคต:")
    st.button("➕ เพิ่มหุ้นใหม่")
    st.button("➖ ขายหุ้น")
    st.button("🔄 อัปเดตราคาล่าสุด (API)")
    
    st.markdown("---")
    st.info("💡 ใบอนุญาต: ใช้เพื่อการศึกษาและการจัดการการเงินส่วนตัวเท่านั้น")
