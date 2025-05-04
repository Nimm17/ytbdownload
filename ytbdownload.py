import streamlit as st
import subprocess
import re
import urllib.parse
from collections import defaultdict

st.set_page_config(page_title="YouTube Direct Links", page_icon="🔗")
st.title("🔗 Tải trực tiếp YouTube")

# Khởi tạo session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = []
if 'clicked_links' not in st.session_state:
    st.session_state.clicked_links = defaultdict(bool)

urls = st.text_area("📺 Nhập danh sách URL video YouTube (mỗi dòng một URL):")

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title)

# Xử lý logic chính trong một hàm riêng
def process_urls(url_list):
    results = []
    processed_urls = set()
    
    for url in url_list:
        if url in processed_urls:
            continue
        processed_urls.add(url)

        try:
            # Lấy tiêu đề video
            title_result = subprocess.run(
                ["yt-dlp", "--get-title", url],
                capture_output=True, 
                text=True,
                check=True
            )
            raw_title = title_result.stdout.strip()
            clean_title = sanitize_filename(raw_title)
            encoded_title = urllib.parse.quote(raw_title)

            # Lấy link tải
            link_result = subprocess.run(
                ["yt-dlp", "-g", "--skip-download", "-f", "bestvideo[ext=webm]", url],
                capture_output=True,
                text=True,
                check=True
            )
            video_url = link_result.stdout.strip()
            video_url_with_title = f"{video_url}&title={encoded_title}"
            
            results.append({
                "original_url": url,
                "download_url": video_url_with_title,
                "clean_title": clean_title,
                "key": f"{url}_{video_url}"
            })
            
        except subprocess.CalledProcessError as e:
            results.append({
                "error": f"❌ Lỗi khi xử lý: {url}",
                "details": e.stderr
            })
    
    return results

if st.button("Lấy link tải"):
    url_list = [url.strip() for url in urls.split("\n") if url.strip()]
    if url_list:
        with st.spinner("🔄 Đang xử lý..."):
            st.session_state.processed_data = process_urls(url_list)

# Hiển thị kết quả từ session state
if st.session_state.processed_data:
    st.divider()
    st.subheader("📥 Danh sách link tải:")
    
    for item in st.session_state.processed_data:
        if "error" in item:
            st.error(item["error"])
            st.code(item["details"])
            continue
            
        col1, col2 = st.columns([1, 4])
        with col1:
            button_label = "✅ Đã tải" if st.session_state.clicked_links[item["key"]] else "🔻 Tải xuống"
            if st.button(
                button_label,
                key=f"btn_{item['key']}",
                help="Nhấn để tải video",
                disabled=st.session_state.clicked_links[item["key"]]
            ):
                st.session_state.clicked_links[item["key"]] = True
                st.session_state.link_to_open = item["download_url"]
                st.rerun()
        
        with col2:
            st.markdown(f"**{item['clean_title']}**")
            st.caption(f"`{item['original_url']}`")

# Xử lý mở link sau khi click
if 'link_to_open' in st.session_state and st.session_state.link_to_open:
    js = f"""
    <script>
        window.open('{st.session_state.link_to_open}', '_blank');
        window.parent.postMessage({{type: 'streamlit:setComponentValue', value: ''}}, '*');
    </script>
    """
    st.components.v1.html(js, height=0)
    st.session_state.link_to_open = None
