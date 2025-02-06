import threading
import webbrowser
from multiprocessing import Queue
from pathlib import Path

# import speech_recognition as sr
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from tkinter import scrolledtext

from llm import DEFAULT_MODEL_NAME
from utils.settings import Settings
from version import version

def open_link(url) -> None:
    webbrowser.open_new(url)

class UI:
    def __init__(self):
        self.main_window = self.MainWindow()

    def run(self) -> None:
        self.main_window.mainloop()

    def display_current_status(self, text: str):
        self.main_window.update_message(text)
        self.main_window.update_technical_output(text)

    class AdvancedSettingsWindow(ttk.Toplevel):
        def __init__(self, parent):
            super().__init__(parent)
            self.title('Advanced Settings')
            self.minsize(300, 300)
            self.settings = Settings()
            self.create_widgets()
            settings_dict = self.settings.get_dict()
            if 'base_url' in settings_dict:
                self.base_url_entry.insert(0, settings_dict['base_url'])
            if 'model' in settings_dict:
                self.model_entry.insert(0, settings_dict['model'])
                self.model_var.set(settings_dict.get('model', 'custom'))
            else:
                self.model_entry.insert(0, DEFAULT_MODEL_NAME)
                self.model_var.set(DEFAULT_MODEL_NAME)

        def create_widgets(self) -> None:
            ttk.Label(self, text='Select Model:', bootstyle="primary").pack(pady=10, padx=10)
            self.model_var = ttk.StringVar(value='custom')
            radio_frame = ttk.Frame(self)
            radio_frame.pack(padx=20, pady=10)
            models = [
                ('GPT-4o (Default. Medium-Accurate, Medium-Fast)', 'gpt-4o'),
                ('GPT-4o-mini (Cheapest, Fastest)', 'gpt-4o-mini'),
                ('GPT-4v (Deprecated. Most-Accurate, Slowest)', 'gpt-4-vision-preview'),
                ('GPT-4-Turbo (Least Accurate, Fast)', 'gpt-4-turbo'),
                ('Custom (Specify Settings Below)', 'custom')
            ]
            for text, value in models:
                ttk.Radiobutton(radio_frame, text=text, value=value, variable=self.model_var, bootstyle="info").pack(
                    anchor=ttk.W, pady=5)
            label_base_url = ttk.Label(self, text='Custom OpenAI-Like API Model Base URL', bootstyle="secondary")
            label_base_url.pack(pady=10)
            self.base_url_entry = ttk.Entry(self, width=30)
            self.base_url_entry.pack()
            label_model = ttk.Label(self, text='Custom Model Name:', bootstyle="secondary")
            label_model.pack(pady=10)
            self.model_entry = ttk.Entry(self, width=30)
            self.model_entry.pack()
            save_button = ttk.Button(self, text='Save Settings', bootstyle="success", command=self.save_button)
            save_button.pack(pady=20)

        def save_button(self) -> None:
            base_url = self.base_url_entry.get().strip()
            model = self.model_var.get() if self.model_var.get() != 'custom' else self.model_entry.get().strip()
            settings_dict = {
                'base_url': base_url,
                'model': model,
            }
            self.settings.save_settings_to_file(settings_dict)
            self.destroy()

    class SettingsWindow(ttk.Toplevel):
        def __init__(self, parent):
            super().__init__(parent)
            self.title('Settings')
            self.minsize(300, 450)
            self.available_themes = ['darkly', 'cyborg', 'journal', 'solar', 'superhero']
            self.create_widgets()
            self.settings = Settings()
            settings_dict = self.settings.get_dict()
            if 'api_key' in settings_dict:
                self.api_key_entry.insert(0, settings_dict['api_key'])
            if 'default_browser' in settings_dict:
                self.browser_combobox.set(settings_dict['default_browser'])
            if 'play_ding_on_completion' in settings_dict:
                self.play_ding.set(1 if settings_dict['play_ding_on_completion'] else 0)
            if 'custom_llm_instructions':
                self.llm_instructions_text.insert('1.0', settings_dict['custom_llm_instructions'])
            self.theme_combobox.set(settings_dict.get('theme', 'superhero'))

        def create_widgets(self) -> None:
            label_api = ttk.Label(self, text='OpenAI API Key:', bootstyle="info")
            label_api.pack(pady=10)
            self.api_key_entry = ttk.Entry(self, width=30)
            self.api_key_entry.pack()
            label_browser = ttk.Label(self, text='Choose Default Browser:', bootstyle="info")
            label_browser.pack(pady=10)
            self.browser_var = ttk.StringVar()
            self.browser_combobox = ttk.Combobox(self, textvariable=self.browser_var,
                                                 values=['Safari', 'Firefox', 'Chrome'])
            self.browser_combobox.pack(pady=5)
            self.browser_combobox.set('Choose Browser')
            label_llm = ttk.Label(self, text='Custom LLM Guidance:', bootstyle="info")
            label_llm.pack(pady=10)
            self.llm_instructions_text = ttk.Text(self, height=10, width=50)
            self.llm_instructions_text.pack(padx=(10, 10), pady=(0, 10))
            self.play_ding = ttk.IntVar()
            play_ding_checkbox = ttk.Checkbutton(self, text="Play Ding on Completion", variable=self.play_ding,
                                                 bootstyle="round-toggle")
            play_ding_checkbox.pack(pady=10)
            label_theme = ttk.Label(self, text='UI Theme:', bootstyle="info")
            label_theme.pack()
            self.theme_var = ttk.StringVar()
            self.theme_combobox = ttk.Combobox(self, textvariable=self.theme_var, values=self.available_themes,
                                               state="readonly")
            self.theme_combobox.pack(pady=5)
            self.theme_combobox.set('superhero')
            self.theme_combobox.bind('<<ComboboxSelected>>', self.on_theme_change)
            save_button = ttk.Button(self, text='Save Settings', bootstyle="success", command=self.save_button)
            save_button.pack(pady=(10, 5))
            advanced_settings_button = ttk.Button(self, text='Advanced Settings', bootstyle="info",
                                                  command=self.open_advanced_settings)
            advanced_settings_button.pack(pady=(0, 10))
            link_label = ttk.Label(self, text='Setup Instructions', bootstyle="primary")
            link_label.pack()
            link_label.bind('<Button-1>', lambda e: open_link(
                'https://github.com/AmberSahdev/Open-Interface?tab=readme-ov-file#setup-%EF%B8%8F'))
            update_label = ttk.Label(self, text='Check for Updates', bootstyle="primary")
            update_label.pack()
            update_label.bind('<Button-1>', lambda e: open_link(
                'https://github.com/AmberSahdev/Open-Interface/releases/latest'))
            version_label = ttk.Label(self, text=f'Version: {str(version)}', font=('Helvetica', 10))
            version_label.pack(side="bottom", pady=10)

        def on_theme_change(self, event=None) -> None:
            theme = self.theme_var.get()
            self.master.change_theme(theme)

        def save_button(self) -> None:
            theme = self.theme_var.get()
            api_key = self.api_key_entry.get().strip()
            default_browser = self.browser_var.get()
            settings_dict = {
                'api_key': api_key,
                'default_browser': default_browser,
                'play_ding_on_completion': bool(self.play_ding.get()),
                'custom_llm_instructions': self.llm_instructions_text.get("1.0", "end-1c").strip(),
                'theme': theme
            }
            self.settings.save_settings_to_file(settings_dict)
            self.destroy()

        def open_advanced_settings(self):
            UI.AdvancedSettingsWindow(self)

    class MainWindow(ttk.Window):
        def change_theme(self, theme_name: str) -> None:
            self.style.theme_use(theme_name)

        def __init__(self):
            settings = Settings()
            settings_dict = settings.get_dict()
            theme = settings_dict.get('theme', 'superhero')
            try:
                super().__init__(themename=theme)
            except:
                super().__init__()
            self.title('Jamie Ai Compute')
            window_width = 450
            window_height = 370 # Increased height for technical output box
            self.minsize(window_width, window_height)
            screen_width = self.winfo_screenwidth()
            x_position = screen_width - window_width - 10
            y_position = 50
            self.geometry(f'{window_width}x{window_height}+{x_position}+{y_position}')
            path_to_icon_png = Path(__file__).resolve().parent.joinpath('resources', 'icon.png')
            self.logo_img = ImageTk.PhotoImage(Image.open(path_to_icon_png).resize((50, 50)))
            self.tk.call('wm', 'iconphoto', self._w, self.logo_img)
            self.user_request_queue = Queue()
            self.create_widgets()
            self.update_model_display()

        def create_widgets(self) -> None:
            frame = ttk.Frame(self, padding='10 10 10 10')
            frame.grid(column=0, row=0, sticky=(ttk.W, ttk.E, ttk.N, ttk.S))
            frame.columnconfigure(0, weight=1)
            logo_label = ttk.Label(frame, image=self.logo_img)
            logo_label.grid(column=0, row=0, sticky=ttk.W, pady=(10, 20))
            heading_label = ttk.Label(frame, text='What would you like me to do?', font=('Helvetica', 16),
                                      bootstyle="primary",
                                      wraplength=300)
            heading_label.grid(column=0, row=1, columnspan=3, sticky=ttk.W)
            self.entry = ttk.Entry(frame, width=38)
            self.entry.grid(column=0, row=2, sticky=(ttk.W, ttk.E))
            self.entry.bind("<Return>", lambda event: self.execute_user_request())
            self.entry.bind("<KP_Enter>", lambda event: self.execute_user_request())
            button = ttk.Button(frame, text='Submit', bootstyle="success", command=self.execute_user_request)
            button.grid(column=2, row=2, padx=10)
            settings_button = ttk.Button(self, text='Settings', bootstyle="info-outline", command=self.open_settings)
            settings_button.place(relx=1.0, rely=0.0, anchor='ne', x=-5, y=5)
            stop_button = ttk.Button(self, text='Stop', bootstyle="danger-outline", command=self.stop_previous_request)
            stop_button.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)
            self.input_display = ttk.Label(frame, text='', font=('Helvetica', 16), wraplength=400)
            self.input_display.grid(column=0, row=3, columnspan=3, sticky=ttk.W)
            self.message_display = ttk.Label(frame, text='', font=('Helvetica', 14), wraplength=400)
            self.message_display.grid(column=0, row=6, columnspan=3, sticky=ttk.W)

            # Add model display
            self.model_label = ttk.Label(self, text='', font=('Helvetica', 10), bootstyle="secondary")
            self.model_label.place(relx=0.0, rely=1.0, anchor='sw', x=10, y=-10)

            # Add technical output box
            self.technical_output = scrolledtext.ScrolledText(frame, wrap=ttk.WORD, height=5)
            self.technical_output.grid(column=0, row=7, columnspan=3, sticky=(ttk.W, ttk.E), pady=(5, 0))
            self.technical_output.config(state=ttk.DISABLED) # initially disable editing

        def update_model_display(self):
            settings = Settings().get_dict()
            model_name = settings.get('model', DEFAULT_MODEL_NAME)
            self.model_label.config(text=f'Active Model: {model_name}')

        def open_settings(self) -> None:
            super().open_settings()
            self.update_model_display()

        def stop_previous_request(self) -> None:
            self.user_request_queue.put('stop')

        def display_input(self) -> str:
            user_input = self.entry.get()
            self.input_display['text'] = f'{user_input}'
            self.entry.delete(0, ttk.END)
            return user_input.strip()

        def execute_user_request(self) -> None:
            user_request = self.display_input()
            if user_request == '' or user_request is None:
                return
            self.update_message('Fetching Instructions')
            self.user_request_queue.put(user_request)

        def start_voice_input_thread(self) -> None:
            threading.Thread(target=self.voice_input, daemon=True).start()

        def update_message(self, message: str) -> None:
            if threading.current_thread() is threading.main_thread():
                self.message_display['text'] = message
            else:
                self.message_display.after(0, lambda: self.message_display.config(text=message))

        def update_technical_output(self, message: str) -> None:
            # Update the technical output box with the provided text.
            # Ensure thread safety when updating the Tkinter GUI.
            if threading.current_thread() is threading.main_thread():
                self.technical_output.config(state=ttk.NORMAL)
                self.technical_output.insert(ttk.END, message + '\n')
                self.technical_output.config(state=ttk.DISABLED)
                self.technical_output.see(ttk.END) # Scroll to the bottom
            else:
                self.technical_output.after(0, lambda: self.update_technical_output(message))
