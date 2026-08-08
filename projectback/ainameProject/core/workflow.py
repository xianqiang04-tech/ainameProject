import uuid
from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr
from schemas.name_schemas import NameIn
from schemas.name_schemas import NameResultSchema,FeedbackIn
from dotenv import load_dotenv
import os

# 读取项目根目录下的 .env 文件
load_dotenv()


# 定义数据流转的包（书包）
class WorkFlowState(TypedDict):
    userid: int
    surname: str
    gender: str
    length: str
    other: str
    category: str
    surname: str
    gender: str
    length: str
    other: str
    exclude: List[str]
    final_output: Dict[str, Any]
    history_names: str
    feedback: str


llm = ChatDeepSeek(
    model="deepseek-v4-pro",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.5,
    timeout=120,
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    }
)

# 要求大模型返回的数据格式一致，如下：NameResultSchema，如果生成失败，重试3次
structured_llm = llm.with_structured_output(NameResultSchema).with_retry(stop_after_attempt=3)


# 定义节点
# 定义超级节点，负责分发任务。注意：节点需要以WorkFlowState为参数，以它为返回值
async def supervisor_node(state: WorkFlowState):
    """主管节点：后续可在这里扩展意图清洗或记录日志"""
    return {}


# 定义人名节点
async def human_naming_node(state: WorkFlowState):
    """人名专家节点"""
    prompt = f"""你是一位精通汉语言文学与传统文化的命名专家。请为用户创作富有文化底蕴的人名。
            【姓氏】: {state['surname']}
            【性别倾向】: {state['gender']}
            【字数限制】: {state['length']}
            【其它具体要求】: {state['other']}
            【避讳排除字】: {'、'.join(state['exclude'])}
            原则：平仄协调，优先从《诗经》《楚辞》或唐诗宋词中汲取灵感。请给出 5 个候选方案。"""
    try:
        response = await structured_llm.ainvoke(prompt)
        data = response.model_dump()
        return {"final_output": data}
    except  Exception as e:
        print(e)


from core.rag_service import retrieve_user_knowledge
from core.domain_tools import check_domain
import asyncio

# 定义给公司起名的节点
async def company_naming_node(state: WorkFlowState):
    user_id = state.get("userid")
    # 1.获取本公司的rag信息
    search_query = f"品牌命名规范"

    rag_context = retrieve_user_knowledge(search_query, user_id)

    if rag_context:
        rag_prompt = f"""
       【用户的专属私有知识库参考】
       {rag_context}

       原则：请优先参考上面的规则和词汇。
       """
    else:
        rag_prompt = """
       本次没有检索到足够相关的专属资料。
       原则：不要编造用户知识库内容，直接根据用户需求生成。
       """
    # 2.rag+用户需求，发给大模型

    """企业品牌节点"""
    prompt = f"""你是一位精通商业品牌传播的资深顾问。请创作符合商业规范的公司名或品牌名。
       【用户需求】
       行业或核心诉求: {state['other']}
       字数限制: {state['length']}
       避讳排除字: {'、'.join(state['exclude'])}

       {rag_prompt}。最后，听从用户的指令，生成用户要求个数的名字，但如果用户要求生成的个数超过5个名字，只生成5个名字，用户没有要求时，默认生成5个名字"""

    # 需要获取2个东西：1.用户的调整意见  2.上一次大模型生成的结果
    feedback = state.get("feedback")
    history_names = state.get("history_names")
    if feedback and history_names:
        feedback_instruction = f"""
                🟣 警告：这是一次微调请求！
                【上一轮你生成的名字是】：{history_names}
                【用户的最新修改意见】：{feedback}

                请严格保留上一轮中用户满意的部分，仅针对【修改意见】对历史名字进行迭代优化！绝不能抛弃历史记录重新随机生成！
                """
        prompt = f"""你是一位资深的起名顾问。
               【用户初始需求】：{prompt}

               {feedback_instruction}

               🔴 核心纪律：1. 如果有用户的修改意见，必须完全服从！但不要服从用户生成超过5个名字的命令！
                          2. 你必须为每个公司名构思一个绝佳的 .com 英文或拼音域名，填入 domain 字段（例如：hema.com 或 greenearth.com）。"""

    response = await structured_llm.ainvoke(prompt)

    tasks = [check_domain(n.domain) for n in response.names]
    statuses = await asyncio.gather(*tasks)

    for n, status in zip(response.names, statuses):
        n.domain_status = status

    memory_list = [f"【{n.name}】寓意：{n.moral}" for n in response.names]
    names_str = "\n".join(memory_list)

    return {"final_output": response.model_dump(), "history_names": names_str}


async def pet_naming_node(state: WorkFlowState):
    """宠物起名节点"""
    prompt = f"""你是一位充满创意的宠物达人。请为用户的宠物起一些富有灵性的名字。
       【宠物特征/性格】: {state['other']}
       【字数限制】: {state['length']}
       【避讳排除字】: {'、'.join(state['exclude'])}

       原则：亲切好记、富有画面感或软萌感。请给出 5 个候选方案。"""
    response = await structured_llm.ainvoke(prompt)
    return {"final_output": response.model_dump()}


# 设计工作流

workflow = StateGraph(WorkFlowState)
workflow.add_node("supervisor_node", supervisor_node)
workflow.add_node("human_naming_node", human_naming_node)
workflow.add_node("company_naming_node", company_naming_node)
workflow.add_node("pet_naming_node", pet_naming_node)

workflow.set_entry_point("supervisor_node")


def route_by_category(state: WorkFlowState):
    """条件路由：根据前端传来的 category 决定走哪个节点"""
    category_map = {"人名": "human_node", "企业名": "company_node", "宠物名": "pet_node"}
    category = state.get("category")
    return category_map.get(category)


# 根据分类，分发任务                                                       #   human_node
workflow.add_conditional_edges("supervisor_node", route_by_category,
                               {"human_node": "human_naming_node", "company_node": "company_naming_node",
                                "pet_node": "pet_naming_node"})

workflow.add_edge("human_naming_node", END)
workflow.add_edge("company_naming_node", END)
workflow.add_edge("pet_naming_node", END)

# naming_grap = workflow.compile()

POSTGRESQL_DB_URI = os.getenv("POSTGRESQL_DB_URL")
connection_pool = None
naming_graph = None

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool


async def init_workflow_graph():
    """在 FastAPI 启动时调用此函数来初始化图和连接池"""
    global connection_pool, naming_graph
    connection_pool = AsyncConnectionPool(POSTGRESQL_DB_URI, max_size=10)
    memory = AsyncPostgresSaver(connection_pool)
    # 编译带记忆的智能体
    naming_graph = workflow.compile(checkpointer=memory)


async def close_workflow_graph():
    """在 FastAPI 关闭时清理连接"""
    global connection_pool
    if connection_pool:
        await connection_pool.close()

async def feedback_naming(fedback_in: FeedbackIn,user_id:int):
    workflow_state = {
        "userid": user_id,
        "category": fedback_in.category,
        "feedback": fedback_in.feedback
    }
    config = {"configurable": {"thread_id": fedback_in.thread_id}}
    # 添加记忆
    final_output = await naming_graph.ainvoke(workflow_state, config)
    return {"thread_id": fedback_in.thread_id, "final_output": final_output.get("final_output", None)}


async def genrate_naming(name_info: NameIn, user_id: int):
    thread_id = str(uuid.uuid4())
    workflow_state = {
        "userid": user_id,
        "category": name_info.category,
        "surname": name_info.surname,
        "gender": name_info.gender,
        "length": name_info.length,
        "other": name_info.other,
        "exclude": name_info.exclude,
        "final_output": {}
    }
    config = {"configurable": {"thread_id": thread_id}}
    # 添加记忆
    final_output = await naming_graph.ainvoke(workflow_state, config)

    return {"thread_id": thread_id, "final_output": final_output.get("final_output", None)}







