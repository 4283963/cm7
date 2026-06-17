# 🏛️ 法律援助中心 AI 法律咨询系统

基于 **RAG (检索增强生成)** + **Milvus 向量数据库** + **大语言模型** 的智能法律咨询系统。

核心亮点：**所有法律分析均基于真实法条向量检索，防止 AI 编造法条。**

---

## ✨ 功能特性

### 前端 (React + Vite)
- 💬 **高交互引导式对话流**：引导当事人依次填写「纠纷类型 → 时间 → 地点 → 当事人 → 案情详情」
- 📋 **实时案情档案面板**：进度条可视化展示信息收集完成度
- 🎯 **快捷选项卡片**：纠纷类型、常见问题一键选择
- 📚 **法条引用展示**：每条回答标注引用的具体法律条文
- 🎨 **专业 UI 设计**：Tailwind CSS + Ant Design，适配法律援助中心专业场景

### 后端 (Python + FastAPI)
- 🧠 **多轮对话状态机**：精准引导案情信息采集
- 🔍 **RAG 检索增强**：向量化案情 → Milvus 相似度检索 → 召回真实法条
- 📐 **多维案情 Prompt 组装**：将口语化描述转化为结构化法律 Prompt
- 🤖 **多模型兼容**：支持 GPT-4o、Claude 3.5、及无密钥 Mock 模式
- 🔒 **法条引用约束**：系统 Prompt 严格限定仅可使用检索到的法条
- 📊 **法条管理 API**：支持插入、批量导入、搜索、统计

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (React)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐   │
│  │ 引导对话流  │  │ 案情档案栏 │  │ Markdown 消息渲染  │   │
│  └──────┬──────┘  └──────┬──────┘  └────────┬───────────┘   │
└─────────┼────────────────┼──────────────────┼───────────────┘
          │                │                  │
          └────────────────┼──────────────────┘
                           ▼
                ┌─────────────────────┐
                │   FastAPI 网关层    │
                └──────────┬──────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌──────────────────┐ ┌───────────┐ ┌──────────────────┐
│  对话状态管理     │ │ Prompt 组装│ │ LLM 代理服务     │
│  (6步引导流程)    │ │ (案情+法条)│ │ (GPT/Claude)     │
└──────────┬───────┘ └───────────┘ └─────────┬────────┘
           │                                  │
           ▼                                  │
    ┌──────────────────┐                     │
    │  Embedding 模块 │                     │
    │ (text2vec-chinese)│                    │
    └────────┬─────────┘                     │
             │                               │
             ▼                               ▼
     ┌─────────────────────┐    ┌──────────────────────┐
     │   Milvus 向量库     │    │   外部大模型 API     │
     │   (中国法律法条)    │    │   GPT / Claude       │
     └─────────────────────┘    └──────────────────────┘
            RAG 检索                           生成回答
```

---

## 📦 项目结构

```
cm7/
├── backend/                          # Python 后端
│   ├── app/
│   │   ├── core/                     # 核心配置
│   │   │   ├── config.py             # 设置管理
│   │   │   └── logging.py            # 日志
│   │   ├── rag/                      # RAG 检索模块
│   │   │   ├── embedding.py          # 中文向量化 (Sentence-Transformers)
│   │   │   └── milvus_store.py       # Milvus 向量存储 + 检索
│   │   ├── services/                 # 业务服务
│   │   │   ├── dialog_manager.py     # 对话状态机 (6步引导)
│   │   │   ├── prompt_builder.py     # 动态案情 Prompt 组装
│   │   │   ├── llm_service.py        # GPT/Claude/Mock 多模型代理
│   │   │   └── consulting_service.py # 核心咨询编排服务
│   │   ├── routers/                  # API 路由
│   │   │   ├── consulting.py         # 咨询接口 /chat /health
│   │   │   └── laws.py               # 法条管理 /insert /search /import
│   │   ├── schemas/                  # Pydantic 模型
│   │   └── main.py                   # FastAPI 入口
│   ├── data/
│   │   ├── seed_laws.json            # 70+ 条真实中国法律种子数据
│   │   └── init_milvus.py            # Milvus 初始化脚本
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                         # React 前端
│   ├── src/
│   │   ├── components/               # UI 组件
│   │   │   ├── Header.tsx
│   │   │   ├── CaseInfoPanel.tsx     # 案情档案侧边栏
│   │   │   ├── GuideQuestionCard.tsx # 引导提问卡片
│   │   │   ├── MessageBubble.tsx     # 消息气泡
│   │   │   ├── MessageList.tsx
│   │   │   └── ChatInput.tsx
│   │   ├── hooks/useChat.ts          # 聊天逻辑 Hook
│   │   ├── services/api.ts           # Axios API 层
│   │   ├── types/index.ts            # TypeScript 类型
│   │   └── styles/index.css          # Tailwind + Markdown 样式
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
│
└── README.md
```

---

## 🚀 快速开始

### 前置条件
- Python 3.10+
- Node.js 18+
- Milvus 向量数据库 (推荐 Docker 启动)
- 大模型 API Key（OpenAI / Anthropic，可选，未配置进入演示模式）

---

### 步骤 1：启动 Milvus 向量数据库

使用 Docker Compose 一键启动：

```bash
# 下载 Milvus 官方 compose 文件
wget https://github.com/milvus-io/milvus/releases/download/v2.4.6/milvus-standalone-docker-compose.yml -O docker-compose.yml

# 启动 Milvus
docker-compose up -d
```

确认 Milvus 启动成功：
- 端口 `19530` gRPC 端口
- 端口 `9091` Web UI (Attu)

---

### 步骤 2：启动后端服务

```bash
cd backend

# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 LLM API Key（可选）
vim .env

# 4. 初始化 Milvus 法条向量库（导入 70+ 条真实法条）
python data/init_milvus.py
# 清空重建：python data/init_milvus.py --drop

# 5. 启动 FastAPI 服务
cd app && uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

访问 `http://localhost:8000/docs` 查看 Swagger API 文档。

---

### 步骤 3：启动前端服务

```bash
cd frontend

# 1. 安装依赖
npm install
# 或使用 pnpm / yarn
pnpm install

# 2. 启动开发服务器
npm run dev
```

访问 `http://localhost:5173` 即可使用 AI 法律咨询系统。

---

## 🛠️ 核心模块说明

### 🎯 引导式对话流 (6步状态机)

| 步骤 | 收集内容 | 关键交互 |
|------|---------|---------|
| 1 | 纠纷类型 | 10类常见纠纷一键选择（劳动/合同/婚姻/交通等） |
| 2 | 事件时间 | 自由文本输入，自动存储 |
| 3 | 发生地点 | 地域信息，决定管辖地判断 |
| 4 | 当事人 | 各方关系描述（员工/公司/邻居/夫妻等） |
| 5 | 案情详情 | 详细经过 + 证据 + 诉求 |
| 6 | 完成 | 基于完整案情生成专业法律分析 |

### 🔍 RAG 法条检索流程

1. **案情组装**：将多轮对话的结构化案情拼接成查询文本
2. **向量化**：使用 `shibing624/text2vec-base-chinese` 中文 Embedding 模型（768维）
3. **相似度检索**：Milvus 余弦相似度检索 Top-5 最匹配法条
4. **阈值过滤**：相似度 < 0.5 的法条自动丢弃
5. **Prompt 注入**：法条原文连同相似度评分注入 System Prompt

### 🛡️ 防编法条机制

System Prompt 中明确规定：
> - 所有法律引用必须来源于下方【检索法条上下文】部分
> - 不得引用、编造上下文以外的任何法条内容
> - 如法条不足，必须如实告知，不得臆造

前端每条回答会显示 **引用法条列表**（蓝色标签），用户可验证。

---

## 📚 种子法条覆盖范围

内置 70+ 条高频使用的中国法律条文，覆盖：

- 《劳动法》《劳动合同法》：工资、加班、辞退、经济补偿金
- 《民法典》：合同、婚姻、继承、侵权、交通事故责任
- 《道路交通安全法》
- 《工伤保险条例》：工伤认定、伤残待遇
- 《消费者权益保护法》：7天无理由、退一赔三
- 《著作权法》《专利法》《商标法》
- 《法律援助法》：法律援助范围
- 《刑事诉讼法》《民事诉讼法》

**可通过管理接口扩展更多法条：**

```bash
# 上传 JSON 批量导入
curl -X POST http://localhost:8000/api/laws/import-json \
  -F "file=@custom_laws.json"
```

---

## 🔑 环境变量说明 (.env)

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LLM_PROVIDER` | openai | `openai` / `anthropic` |
| `OPENAI_API_KEY` | - | 必填（否则进入 Mock 模式） |
| `OPENAI_API_BASE` | https://api.openai.com/v1 | 可改为代理地址 |
| `OPENAI_MODEL` | gpt-4o | 推荐 gpt-4o / gpt-4o-mini |
| `ANTHROPIC_API_KEY` | - | Claude 模型时填写 |
| `MILVUS_HOST` | localhost | Milvus 地址 |
| `MILVUS_PORT` | 19530 | Milvus gRPC 端口 |
| `RAG_TOP_K` | 5 | 法条检索数量 |
| `RAG_SIMILARITY_THRESHOLD` | 0.5 | 相似度过滤阈值 |

**💡 无 API Key 时自动启用 Mock 模式**，前端可正常交互体验引导流程。

---

## 🧪 API 接口速查

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/consulting/chat` | 核心对话接口 |
| `GET` | `/api/consulting/health` | 健康检查 + Milvus 状态 |
| `POST` | `/api/laws/init-collection` | 初始化向量集合 |
| `POST` | `/api/laws/insert` | 插入单条法条 |
| `POST` | `/api/laws/batch-insert` | 批量插入法条 |
| `POST` | `/api/laws/import-json` | JSON 文件批量导入 |
| `GET` | `/api/laws/search?query=xxx` | 测试法条检索 |
| `GET` | `/api/laws/stats` | 向量库统计 |

---

## ⚠️ 重要声明

1. **本系统为技术演示项目**，法律咨询意见仅供参考，不构成正式法律意见
2. 真实案件请携带材料前往**当地法律援助中心**或拨打热线 **12348**
3. 内置种子法条仅为常见高频法条示例，如需完整法律库请对接专业法条数据源
4. 大模型具有概率性生成特性，即使有 RAG 约束也建议人工复核关键引用

---

## 📝 License

MIT License - 技术交流用途
