import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import qrcode
from PIL import Image, ImageTk
import os
import threading
from datetime import datetime
class QRGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор QR-кода")
        self.root.geometry("700x600")
        self.root.configure(bg='#f0f0f0')
        style = ttk.Style()
        style.theme_use('clam')
        self.current_qr_image = None
        self.setup_ui()
    def setup_ui(self):
        title_label = tk.Label(
            self.root, 
            text="📱 Генератор QR-кода", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)
        input_frame = tk.Frame(self.root, bg='#f0f0f0')
        input_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(input_frame, text="Данные для QR-кода:", font=("Arial", 10), bg='#f0f0f0').pack(anchor='w')
        self.data_var = tk.StringVar()
        self.data_entry = tk.Entry(input_frame, textvariable=self.data_var, width=60, font=("Arial", 10))
        self.data_entry.pack(fill='x', pady=5)
        type_frame = tk.Frame(self.root, bg='#f0f0f0')
        type_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(type_frame, text="Тип данных:", font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w')
        self.data_type_var = tk.StringVar(value="text")
        data_types = [
            ("Текст", "text"),
            ("URL", "url"),
            ("Email", "email"),
            ("Телефон", "phone"),
            ("WiFi", "wifi"),
            ("SMS", "sms"),
            ("VCard", "vcard")
        ]
        for i, (text, value) in enumerate(data_types):
            tk.Radiobutton(
                type_frame, 
                text=text, 
                variable=self.data_type_var, 
                value=value,
                bg='#f0f0f0',
                font=("Arial", 9),
                command=self.on_data_type_change
            ).grid(row=0, column=i, sticky='w', padx=(0, 20))
        settings_frame = tk.Frame(self.root, bg='#f0f0f0')
        settings_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(settings_frame, text="Настройки QR-кода:", font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w')
        size_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        size_frame.pack(fill='x', pady=5)
        tk.Label(size_frame, text="Размер:", font=("Arial", 9), bg='#f0f0f0').pack(side='left')
        self.size_var = tk.StringVar(value="10")
        size_spinbox = tk.Spinbox(size_frame, from_=1, to=20, textvariable=self.size_var, width=5, font=("Arial", 9))
        size_spinbox.pack(side='left', padx=(5, 20))
        tk.Label(size_frame, text="Коррекция ошибок:", font=("Arial", 9), bg='#f0f0f0').pack(side='left')
        self.error_correction_var = tk.StringVar(value="M")
        error_correction_combo = ttk.Combobox(size_frame, textvariable=self.error_correction_var, 
                                            values=["L", "M", "Q", "H"], width=5, state="readonly")
        error_correction_combo.pack(side='left', padx=(5, 0))
        color_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        color_frame.pack(fill='x', pady=5)
        tk.Label(color_frame, text="Цвет заливки:", font=("Arial", 9), bg='#f0f0f0').pack(side='left')
        self.fill_color_var = tk.StringVar(value="#000000")
        fill_color_entry = tk.Entry(color_frame, textvariable=self.fill_color_var, width=10, font=("Arial", 9))
        fill_color_entry.pack(side='left', padx=(5, 20))
        tk.Label(color_frame, text="Цвет фона:", font=("Arial", 9), bg='#f0f0f0').pack(side='left')
        self.back_color_var = tk.StringVar(value="#FFFFFF")
        back_color_entry = tk.Entry(color_frame, textvariable=self.back_color_var, width=10, font=("Arial", 9))
        back_color_entry.pack(side='left', padx=(5, 0))
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(fill='x', padx=20, pady=10)
        self.generate_btn = tk.Button(
            button_frame, 
            text="🎯 Сгенерировать QR-код", 
            command=self.generate_qr,
            bg='#27ae60',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            padx=30,
            pady=10
        )
        self.generate_btn.pack(side='left')
        self.save_btn = tk.Button(
            button_frame, 
            text="💾 Сохранить", 
            command=self.save_qr,
            bg='#3498db',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            padx=30,
            pady=10,
            state='disabled'
        )
        self.save_btn.pack(side='left', padx=(10, 0))
        clear_btn = tk.Button(
            button_frame, 
            text="🗑️ Очистить", 
            command=self.clear_all,
            bg='#95a5a6',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            padx=30,
            pady=10
        )
        clear_btn.pack(side='left', padx=(10, 0))
        preview_frame = tk.Frame(self.root, bg='#f0f0f0')
        preview_frame.pack(fill='both', expand=True, padx=20, pady=10)
        tk.Label(preview_frame, text="Предварительный просмотр:", font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w')
        image_frame = tk.Frame(preview_frame, bg='#ffffff', relief='sunken', bd=2)
        image_frame.pack(fill='both', expand=True, pady=5)
        self.image_label = tk.Label(image_frame, text="QR-код появится здесь", 
                                  font=("Arial", 12), bg='#ffffff', fg='#7f8c8d')
        self.image_label.pack(expand=True)
        log_frame = tk.Frame(self.root, bg='#f0f0f0')
        log_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(log_frame, text="Лог операций:", font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w')
        self.log_text = tk.Text(
            log_frame, 
            height=4, 
            font=("Consolas", 9),
            bg='#ffffff',
            fg='#2c3e50',
            wrap='word'
        )
        self.log_text.pack(fill='x', pady=5)
        log_scrollbar = tk.Scrollbar(self.log_text)
        log_scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.log_text.yview)
        self.data_entry.bind('<KeyRelease>', self.on_data_change)
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    def on_data_type_change(self):
        data_type = self.data_type_var.get()
        placeholder_text = {
            'text': 'Введите любой текст',
            'url': 'https://example.com',
            'email': 'example@email.com',
            'phone': '+7 (999) 123-45-67',
            'wifi': 'SSID:MyWiFi,Password:12345678',
            'sms': 'Номер: +7 (999) 123-45-67, Текст: Привет!',
            'vcard': 'BEGIN:VCARD\nFN:Иван Иванов\nTEL:+79991234567\nEND:VCARD'
        }
        self.data_entry.delete(0, tk.END)
        self.data_entry.insert(0, placeholder_text.get(data_type, ''))
    def on_data_change(self, event=None):
        if self.data_var.get().strip():
            self.root.after(1000, self.auto_generate)  
    def auto_generate(self):
        if self.data_var.get().strip() and not self.generate_btn['state'] == 'disabled':
            self.generate_qr()
    def generate_qr(self):
        data = self.data_var.get().strip()
        if not data:
            messagebox.showwarning("Предупреждение", "Введите данные для QR-кода!")
            return
        try:
            self.log_message("Генерируем QR-код...")
            formatted_data = self.format_data(data)
            qr = qrcode.QRCode(
                version=1,
                error_correction=getattr(qrcode.constants, f'ERROR_CORRECT_{self.error_correction_var.get()}'),
                box_size=int(self.size_var.get()),
                border=4,
            )
            qr.add_data(formatted_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color=self.fill_color_var.get(), 
                              back_color=self.back_color_var.get())
            self.current_qr_image = img
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk, text="")
            self.image_label.image = img_tk  
            self.save_btn.config(state='normal')
            self.log_message("QR-код успешно сгенерирован!")
        except Exception as e:
            self.log_message(f"Ошибка при генерации QR-кода: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать QR-код: {e}")
    def format_data(self, data):
        data_type = self.data_type_var.get()
        if data_type == 'url':
            if not data.startswith(('http://', 'https://')):
                return f'https://{data}'
            return data
        elif data_type == 'email':
            return f'mailto:{data}'
        elif data_type == 'phone':
            clean_phone = ''.join(c for c in data if c.isdigit() or c == '+')
            return f'tel:{clean_phone}'
        elif data_type == 'wifi':
            parts = data.split(',')
            ssid = parts[0].split(':')[1] if ':' in parts[0] else parts[0]
            password = parts[1].split(':')[1] if len(parts) > 1 and ':' in parts[1] else ''
            return f'WIFI:T:WPA;S:{ssid};P:{password};H:false;;'
        elif data_type == 'sms':
            if ':' in data:
                return f'sms:{data}'
            else:
                return f'sms:{data}'
        else:
            return data
    def save_qr(self):
        if not self.current_qr_image:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте QR-код!")
            return
        file_path = filedialog.asksaveasfilename(
            title="Сохранить QR-код",
            defaultextension=".png",
            filetypes=[
                ("PNG файлы", "*.png"),
                ("JPEG файлы", "*.jpg"),
                ("Все файлы", "*.*")
            ]
        )
        if file_path:
            try:
                self.current_qr_image.save(file_path)
                self.log_message(f"QR-код сохранён: {file_path}")
                messagebox.showinfo("Успех", f"QR-код сохранён в файл:\n{file_path}")
            except Exception as e:
                self.log_message(f"Ошибка при сохранении: {e}")
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    def clear_all(self):
        self.data_var.set("")
        self.image_label.config(image="", text="QR-код появится здесь")
        self.image_label.image = None
        self.current_qr_image = None
        self.save_btn.config(state='disabled')
        self.log_text.delete(1.0, tk.END)
        self.log_message("Очищено")
def main():
    root = tk.Tk()
    app = QRGeneratorApp(root)
    root.mainloop()
if __name__ == "__main__":
    main()