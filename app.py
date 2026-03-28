import streamlit as st

st.title("💰 โปรแกรมติดตามสินทรัพย์")
st.write("ยินดีด้วย! คุณรันแอปสำเร็จแล้ว")

# ลองใส่ตัวอย่างง่ายๆ
money = st.number_input("ใส่จำนวนเงินต้น", value=1000)
interest = st.number_input("ดอกเบี้ย (%)", value=1.5)
total = money + (money * interest / 100)

st.success(f"รวมยอดทั้งหมด: {total:,.2f} บาท")
