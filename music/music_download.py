import yt_dlp
import os
import tkinter as tk
from tkinter import messagebox, filedialog

# 下載音樂的函數
def download_music():
    url = url_entry.get()  # 從輸入框獲取 URL
    if not url:
        messagebox.showerror("錯誤", "請輸入 YouTube 影片的 URL")
        return

    # 讓用戶選擇輸出目錄
    output_dir = filedialog.askdirectory(title="選擇儲存目錄")
    if not output_dir:
        messagebox.showerror("錯誤", "請選擇一個有效的目錄")
        return

    # 設定 FFmpeg 路徑 (根據你的安裝位置修改)
    ffmpeg_path = "ffmpeg.exe"  # 替換為你實際的 FFmpeg 路徑

    # 下載選項設定
    ydl_opts = {
        "format": "bestaudio/best",  # 最佳音訊格式
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),  # 使用影片標題命名檔案
        "postprocessors": [{
            "key": "FFmpegExtractAudio",  # 使用 FFmpeg 轉換格式
            "preferredcodec": "mp3",  # 儲存為 MP3
            "preferredquality": "192",  # 可選品質設置
        }],
        "ffmpeg_location": ffmpeg_path,  # 明確指定 FFmpeg 的路徑
    }

    try:
        # 使用 yt-dlp 下載音訊
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("完成", "音軌下載並轉換為 MP3 完成！")

    except Exception as e:
        # 顯示錯誤訊息
        messagebox.showerror("錯誤", f"發生錯誤: {e}")

# 設置 Tkinter 視窗
root = tk.Tk()
root.title("YouTube 音樂下載器")

# 設定視窗大小
root.geometry("400x200")

# 設置說明標籤
label = tk.Label(root, text="請輸入 YouTube 影片的 URL")
label.pack(pady=10)

# 設置 URL 輸入框
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=10)

# 設置下載按鈕
download_button = tk.Button(root, text="下載音樂", command=download_music)
download_button.pack(pady=10)

# 啟動 Tkinter 主迴圈
root.mainloop()
