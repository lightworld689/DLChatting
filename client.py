import tkinter as tk
from tkinter import scrolledtext, messagebox
import asyncio
import websockets
import threading
import time
import os
import re
from datetime import datetime
from plyer import notification

NotifyOnMessage = True  # 默认开启消息通知
TrustUserMode = False  # 不要开启这个，自用

class ChatClient:
    def __init__(self, root):
        self.root = root # 窗口
        self.username = None # 用户名
        self.websocket = None # websocket
        self.loop = None # 事件循环
        self.is_receiving_history = False # 是否正在接收历史消息
        self.last_sent_message = None  # 用于存储最后发送的消息
        
        if TrustUserMode:
            self.username = os.getlogin()
            self.create_chat_window()
            threading.Thread(target=self.run_event_loop).start()
        else:
            self.create_login_window()

    def create_login_window(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("登录")
        self.login_window.geometry("300x100")

        tk.Label(self.login_window, text="请输入用户名:").pack(pady=10)
        self.username_entry = tk.Entry(self.login_window)
        self.username_entry.pack(pady=5)
        self.username_entry.bind("<Return>", self.on_login)

    def on_login(self, event=None):
        self.username = self.username_entry.get()
        if self.username:
            # 用户名是否符合要求
            if not re.match(r'^[a-zA-Z0-9_]{3,20}$', self.username):
                messagebox.showerror("用户名错误", "用户名只能包含26字母、数字及下划线（_），且长度必须为3~20")
                return
            self.login_window.destroy()
            self.create_chat_window()
            threading.Thread(target=self.run_event_loop).start()

    def create_chat_window(self):
        self.root.title(f"欢迎使用DLChatting客户端 - {self.username}")
        self.root.geometry("400x500")

        self.chat_text = scrolledtext.ScrolledText(self.root, state='disabled')
        self.chat_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.chat_text.tag_configure("green", foreground="green")
        self.chat_text.tag_configure("orange", foreground="orange")

        self.message_entry = tk.Text(self.root, height=3)
        self.message_entry.pack(padx=10, pady=10, fill=tk.X)
        self.message_entry.bind("<Return>", self.on_send_message)
        self.message_entry.bind("<Shift-Return>", self.on_newline)

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
        self.last_sent_message = message  # 记录最后发送的消息
        await self.websocket.send(message)

    def insert_message(self, message, color=None, notify=True):
        self.chat_text.config(state='normal')
        if color:
            self.chat_text.insert(tk.END, message + "\n", color)
        else:
            self.chat_text.insert(tk.END, message + "\n")
        self.chat_text.config(state='disabled')
        self.chat_text.yview(tk.END)

        # 改进的检测逻辑：检查是否为自己发送的最后一条消息
        is_own_message = False
        if self.last_sent_message:
            # 提取消息内容（去除时间戳和用户名）
            message_content = re.search(r'\] .*?: (.+)$', message)
            if message_content:
                message_content = message_content.group(1)
                is_own_message = message_content == self.last_sent_message

        # 历史记录不弹窗，自己发的消息不弹窗，且不弹窗消息为“---以上是历史记录---”
        if NotifyOnMessage and notify and not self.is_receiving_history and not is_own_message and message != "---以上是历史记录---":
            self.show_notification(message)

        # 重置最后发送的消息
        if is_own_message:
            self.last_sent_message = None

    def show_notification(self, message):
        notification.notify(
            title="新消息",
            message=message,
            timeout=2
        )

    async def receive_messages(self):
        try:
            self.is_receiving_history = True
            async for message in self.websocket:
                color = None
                if message.startswith("\033[32m") and message.endswith("\033[0m"):
                    message = message[5:-4]
                    color = "green"
                elif message.startswith("\033[33m") and message.endswith("\033[0m"):
                    message = message[5:-4]
                    color = "orange"
                
                # 检查是否是历史记录的结束标志
                if "---以上是历史记录---" in message:
                    self.is_receiving_history = False

                notify = not self.is_receiving_history
                self.insert_message(message, color, notify)
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
        while True:
            reconnect_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [√] 系统: 掉线了！正在重新连接……"
            self.insert_message(reconnect_message, "orange", notify=False)
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