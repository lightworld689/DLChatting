# DLChatting

### 一种基于 python + ws 的局域网Chat方法

---

### 前言

有的时候要在内网/同机不同用户传递消息，其他平台部署困难，就做了这个。

---

### 使用方法

安装requirements

```bash
pip install -r requirements.txt
```

在服务端输入

```bash
python server.py
```

要连接的客户端先打开client.py调整设置

```python
NotifyOnMessage = True  # 默认开启消息通知
TrustUserMode = False  # 不要开启这个，自用
```

然后输入

```bash
python client.py
```

即可连接！

注意：如果您打算在客户端连接非localhost的服务器，也就是在不同的电脑连接，需自行在源代码进行修改，后期会添加设置进行修改。

```python
    async def connect(self):
        uri = f"ws://localhost:8765/{self.username}"
        self.websocket = await websockets.connect(uri)
        await self.receive_messages()
```

### 关于

如果您喜欢它，请给我一个免费的 ![Star](https://img.shields.io/github/stars/lightworld689/DLChatting.svg) ！有任何问题请给我提交 Issues 或者 PR 。

offical site: dqjl.eu.org , lr689.eu.org

contact me at light689@163.com or bilibili 灯确吉L

Github: https://github.com/lightworld689
