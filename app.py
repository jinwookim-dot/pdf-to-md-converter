import streamlit as st
import pdfplumber
import re
import logging
import io

# 1. 시스템 로그 정리
logging.getLogger("pdfminer").setLevel(logging.ERROR)

st.set_page_config(page_title="AI 제안서 텍스트 변환기", page_icon="📝", layout="wide")

st.title("📑 AI 제안서 텍스트 자동 변환기")
st.markdown("분석이 완료된 파일은 다시 로딩 없이 즉시 다운로드됩니다.")

# --- 재분석 방지를 위한 캐싱 로직 ---
@st.cache_data(show_spinner=False)
def convert_pdf_to_md(file_bytes, file_name):
    """PDF 데이터를 MD로 변환하고 결과를 메모리에 저장"""
    # 바이너리 데이터를 읽기 가능한 형태로 변환
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        full_md = []
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text(x_tolerance=2)
            if page_text:
                # 불필요한 공백 제거
                clean = re.sub(r'[ ]+', ' ', page_text).strip()
                full_md.append(f"## Page {i+1}\n\n{clean}\n")
        return "\n".join(full_md)

# 2. 파일 업로드
uploaded_files = st.file_uploader("PDF 파일들을 선택하세요", type="pdf", accept_multiple_files=True)

if uploaded_files:
    st.subheader("✅ 변환 리스트")
    
    for uploaded_file in uploaded_files:
        col1, col2, col3 = st.columns([5, 2, 2])
        
        with col1:
            st.write(f"📄 **{uploaded_file.name}**")
            
        with col2:
            status_placeholder = st.empty()
            status_placeholder.text("⏳ 준비 중...")
            
        # 파일 데이터를 읽어와서 캐싱 함수에 전달
        file_data = uploaded_file.getvalue()
        md_result = convert_pdf_to_md(file_data, uploaded_file.name)
        
        status_placeholder.text("✨ 변환 완료!")
        
        with col3:
            new_filename = uploaded_file.name.replace(".pdf", ".md")
            st.download_button(
                label="📥 MD 다운로드",
                data=md_result,
                file_name=new_filename,
                mime="text/markdown",
                key=f"btn_{uploaded_file.name}"
            )
    
    # 이 부분의 들여쓰기를 정확히 맞췄습니다.
    st.divider()
