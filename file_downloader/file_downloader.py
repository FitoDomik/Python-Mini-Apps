import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import os
import threading
from urllib.parse import urlparse
import time
class FileDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Скачивание файла по ссылке")
        self.root.geometry("700x500")
        self.root.configure(bg='#f0f0f0')
        style = ttk.Style()
        style.theme_use('clam')
        self.downloading = False
        self.setup_ui()
    def setup_ui(self):
        title_label = tk.Label(
            self.root, 
            text="📥 Скачивание файла по ссылке", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)
        url_frame = tk.Frame(self.root, bg='#f0f0f0')
        url_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(url_frame, text="URL для скачивания:", font=("Arial", 10), bg='#f0f0f0').pack(anchor='w')
        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var, width=80, font=("Arial", 10))
        self.url_entry.pack(fill='x', pady=5)
        folder_frame = tk.Frame(self.root, bg='#f0f0f0')
        folder_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(folder_frame, text="Папка для сохранения:", font=("Arial", 10), bg='#f0f0f0').pack(anchor='w')
        folder_select_frame = tk.Frame(folder_frame, bg='#f0f0f0')
        folder_select_frame.pack(fill='x', pady=5)
        self.folder_var = tk.StringVar()
        self.folder_entry = tk.Entry(folder_select_frame, textvariable=self.folder_var, width=60, font=("Arial", 10))
        self.folder_entry.pack(side='left', fill='x', expand=True)
        browse_btn = tk.Button(
            folder_select_frame, 
            text="Обзор", 
            command=self.browse_folder,
            bg='#3498db',
            fg='white',
            font=("Arial", 10),
            relief='flat',
            padx=20
        )
        browse_btn.pack(side='right', padx=(10, 0))
        options_frame = tk.Frame(self.root, bg='#f0f0f0')
        options_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(options_frame, text="Опции:", font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w')
        self.overwrite_var = tk.BooleanVar()
        self.show_progress_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame, 
            text="Перезаписать существующий файл", 
            variable=self.overwrite_var,
            bg='#f0f0f0',
            font=("Arial", 9)
        ).pack(anchor='w')
        tk.Checkbutton(
            options_frame, 
            text="Показать прогресс скачивания", 
            variable=self.show_progress_var,
            bg='#f0f0f0',
            font=("Arial", 9)
        ).pack(anchor='w')
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(fill='x', padx=20, pady=10)
        self.download_btn = tk.Button(
            button_frame, 
            text="📥 Скачать", 
            command=self.start_download,
            bg='#27ae60',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            padx=30,
            pady=10
        )
        self.download_btn.pack(side='left')
        self.stop_btn = tk.Button(
            button_frame, 
            text="⏹️ Остановить", 
            command=self.stop_download,
            bg='#e74c3c',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            padx=30,
            pady=10,
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=(10, 0))
        clear_btn = tk.Button(
            button_frame, 
            text="🗑️ Очистить", 
            command=self.clear_log,
            bg='#95a5a6',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            padx=30,
            pady=10
        )
        clear_btn.pack(side='left', padx=(10, 0))
        self.progress_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.progress_frame.pack(fill='x', padx=20, pady=5)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            variable=self.progress_var, 
            maximum=100,
            length=400
        )
        self.progress_bar.pack(fill='x')
        self.progress_label = tk.Label(
            self.progress_frame, 
            text="", 
            font=("Arial", 9), 
            bg='#f0f0f0',
            fg='#7f8c8d'
        )
        self.progress_label.pack(anchor='w', pady=(2, 0))
        log_frame = tk.Frame(self.root, bg='#f0f0f0')
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        tk.Label(log_frame, text="Лог скачивания:", font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w')
        self.log_text = tk.Text(
            log_frame, 
            height=8, 
            font=("Consolas", 9),
            bg='#ffffff',
            fg='#2c3e50',
            wrap='word'
        )
        self.log_text.pack(fill='both', expand=True, pady=5)
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="Выберите папку для сохранения")
        if folder_path:
            self.folder_var.set(folder_path)
    def log_message(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    def start_download(self):
        url = self.url_var.get().strip()
        folder = self.folder_var.get().strip()
        if not url:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите URL для скачивания!")
            return
        if not folder:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите папку для сохранения!")
            return
        if not os.path.exists(folder):
            messagebox.showerror("Ошибка", "Выбранная папка не существует!")
            return
        self.downloading = True
        self.download_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        thread = threading.Thread(target=self.download_file, args=(url, folder))
        thread.daemon = True
        thread.start()
    def stop_download(self):
        self.downloading = False
        self.download_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.log_message("Скачивание остановлено пользователем")
    def download_file(self, url, folder):
        try:
            self.log_message(f"Начинаем скачивание: {url}")
            response = requests.head(url, timeout=10)
            if response.status_code != 200:
                self.log_message(f"Ошибка: HTTP {response.status_code}")
                return
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename or '.' not in filename:
                filename = "downloaded_file"
            file_path = os.path.join(folder, filename)
            if os.path.exists(file_path) and not self.overwrite_var.get():
                self.log_message(f"Файл уже существует: {filename}")
                return
            self.log_message(f"Скачиваем в: {file_path}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if not self.downloading:
                        self.log_message("Скачивание прервано")
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        return
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0 and self.show_progress_var.get():
                            progress = (downloaded_size / total_size) * 100
                            self.progress_var.set(progress)
                            self.progress_label.config(
                                text=f"Скачано: {downloaded_size / 1024 / 1024:.1f} MB / {total_size / 1024 / 1024:.1f} MB ({progress:.1f}%)"
                            )
            self.log_message(f"Скачивание завершено: {filename}")
            self.progress_var.set(100)
            self.progress_label.config(text="Скачивание завершено!")
        except requests.exceptions.RequestException as e:
            self.log_message(f"Ошибка сети: {e}")
        except Exception as e:
            self.log_message(f"Ошибка: {e}")
        finally:
            self.downloading = False
            self.download_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
def main():
    root = tk.Tk()
    app = FileDownloaderApp(root)
    root.mainloop()
if __name__ == "__main__":
    main()
