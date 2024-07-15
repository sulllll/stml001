import streamlit as st
import os
from PIL import Image
from datetime import datetime
import math
import json

def load_likes():
    try:
        with open('likes.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_likes(likes):
    with open('likes.json', 'w') as f:
        json.dump(likes, f)

def get_image_files(directory):
    image_files = []
    likes = load_likes()
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            filepath = os.path.join(directory, filename)
            created_time = os.path.getmtime(filepath)  # 수정: getctime에서 getmtime으로 변경
            like_count = likes.get(filepath, 0)
            image_files.append((filepath, created_time, like_count))
    return sorted(image_files, key=lambda x: x[1], reverse=True)  # 수정: 기본적으로 최신순 정렬

def sort_images(images, sort_option):
    if sort_option == "최신순":
        return sorted(images, key=lambda x: x[1], reverse=True)
    elif sort_option == "추천순":
        return sorted(images, key=lambda x: x[2], reverse=True)
    return images

def main():
    st.set_page_config(layout="wide", page_title="감자붓의 미드저니 Gallery")
    
    st.title("감자붓의 미드저니 Gallery")

    # 정렬 옵션
    sort_option = st.selectbox("정렬", ["최신순", "추천순"])

    # 이미지 파일 경로
    image_directory = "static/gallery"
    
    image_files = get_image_files(image_directory)
    sorted_images = sort_images(image_files, sort_option)

    # 페이지네이션
    images_per_page = 20
    total_pages = math.ceil(len(sorted_images) / images_per_page)
    
    # 페이지 번호 (1부터 시작)
    page_number = int(st.query_params.get("page", 1))
    
    start_idx = (page_number - 1) * images_per_page
    end_idx = start_idx + images_per_page
    
    likes = load_likes()
    
    for filepath, created_time, like_count in sorted_images[start_idx:end_idx]:
        img = Image.open(filepath)
        caption = f"{os.path.basename(filepath)} (작성일: {datetime.fromtimestamp(created_time).strftime('%Y-%m-%d %H:%M:%S')})"
        st.image(img, use_column_width=True, caption=caption)
        
        if st.button(f"좋아요 ({like_count})", key=f"like_{filepath}"):
            likes[filepath] = likes.get(filepath, 0) + 1
            save_likes(likes)
            st.experimental_rerun()
        
        st.write("---")  # 구분선 추가

    # 페이지네이션 UI
    pages = list(range(max(1, page_number - 4), min(total_pages, page_number + 5) + 1))
    
    pagination = st.container()
    with pagination:
        cols = st.columns(len(pages) + 4)
        
        if page_number > 1:
            if cols[0].button("이전"):
                st.query_params["page"] = page_number - 1
                st.experimental_rerun()
        
        for i, page in enumerate(pages, 1):
            if cols[i].button(str(page), key=f"page_{page}"):
                st.query_params["page"] = page
                st.experimental_rerun()
        
        if page_number < total_pages:
            if cols[-1].button("다음"):
                st.query_params["page"] = page_number + 1
                st.experimental_rerun()

if __name__ == "__main__":
    main()