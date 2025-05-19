import os

from dotenv import load_dotenv

from mem0 import Memory

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


print(f"这是llm模型的BASE-URL: {os.environ.get('OPENAI_BASE_URL')}")
print(f"这是llm模型的API-KEY: {os.environ.get('OPENAI_API_KEY')}")
print(f"这是llm模型的MODEL: {os.environ.get('OPENAI_COMPLETION_MODEL')}")
print(f"这是嵌入模型的BASE-URL: {os.environ.get('OPENAI_EMBEDDING_BASE_URL')}")
print(f"这是嵌入模型的API-KEY: {os.environ.get('OPENAI_EMBEDDING_API_KEY')}")
print(f"这是嵌入模型的MODEL: {os.environ.get('OPENAI_EMBEDDING_MODEL')}")
print(f"这是嵌入模型的维度: {os.environ.get('OPENAI_EMBEDDING_DIMENSION')}")

memory_client = None


def get_memory_client(custom_instructions: str = None):
    """
    Get or initialize the Mem0 client.

    Args:
        custom_instructions: Optional instructions for the memory project.

    Returns:
        Initialized Mem0 client instance.

    Raises:
        Exception: If required API keys are not set.
    """
    global memory_client

    if memory_client is not None:
        return memory_client

    try:
        config = {
            # "vector_store": {
            #     "provider": "qdrant",
            #     "config": {
            #         "collection_name": "openmemory",
            #         "host": "mem0_store",
            #         "port": 6333,
            #     },
            # },
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "embedding_model_dims": int(
                        os.environ.get("OPENAI_EMBEDDING_DIMENSION", "1536")
                    ),
                    "collection_name": "openmemory",
                    "host": "mem0_store",
                    # "host": "localhost",
                    "port": 6333,
                    "on_disk": True,  # 是否持久化存储
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
                    "embedding_dims": int(
                        os.environ.get("OPENAI_EMBEDDING_DIMENSION", "1536")
                    ),
                },
            },
        }

        memory_client = Memory.from_config(config_dict=config)
    except Exception:
        raise Exception("Exception occurred while initializing memory client")

    # Update project with custom instructions if provided
    if custom_instructions:
        memory_client.update_project(custom_instructions=custom_instructions)

    return memory_client


def get_default_user_id():
    return "default_user"
