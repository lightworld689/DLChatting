import sqlite3
import asyncio
import websockets
import re
from datetime import datetime

clients = set()

def init_db():
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_message(username, message):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (username, message) VALUES (?, ?)', (username, message))
    conn.commit()
    conn.close()

async def broadcast_message(message):
    if clients:
        tasks = [client.send(message) for client in clients]
        await asyncio.gather(*tasks, return_exceptions=True)

async def handle_client(websocket, path):
    username = path.strip('/')
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        error_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 系统: 用户名只能包含26字母、数字及下划线（_）"
        await websocket.send(f"\033[33m{error_message}\033[0m")
        await websocket.close()
        return

    clients.add(websocket)
    try:
        join_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 系统: {username} 加入了聊天室"
        await broadcast_message(f"\033[32m{join_message}\033[0m")
        save_message("系统", join_message)
        async for message in websocket:
            formatted_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {username}: {message}"
            print(formatted_message)
            save_message(username, formatted_message)
            await broadcast_message(formatted_message)
    except websockets.ConnectionClosedError:
        print(f"{username} 断开连接")
    except Exception as e:
        print(f"连接处理失败: {e}")
    finally:
        clients.remove(websocket)
        leave_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 系统: {username} 退出了聊天室"
        await broadcast_message(f"\033[33m{leave_message}\033[0m")
        save_message("系统", leave_message)

async def main():
    init_db()
    async with websockets.serve(handle_client, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
