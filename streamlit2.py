import streamlit as st
import pandas as pd
import pydeck as pdk
import json

# 데이터 로드
file_path = '교통사고+현황(구별)_20241114203251.csv'
data = pd.read_csv(file_path, encoding='EUC-KR')

# 열 이름 변경
data = data.rename(columns={"자치구별": "구", "발생건수 (건)": "발생건수", "사망자수 (명)": "사망자수"})

# GeoJSON 파일 경로
geojson_path = '서울특별시 지역구.geojson'
with open(geojson_path, encoding='utf-8') as f:
    geojson = json.load(f)
    
# 로그인 섹션
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("교통사고 현황 서비스")

    with st.form("login_form"):
        ID = st.text_input("아이디", placeholder="아이디를 입력하세요")
        PW = st.text_input("비밀번호", placeholder="비밀번호를 입력하세요", type="password")
        submit_button = st.form_submit_button("로그인")

    if submit_button:
        if ID == "황종수" and PW == "1234":  # 로그인 정보 하드코딩 예시
            st.session_state["authenticated"] = True
            st.success(f"{ID}님, 환영합니다!")
        else:
            st.warning("사용자 정보가 일치하지 않습니다.")
else:
    # 메인 페이지
    st.title("서울시 교통사고 현황")

    # 시각화 옵션 선택
    selected_option = st.selectbox("보기 옵션을 선택하세요", ["사망자수", "발생건수"])

    # 지도 시각화
    st.write(f"### 서울시 구별 {selected_option} 지도")

    # 구별 데이터를 동별로 할당
    map_data = data.set_index("구")[selected_option].to_dict()
    for feature in geojson["features"]:
        구이름 = feature["properties"]["adm_nm"].split()[1]  # 구 이름 추출
        value = map_data.get(구이름, 0)
        
        # 사망자수와 발생건수의 범위에 맞게 값 조정
        if selected_option == "사망자수":
            # 사망자수는 0~15 사이로 가정, 진하기를 극대화
            feature["properties"]["value"] = min(255, value * (255 / 15))  # 배율 적용
        else:
            # 발생건수는 0~4000 사이로 가정
            feature["properties"]["value"] = min(255, value * (255 / 4000))  # 배율 적용

    # 색상 설정
    if selected_option == "사망자수":
        # 사망자수에 따른 빨간색 계열 진하기
        fill_color = "[255, 180 - properties.value, 0, 200]"
    else:
        # 발생건수에 따른 파란색 계열 진하기
        fill_color = "[0, 100, properties.value, 200]"

    # GeoJsonLayer로 지도 표시
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=37.5665,
            longitude=126.9780,
            zoom=10,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "GeoJsonLayer",
                data=geojson,
                get_fill_color=fill_color,
                pickable=True,
                auto_highlight=True
            ),
        ],
    ))

    # 선택된 옵션에 따른 막대 그래프
    st.write(f"### 구별 {selected_option} 막대 그래프")
    st.bar_chart(data.set_index("구")[selected_option])
