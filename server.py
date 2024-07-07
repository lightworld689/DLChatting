# server.py

import sqlite3
import asyncio
import websockets

clients = set()

# 创建数据库连接并初始化表
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

# 保存消息到数据库
def save_message(username, message):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (username, message) VALUES (?, ?)', (username, message))
    conn.commit()
    conn.close()

# 广播消息给所有已连接的客户端
async def broadcast_message(message):
    if clients:
        tasks = [client.send(message) for client in clients]
        await asyncio.gather(*tasks)

# 处理每个客户端连接
async def handle_client(websocket, path):
    username = path.strip('/')
    clients.add(websocket)
    try:
        async for message in websocket:
            formatted_message = f"{username}: {message}"
            print(formatted_message)
            save_message(username, message)
            await broadcast_message(formatted_message)
    finally:
        clients.remove(websocket)

# 启动WebSocket服务器
async def main():
    init_db()
    async with websockets.serve(handle_client, "localhost", 8765):
        await asyncio.Future()  # 保持服务器运行

if __name__ == "__main__":
    asyncio.run(main())
