感谢mem0开源！

为了研发AliceChat系统，给爱丽丝和kei持久化的记忆
所以决定引入mem0作为中间层，配置neo4j图数据库和qdrant向量数据库作为记忆整理手段
本文将记录一些使用过程中的心得

[AliceChat仓库地址](https://github.com/code-with-Anson/AliceChat)
[本文修改后的兼容openai规范第三方ai服务的Alice-mem0仓库地址](https://github.com/code-with-Anson/Alice-mem0)

[mem0官方github](https://github.com/mem0ai/mem0)
[deepwiki解析mem0官方的github仓库](https://deepwiki.com/mem0ai/mem0)

## 这篇文章存在的意义
未来某一天我可能忘记这个项目的结构，为了方便我自己以及后来的学者们，我将通过本篇笔记解决以下问题：
1. 理清mem0的原理，项目结构
2. 如何使用兼容openai规范的第三方ai服务商
3. 如何快速上手进行使用

说在前面：
本次会简单讲一下ts和python版本的目录结构，**但实际最后的运行我们会使用python的版本**，因为**mem0官方在server文件夹已经用python的版本给我们写好了一个对外暴露接口的fastAPI服务**，我们没有道理重新自己去写，直接用就好了，很方便的

**而且ts和python版本的实现都一样，几乎完全相同**，我更推荐python版本，这里面写的感觉比ts规范一点，所以我们最后运行使用python版本

**所以本文会详细讲python版本的时候，ts版本作为了解原理的辅助工具**

## 项目速览
用deepwiki生成的项目结构图，速览一下核心逻辑
下图是记忆配置逻辑
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831686.png" />
一共有四个配置项
1. 向量数据库配置：用来做记忆持久化
2. llm模型配置：构造的llm模型用来语义化精简对话内容，方便嵌入模型解析
3. 嵌入模型配置：把解析后的记忆嵌入向量数据库，实现向量检索
4. 图数据库配置：用来记录实体之间的关系，比如爱丽丝是sensei的女儿

先明白有这几个东西就行，往下走

下图是对上面讲到的四个配置项的一个具体用法解释以及对应的工具
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831687.png" />

主要看这个流程图，这东西才是核心
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831688.png" />

简单瞅一眼，可以看到mem0这东西核心的逻辑就是在我们和ai聊天的时候需要主动发一个add请求到mem0，然后他会把我们的聊天消息交给一个llm模型进行语义化总结，之后把这个总结好的数据发给传统的嵌入模型，进行信息的向量化，之后需要使用的时候检索就完了

总而言之，**这东西是传统的rag但是加了个llm语义化消息的过程**，很好理解
最后由嵌入模型把消息保存到**向量数据库**和**图数据库**，让ai一方面可以快速检索消息，另一方面有知识图谱的能力，可以理解不同事物的关系

## 仓库结构
把官方github仓库的源码下载或是创建分支后拉取，怎么做都好，总之搞一份到本地，不然难以阅读，之后简单看一下源码结构
要关心的只有这三个目录

这是用py实现mem0核心功能的目录
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831690.png" style='width: 285px;' />

这是用ts实现mem0核心功能的目录
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831691.png" style='width: 291px;' />

这里有一个写好的main.py，可以对外提供fastAPI的接口服务，这里面引用的工具类和各种方法源自于我们刚刚看见的mem0文件夹，也就是那个用python实现mem0的文件夹
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831692.png" style='width: 275px;' />

## mem0-ts目录速通
### 1.client目录-对接在线api

**你只要看下面这一句话就可以，了解这是用来对接在线api的就行，我们本次不用ts版本的mem0，而且讲解实现也是用oss版本来讲，这个client目录对我们意义不大**

这是client目录下面的结构，目录包含了 Mem0 平台的 TypeScript 客户端库的核心实现。这个库提供了与 Mem0 API 交互的接口，允许开发者管理记忆、搜索内容、处理用户数据等。
```
client/
├── index.ts           # 导出入口文件，重新导出主要类和类型
├── mem0.ts            # 核心客户端实现，包含与API交互的所有方法
├── mem0.types.ts      # 类型定义文件，定义客户端使用的所有接口和类型
├── telemetry.ts       # 遥测功能实现，用于收集使用数据和错误报告
├── telemetry.types.ts # 遥测相关的类型定义
└── tests/
    └── memoryClient.test.ts # 客户端测试文件
```

**下面这一大段选择性看，可以不看：**
1. index.ts
作为库的入口点，主要功能是重新导出其他文件中定义的类型和类：
- 重新导出 `mem0.types.ts` 中的所有类型定义
- 导出 [MemoryClient](vscode-file://vscode-app/d:/Software/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 类，同时作为命名导出和默认导出
- 简化了用户导入路径，使开发者可以直接从库的根路径导入所需内容

2. mem0.ts
核心实现文件，包含与 Mem0 API 交互的 [MemoryClient](vscode-file://vscode-app/d:/Software/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 类：
- 提供构造函数配置连接参数（API密钥、主机、组织、项目等）
- 实现记忆管理方法：添加、更新、获取、搜索、删除记忆
- 提供用户和实体管理功能
- 实现项目配置和Webhook管理
- 处理批量操作（批量更新、删除）
- 集成遥测收集功能
- 提供错误处理和API请求封装

3. mem0.types.ts
定义客户端库使用的所有类型和接口：
- Memory - 记忆数据结构
- MemoryOptions - 记忆操作选项
- SearchOptions- 搜索配置选项
- Message- 消息格式
- ProjectOptions - 项目配置选项
- Webhook 相关类型
- FeedbackPayload - 反馈数据格式
- 其他辅助类型和接口

4. telemetry.ts
实现遥测数据收集功能：
- captureClientEvent - 捕获客户端事件和使用数据
- generateHash - 生成唯一标识符
- 收集API使用情况、错误报告等非敏感信息
- 用于改进服务和监控API健康状况

5. telemetry.types.ts
定义遥测相关的类型：
- 事件类型
- 遥测数据结构
- 遥测配置选项

6. tests/memoryClient.test.ts
客户端测试文件：
- 对 MemoryClient 的各种方法进行单元测试
- 验证API调用的正确性
- 测试错误处理和边缘情况

**主要功能总结**
Mem0 客户端库提供以下核心功能：
1. **记忆管理**：添加、获取、搜索、更新和删除记忆
2. **用户管理**：列出和删除用户和其他实体
3. **项目配置**：获取和更新项目设置
4. **Webhook管理**：创建、更新、删除和获取webhooks
5. **批量操作**：批量更新和删除记忆
6. **遥测**：收集使用数据以改进服务

这个客户端库的设计使开发者能够轻松地将 Mem0 的记忆和上下文管理功能集成到自己的应用程序中，同时提供了灵活的配置选项和完整的类型支持。

### 2.community目录-集成langchain
**这一段也可以直接跳过不看，我们主要看oss版本，简单看一眼就行**
这是community目录下面的结构
```
community/
├── .prettierignore       // Prettier 配置忽略文件
├── package.json          // 包配置文件
├── tsconfig.json         // TypeScript 配置文件
└── src/
    ├── index.ts          // 入口文件
    └── integrations/
        └── langchain/    // LangChain 集成
            ├── index.ts  // LangChain 集成入口
            └── mem0.ts   // Mem0 与 LangChain 集成的核心实现
```

`community` 文件夹包含的是 **Mem0 与社区工具的集成**，特别是 LangChain 框架：

1. **面向集成**：将 Mem0 与其他开源工具结合使用
2. **扩展生态系统**：让 Mem0 可以无缝集成到更广泛的 AI 应用生态中
3. **自定义工作流**：允许开发者将 Mem0 集成到现有的 LangChain 工作流中
4. **社区贡献**：接受社区贡献和扩展
5. **开源兼容**：与流行的开源框架兼容

这里给个例子
```ts
// 将 Mem0 与 LangChain 集成
import { Mem0Memory } from "@mem0/community/langchain";
import { ChatOpenAI } from "@langchain/openai";
import { ConversationChain } from "langchain/chains";

// 创建 Mem0 记忆实例
const memory = new Mem0Memory({
  sessionId: "user123",
  apiKey: "your-api-key"
});

// 与 LangChain 一起使用
const model = new ChatOpenAI();
const chain = new ConversationChain({ llm: model, memory });

const response = await chain.call({ input: "你好，能记住我吗？" });
```

### 3.oss目录-本地部署mem0-划重点
**这个是重点，主要是实现了完整的mem0的功能，请认真看**
目录速览
`oss` 文件夹是 Mem0 项目的开源实现部分，提供了完全本地化的记忆管理系统，可以独立于 Mem0 云服务以外运行，这是我最感兴趣的部分
```
oss/
├── .env.example              // 环境变量示例文件
├── .gitignore                // Git忽略文件
├── package.json              // 项目配置与依赖
├── README.md                 // 项目文档
├── tsconfig.json             // TypeScript配置
│
├── examples/                 // 使用示例
│   ├── basic.ts              // 基本用法示例
│   ├── local-llms.ts         // 本地语言模型使用示例
│   ├── llms/                 // 不同LLM的示例
│   │   └── mistral-example.ts  // Mistral AI模型示例
│   ├── utils/                // 示例工具
│   │   └── test-utils.ts     // 测试工具函数
│   └── vector-stores/        // 向量存储示例
│       ├── index.ts          // 向量存储入口
│       ├── memory.ts         // 内存向量存储示例
│       ├── pgvector.ts       // PostgreSQL向量存储示例
│       ├── qdrant.ts         // Qdrant向量存储示例
│       ├── redis.ts          // Redis向量存储示例
│       └── supabase.ts       // Supabase向量存储示例
│
├── src/                      // 源代码
│   ├── index.ts              // 主入口文件
│   │
│   ├── config/               // 配置管理
│   │   ├── defaults.ts       // 默认配置
│   │   └── manager.ts        // 配置管理器
│   │
│   ├── embeddings/           // 嵌入模型实现
│   │   ├── azure.ts          // Azure OpenAI嵌入
│   │   ├── base.ts          // 基础嵌入类
│   │   ├── google.ts        // Google嵌入
│   │   ├── langchain.ts     // LangChain集成
│   │   ├── ollama.ts        // Ollama本地嵌入
│   │   └── openai.ts        // OpenAI嵌入
│   │
│   ├── graphs/               // 知识图谱实现
│   │   ├── configs.ts        // 图配置
│   │   ├── tools.ts          // 图操作工具
│   │   └── utils.ts          // 图工具函数
│   │
│   ├── llms/                 // 大语言模型实现
│   │   ├── anthropic.ts      // Anthropic Claude模型
│   │   ├── azure.ts          // Azure OpenAI模型  
│   │   ├── base.ts           // 基础LLM类
│   │   ├── google.ts         // Google模型
│   │   ├── groq.ts           // Groq模型
│   │   ├── mistral.ts        // Mistral AI模型
│   │   ├── ollama.ts         // Ollama本地模型
│   │   ├── openai.ts         // OpenAI模型
│   │   └── openai_structured.ts // 结构化OpenAI调用
│   │
│   ├── memory/               // 记忆管理核心
│   │   ├── graph_memory.ts   // 图形记忆实现
│   │   ├── index.ts          // 主记忆类
│   │   └── memory.types.ts   // 记忆类型定义
│   │
│   ├── prompts/              // 提示词模板
│   │   ├── index.ts          // 提示词入口
│   │   ├── message_prompts.ts // 消息处理提示词
│   │   └── system_prompts.ts // 系统提示词
│   │
│   ├── storage/              // 历史存储实现
│   │   ├── base.ts           // 基础存储类
│   │   ├── DummyHistoryManager.ts // 虚拟历史管理器
│   │   ├── MemoryHistoryManager.ts // 内存历史管理器
│   │   ├── SQLiteManager.ts  // SQLite历史管理器
│   │   └── SupabaseHistoryManager.ts // Supabase历史管理器
│   │
│   ├── types/                // 类型定义
│   │   └── index.ts          // 类型入口文件
│   │
│   ├── utils/                // 工具函数
│   │   ├── bm25.ts           // BM25搜索算法
│   │   ├── factory.ts        // 工厂类
│   │   ├── logger.ts         // 日志工具
│   │   ├── memory.ts         // 记忆工具函数
│   │   └── telemetry.ts      // 遥测工具
│   │
│   └── vector_stores/        // 向量存储实现
│       ├── base.ts           // 基础向量存储类
│       ├── memory.ts         // 内存向量存储
│       ├── pgvector.ts       // PostgreSQL向量存储
│       ├── qdrant.ts         // Qdrant向量存储
│       ├── redis.ts          // Redis向量存储
│       └── supabase.ts       // Supabase向量存储
│
└── tests/                    // 测试文件
    └── memory.test.ts        // 记忆功能测试
```

核心模块
1. **Memory 类** - 核心组件，提供记忆管理接口
2. **嵌入层** - 支持多种嵌入模型，将文本转换为向量
3. **向量存储层** - 提供多种存储选项，从内存到专业向量数据库
4. **LLM 层** - 支持多种大语言模型，包括本地模型和云服务
5. **图存储层** - 使用 Neo4j 实现实体关系和知识图谱
6. **历史存储** - 维护记忆历史和变更记录

## ts版本快速理解
client目录是教我们怎么和官方云服务的api进行交互
oss版本是开源版本，里面有完整的mem0实现

**接下来我带你快速搞明白怎么配置ts版本，实现自定义使用符合openai规范的第三方ai服务**

在oss版本中，通过factory工厂类实现不同的ai服务商通讯工具的生成
**具体的代码文件是mem0-ts\src\oss\src\utils\factory.ts**
主要是这一段
通过传入的provider字段决定使用哪个构造方式
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831693.png" />


这里以OPENAI为例，直接ctrl加左键点击**return new OpenAILLM（config）** 的**OpenAILLM**
我们可以直接到**mem0-ts\src\oss\src\llms\openai.ts**文件里面看到构造函数
只要在这里传入我们需要的baseURL就可以指定一些符合openai规范的第三方的ai服务商
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831694.png" />
这里一开始是没有baseURL的这个可选项的，为什么我知道要这么写呢？
因为你在项目根目录使用npm install之后，会安装node_modules
其中就有openai的依赖，所以这里ctrl加左键点new OpenAI的OpenAI
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831695.png" />

**可以看到官方其实提供了baseURL这个可选参数**，所以我们传入就可以构造出支持不同第三方服务商的openai实例进行接口的调用
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831696.png" />

现在已知在使用图数据库的时候还会用到OpenAIStructuredLLM的构造函数，**这个也要改一下传入的baseURL**，这里修改比较潦草，直接写死在构造函数里面了，硬性读环境变量，没有留下传参的灵活性，不过我相信大多数时候这个用不到，一般人只要配置环境变量就完事了
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831697.png" />

mem0一共用到两个模型，一个语义化并精简对话的llm模型，还有一个嵌入模型，所以这里也要改一下嵌入模型的构造函数，这段代码在**mem0-ts\src\oss\src\embeddings\openai.ts**文件里面，这样就可以自定义第三方的嵌入模型
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831698.png" />

接下来可以看到mem0-ts\src\oss\examples\basic.ts文件里面提供了一些测试方法
这里以qdrant为例
可以看到主要需要配置embedder模型和llm模型的参数，还需要配置一下qdrant，qdrant可以直接使用docker本地部署一个，然后写环境变量就可以了
这里比较重要的是embeddingModelDims参数，这个是嵌入模型的维度，**text-embedding-3-small**是**1536**维，而测试的时候我用的是硅基流动提供的嵌入模型是**BAAI/bge-m3**，这个维度是**1024**，需要在环境变量配置，同时这里要加一个显式的Number转换
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831699.png" />

### 总结：
mem0通过**mem0-ts\src\oss\src\utils\factory.ts**使用工厂模式构造不同的ai客户端

**mem0-ts\src\oss\src\llms**这个文件夹下面是每个不同ai服务商的llm客户端构建方式

**mem0-ts\src\oss\src\embeddings**这个文件夹下面是embedding客户端构造函数

为了支持符合openai规范的第三方ai服务商，我们要在**mem0-ts\src\oss\src\llms\openai.ts**，**mem0-ts\src\oss\src\llms\openai_structured.ts**，**mem0-ts\src\oss\src\embeddings\openai.ts**这三个文件的构造函数里面提供一个baseURL的参数，这样就可以自定义api地址了

之后通过docker正常的配置Qdrant和neo4j，填一下参数就可以了
在**mem0-ts\src\oss\examples\basic.ts**里面提供了很多测试方法，你可以在这里进行测试，自由的探索配置

### 配置示例
#### 环境变量示例
请创建一个 **.env** 文件
```ts
# 这是语义化llm的配置文件，这个允许你使用OPENAI的API来进行对话的语义化处理
OPENAI_API_KEY=你的apikey
OPENAI_BASE_URL=https://api.deepseek.com
# 这个是你使用的模型的名称
OPENAI_COMPLETION_MODEL=deepseek-chat

# 这个是嵌入模型的API地址和密钥
OPENAI_EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
OPENAI_EMBEDDING_API_KEY=你的apikey
# 这个是你使用的嵌入模型（embedding模型）的名称
OPENAI_EMBEDDING_MODEL=BAAI/bge-m3
# 这个是你使用的embedding模型的向量维度
OPENAI_EMBEDDING_DIMENSION=1024

# Qdrant Configuration (optional)
# Uncomment and set these values to use Qdrant
QDRANT_URL=http://localhost:6333
#QDRANT_API_KEY=your-api-key-here
#QDRANT_PATH=/path/to/local/storage # For local file-based storage
#QDRANT_HOST=localhost # Alternative to URL
#QDRANT_PORT=6333 # Alternative to URL

# Neo4j Configuration (optional)
NEO4J_URL=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=NEO4J_PASSWORD

# PGVector Configuration (optional)
# Uncomment and set these values to use PGVector
#PGVECTOR_DB=vectordb
#PGVECTOR_USER=postgres
#PGVECTOR_PASSWORD=postgres
#PGVECTOR_HOST=localhost
#PGVECTOR_PORT=5432

# Redis Configuration (optional)
# Uncomment and set these values to use Redis
# REDIS_URL=redis://localhost:6379
# REDIS_USERNAME=default
# REDIS_PASSWORD=your-password-here
```


#### Qdrant测试配置
``` ts
async function demoQdrant() {
  console.log("\n=== 测试Qdrant存储 ===\n");
  // 使用Qdrant作为向量数据库

  const memory = new Memory({
    version: "v1.1",
    embedder: {
      provider: "openai",
      config: {
	    // 这里没写自定义的baseURL，因为我直接在构造函数里面定义好了
	    // 在 mem0-ts\src\oss\src\embeddings\openai.ts 这里写过了
        apiKey: process.env.OPENAI_API_KEY || "",
        model: process.env.OPENAI_EMBEDDING_MODEL || "text-embedding-3-small",
      },
    },
    vectorStore: {
      provider: "qdrant", // 使用Qdrant作为向量存储
      config: {
        collectionName: "memories",
        dimension: Number(process.env.OPENAI_EMBEDDING_DIMENSION), // 嵌入模型维度
        embeddingModelDims: Number(process.env.OPENAI_EMBEDDING_DIMENSION), // 嵌入模型维
        url: process.env.QDRANT_URL, // Qdrant服务URL
        apiKey: process.env.QDRANT_API_KEY, // API密钥
        path: process.env.QDRANT_PATH, // 路径
        host: process.env.QDRANT_HOST, // 主机
        port: process.env.QDRANT_PORT
          ? parseInt(process.env.QDRANT_PORT)
          : undefined, // 端口
        onDisk: true, // 数据存储在磁盘上而非内存中
      },
    },
    llm: {
      provider: "openai",
      config: {
        // 这里没写自定义的baseURL，因为我直接在构造函数里面定义好了
	    // 在 mem0-ts\src\oss\src\llm\openai.ts 和 openai_structured.ts 这里写过了
        apiKey: process.env.OPENAI_API_KEY || "",
        model: process.env.OPENAI_COMPLETION_MODEL, // LLM模型
      },
    },
    historyDbPath: "memory.db",
  });
  
  await runTests(memory);
}
```

接下来我们主要看python版本，python版本才有意义，讲ts是帮助我们了解

## python版本-重点！
**接下来讲的要敲黑板了，我们最终运行的也是python版本，所以好好看**

### 目录速通
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831700.png" />

有两个文件夹和python的版本有关，一个mem0，这个是用python实现了mem0的完整功能，另一个则是server，这里面的main.py使用了fastAPI，完成了对外的接口暴露

简单举个例子，虽然我不是做python，而是做java开发的，但是对于这种写法也是非常的眼熟
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831701.png" />

也就是说，我们只需要对这个项目进行一些配置的微调，之后运行这个main.py就可以了

事实上也正是如此，这是运行在8000时，mem0的openapi文档
（openapi是api文档规范，openai是ai服务接口规范，不是一个东西哦）
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831702.png" />

那我们只要按照刚刚ts版本的思路来操作就可以了

### 微调配置
首先我们要知道py版本是怎么构建ai客户端的，可以在**mem0/utils/factory.py**中看到这也是通过判断provider来实现实例化不同的客户端
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831703.png" />

根据不同的ai服务商创建不同的客户端，并且可以传入配置
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831704.png" />

通过 `base_config = BaseLlmConfig(**config)`这一行，可以看到这是一个**BaseLlmConfig**类型的配置参数

果断跟进去看一下，可以发现openai的客户端在构造时直接允许传入baseURL，ts版本没有写出来可以添加，需要我们自己去查看openai客户端的构造过程，但是在py版本里面，config类直接定义了openai_base_url，这也是为什么我更推荐python版本，因为我觉得这个版本有认真维护
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831705.png" />

那接下来就很简单了
打开**mem0/llms/openai.py**
可以看到直接就写好了会检查传入的config有没有配置base_url属性，如果没有还会检查环境变量，环境变量也没有才会使用默认的地址，所以我真的很喜欢这个python版本啊！
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831706.png" />

所以**mem0/llms/openai.py**和**mem0/llms/openai_structured.py**这两个文件不需要修改，我们只需要配置环境变量就可以了

buuuut，这里有个比较重要的地方提一嘴
来到**mem0/embeddings/openai.py**里面，会发现嵌入模型的baseURL默认也是读取环境变量的OPENAI_API_BASE，这样会导致嵌入模型和语义化的llm模型不能使用两家不同的ai提供商，不能忍，必须要改一下
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831707.png" />

这里只需要简单的修改几个字就好了，之后记得去环境变量里面配一下
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831708.png" />

### 启动主程序
接下来去main.py里面看主程序是怎么使用的
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831709.png" />

可以看到是通过注入一个配置来实例化记忆操作对象的
而在本文件的上方就有**DEFAULT_CONFIG**的构造
这里丢个我写好的模板参考

```python
import logging  
import os  
from typing import Any, Dict, List, Optional  
  
from dotenv import load_dotenv  
from fastapi import FastAPI, HTTPException  
from fastapi.responses import JSONResponse, RedirectResponse  
from pydantic import BaseModel, Field  
  
from mem0 import Memory  
  
logging.basicConfig(  
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"  
)  
  
# Load environment variables  
load_dotenv()  
  
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "postgres")  
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")  
POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")  
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")  
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")  
POSTGRES_COLLECTION_NAME = os.environ.get("POSTGRES_COLLECTION_NAME", "memories")  
  
# NEO4J的配置项  
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")  
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")  
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "mem0graph")  
  
MEMGRAPH_URI = os.environ.get("MEMGRAPH_URI", "bolt://localhost:7687")  
MEMGRAPH_USERNAME = os.environ.get("MEMGRAPH_USERNAME", "memgraph")  
MEMGRAPH_PASSWORD = os.environ.get("MEMGRAPH_PASSWORD", "mem0graph")  
  
# 这个是符合OPENAI规范的大模型的配置项  
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")  
OPENAI_COMPLETION_MODEL = os.environ.get("OPENAI_COMPLETION_MODEL", "gpt-4o")  
  
# 这个是符合OPENAI规范的嵌入模型的配置项  
# 这个是嵌入模型的API地址和密钥  
OPENAI_EMBEDDING_BASE_URL = os.environ.get(  
    "OPENAI_EMBEDDING_BASE_URL", "https://api.openai.com/v1"  
)  
OPENAI_EMBEDDING_API_KEY = os.environ.get("OPENAI_EMBEDDING_API_KEY")  
# 这个是你使用的嵌入模型（embedding模型）的名称  
OPENAI_EMBEDDING_MODEL = os.environ.get(  
    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"  
)  
# 这个是你使用的embedding模型的向量维度  
OPENAI_EMBEDDING_DIMENSION = os.environ.get("OPENAI_EMBEDDING_DIMENSION", 1536)  
  
# 这是Qdrant向量数据库的配置项  
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")  
QDRANT_COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION_NAME", "memories")  
# QDRANT_API_KEY=your-api-key-here  
# QDRANT_PATH=/path/to/local/storage # For local file-based storage  
# QDRANT_HOST=localhost # Alternative to URL  
# QDRANT_PORT=6333 # Alternative to URL  
  
# 这是历史数据库的配置项，为docker设置  
# HISTORY_DB_PATH = os.environ.get("HISTORY_DB_PATH", "/app/history/history.db")  
  
# 这是历史数据库的配置项，为windows设置  
HISTORY_DB_PATH = os.environ.get("HISTORY_DB_PATH", "./history.db")  
  
print(f"OPENAI_EMBEDDING_API_KEY: {os.environ.get('OPENAI_EMBEDDING_API_KEY')}")  
print(f"OPENAI_API_KEY: {os.environ.get('OPENAI_API_KEY')}")

DEFAULT_CONFIG = {  
    "version": "v1.1",  
    # 这里写一个pgvector的配置示例  
    # "vector_store": {  
    #     "provider": "pgvector",    
    #     "config": {    
    #         "host": POSTGRES_HOST,    
    #         "port": int(POSTGRES_PORT),    
    #         "dbname": POSTGRES_DB,    
    #         "user": POSTGRES_USER,    
    #         "password": POSTGRES_PASSWORD,    
    #         "collection_name": POSTGRES_COLLECTION_NAME,    
    #     }    
    # },    
    
    # 这里写一个qdrant的配置示例  
    "vector_store": {  
        "provider": "qdrant",  
        "config": {  
            "embedding_model_dims": int(  
                os.environ.get("OPENAI_EMBEDDING_DIMENSION", "1536")  
            ),  
            "url": os.environ.get("QDRANT_URL", "http://localhost:6333"),  
            "collection_name": QDRANT_COLLECTION_NAME,  
            "on_disk": True,  # 是否持久化存储  
        },  
    },  
    "graph_store": {  
        "provider": "neo4j",  
        "config": {  
            "url": NEO4J_URI,  
            "username": NEO4J_USERNAME,  
            "password": NEO4J_PASSWORD,  
        },  
    },  
    "llm": {  
        "provider": "openai",  
        "config": {  
            "openai_base_url": OPENAI_BASE_URL,  
            "api_key": OPENAI_API_KEY,  
            "temperature": 0.7,  
            "model": OPENAI_COMPLETION_MODEL,  
        },  
    },  
    "embedder": {  
        "provider": "openai",  
        "config": {  
            "openai_base_url": OPENAI_EMBEDDING_BASE_URL,  
            "api_key": OPENAI_EMBEDDING_API_KEY,  
            "model": OPENAI_EMBEDDING_MODEL,  
            "embedding_dims": int(os.environ.get("OPENAI_EMBEDDING_DIMENSION", "1536")),  
        },  
    },  
    "history_db_path": HISTORY_DB_PATH,  
}  
  
MEMORY_INSTANCE = Memory.from_config(DEFAULT_CONFIG)
```

需要着重注意的是下面两个配置的向量维度参数写法是不一样的！
``` python
    "vector_store": {  
        "provider": "qdrant",  
        "config": {  
            "embedding_model_dims": int(  
                os.environ.get("OPENAI_EMBEDDING_DIMENSION", "1536")  
            ),  
            "url": os.environ.get("QDRANT_URL", "http://localhost:6333"),  
            "collection_name": QDRANT_COLLECTION_NAME,  
            "on_disk": True,  # 是否持久化存储  
        },  
    },  
```

```python
    "embedder": {  
        "provider": "openai",  
        "config": {  
            "openai_base_url": OPENAI_EMBEDDING_BASE_URL,  
            "api_key": OPENAI_EMBEDDING_API_KEY,  
            "model": OPENAI_EMBEDDING_MODEL,  
            "embedding_dims": int(os.environ.get("OPENAI_EMBEDDING_DIMENSION", "1536")),  
        },  
    },  
```

这两个配置的向量维度配置是不同的！
前者接受的是 **"embedding_model_dims"** 这个参数
而后者则是 **"embedding_dims"** 这个参数
请注意区别

接下来就是创建一个.env文件
写好配置

```python
# 下面是必要的配置  
NEO4J_URI=neo4j://localhost:17687  
NEO4J_USERNAME=neo4j  
NEO4J_PASSWORD=NEO4J_PASSWORD  
  
QDRANT_URL=http://localhost:6333  
  
OPENAI_API_KEY=API_KEY  
OPENAI_BASE_URL=https://api.deepseek.com  
OPENAI_COMPLETION_MODEL=deepseek-chat  
  
OPENAI_EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1  
OPENAI_EMBEDDING_API_KEY=API_KEY  
OPENAI_EMBEDDING_MODEL=BAAI/bge-m3  
OPENAI_EMBEDDING_DIMENSION=1024  
  
# 下面是main.py在加载配置文件时的具体实现  
# 默认会初始化qdrant作为向量数据库，如果需要使用其他的向量数据库，请在main.py中修改  
# NEO4J的配置项  
# NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")  
# NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")  
# NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "mem0graph")  
#  
# POSTGRES的配置项  
# POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "postgres")  
# POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")  
# POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")  
# POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")  
# POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")  
# POSTGRES_COLLECTION_NAME = os.environ.get("POSTGRES_COLLECTION_NAME", "memories")  
  
# NEO4J的配置项  
# NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")  
# NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")  
# NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "mem0graph")  
#  
# MEMGRAPH_URI = os.environ.get("MEMGRAPH_URI", "bolt://localhost:7687")  
# MEMGRAPH_USERNAME = os.environ.get("MEMGRAPH_USERNAME", "memgraph")  
# MEMGRAPH_PASSWORD = os.environ.get("MEMGRAPH_PASSWORD", "mem0graph")  
  
# 这个是符合OPENAI规范的大模型的配置项  
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  
# OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")  
# OPENAI_COMPLETION_MODEL = os.environ.get("OPENAI_COMPLETION_MODEL", "gpt-4o")  
  
# 这个是符合OPENAI规范的嵌入模型的配置项  
# 这个是嵌入模型的API地址和密钥  
# OPENAI_EMBEDDING_BASE_URL = os.environ.get(  
#     "OPENAI_EMBEDDING_BASE_URL", "https://api.openai.com/v1"  
# )  
# OPENAI_EMBEDDING_API_KEY = os.environ.get("OPENAI_EMBEDDING_API_KEY")  
# 这个是你使用的嵌入模型（embedding模型）的名称  
# OPENAI_EMBEDDING_MODEL = os.environ.get(  
#     "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"  
# )  
# 这个是你使用的embedding模型的向量维度  
# OPENAI_EMBEDDING_DIMENSION = os.environ.get("OPENAI_EMBEDDING_DIMENSION", 1536)  
  
# 这是Qdrant向量数据库的配置项  
# QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")  
# QDRANT_COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION_NAME", "memories")  
# QDRANT_API_KEY=your-api-key-here  
# QDRANT_PATH=/path/to/local/storage # For local file-based storage  
# QDRANT_HOST=localhost # Alternative to URL  
# QDRANT_PORT=6333 # Alternative to URL
```

cd到当前目录，使用uvicorn运行就可以了，如果没有安装uvicorn用pip安装一下，这里可以直接问ai怎么做，我是比较喜欢问claude啦，各位自便
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831710.png" />

接下来就可以直接访问了！
<img src="https://raw.githubusercontent.com/code-with-Anson/md-imgs/main/imgs/20250518022831711.png" />

