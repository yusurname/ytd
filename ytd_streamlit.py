import streamlit as st
import yt_dlp
import os
from pathlib import Path

st.set_page_config(page_title="YouTube Downloader", page_icon=":arrow_down:", layout="centered")
st.title("YouTube Video Downloader")

st.markdown("""
Enter a YouTube video URL, select format and quality, and download the video directly from your browser.
""")

url = st.text_input("YouTube URL", "")
format_type = st.selectbox("Format", ["mp4", "webm", "mp3"])

if format_type == "mp3":
    quality = st.selectbox("Audio Quality (kbps)", ["320", "256", "192", "128", "96", "64", "best", "worst"])
else:
    quality = st.selectbox("Video Quality", ["best", "worst", "1080p", "720p", "480p", "360p", "240p", "144p"])

download_btn = st.button("Download")

@st.cache_data(show_spinner=False)
def download_video(url, format_type, quality):
    temp_dir = Path("temp_download")
    temp_dir.mkdir(exist_ok=True)
    if format_type == "mp3":
        outtmpl = str(temp_dir / '%(title)s.%(ext)s')
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality if quality.isdigit() else '192',
            }],
        }
    else:
        outtmpl = str(temp_dir / '%(title)s.%(ext)s')
        if quality == 'best':
            ydl_format = f'best[ext={format_type}]/best'
        elif quality == 'worst':
            ydl_format = f'worst[ext={format_type}]/worst'
        else:
            height = quality.replace('p', '')
            ydl_format = f'best[height<={height}][ext={format_type}]/best[height<={height}]/best'
        ydl_opts = {
            'format': ydl_format,
            'outtmpl': outtmpl,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info and isinstance(info, dict) and 'entries' in info:
            info = info['entries'][0]
        filename = ydl.prepare_filename(info)
        if format_type == "mp3":
            filename = os.path.splitext(filename)[0] + ".mp3"
    return filename

if download_btn and url:
    with st.spinner("Downloading..."):
        try:
            filepath = download_video(url, format_type, quality)
            st.success("Download complete!")
            with open(filepath, "rb") as f:
                st.download_button(
                    label="Download File",
                    data=f,
                    file_name=os.path.basename(filepath),
                    mime="audio/mpeg" if format_type == "mp3" else ("video/mp4" if format_type == "mp4" else "video/webm")
                )
            # Clean up
            os.remove(filepath)
            try:
                os.rmdir(os.path.dirname(filepath))
            except Exception:
                pass
        except Exception as e:
            st.error(f"Error: {e}") 