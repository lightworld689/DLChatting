# client.py

import tkinter as tk
from tkinter import scrolledtext
import asyncio
import websockets
import threading
import sqlite3

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.username = None
        self.websocket = None
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
        self.root.title(f"欢迎使用 DLChatting ， - {self.username}")
        self.root.geometry("400x500")

        self.chat_text = scrolledtext.ScrolledText(self.root, state='disabled')
        self.chat_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.message_entry = tk.Text(self.root, height=3)
        self.message_entry.pack(padx=10, pady=10, fill=tk.X)
        self.message_entry.bind("<Return>", self.on_send_message)
        self.message_entry.bind("<Shift-Return>", self.on_newline)

        self.load_history()

    def load_history(self):
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username, message FROM messages ORDER BY timestamp')
        rows = cursor.fetchall()
        conn.close()

        self.chat_text.config(state='normal')
        for row in rows:
            self.chat_text.insert(tk.END, f"{row[0]}: {row[1]}\n")
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

    async def receive_messages(self):
        async for message in self.websocket:
            self.chat_text.config(state='normal')
            self.chat_text.insert(tk.END, message + "\n")
            self.chat_text.config(state='disabled')
            self.chat_text.yview(tk.END)

    async def connect(self):
        uri = f"ws://localhost:8765/{self.username}"
        self.websocket = await websockets.connect(uri)
        await self.receive_messages()

    def run_event_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect())

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
