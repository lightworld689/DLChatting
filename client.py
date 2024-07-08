import tkinter as tk
from tkinter import scrolledtext, messagebox
import asyncio
import websockets
import threading
import sqlite3
import time
from datetime import datetime

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.username = None
        self.websocket = None
        self.loop = None
        self.create_login_window()

    def create_login_window(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("登录")
        self.login_window.geometry("300x100")

        tk.Label(self.login_window, text="请输入用户名:").pack(pady=10)
        self.username_entry = tk.Entry(self.login_window)
        self.username_entry.pack(pady=5)
        self.username_entry.bind("<Return>", self.on_login)

    def on_login(self, event):
        self.username = self.username_entry.get()
        if self.username:
            self.login_window.destroy()
            self.create_chat_window()
            threading.Thread(target=self.run_event_loop).start()

    def create_chat_window(self):
        self.root.title(f"欢迎使用DLChatting - {self.username}")
        self.root.geometry("400x500")

        self.chat_text = scrolledtext.ScrolledText(self.root, state='disabled')
        self.chat_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.chat_text.tag_configure("green", foreground="green")
        self.chat_text.tag_configure("orange", foreground="orange")

        self.message_entry = tk.Text(self.root, height=3)
        self.message_entry.pack(padx=10, pady=10, fill=tk.X)
        self.message_entry.bind("<Return>", self.on_send_message)
        self.message_entry.bind("<Shift-Return>", self.on_newline)

        self.load_history()

    def load_history(self):
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username, message FROM (SELECT * FROM messages ORDER BY timestamp DESC LIMIT 20) ORDER BY timestamp')
        rows = cursor.fetchall()
        conn.close()

        self.chat_text.config(state='normal')
        for row in rows:
            message = f"{row[1]}"
            color = None
            if row[0] == "系统":
                if "加入了聊天室" in row[1]:
                    color = "green"
                elif "退出了聊天室" in row[1]:
                    color = "orange"
            self.insert_message(message, color)
        self.insert_message(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 系统: ---以上是历史记录", "green")
        self.chat_text.config(state='disabled')

    def on_send_message(self, event):
        message = self.message_entry.get("1.0", tk.END).strip()
        if message:
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
            self.message_entry.delete("1.0", tk.END)
        return "break"

    def on_newline(self, event):
        self.message_entry.insert(tk.INSERT, "\n")
        return "break"

    async def send_message(self, message):
        await self.websocket.send(message)

    def insert_message(self, message, color=None):
        self.chat_text.config(state='normal')
        if color:
            self.chat_text.insert(tk.END, message + "\n", color)
        else:
            self.chat_text.insert(tk.END, message + "\n")
        self.chat_text.config(state='disabled')
        self.chat_text.yview(tk.END)

    async def receive_messages(self):
        try:
            async for message in self.websocket:
                color = None
                if message.startswith("\033[32m") and message.endswith("\033[0m"):
                    message = message[5:-4]
                    color = "green"
                elif message.startswith("\033[33m") and message.endswith("\033[0m"):
                    message = message[5:-4]
                    color = "orange"
                self.insert_message(message, color)
        except websockets.ConnectionClosed:
            self.handle_disconnection()

    async def connect(self):
        uri = f"ws://localhost:8765/{self.username}"
        self.websocket = await websockets.connect(uri)
        await self.receive_messages()

    def run_event_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect())

    def handle_disconnection(self):
        for i in range(1, 6):
            reconnect_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 系统: 掉线了！正在重新连接……（{i}/5）"
            self.insert_message(reconnect_message, "orange")
            time.sleep(1)
            try:
                asyncio.run(self.connect())
                return
            except:
                continue

        messagebox.showerror("连接错误", "从服务器断开连接")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
