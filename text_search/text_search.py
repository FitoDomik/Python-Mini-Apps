import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import re
class TextSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Поиск текста в файле")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        style = ttk.Style()
        style.theme_use('clam')
        self.setup_ui()
    def setup_ui(self):
        title_label = tk.Label(
            self.root, 
            text="🔍 Поиск текста в файле", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)
        file_frame = tk.Frame(self.root, bg='#f0f0f0')
        file_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(file_frame, text="Выберите файл:", font=("Arial", 10), bg='#f0f0f0').pack(anchor='w')
        file_select_frame = tk.Frame(file_frame, bg='#f0f0f0')
        file_select_frame.pack(fill='x', pady=5)
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(file_select_frame, textvariable=self.file_path_var, width=60, font=("Arial", 10))
        self.file_entry.pack(side='left', fill='x', expand=True)
        browse_btn = tk.Button(
            file_select_frame, 
            text="Обзор", 
            command=self.browse_file,
            bg='#3498db',
            fg='white',
            font=("Arial", 10),
            relief='flat',
            padx=20
        )
        browse_btn.pack(side='right', padx=(10, 0))
        search_frame = tk.Frame(self.root, bg='#f0f0f0')
        search_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(search_frame, text="Текст для поиска:", font=("Arial", 10), bg='#f0f0f0').pack(anchor='w')
        search_input_frame = tk.Frame(search_frame, bg='#f0f0f0')
        search_input_frame.pack(fill='x', pady=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_input_frame, textvariable=self.search_var, width=60, font=("Arial", 10))
        self.search_entry.pack(side='left', fill='x', expand=True)
        options_frame = tk.Frame(search_frame, bg='#f0f0f0')
        options_frame.pack(fill='x', pady=5)
        self.case_sensitive_var = tk.BooleanVar()
        self.regex_var = tk.BooleanVar()
        tk.Checkbutton(
            options_frame, 
            text="Учитывать регистр", 
            variable=self.case_sensitive_var,
            bg='#f0f0f0',
            font=("Arial", 9)
        ).pack(side='left')
        tk.Checkbutton(
            options_frame, 
            text="Регулярные выражения", 
            variable=self.regex_var,
            bg='#f0f0f0',
            font=("Arial", 9)
        ).pack(side='left', padx=(20, 0))
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(fill='x', padx=20, pady=10)
        search_btn = tk.Button(
            button_frame, 
            text="🔍 Найти", 
            command=self.search_text,
            bg='#27ae60',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            padx=30,
            pady=10
        )
        search_btn.pack(side='left')
        clear_btn = tk.Button(
            button_frame, 
            text="🗑️ Очистить", 
            command=self.clear_results,
            bg='#e74c3c',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            padx=30,
            pady=10
        )
        clear_btn.pack(side='left', padx=(10, 0))
        results_frame = tk.Frame(self.root, bg='#f0f0f0')
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        tk.Label(results_frame, text="Результаты поиска:", font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w')
        self.results_text = scrolledtext.ScrolledText(
            results_frame, 
            height=15, 
            font=("Consolas", 10),
            bg='#ffffff',
            fg='#2c3e50',
            wrap='word'
        )
        self.results_text.pack(fill='both', expand=True, pady=5)
        self.stats_label = tk.Label(
            results_frame, 
            text="", 
            font=("Arial", 9), 
            bg='#f0f0f0',
            fg='#7f8c8d'
        )
        self.stats_label.pack(anchor='w', pady=(5, 0))
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл для поиска",
            filetypes=[
                ("Все файлы", "*.*"),
                ("Текстовые файлы", "*.txt"),
                ("Python файлы", "*.py"),
                ("HTML файлы", "*.html"),
                ("CSS файлы", "*.css"),
                ("JavaScript файлы", "*.js")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
    def search_text(self):
        file_path = self.file_path_var.get()
        search_text = self.search_var.get()
        if not file_path or not search_text:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите файл и введите текст для поиска!")
            return
        if not os.path.exists(file_path):
            messagebox.showerror("Ошибка", "Файл не найден!")
            return
        try:
            encodings = ['utf-8', 'cp1251', 'latin-1']
            content = None
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            if content is None:
                messagebox.showerror("Ошибка", "Не удалось прочитать файл с поддерживаемой кодировкой!")
                return
            if self.regex_var.get():
                try:
                    flags = 0 if self.case_sensitive_var.get() else re.IGNORECASE
                    pattern = re.compile(search_text, flags)
                    matches = list(pattern.finditer(content))
                except re.error as e:
                    messagebox.showerror("Ошибка", f"Ошибка в регулярном выражении: {e}")
                    return
            else:
                if self.case_sensitive_var.get():
                    matches = []
                    start = 0
                    while True:
                        pos = content.find(search_text, start)
                        if pos == -1:
                            break
                        matches.append((pos, pos + len(search_text)))
                        start = pos + 1
                else:
                    matches = []
                    content_lower = content.lower()
                    search_lower = search_text.lower()
                    start = 0
                    while True:
                        pos = content_lower.find(search_lower, start)
                        if pos == -1:
                            break
                        matches.append((pos, pos + len(search_text)))
                        start = pos + 1
            self.display_results(content, matches, search_text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при чтении файла: {e}")
    def display_results(self, content, matches, search_text):
        self.results_text.delete(1.0, tk.END)
        if not matches:
            self.results_text.insert(tk.END, "Текст не найден в файле.")
            self.stats_label.config(text="Найдено совпадений: 0")
            return
        lines = content.split('\n')
        line_num = 1
        char_pos = 0
        results = []
        for match in matches:
            start_pos, end_pos = match
            line_start = content.rfind('\n', 0, start_pos) + 1
            line_end = content.find('\n', start_pos)
            if line_end == -1:
                line_end = len(content)
            line_content = content[line_start:line_end]
            line_number = content[:start_pos].count('\n') + 1
            before_match = line_content[:start_pos - line_start]
            match_text = line_content[start_pos - line_start:end_pos - line_start]
            after_match = line_content[end_pos - line_start:]
            result_line = f"Строка {line_number}: {before_match}[{match_text}]{after_match}"
            results.append(result_line)
        self.results_text.insert(tk.END, f"Найдено {len(matches)} совпадений:\n\n")
        for i, result in enumerate(results, 1):
            self.results_text.insert(tk.END, f"{i}. {result}\n")
        self.stats_label.config(text=f"Найдено совпадений: {len(matches)}")
    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
        self.stats_label.config(text="")
def main():
    root = tk.Tk()
    app = TextSearchApp(root)
    root.mainloop()
if __name__ == "__main__":
    main()