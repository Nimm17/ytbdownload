import streamlit as st
import subprocess
import re
import urllib.parse

st.set_page_config(page_title="YouTube Direct Links", page_icon="🔗")
st.title("🔗 Tải trực tiếp YouTube")

urls = st.text_area("📺 Nhập danh sách URL video YouTube (mỗi dòng một URL):")

# Hàm làm sạch tiêu đề để thành tên file hợp lệ
def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title)

if st.button("Lấy link tải"):
    url_list = [url.strip() for url in urls.split("\n") if url.strip()]

    if not url_list:
        st.warning("⚠️ Vui lòng nhập ít nhất một URL video.")
    else:
        with st.spinner("🔄 Đang xử lý..."):
            for url in url_list:
                # Lấy tiêu đề video
                title_cmd = ["yt-dlp", "--get-title", url]
                title_result = subprocess.run(title_cmd, capture_output=True, text=True)

                if title_result.returncode != 0:
                    st.error(f"❌ Lỗi khi xử lý: {url}")
                    st.code(title_result.stderr)
                else:
                    raw_title = title_result.stdout.strip()
                    clean_title = sanitize_filename(raw_title)
                    encoded_title = urllib.parse.quote(raw_title)

                    # Lấy link video nhanh hơn bằng --skip-download
                    link_cmd = ["yt-dlp", "-g", "--skip-download", "-f", "bestvideo[ext=webm]", url]
                    link_result = subprocess.run(link_cmd, capture_output=True, text=True)

                    if link_result.returncode == 0:
                        video_url = link_result.stdout.strip()
                        video_url_with_title = f"{video_url}&title={encoded_title}"
                        st.markdown(f"[🔻 Tải video ({clean_title}.webm)]({video_url_with_title})", unsafe_allow_html=True)
                    else:
                        st.error(f"❌ Lỗi khi trích xuất link cho: {url}")
                        st.code(link_result.stderr)
