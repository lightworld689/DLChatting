# DLChatting

### 一种基于 Python + WebSocket 的局域网聊天方法

---

### 前言

在某些情况下，需要在局域网内或同一台机器的不同用户之间传递消息，而其他平台的部署较为困难，因此开发了这个基于 Python 和 WebSocket 的聊天工具。

---

### 使用方法

#### 安装依赖

首先，安装所需的依赖包：

```bash
pip install -r requirements.txt
```

#### 启动服务器

在服务器端输入以下命令启动服务器：

```bash
python server.py
```

#### 配置客户端

要连接的客户端需要先打开 `client.py` 调整设置：

```python
NotifyOnMessage = True  # 默认开启消息通知
TrustUserMode = False  # 不要开启这个，自用
```

然后输入以下命令启动客户端：

```bash
python client.py
```

即可连接！

**注意**：如果您打算在客户端连接非 `localhost` 的服务器，也就是在不同的电脑连接，需自行在源代码进行修改，后期会添加设置进行修改。

```python
    async def connect(self):
        uri = f"ws://localhost:8765/{self.username}"
        self.websocket = await websockets.connect(uri)
        await self.receive_messages()
```

### 如何实现？

#### 服务器端

服务器端使用 `websockets` 库来创建一个 WebSocket 服务器，监听指定的端口（例如 8765）。服务器处理客户端的连接请求，并负责转发消息。

#### 客户端

客户端同样使用 `websockets` 库来连接服务器。客户端可以发送消息到服务器，并接收来自其他客户端的消息。

### 关于

如果您喜欢它，请给我一个免费的 ![Star](https://img.shields.io/github/stars/lightworld689/DLChatting.svg) ！有任何问题请给我提交 Issues 或者 PR 。

官方网站: dqjl.eu.org , lr689.eu.org

联系我: light689@163.com 或 bilibili 灯确吉L

Github: https://github.com/lightworld689

