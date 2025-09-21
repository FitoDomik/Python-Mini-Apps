import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
import threading
from datetime import datetime
from pathlib import Path
class FileSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сортировка файлов по папкам")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        style = ttk.Style()
        style.theme_use('clam')
        self.sorting = False
        self.setup_ui()
        self.default_rules = {
            'Изображения': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
            'Документы': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'Таблицы': ['.xls', '.xlsx', '.csv', '.ods'],
            'Презентации': ['.ppt', '.pptx', '.odp'],
            'Архивы': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'Видео': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'Аудио': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
            'Код': ['.py', '.js', '.html', '.css', '.cpp', '.c', '.java', '.php', '.rb'],
            'Исполняемые': ['.exe', '.msi', '.deb', '.rpm', '.dmg']
        }
    def setup_ui(self):
        title_label = tk.Label(
            self.root, 
            text="📁 Сортировка файлов по папкам", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)
        folder_frame = tk.Frame(self.root, bg='#f0f0f0')
        folder_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(folder_frame, text="Папка для сортировки:", font=("Arial", 10), bg='#f0f0f0').pack(anchor='w')
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
        rules_frame = tk.Frame(self.root, bg='#f0f0f0')
        rules_frame.pack(fill='both', expand=True, padx=20, pady=10)
        tk.Label(rules_frame, text="Правила сортировки:", font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w')
        rules_list_frame = tk.Frame(rules_frame, bg='#f0f0f0')
        rules_list_frame.pack(fill='both', expand=True, pady=5)
        columns = ('Папка', 'Расширения')
        self.rules_tree = ttk.Treeview(rules_list_frame, columns=columns, show='headings', height=8)
        self.rules_tree.heading('Папка', text='Папка назначения')
        self.rules_tree.heading('Расширения', text='Расширения файлов')
        self.rules_tree.column('Папка', width=150)
        self.rules_tree.column('Расширения', width=400)
        self.rules_tree.pack(side='left', fill='both', expand=True)
        rules_scrollbar = ttk.Scrollbar(rules_list_frame, orient='vertical', command=self.rules_tree.yview)
        rules_scrollbar.pack(side='right', fill='y')
        self.rules_tree.config(yscrollcommand=rules_scrollbar.set)
        rules_buttons_frame = tk.Frame(rules_frame, bg='#f0f0f0')
        rules_buttons_frame.pack(fill='x', pady=5)
        add_rule_btn = tk.Button(
            rules_buttons_frame, 
            text="➕ Добавить правило", 
            command=self.add_rule,
            bg='#27ae60',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            padx=15
        )
        add_rule_btn.pack(side='left')
        edit_rule_btn = tk.Button(
            rules_buttons_frame, 
            text="✏️ Редактировать", 
            command=self.edit_rule,
            bg='#f39c12',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            padx=15
        )
        edit_rule_btn.pack(side='left', padx=(5, 0))
        delete_rule_btn = tk.Button(
            rules_buttons_frame, 
            text="🗑️ Удалить", 
            command=self.delete_rule,
            bg='#e74c3c',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            padx=15
        )
        delete_rule_btn.pack(side='left', padx=(5, 0))
        load_defaults_btn = tk.Button(
            rules_buttons_frame, 
            text="📋 Загрузить по умолчанию", 
            command=self.load_default_rules,
            bg='#9b59b6',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            padx=15
        )
        load_defaults_btn.pack(side='left', padx=(5, 0))
        options_frame = tk.Frame(self.root, bg='#f0f0f0')
        options_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(options_frame, text="Опции сортировки:", font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w')
        self.create_subdirs_var = tk.BooleanVar(value=True)
        self.move_files_var = tk.BooleanVar(value=True)
        self.overwrite_var = tk.BooleanVar()
        self.preview_only_var = tk.BooleanVar()
        options_grid = tk.Frame(options_frame, bg='#f0f0f0')
        options_grid.pack(fill='x', pady=5)
        tk.Checkbutton(
            options_grid, 
            text="Создавать подпапки автоматически", 
            variable=self.create_subdirs_var,
            bg='#f0f0f0',
            font=("Arial", 9)
        ).grid(row=0, column=0, sticky='w')
        tk.Checkbutton(
            options_grid, 
            text="Перемещать файлы (иначе копировать)", 
            variable=self.move_files_var,
            bg='#f0f0f0',
            font=("Arial", 9)
        ).grid(row=0, column=1, sticky='w', padx=(20, 0))
        tk.Checkbutton(
            options_grid, 
            text="Перезаписывать существующие файлы", 
            variable=self.overwrite_var,
            bg='#f0f0f0',
            font=("Arial", 9)
        ).grid(row=1, column=0, sticky='w')
        tk.Checkbutton(
            options_grid, 
            text="Только предварительный просмотр", 
            variable=self.preview_only_var,
            bg='#f0f0f0',
            font=("Arial", 9)
        ).grid(row=1, column=1, sticky='w', padx=(20, 0))
        action_frame = tk.Frame(self.root, bg='#f0f0f0')
        action_frame.pack(fill='x', padx=20, pady=10)
        self.sort_btn = tk.Button(
            action_frame, 
            text="📁 Начать сортировку", 
            command=self.start_sorting,
            bg='#27ae60',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            padx=30,
            pady=10
        )
        self.sort_btn.pack(side='left')
        self.stop_btn = tk.Button(
            action_frame, 
            text="⏹️ Остановить", 
            command=self.stop_sorting,
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
            action_frame, 
            text="🗑️ Очистить лог", 
            command=self.clear_log,
            bg='#95a5a6',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            padx=30,
            pady=10
        )
        clear_btn.pack(side='left', padx=(10, 0))
        log_frame = tk.Frame(self.root, bg='#f0f0f0')
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        tk.Label(log_frame, text="Лог операций:", font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w')
        self.log_text = tk.Text(
            log_frame, 
            height=6, 
            font=("Consolas", 9),
            bg='#ffffff',
            fg='#2c3e50',
            wrap='word'
        )
        self.log_text.pack(fill='both', expand=True, pady=5)
        log_scrollbar = tk.Scrollbar(self.log_text)
        log_scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.log_text.yview)
        self.load_default_rules()
    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="Выберите папку для сортировки")
        if folder_path:
            self.folder_var.set(folder_path)
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    def load_default_rules(self):
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        for folder, extensions in self.default_rules.items():
            self.rules_tree.insert('', 'end', values=(folder, ', '.join(extensions)))
    def add_rule(self):
        dialog = RuleDialog(self.root, "Добавить правило")
        if dialog.result:
            folder, extensions = dialog.result
            self.rules_tree.insert('', 'end', values=(folder, ', '.join(extensions)))
    def edit_rule(self):
        selected = self.rules_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите правило для редактирования!")
            return
        item = self.rules_tree.item(selected[0])
        folder, extensions_str = item['values']
        extensions = [ext.strip() for ext in extensions_str.split(',')]
        dialog = RuleDialog(self.root, "Редактировать правило", folder, extensions)
        if dialog.result:
            new_folder, new_extensions = dialog.result
            self.rules_tree.item(selected[0], values=(new_folder, ', '.join(new_extensions)))
    def delete_rule(self):
        selected = self.rules_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите правило для удаления!")
            return
        result = messagebox.askyesno("Подтверждение", "Удалить выбранное правило?")
        if result:
            self.rules_tree.delete(selected[0])
    def start_sorting(self):
        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showwarning("Предупреждение", "Выберите папку для сортировки!")
            return
        if not os.path.exists(folder):
            messagebox.showerror("Ошибка", "Выбранная папка не существует!")
            return
        rules = {}
        for item in self.rules_tree.get_children():
            values = self.rules_tree.item(item)['values']
            folder_name = values[0]
            extensions = [ext.strip() for ext in values[1].split(',')]
            rules[folder_name] = extensions
        if not rules:
            messagebox.showwarning("Предупреждение", "Добавьте правила сортировки!")
            return
        self.sorting = True
        self.sort_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        thread = threading.Thread(target=self.sort_files, args=(folder, rules))
        thread.daemon = True
        thread.start()
    def stop_sorting(self):
        self.sorting = False
        self.sort_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.log_message("Сортировка остановлена пользователем")
    def sort_files(self, folder, rules):
        try:
            self.log_message(f"Начинаем сортировку в папке: {folder}")
            files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
            if not files:
                self.log_message("В папке нет файлов для сортировки")
                return
            self.log_message(f"Найдено {len(files)} файлов")
            sorted_count = 0
            unsorted_files = []
            for filename in files:
                if not self.sorting:
                    break
                file_path = os.path.join(folder, filename)
                file_ext = os.path.splitext(filename)[1].lower()
                target_folder = None
                for folder_name, extensions in rules.items():
                    if file_ext in extensions:
                        target_folder = folder_name
                        break
                if target_folder:
                    target_path = os.path.join(folder, target_folder)
                    if self.create_subdirs_var.get() and not os.path.exists(target_path):
                        os.makedirs(target_path)
                        self.log_message(f"Создана папка: {target_folder}")
                    new_file_path = os.path.join(target_path, filename)
                    if os.path.exists(new_file_path) and not self.overwrite_var.get():
                        self.log_message(f"Файл уже существует: {filename}")
                        continue
                    if not self.preview_only_var.get():
                        if self.move_files_var.get():
                            shutil.move(file_path, new_file_path)
                            self.log_message(f"Перемещен: {filename} -> {target_folder}")
                        else:
                            shutil.copy2(file_path, new_file_path)
                            self.log_message(f"Скопирован: {filename} -> {target_folder}")
                    else:
                        self.log_message(f"[ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР] {filename} -> {target_folder}")
                    sorted_count += 1
                else:
                    unsorted_files.append(filename)
            self.log_message(f"Сортировка завершена! Обработано: {sorted_count} файлов")
            if unsorted_files:
                self.log_message(f"Не отсортированы: {', '.join(unsorted_files)}")
        except Exception as e:
            self.log_message(f"Ошибка при сортировке: {e}")
        finally:
            self.sorting = False
            self.sort_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
class RuleDialog:
    def __init__(self, parent, title, folder="", extensions=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        # Центрируем окно
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        self.setup_ui(folder, extensions or [])
    def setup_ui(self, folder, extensions):
        tk.Label(
            self.dialog, 
            text=self.dialog.title(), 
            font=("Arial", 12, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        ).pack(pady=10)
        # Название папки
        tk.Label(self.dialog, text="Название папки:", font=("Arial", 10), bg='#f0f0f0').pack(anchor='w', padx=20)
        self.folder_var = tk.StringVar(value=folder)
        folder_entry = tk.Entry(self.dialog, textvariable=self.folder_var, width=40, font=("Arial", 10))
        folder_entry.pack(fill='x', padx=20, pady=5)
        # Расширения
        tk.Label(self.dialog, text="Расширения файлов (через запятую):", font=("Arial", 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
        self.extensions_text = tk.Text(self.dialog, height=8, font=("Arial", 10), wrap='word')
        self.extensions_text.pack(fill='both', expand=True, padx=20, pady=5)
        if extensions:
            self.extensions_text.insert('1.0', ', '.join(extensions))
        # Кнопки
        button_frame = tk.Frame(self.dialog, bg='#f0f0f0')
        button_frame.pack(fill='x', padx=20, pady=10)
        ok_btn = tk.Button(
            button_frame, 
            text="OK", 
            command=self.ok_clicked,
            bg='#27ae60',
            fg='white',
            font=("Arial", 10, "bold"),
            relief='flat',
            padx=20
        )
        ok_btn.pack(side='right')
        cancel_btn = tk.Button(
            button_frame, 
            text="Отмена", 
            command=self.cancel_clicked,
            bg='#95a5a6',
            fg='white',
            font=("Arial", 10, "bold"),
            relief='flat',
            padx=20
        )
        cancel_btn.pack(side='right', padx=(0, 10))
    def ok_clicked(self):
        folder = self.folder_var.get().strip()
        extensions_text = self.extensions_text.get('1.0', tk.END).strip()
        if not folder or not extensions_text:
            messagebox.showwarning("Предупреждение", "Заполните все поля!")
            return
        extensions = [ext.strip() for ext in extensions_text.split(',') if ext.strip()]
        if not extensions:
            messagebox.showwarning("Предупреждение", "Введите хотя бы одно расширение!")
            return
        self.result = (folder, extensions)
        self.dialog.destroy()
    def cancel_clicked(self):
        self.dialog.destroy()
def main():
    root = tk.Tk()
    app = FileSorterApp(root)
    root.mainloop()
if __name__ == "__main__":
    main()
