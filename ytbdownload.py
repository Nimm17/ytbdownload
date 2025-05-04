import streamlit as st
import subprocess
import re
import urllib.parse
from collections import defaultdict

st.set_page_config(page_title="YouTube Direct Links", page_icon="🔗")
st.title("🔗 Tải trực tiếp YouTube")

# Khởi tạo session state để theo dõi các link đã click
if 'clicked_links' not in st.session_state:
    st.session_state.clicked_links = defaultdict(bool)

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
            processed_urls = set()  # Để tránh trùng lặp URL
            for url in url_list:
                if url in processed_urls:
                    continue
                processed_urls.add(url)
                
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
                        
                        # Tạo key duy nhất cho link này
                        link_key = f"{url}_{video_url}"
                        
                        # Kiểm tra xem link đã được click chưa
                        is_clicked = st.session_state.clicked_links[link_key]
                        
                        # Thay đổi style dựa trên trạng thái click
                        if is_clicked:
                            button_style = "color: #888888; text-decoration: line-through;"
                            icon = "✅"
                            tooltip = " (Đã tải)"
                        else:
                            button_style = "color: #1f77b4;"
                            icon = "🔻"
                            tooltip = ""
                        
                        # Tạo button với callback để cập nhật trạng thái click
                        button = st.markdown(
                            f'<a href="{video_url_with_title}" style="{button_style}" target="_blank" '
                            f'onclick="this.style.color=\'#888888\'; this.style.textDecoration=\'line-through\'">'
                            f'{icon} Tải video {clean_title}.webm{tooltip}</a>', 
                            unsafe_allow_html=True
                        )
                        
                        # Lưu ý: Vì Streamlit không hỗ trợ JavaScript callback trực tiếp,
                        # nên chúng ta sử dụng HTML inline onclick để thay đổi giao diện
                        # Để lưu trạng thái thực sự, cần một giải pháp phức tạp hơn
                        
                    else:
                        st.error(f"❌ Lỗi khi trích xuất link cho: {url}")
                        st.code(link_result.stderr)
