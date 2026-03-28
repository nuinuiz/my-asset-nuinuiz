import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="My Wealth Tracker", layout="wide", page_icon="💰")

# ส่วนหัวของแอป
st.title("📂 ระบบบันทึกสินทรัพย์และปันผลส่วนตัว")
st.markdown("---")

# --- 2. ฟังก์ชันโหลดข้อมูล (จำลองรายการสินทรัพย์ของคุณ) ---
@st.cache_data
def load_assets():
    # ข้อมูลตัวอย่าง: คุณสามารถแก้ไขตัวเลขตรงนี้เป็นของคุณได้เลย
    data = [
        {"ประเภท": "หุ้นตลาดหลักทรัพย์", "ชื่อ": "CPALL", "จำนวน": 1000, "ราคาซื้อ": 60.00, "ราคาปัจจุบัน": 65.00, "ปันผลต่อหุ้น": 1.00},
        {"ประเภท": "หุ้นตลาดหลักทรัพย์", "ชื่อ": "PTT", "จำนวน": 2000, "ราคาซื้อ": 32.00, "ราคาปัจจุบัน": 34.50, "ปันผลต่อหุ้น": 1.20},
        {"ประเภท": "หุ้นสหกรณ์", "ชื่อ": "สหกรณ์ออมทรัพย์ ก.", "จำนวน": 5000, "ราคาซื้อ": 10.00, "ราคาปัจจุบัน": 10.00, "ปันผลต่อหุ้น": 0.50}, # หุ้นสหกรณ์ปกติราคาคงที่ 10 บาท
        {"ประเภท": "หุ้นสหกรณ์", "ชื่อ": "สหกรณ์ออมทรัพย์ ข.", "จำนวน": 10000, "ราคาซื้อ": 10.00, "ราคาปัจจุบัน": 10.00, "ปันผลต่อหุ้น": 0.45},
    ]
    df = pd.DataFrame(data)
    
    # คำนวณมูลค่า
    df['มูลค่าต้นทุน'] = df['จำนวน'] * df['ราคาซื้อ']
    df['มูลค่าปัจจุบัน'] = df['จำนวน'] * df['ราคาปัจจุบัน']
    df['กำไร/ขาดทุน'] = df['มูลค่าปัจจุบัน'] - df['มูลค่าต้นทุน']
    df['ปันผลคาดการณ์'] = df['จำนวน'] * df['ปันผลต่อหุ้น']
    df['Yield (%)'] = (df['ปันผลต่อหุ้น'] / df['ราคาซื้อ']) * 100
    
    return df

df = load_assets()

# --- 3. ส่วนสรุปตัวเลขสำคัญ (Top Metrics) ---
total_cost = df['มูลค่าต้นทุน'].sum()
total_value = df['มูลค่าปัจจุบัน'].sum()
total_dividend = df['ปันผลคาดการณ์'].sum()
total_pnl = df['กำไร/ขาดทุน'].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 ต้นทุนรวม", f"{total_cost:,.2f} บาท")
with col2:
    st.metric("🚀 มูลค่าปัจจุบัน", f"{total_value:,.2f} บาท", delta=f"{total_pnl:,.2f}")
with col3:
    st.metric("💸 ปันผลรวมต่อปี", f"{total_dividend:,.2f} บาท")
with col4:
    avg_yield = (total_dividend / total_cost) * 100 if total_cost > 0 else 0
    st.metric("📈 Yield เฉลี่ยพอร์ต", f"{avg_yield:.2f}%")

st.markdown("---")

# --- 4. กราฟและตารางแยกตามประเภท ---
tab1, tab2 = st.tabs(["📊 สรุปแยกประเภท", "📋 รายละเอียดสินทรัพย์"])

with tab1:
    col_pie, col_bar = st.columns(2)
    
    with col_pie:
        st.subheader("สัดส่วนสินทรัพย์")
        fig_pie = px.pie(df, values='มูลค่าปัจจุบัน', names='ประเภท', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_bar:
        st.subheader("ปันผลคาดการณ์รายตัว")
        fig_bar = px.bar(df, x='ชื่อ', y='ปันผลคาดการณ์', color='ประเภท', text_auto='.2s')
        st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.subheader("ตารางข้อมูลสินทรัพย์ทั้งหมด")
    # แสดงตารางแบบจัดรูปแบบสวยงาม
    st.dataframe(df.style.format({
        "ราคาซื้อ": "{:,.2f}",
        "ราคาปัจจุบัน": "{:,.2f}",
        "มูลค่าต้นทุน": "{:,.2f}",
        "มูลค่าปัจจุบัน": "{:,.2f}",
        "กำไร/ขาดทุน": "{:,.2f}",
        "ปันผลต่อหุ้น": "{:,.2f}",
        "ปันผลคาดการณ์": "{:,.2f}",
        "Yield (%)": "{:.2f}%"
    }), use_container_width=True)

# --- 5. Sidebar สำหรับเพิ่มข้อมูล (จำลอง) ---
with st.sidebar:
    st.header("➕ เพิ่มข้อมูลใหม่")
    new_type = st.selectbox("ประเภทสินทรัพย์", ["หุ้นตลาดหลักทรัพย์", "หุ้นสหกรณ์"])
    new_name = st.text_input("ชื่อหุ้น/สหกรณ์")
    new_qty = st.number_input("จำนวนหุ้น", min_value=0)
    new_price = st.number_input("ราคาซื้อเฉลี่ย", min_value=0.0)
    new_div = st.number_input("ปันผลต่อหุ้นที่คาดว่าจะได้รับ", min_value=0.0)
    
    if st.button("บันทึกข้อมูล (จำลอง)"):
        st.success(f"บันทึก {new_name} เรียบร้อยแล้ว! (ในเวอร์ชันถัดไปข้อมูลนี้จะถูกเก็บลงฐานข้อมูลจริง)")

    st.markdown("---")
    st.info("หมายเหตุ: ราคาหุ้นตลาดหลักทรัพย์ในระบบนี้ยังเป็นราคาที่คุณระบุเอง (Manual Update)")
