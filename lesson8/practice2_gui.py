import random
import tkinter as tk
from tkinter import messagebox


# ── 色彩主題 ──────────────────────────────────────────
BG_DARK   = "#1a1a2e"
BG_MID    = "#16213e"
BG_CARD   = "#0f3460"
ACCENT    = "#e94560"
ACCENT_HL = "#ff6b81"
TEXT_WHITE = "#eaeaea"
TEXT_GRAY  = "#a0a0b0"
BTN_BG    = "#e94560"
BTN_HOVER  = "#ff6b81"
SUCCESS   = "#2ecc71"
WARN_UP   = "#e67e22"
WARN_DOWN  = "#3498db"

FONT_TITLE  = ("Microsoft JhengHei", 22, "bold")
FONT_SUB    = ("Microsoft JhengHei", 11)
FONT_LABEL  = ("Microsoft JhengHei", 12)
FONT_ENTRY  = ("Consolas", 16)
FONT_BTN    = ("Microsoft JhengHei", 12, "bold")
FONT_MSG    = ("Microsoft JhengHei", 13, "bold")
FONT_HIST   = ("Consolas", 11)
FONT_SMALL  = ("Microsoft JhengHei", 9)


class RoundedFrame(tk.Canvas):
    """用 Canvas 畫出圓角矩形當背景卡片"""
    def __init__(self, parent, width, height, radius=20, **kw):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, **kw)
        self._draw(radius, width, height)

    def _draw(self, r, w, h):
        self.create_arc(0, 0, 2 * r, 2 * r, start=90, extent=90, fill=BG_CARD, outline="")
        self.create_arc(w - 2 * r, 0, w, 2 * r, start=0, extent=90, fill=BG_CARD, outline="")
        self.create_arc(0, h - 2 * r, 2 * r, h, start=180, extent=90, fill=BG_CARD, outline="")
        self.create_arc(w - 2 * r, h - 2 * r, w, h, start=270, extent=90, fill=BG_CARD, outline="")
        self.create_rectangle(r, 0, w - r, h, fill=BG_CARD, outline="")
        self.create_rectangle(0, r, w, h - r, fill=BG_CARD, outline="")


class GuessGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("猜數字遊戲")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        self.target = random.randint(1, 100)
        self.low = 1
        self.high = 100
        self.attempts = 0
        self.history = []

        # ── 主容器 ────────────────────────────────
        main = tk.Frame(root, bg=BG_DARK, padx=25, pady=20)
        main.pack(fill=tk.BOTH, expand=True)

        # ── 標題區 ────────────────────────────────
        tk.Label(main, text="🎯 猜數字遊戲", font=FONT_TITLE,
                 bg=BG_DARK, fg=TEXT_WHITE).pack(pady=(0, 2))
        tk.Label(main, text="1 ~ 100 之間的神祕數字，你能幾次猜中？",
                 font=FONT_SUB, bg=BG_DARK, fg=TEXT_GRAY).pack(pady=(0, 15))

        # ── 範圍視覺化（進度條）──────────────────
        bar_frame = tk.Frame(main, bg=BG_DARK)
        bar_frame.pack(fill=tk.X, pady=(0, 5))
        self.bar_canvas = tk.Canvas(bar_frame, height=28, bg="#2a2a4a",
                                    highlightthickness=0, bd=0)
        self.bar_canvas.pack(fill=tk.X)
        self._draw_bar()

        self.range_label = tk.Label(
            main, text=f"目前範圍：{self.low} ~ {self.high}",
            font=("Microsoft JhengHei", 11), bg=BG_DARK, fg=TEXT_GRAY,
        )
        self.range_label.pack(pady=(2, 12))

        # ── 輸入卡片 ──────────────────────────────
        card = RoundedFrame(main, 380, 70, radius=16, bg=BG_DARK)
        card.pack(pady=(0, 5))
        card_inner = tk.Frame(card, bg=BG_CARD)
        card_inner.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.92, relheight=0.78)

        tk.Label(card_inner, text="輸入數字：", font=FONT_LABEL,
                 bg=BG_CARD, fg=TEXT_GRAY).pack(side=tk.LEFT, padx=(8, 4))

        self.entry = tk.Entry(card_inner, font=FONT_ENTRY, width=6,
                              bg="#1a1a3e", fg=TEXT_WHITE, insertbackground=TEXT_WHITE,
                              relief=tk.FLAT, bd=4, justify=tk.CENTER)
        self.entry.pack(side=tk.LEFT, padx=4)
        self.entry.bind("<Return>", lambda e: self.make_guess())
        self.entry.focus_set()

        self.guess_btn = tk.Button(
            card_inner, text="猜！", font=FONT_BTN, bg=BTN_BG, fg="white",
            activebackground=BTN_HOVER, activeforeground="white",
            relief=tk.FLAT, bd=0, padx=18, pady=4,
            cursor="hand2", command=self.make_guess,
        )
        self.guess_btn.pack(side=tk.LEFT, padx=8)
        self._bind_hover(self.guess_btn, BTN_BG, BTN_HOVER)

        # ── 訊息區 ────────────────────────────────
        self.message_label = tk.Label(
            main, text="", font=FONT_MSG, bg=BG_DARK, fg=TEXT_WHITE, width=32,
        )
        self.message_label.pack(pady=(8, 8))

        # ── 猜測紀錄 ──────────────────────────────
        hist_header = tk.Frame(main, bg=BG_DARK)
        hist_header.pack(fill=tk.X, padx=2)
        tk.Label(hist_header, text="📋 猜測紀錄", font=("Microsoft JhengHei", 10, "bold"),
                 bg=BG_DARK, fg=TEXT_GRAY).pack(side=tk.LEFT)
        self.attempts_label = tk.Label(
            hist_header, text="共 0 次", font=FONT_SMALL, bg=BG_DARK, fg=TEXT_GRAY,
        )
        self.attempts_label.pack(side=tk.RIGHT)

        list_frame = tk.Frame(main, bg="#0d1b3e", bd=0, highlightthickness=1,
                              highlightbackground="#2a2a5a")
        list_frame.pack(fill=tk.X, pady=(4, 12))

        self.history_listbox = tk.Listbox(
            list_frame, font=FONT_HIST, bg="#0d1b3e", fg=TEXT_GRAY,
            selectbackground=BG_CARD, selectforeground=TEXT_WHITE,
            activestyle="none", bd=0, highlightthickness=0,
            height=6,
        )
        self.history_listbox.pack(fill=tk.X)

        # ── 按鈕列 ────────────────────────────────
        btn_frame = tk.Frame(main, bg=BG_DARK)
        btn_frame.pack(fill=tk.X)

        self.restart_btn = tk.Button(
            btn_frame, text="🔄  重新開始", font=("Microsoft JhengHei", 11),
            bg="#2a2a4a", fg=TEXT_WHITE, activebackground="#3a3a5a",
            activeforeground=TEXT_WHITE, relief=tk.FLAT, bd=0,
            padx=20, pady=6, cursor="hand2", command=self.restart,
        )
        self.restart_btn.pack(side=tk.RIGHT)
        self._bind_hover(self.restart_btn, "#2a2a4a", "#3a3a5a")

        self.hint_btn = tk.Button(
            btn_frame, text="💡 提示", font=("Microsoft JhengHei", 11),
            bg="#2a2a4a", fg=TEXT_WHITE, activebackground="#3a3a5a",
            activeforeground=TEXT_WHITE, relief=tk.FLAT, bd=0,
            padx=20, pady=6, cursor="hand2", command=self.show_hint,
        )
        self.hint_btn.pack(side=tk.RIGHT, padx=(0, 8))
        self._bind_hover(self.hint_btn, "#2a2a4a", "#3a3a5a")

        self._center_window(420, 530)
        self.root.after(50, self._draw_bar)

    # ── 範圍進度條 ──────────────────────────────────
    def _draw_bar(self):
        c = self.bar_canvas
        c.delete("all")
        w = c.winfo_width() or 370
        h = 28
        pad = 4

        # 背景軌道
        c.create_rectangle(pad, pad, w - pad, h - pad, fill="#2a2a4a", outline="", width=0)

        # 已排除的左側（深色）
        total = 100
        x_low = pad + (self.low - 1) / total * (w - 2 * pad)
        x_high = pad + self.high / total * (w - 2 * pad)

        if x_low > pad:
            c.create_rectangle(pad, pad, x_low, h - pad, fill="#111128", outline="")
        if x_high < w - pad:
            c.create_rectangle(x_high, pad, w - pad, h - pad, fill="#111128", outline="")

        # 目前範圍（亮色）
        bar_color = SUCCESS if self.low == self.high else ACCENT
        c.create_rectangle(x_low, pad, x_high, h - pad, fill=bar_color, outline="")

        # 邊界標記
        c.create_text(x_low + 2, h // 2, anchor=tk.W, text=str(self.low),
                       fill=TEXT_WHITE, font=("Consolas", 8))
        if self.high != self.low:
            c.create_text(x_high - 2, h // 2, anchor=tk.E, text=str(self.high),
                           fill=TEXT_WHITE, font=("Consolas", 8))

    # ── 滑鼠懸停效果 ────────────────────────────────
    def _bind_hover(self, widget, normal_color, hover_color):
        def enter(e):
            if str(widget["state"]) != "disabled":
                widget.configure(bg=hover_color)
        def leave(e):
            if str(widget["state"]) != "disabled":
                widget.configure(bg=normal_color)
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    # ── 視窗置中 ────────────────────────────────────
    def _center_window(self, w, h):
        sx = self.root.winfo_screenwidth()
        sy = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sx - w) // 2}+{(sy - h) // 2}")

    # ── 提示功能 ────────────────────────────────────
    def show_hint(self):
        remaining = self.high - self.low + 1
        if remaining <= 1:
            return
        parity = "偶數" if self.target % 2 == 0 else "奇數"
        half = (self.low + self.high) // 2
        hint = f"提示：答案是{parity}"
        if self.target <= half:
            hint += f"，且在 {self.low} ~ {half} 之間"
        else:
            hint += f"，且在 {half + 1} ~ {self.high} 之間"
        messagebox.showinfo("💡 提示", hint)

    # ── 猜測邏輯 ────────────────────────────────────
    def make_guess(self):
        text = self.entry.get().strip()
        if not text:
            return

        try:
            guess = int(text)
        except ValueError:
            messagebox.showwarning("輸入錯誤", "請輸入有效整數！")
            self.entry.delete(0, tk.END)
            return

        if guess < self.low or guess > self.high:
            messagebox.showwarning("超出範圍", f"請輸入 {self.low} ~ {self.high} 之間的數字")
            self.entry.delete(0, tk.END)
            return

        self.attempts += 1
        self.entry.delete(0, tk.END)

        if guess == self.target:
            self._record_guess(guess, "✅ 正確！", SUCCESS)
            self.message_label.config(
                text=f"🎉 恭喜！答案就是 {self.target}", fg=SUCCESS,
            )
            messagebox.showinfo("🎉 恭喜", f"答案就是 {self.target}\n你總共猜了 {self.attempts} 次")
            self.entry.config(state=tk.DISABLED)
            self.guess_btn.config(state=tk.DISABLED, bg="#555")
        elif guess < self.target:
            self.low = guess + 1
            self._record_guess(guess, "⬆ 太小了", WARN_DOWN)
            self.message_label.config(
                text=f"再大一點！範圍 → {self.low} ~ {self.high}", fg=WARN_DOWN,
            )
        else:
            self.high = guess - 1
            self._record_guess(guess, "⬇ 太大了", WARN_UP)
            self.message_label.config(
                text=f"再小一點！範圍 → {self.low} ~ {self.high}", fg=WARN_UP,
            )

        self.range_label.config(text=f"目前範圍：{self.low} ~ {self.high}")
        self.attempts_label.config(text=f"共 {self.attempts} 次")
        self._draw_bar()
        self.history_listbox.see(tk.END)
        self.entry.focus_set()

    def _record_guess(self, guess, result, color):
        entry = f"  #{self.attempts:<3d}  猜 {guess:<4d}  {result}"
        self.history_listbox.insert(tk.END, entry)
        self.history_listbox.itemconfig(tk.END, fg=color)

    # ── 重新開始 ────────────────────────────────────
    def restart(self):
        self.target = random.randint(1, 100)
        self.low, self.high = 1, 100
        self.attempts = 0

        self.entry.config(state=tk.NORMAL)
        self.entry.delete(0, tk.END)
        self.guess_btn.config(state=tk.NORMAL, bg=BTN_BG)
        self.range_label.config(text=f"目前範圍：{self.low} ~ {self.high}")
        self.attempts_label.config(text="共 0 次")
        self.message_label.config(text="", fg=TEXT_WHITE)
        self.history_listbox.delete(0, tk.END)
        self._draw_bar()
        self.entry.focus_set()


if __name__ == "__main__":
    root = tk.Tk()
    app = GuessGameGUI(root)
    root.mainloop()
