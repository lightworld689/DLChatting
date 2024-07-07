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
        await asyncio.gather(*tasks, return_exceptions=True)

# 处理每个客户端连接
async def handle_client(websocket, path):
    username = path.strip('/')
    clients.add(websocket)
    try:
        join_message = f"{username} 加入了聊天室"
        await broadcast_message(f"\033[32m系统: {join_message}\033[0m")
        save_message("系统", join_message)
        async for message in websocket:
            formatted_message = f"{username}: {message}"
            print(formatted_message)
            save_message(username, message)
            await broadcast_message(formatted_message)
    except websockets.ConnectionClosedError:
        print(f"{username} 断开连接")
    except Exception as e:
        print(f"连接处理失败: {e}")
    finally:
        clients.remove(websocket)
        leave_message = f"{username} 退出了聊天室"
        await broadcast_message(f"\033[33m系统: {leave_message}\033[0m")  # 改为橙色
        save_message("系统", leave_message)

# 启动WebSocket服务器
async def main():
    init_db()
    async with websockets.serve(handle_client, "localhost", 8765):
        await asyncio.Future()  # 保持服务器运行

if __name__ == "__main__":
    asyncio.run(main())
