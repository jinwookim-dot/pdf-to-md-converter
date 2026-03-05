import streamlit as st
import pdfplumber
import re
import logging

# 1. 시스템 로그 정리
logging.getLogger("pdfminer").setLevel(logging.ERROR)

st.set_page_config(page_title="AI 제안서 텍스트 변환기", page_icon="📝", layout="wide")

st.title("📑 AI 제안서 텍스트 자동 변환기")
st.markdown("한 번 분석한 파일은 캐시에 저장되어 즉시 다운로드 가능합니다.")

# --- 핵심: 분석 로직을 함수로 분리하고 캐싱 적용 ---
@st.cache_data(show_spinner=False)
def convert_pdf_to_md(file_contents, file_name):
    """PDF 바이트 데이터를 입력받아 MD 텍스트로 변환 (결과를 캐시에 저장)"""
    with pdfplumber.open(file_contents) as pdf:
        full_md = []
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text(x_tolerance=2)
            if page_text:
                # 불필요한 공백 제거 로직 포함
                clean = re.sub(r'[ ]+', ' ', page_text).strip()
                full_md.append(f"## Page {i+1}\n\n{clean}\n")
        return "\n".join(full_md)

uploaded_files = st.file_uploader("변환할 PDF 파일들을 선택하세요", type="pdf", accept_multiple_files=True)

if uploaded_files:
    st.subheader("✅ 변환 리스트")
    
    for uploaded_file in uploaded_files:
        col1, col2, col3 = st.columns([5, 2, 2])
        
        with col1:
            st.write(f"📄 **{uploaded_file.name}**")
            
        with col2:
            status_placeholder = st.empty()
            
        # 2. 캐싱된 함수 호출 (이미 분석했다면 0.1초만에 결과 반환)
        # 파일을 직접 전달하면 에러가 날 수 있어 BytesIO나 Bytes로 전달
        file_bytes = uploaded_file.getvalue()
        md_result = convert_pdf_to_md(io.BytesIO(file_bytes), uploaded_file.name)
        
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
    st.divider()

import io # io 모듈 추가 확인

    st.divider()

