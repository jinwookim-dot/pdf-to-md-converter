import streamlit as st
import pdfplumber
import pandas as pd
import re
import logging

# 1. 지저분한 로그 메시지 숨기기
logging.getLogger("pdfminer").setLevel(logging.ERROR)

st.set_page_config(page_title="AI 제안서 텍스트 변환기", page_icon="📝", layout="wide")

# 상단 UI 개선
st.title("📑 AI 제안서 텍스트 자동 변환기")
st.markdown("""
- **기능:** PDF 내의 텍스트를 중복 없이 마크다운(MD)으로 변환합니다.
- **특징:** 표 데이터를 별도로 추출하지 않아 텍스트 겹침 현상을 방지했습니다.
""")

uploaded_files = st.file_uploader("변환할 PDF 파일들을 선택하세요", type="pdf", accept_multiple_files=True)

def clean_text(text):
    """비정상적인 공백을 제거하고 문장을 정돈"""
    if not text: return ""
    # 여러 개의 공백을 하나로 합치고 앞뒤 공백 제거
    text = re.sub(r'[ ]+', ' ', text)
    return text.strip()

# 분석 결과가 업로드 즉시 상단에 보이도록 배치
if uploaded_files:
    st.subheader("✅ 변환 리스트")
    
    for uploaded_file in uploaded_files:
        col1, col2, col3 = st.columns([5, 2, 2])
        
        with col1:
            st.write(f"📄 **{uploaded_file.name}**")
            
        with col2:
            status_placeholder = st.empty()
            status_placeholder.text("⏳ 처리 중...")
            
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                full_md = []
                for i, page in enumerate(pdf.pages):
                    # 레이아웃을 최대한 유지하며 텍스트 추출 (표 포함 모든 텍스트)
                    page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
                    if page_text:
                        full_md.append(f"## Page {i+1}\n\n{clean_text(page_text)}\n")
                
                md_result = "\n".join(full_md)
            
            status_placeholder.text("✨ 변환 완료!")
            
            with col3:
                new_filename = uploaded_file.name.replace(".pdf", ".md")
                st.download_button(
                    label="📥 MD 다운로드",
                    data=md_result,
                    file_name=new_filename,
                    mime="text/markdown",
                    key=f"btn_{uploaded_file.name}" # 고유 키
                )
        except Exception as e:
            status_placeholder.text("❌ 오류 발생")
            st.error(f"에러 내용: {e}")

    st.divider()