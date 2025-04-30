import streamlit as st
import subprocess
import re
import urllib.parse

st.set_page_config(page_title="YouTube Direct Links", page_icon="🔗")
st.title("🔗 Trích xuất link tải trực tiếp YouTube")

urls = st.text_area("📺 Nhập danh sách URL video YouTube (mỗi dòng một URL):")

# Hàm làm sạch tiêu đề để thành tên file hợp lệ
def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title)

if st.button("Lấy link video"):
    url_list = [url.strip() for url in urls.split("\n") if url.strip()]
    
    if not url_list:
        st.warning("⚠️ Vui lòng nhập ít nhất một URL video.")
    else:
        with st.spinner("🔄 Đang xử lý..."):
            results = []
            for url in url_list:
                # Lấy tiêu đề video
                title_cmd = ["yt-dlp", "--get-title", url]
                title_result = subprocess.run(title_cmd, capture_output=True, text=True)

                if title_result.returncode != 0:
                    results.append((url, None, None, title_result.stderr))
                else:
                    raw_title = title_result.stdout.strip()
                    clean_title = sanitize_filename(raw_title)
                    encoded_title = urllib.parse.quote(raw_title)

                    # Lấy link video nhanh hơn bằng --skip-download
                    link_cmd = ["yt-dlp", "-g", "--skip-download", "--cache-dir", "-f", "bestvideo", url]
                    link_result = subprocess.run(link_cmd, capture_output=True, text=True)

                    if link_result.returncode == 0:
                        video_url = link_result.stdout.strip()
                        video_url_with_title = f"{video_url}&title={encoded_title}"
                        results.append((url, raw_title, video_url_with_title, None))
                    else:
                        results.append((url, raw_title, None, link_result.stderr))

            # Hiển thị kết quả
            for url, title, video_url, error in results:
                if error:
                    st.error(f"❌ Lỗi khi xử lý: {url}")
                    st.code(error)
                else:
                    st.success(f"✅ Đã lấy được link cho video: **{title}**")
                    st.markdown("### 🎥 Video")
                    st.code(video_url)
                    st.markdown(f"[🔻 Tải video ({sanitize_filename(title)}.webm)]({video_url})", unsafe_allow_html=True)
