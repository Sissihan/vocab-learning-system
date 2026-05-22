# VocabFusion — 情境感知词根-语义融合词汇学习系统

面向远程教育碎片化场景的智能词汇学习学术研究演示原型。

## 核心特性

- **双通道推荐引擎**: `Score = α × R_sim + (1-α) × S_sim`
  - R_sim: 知识图谱最短路径形态关联
  - S_sim: 词向量余弦语义相似度
  - α: 规则引擎动态调节（初学侧重形态，熟练侧重语义）
- **情境感知**: 通勤 / 专注 / 碎片化 / 复习 四类场景适配
- **游戏化**: 词根拼图、语义连线、词汇星球
- **知识追踪**: 简化 DKT + 五维学习者画像
- **内容生成**: 基于词根知识图谱的 RAG 约束例句生成

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.10+, FastAPI, SQLAlchemy |
| 前端 | Next.js 14, React 18, TypeScript |
| 数据库 | SQLite（JSON 字段存储嵌入向量与画像） |

## 环境要求

- Python 3.10+
- Node.js 18+（含 npm）
- 默认端口：后端 **8000**，前端 **3000**

## 运维脚本（项目根目录）

| 平台 | 启动 | 停止 | 状态 |
|------|------|------|------|
| Windows | `start.bat` | `stop.bat` | `status.bat` |
| Linux / macOS | `./start.sh` | `./stop.sh` | `./status.sh` |

首次在 Unix 上请执行：`chmod +x start.sh stop.sh status.sh scripts/check_system.sh`

**系统健康检查**（venv、数据库、导入；服务已启动时含 API 冒烟）：

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File scripts/check_system.ps1
```

```bash
# Linux / macOS
./scripts/check_system.sh
```

完整操作流程、排错与功能说明见 **[docs/OPERATIONS.md](docs/OPERATIONS.md)**。

## 快速启动

### Windows

```bat
start.bat
```

停止与查看状态：`stop.bat`、`status.bat`

### Linux / macOS

```bash
chmod +x start.sh stop.sh status.sh
./start.sh
```

停止与查看状态：`./stop.sh`、`./status.sh`

### 手动启动

**后端:**

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Unix: source venv/bin/activate
pip install -r requirements.txt
python scripts/seed_data.py
python run.py
```

**前端:**

```bash
cd frontend
npm install
npm run dev
```

访问:

- 前端: http://localhost:3000
- API 文档: http://localhost:8000/docs
- 演示账号: `demo` / `demo123`

## 项目结构

```
vocab-learning-system/
├── start.bat / start.sh      # 启动
├── stop.bat  / stop.sh       # 停止
├── status.bat / status.sh    # 运行状态
├── scripts/
│   ├── check_system.ps1      # Windows 健康检查
│   └── check_system.sh       # Unix 健康检查
├── backend/
│   ├── app/
│   │   ├── api/          # REST 端点
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/      # Pydantic 模式
│   │   ├── services/     # 推荐、DKT、情境、游戏、内容
│   │   ├── utils/        # JWT、JSON 工具
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── scripts/
│   │   ├── init_db.py
│   │   ├── seed_data.py  # 25 词根 + 110 词汇
│   │   └── verify_api.py # API 冒烟测试
│   ├── data/             # SQLite（运行时生成）
│   └── requirements.txt
├── frontend/
│   └── src/app/          # 登录、仪表盘、学习、游戏、个人中心
├── docs/
│   └── OPERATIONS.md     # 操作手册
└── README.md
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login/json` | 登录 |
| GET | `/api/user/profile` | 获取画像 |
| PUT | `/api/user/profile` | 更新画像 |
| GET | `/api/recommend` | 个性化推荐 |
| POST | `/api/learning/record` | 记录学习行为 |
| GET | `/api/knowledge/status` | 知识状态 |
| GET | `/api/games/root-puzzle` | 词根拼图 |
| POST | `/api/games/root-puzzle/result` | 提交拼图结果 |
| GET | `/api/games/semantic-match` | 语义连线 |
| GET | `/api/games/word-planet` | 词汇星球 |
| GET | `/api/content/generate` | 生成学习内容 |
| GET | `/api/context/scenes` | 场景配置 |
| POST | `/api/context/infer` | 情境推断 |

## 多语言支持

系统支持 **简体中文** (`zh-CN`)、**English** (`en`)、**繁體中文** (`zh-TW`)。

- 前端：导航栏或登录页语言切换器；个人中心可保存偏好语言
- 后端：API 通过 `?lang=zh-CN|en|zh-TW` 或 `Accept-Language` 请求头返回对应语言的推荐说明、游戏文案、学习内容等

示例：

```
GET /api/recommend?scene_type=focus&lang=en
GET /api/content/generate?word_id=1&level=intermediate&lang=zh-TW
```

## 验证安装

1. 运行 `scripts/check_system.ps1` 或 `scripts/check_system.sh`
2. 启动后执行 `status.bat` / `./status.sh` 确认端口与 HTTP 正常
3. 后端目录下运行冒烟测试：

```bash
cd backend
venv\Scripts\python scripts\verify_api.py   # Windows
# source venv/bin/activate && python scripts/verify_api.py  # Linux/macOS
```

应输出全部 `[OK]` 检查项。

## 演示流程

1. 使用 `demo/demo123` 登录
2. 在**仪表盘**切换场景（通勤/专注/碎片化/复习），观察推荐词汇与 α 权重变化
3. 点击推荐词汇进入**学习**界面，查看词根分析与例句
4. 在**游戏**模块体验三种认知游戏
5. 在**个人中心**查看五维画像并调整学习偏好

## 算法说明

推荐得分计算示例（可在推荐列表 explanation 字段查看）:

```
Score = α × R_sim + (1-α) × S_sim - difficulty_penalty
```

α 由学习者水平、平均掌握度、形态能力、场景类型、近期正确率共同决定。

## 许可证

学术研究演示用途。
