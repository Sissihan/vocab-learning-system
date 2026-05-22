# VocabFusion 操作手册

本文档说明系统的安装、启停、状态检查、日常运维与功能操作流程。适用于 Windows、Linux 与 macOS。

---

## 1. 环境要求

| 组件 | 版本要求 |
|------|----------|
| Python | 3.10+ |
| Node.js | 18+（含 npm） |
| 操作系统 | Windows 10+ / Linux / macOS |

默认端口：

| 服务 | 端口 | 说明 |
|------|------|------|
| 后端 API | 8000 | FastAPI + Uvicorn |
| 前端 Web | 3000 | Next.js 开发服务器 |

---

## 2. 一键脚本（项目根目录）

### Windows（`.bat`）

| 脚本 | 作用 |
|------|------|
| `start.bat` | 创建/激活虚拟环境、安装依赖、播种数据库，在新窗口启动后端与前端 |
| `stop.bat` | 结束占用 8000、3000 端口的进程，并关闭标题为 VocabFusion 的控制台窗口 |
| `status.bat` | 检查端口监听与 HTTP 健康状态 |

### Linux / macOS（`.sh`）

首次使用请赋予执行权限：

```bash
chmod +x start.sh stop.sh status.sh scripts/check_system.sh
```

| 脚本 | 作用 |
|------|------|
| `./start.sh` | 安装依赖、播种数据，后台启动后端与前端（PID 写入 `.pids/`） |
| `./stop.sh` | 按 PID 文件与端口停止服务 |
| `./status.sh` | 检查端口、PID 与 HTTP 可达性 |
| `scripts/check_system.sh` | 完整环境检查（venv、数据库、导入、可选 API 冒烟） |

### 系统健康检查

**Windows：**

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check_system.ps1
```

**Linux / macOS：**

```bash
./scripts/check_system.sh
```

检查项包括：虚拟环境、SQLite 数据库、后端模块导入、前端 `node_modules`；若服务已运行，还会调用 `verify_api.py` 做 API 冒烟测试。

---

## 3. 启动流程详解

### 3.1 自动启动（推荐）

**Windows：** 双击或在命令行执行 `start.bat`。

**Unix：** 在项目根目录执行 `./start.sh`，按 `Ctrl+C` 或执行 `./stop.sh` 停止。

启动后访问：

- 前端：http://localhost:3000
- API 文档：http://localhost:8000/docs
- 演示账号：`demo` / `demo123`

### 3.2 手动启动

**后端：**

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Unix:    source venv/bin/activate
pip install -r requirements.txt
python scripts/seed_data.py    # 首次或需重置数据时
python run.py
```

**前端（另开终端）：**

```bash
cd frontend
npm install
npm run dev
```

### 3.3 数据初始化

| 脚本 | 说明 |
|------|------|
| `backend/scripts/init_db.py` | 仅创建表结构 |
| `backend/scripts/seed_data.py` | 初始化表并导入 25 词根、110 词汇及演示用户 |

数据库文件：`backend/data/vocab.db`（运行时生成，已在 `.gitignore` 中忽略）。

---

## 4. 停止与状态检查

### 4.1 停止服务

- **Windows：** `stop.bat`
- **Unix：** `./stop.sh`

`start.bat` 在独立 `cmd` 窗口中运行服务；`stop.bat` 会通过端口与窗口标题一并清理。

### 4.2 查看运行状态

- **Windows：** `status.bat`
- **Unix：** `./status.sh`

正常输出示例：

- `Backend (port 8000): LISTENING` 且 `[OK] Backend API /health`
- `Frontend (port 3000): LISTENING` 且 `[OK] Frontend http://127.0.0.1:3000`

### 4.3 API 验证

后端运行时在 `backend` 目录执行：

```bash
# Windows
venv\Scripts\python scripts\verify_api.py

# Unix
source venv/bin/activate && python scripts/verify_api.py
```

全部项应显示 `[OK]`。

---

## 5. 功能操作流程（用户侧）

### 5.1 登录

1. 打开 http://localhost:3000
2. 使用演示账号 `demo` / `demo123`，或注册新账号
3. 可在登录页或导航栏切换语言（简体 / English / 繁體）

### 5.2 仪表盘（推荐与学习场景）

1. 登录后进入**仪表盘**
2. 切换场景：**通勤** / **专注** / **碎片化** / **复习**
3. 观察推荐列表中的词汇、`α` 权重与 `explanation` 说明
4. 点击推荐词汇进入学习页

### 5.3 学习页

1. 查看目标词释义、词根拆解、例句
2. 学习行为会经 `POST /api/learning/record` 记录，影响后续推荐与 DKT 画像

### 5.4 游戏模块

路径：**游戏**（`/games`）

| 游戏 | API | 操作 |
|------|-----|------|
| 词根拼图 | `GET /api/games/root-puzzle` | 选择正确词缀，提交 `POST .../result` |
| 语义连线 | `GET /api/games/semantic-match` | 配对词与释义，提交结果 |
| 词汇星球 | `GET /api/games/word-planet` | 浏览词根-词汇关系网络 |

### 5.5 个人中心

1. 查看五维学习者画像（掌握度、形态能力等）
2. 调整学习偏好与界面语言（`PUT /api/user/profile`）

### 5.6 多语言 API

请求时附加 `?lang=zh-CN|en|zh-TW` 或 `Accept-Language` 头，例如：

```
GET /api/recommend?scene_type=focus&lang=en
GET /api/content/generate?word_id=1&level=intermediate&lang=zh-TW
```

---

## 6. 运维与排错

### 6.1 端口被占用

**Windows：**

```bat
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

或执行 `stop.bat`。

**Unix：**

```bash
lsof -i :8000
kill <pid>
# 或
./stop.sh
```

### 6.2 后端无法导入 / 依赖缺失

```bash
cd backend
pip install -r requirements.txt
python -c "from app.main import app"
```

### 6.3 数据库损坏或需重置

```bash
cd backend
rm -f data/vocab.db    # Windows: del data\vocab.db
python scripts/seed_data.py
```

### 6.4 前端编译或依赖问题

```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

### 6.5 CORS 或 API 连不上

确认前端 `src/lib/api.ts` 中 API 基址为 `http://127.0.0.1:8000`（或环境变量配置），且后端已监听 `0.0.0.0:8000`。

---

## 7. 生产构建（可选）

开发环境使用 `npm run dev` 与 `python run.py`（热重载）。

生产部署建议：

```bash
# 前端
cd frontend && npm run build && npm run start   # 默认端口 3000

# 后端（无 reload）
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

需配置反向代理、HTTPS 与 `settings.cors_origins`。

---

## 8. 目录与脚本索引

```
vocab-learning-system/
├── start.bat / start.sh      # 启动
├── stop.bat  / stop.sh       # 停止
├── status.bat / status.sh    # 状态
├── scripts/
│   ├── check_system.ps1      # Windows 健康检查
│   └── check_system.sh       # Unix 健康检查
├── backend/
│   ├── run.py
│   ├── scripts/seed_data.py
│   └── scripts/verify_api.py
├── frontend/
│   └── src/app/              # 页面路由
└── docs/
    └── OPERATIONS.md         # 本手册
```

---

## 9. 快速检查清单

- [ ] `python --version` ≥ 3.10，`node --version` ≥ 18
- [ ] 执行 `check_system.ps1` 或 `check_system.sh` 无 `[FAIL]`
- [ ] `status.bat` / `status.sh` 显示后端、前端均为 LISTENING
- [ ] `verify_api.py` 全部 `[OK]`
- [ ] 浏览器可登录 `demo` / `demo123` 并完成仪表盘 → 学习 → 游戏流程

如有问题，请先运行健康检查脚本并将完整终端输出保存以便排查。
