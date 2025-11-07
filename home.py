import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import re

VALID_USERNAME = "aluno"
VALID_PASSWORD = "senha123"

THEMES = {
    "light": {
        "bg": "#f2f2f2",
        "chat_bg": "#ffffff",
        "user_bg": "#d0f0ff",
        "bot_bg": "#f0f0f5",
        "text": "#111111",
        "accent": "#2b7cff",
        "input_bg": "#ffffff",
        "button_bg": "#e6e6e6"
    },
    "dark": {
        "bg": "#1f1f1f",
        "chat_bg": "#2b2b2b",
        "user_bg": "#14344a",
        "bot_bg": "#2f2f36",
        "text": "#eaeaea",
        "accent": "#59a6ff",
        "input_bg": "#3a3a3a",
        "button_bg": "#333333"
    }
}

TI_RESPONSES = [
    (r"\bpython\b", "Você mencionou Python. Dica: use virtualenv ou venv para isolar dependências. Quer um exemplo de requirements.txt?"),
    (r"\bdocker\b", "Docker é ótimo para empacotar aplicações. Lembre-se de criar .dockerignore e usar imagens base leves como python:3.11-slim."),
    (r"\bgit\b", "Para problemas com Git: verifique branches com `git branch` e use `git log --oneline --graph` para histórico compacto."),
    (r"\bsql\b|\bmysql\b|\bpostgres\b|\bpostgresql\b", "Banco de dados: sempre sanitize inputs e use prepared statements. Indexe colunas que aparecem em JOINs e WHERE."),
    (r"\blinux\b|\bubuntu\b|\bcentos\b", "No Linux: use `journalctl -xe` para logs do sistema e `top`/`htop` para monitorar processos."),
    (r"\baws\b|\bazure\b|\bgcp\b|\bcloud\b", "Ao usar Cloud, esteja atento a políticas de IAM e aos custos — habilite alertas de orçamento."),
    (r"\bhtml\b|\bcss\b|\bjavascript\b|\bjs\b", "Front-end: separe estrutura (HTML), apresentação (CSS) e comportamento (JS). Otimize assets para carregar rápido."),
    (r"\bbug\b|\berro\b|\bexception\b|\btraceback\b", "Depuração: leia o traceback, isole o problema em testes pequenos e use prints/logs para entender o fluxo."),
    (r"\bapi\b|\brest\b|\bgraphql\b", "Ao projetar APIs: documente endpoints (OpenAPI/Swagger), use status codes HTTP corretos e autenticação robusta."),
    (r"\bservidor\b|\bdeploy\b|\bdeployments\b", "Deploy: automatize com CI/CD, realize deploys em ambientes de staging antes da produção e monitore após release.")
]

DEFAULT_TI_REPLY = "Posso responder só sobre assuntos de TI. Pergunte algo sobre programação, redes, servidores, bancos de dados, Docker, Git, Linux, nuvem, etc."

def match_ti_response(message: str) -> str:
    msg = message.lower()
    for pattern, reply in TI_RESPONSES:
        if re.search(pattern, msg):
            return reply
    return None

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login - ChatTI")
        self.geometry("360x220")
        self.resizable(False, False)
        self.eval('tk::PlaceWindow . center')
        self.configure(padx=16, pady=12, bg=THEMES["light"]["bg"])
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        title = tk.Label(self, text="ChatTI - Acesso", font=("Segoe UI", 16, "bold"), bg=THEMES["light"]["bg"], fg=THEMES["light"]["text"])
        title.pack(pady=(4, 12))
        frm = tk.Frame(self, bg=THEMES["light"]["bg"])
        frm.pack(fill="x", padx=8)
        lbl_user = tk.Label(frm, text="Usuário:", anchor="w", bg=THEMES["light"]["bg"])
        lbl_user.pack(fill="x")
        ent_user = tk.Entry(frm, textvariable=self.username_var)
        ent_user.pack(fill="x", pady=(0, 8))
        lbl_pass = tk.Label(frm, text="Senha:", anchor="w", bg=THEMES["light"]["bg"])
        lbl_pass.pack(fill="x")
        ent_pass = tk.Entry(frm, textvariable=self.password_var, show="*")
        ent_pass.pack(fill="x", pady=(0, 8))
        btn_frame = tk.Frame(self, bg=THEMES["light"]["bg"])
        btn_frame.pack(pady=(8,0))
        btn_login = tk.Button(btn_frame, text="Entrar", width=10, command=self.try_login)
        btn_login.grid(row=0, column=0, padx=6)
        btn_quit = tk.Button(btn_frame, text="Sair", width=10, command=self.destroy)
        btn_quit.grid(row=0, column=1, padx=6)
        self.bind("<Return>", lambda e: self.try_login())

    def try_login(self):
        user = self.username_var.get().strip()
        pwd = self.password_var.get().strip()
        if user == VALID_USERNAME and pwd == VALID_PASSWORD:
            self.withdraw()
            MainChatWindow(username=user, user_icon="🧑‍💻").mainloop()
            self.destroy()
        else:
            messagebox.showerror("Erro de autenticação", "Usuário ou senha inválidos.")

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas = canvas

class MainChatWindow(tk.Tk):
    def __init__(self, username: str, user_icon: str = "🙂"):
        super().__init__()
        self.title("ChatTI - Conversa")
        self.geometry("760x600")
        self.minsize(640, 480)
        self.username = username
        self.user_icon = user_icon
        self.chatbot_name = "ChatTI"
        self.chatbot_icon = "🤖"
        self.theme = "light"
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.container = tk.Frame(self, bg=THEMES[self.theme]["bg"])
        self.container.grid(sticky="nsew")
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(1, weight=1)
        self._build_header()
        self._build_chat_area()
        self._build_input_area()
        self.apply_theme()
        self.input_entry.focus_set()

    def _build_header(self):
        header = tk.Frame(self.container, height=54, bg=THEMES[self.theme]["bg"])
        header.grid(row=0, column=0, sticky="ew", pady=(6,6))
        header.columnconfigure(0, weight=1)
        title = tk.Label(header, text=f"Bem-vindo, {self.username}!", font=("Segoe UI", 14, "bold"), bg=THEMES[self.theme]["bg"])
        title.grid(row=0, column=0, sticky="w", padx=(12,0))
        btn_theme = tk.Button(header, text="Alternar Tema", command=self.toggle_theme, width=14)
        btn_theme.grid(row=0, column=1, padx=6)
        btn_clear = tk.Button(header, text="Limpar", command=self.clear_chat, width=10)
        btn_clear.grid(row=0, column=2, padx=6)
        self.header_widgets = {"title": title, "btn_theme": btn_theme, "btn_clear": btn_clear}

    def _build_chat_area(self):
        chat_frame = tk.Frame(self.container, bg=THEMES[self.theme]["bg"])
        chat_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0,12))
        chat_frame.rowconfigure(0, weight=1)
        chat_frame.columnconfigure(0, weight=1)
        self.scrollable = ScrollableFrame(chat_frame)
        self.scrollable.grid(row=0, column=0, sticky="nsew")
        self._after_id = None

    def _build_input_area(self):
        input_frame = tk.Frame(self.container, bg=THEMES[self.theme]["bg"])
        input_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(0,12))
        input_frame.columnconfigure(0, weight=1)
        self.input_entry = tk.Entry(input_frame, font=("Segoe UI", 11))
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0,8), ipady=6)
        self.input_entry.bind("<Return>", lambda e: self.on_send())
        send_btn = tk.Button(input_frame, text="Enviar", width=10, command=self.on_send)
        send_btn.grid(row=0, column=1, padx=(0,4))
        self.button_send = send_btn

    def add_message(self, who: str, icon: str, text: str, align="left"):
        msg_wrap = tk.Frame(self.scrollable.scrollable_frame, pady=6, padx=4, bg=THEMES[self.theme]["chat_bg"])
        content = tk.Frame(msg_wrap, bg=THEMES[self.theme]["chat_bg"])
        meta = tk.Frame(content, bg=THEMES[self.theme]["chat_bg"])
        lbl_icon = tk.Label(meta, text=icon, font=("Segoe UI Emoji", 14), bg=THEMES[self.theme]["chat_bg"])
        lbl_name = tk.Label(meta, text=f" {who}", font=("Segoe UI", 9, "bold"), bg=THEMES[self.theme]["chat_bg"], fg=THEMES[self.theme]["text"])
        lbl_icon.pack(side="left")
        lbl_name.pack(side="left")
        meta.pack(anchor="w", pady=(0,4))
        bubble_bg = THEMES[self.theme]["bot_bg"] if align == "left" else THEMES[self.theme]["user_bg"]
        fg = THEMES[self.theme]["text"]
        bubble = tk.Label(content, text=text, justify="left", anchor="w",
                          font=("Segoe UI", 10), wraplength=440, bd=0, padx=10, pady=8,
                          bg=bubble_bg, fg=fg)
        bubble.pack(fill="both", expand=True)
        content.pack()
        if align == "left":
            msg_wrap.pack(anchor="w", fill="x", padx=(6, 80))
        else:
            msg_wrap.pack(anchor="e", fill="x", padx=(80, 6))
        self.after(100, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        c = self.scrollable.canvas
        c.update_idletasks()
        c.yview_moveto(1.0)

    def on_send(self):
        text = self.input_entry.get().strip()
        if not text:
            return
        self.input_entry.delete(0, "end")
        self.add_message(self.username, self.user_icon, text, align="right")
        threading.Thread(target=self._simulate_bot_reply, args=(text,), daemon=True).start()

    def _simulate_bot_reply(self, user_text: str):
        typing_placeholder = f"{self.chatbot_icon} {self.chatbot_name} está digitando..."
        self._add_temporary_typing(typing_placeholder)
        time.sleep(0.9 + min(1.0, len(user_text) / 40))
        response = match_ti_response(user_text)
        if response is None:
            response = DEFAULT_TI_REPLY
        self._replace_temporary_with(response)

    def _add_temporary_typing(self, text):
        def _add():
            self._typing_widget = tk.Frame(self.scrollable.scrollable_frame, pady=6, padx=4, bg=THEMES[self.theme]["chat_bg"])
            content = tk.Frame(self._typing_widget, bg=THEMES[self.theme]["chat_bg"])
            meta = tk.Frame(content, bg=THEMES[self.theme]["chat_bg"])
            lbl_icon = tk.Label(meta, text=self.chatbot_icon, font=("Segoe UI Emoji", 14), bg=THEMES[self.theme]["chat_bg"])
            lbl_name = tk.Label(meta, text=f" {self.chatbot_name}", font=("Segoe UI", 9, "bold"), bg=THEMES[self.theme]["chat_bg"], fg=THEMES[self.theme]["text"])
            lbl_icon.pack(side="left")
            lbl_name.pack(side="left")
            meta.pack(anchor="w", pady=(0,4))
            bubble = tk.Label(content, text="digitando...", justify="left", anchor="w",
                              font=("Segoe UI", 10), wraplength=440, bd=0, padx=10, pady=8,
                              bg=THEMES[self.theme]["bot_bg"], fg=THEMES[self.theme]["text"])
            bubble.pack(fill="both", expand=True)
            content.pack()
            self._typing_widget.pack(anchor="w", fill="x", padx=(6, 80))
            self.scroll_to_bottom()
        self.after(0, _add)

    def _replace_temporary_with(self, final_text):
        def _replace():
            try:
                if hasattr(self, "_typing_widget") and self._typing_widget:
                    self._typing_widget.destroy()
                    self._typing_widget = None
            except Exception:
                pass
            self.add_message(self.chatbot_name, self.chatbot_icon, final_text, align="left")
        self.after(0, _replace)

    def clear_chat(self):
        for child in self.scrollable.scrollable_frame.winfo_children():
            child.destroy()

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme()

    def apply_theme(self):
        t = THEMES[self.theme]
        self.container.configure(bg=t["bg"])
        self.configure(bg=t["bg"])
        for name, widget in self.header_widgets.items():
            widget.configure(bg=t["bg"], fg=t["text"])
        self.scrollable.canvas.configure(bg=t["chat_bg"])
        self.scrollable.scrollable_frame.configure(style="Custom.TFrame")
        self.input_entry.configure(bg=t["input_bg"], fg=t["text"], insertbackground=t["text"])
        self.button_send.configure(bg=t["button_bg"])
        for child in self.scrollable.scrollable_frame.winfo_children():
            for sub in child.winfo_children():
                try:
                    sub.configure(bg=t["chat_bg"])
                except Exception:
                    pass
                for g in sub.winfo_children():
                    try:
                        txt = g.cget("text") if isinstance(g, tk.Label) else ""
                        if isinstance(g, tk.Label) and txt == "digitando...":
                            g.configure(bg=t["bot_bg"], fg=t["text"])
                        else:
                            g.configure(bg=t["chat_bg"], fg=t["text"])
                    except Exception:
                        pass
        self.update_idletasks()

if __name__ == "__main__":
    LoginWindow().mainloop()
