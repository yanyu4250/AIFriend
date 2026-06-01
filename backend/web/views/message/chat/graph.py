import os
from typing import TypedDict, Annotated, Sequence

import lancedb
from django.conf import settings
from django.db import connection
from django.utils.timezone import localtime, now
from langchain_community.vectorstores import LanceDB
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode
from openai import embeddings

from web.documents.utils.custom_embeddings import CustomEmbeddings


class ChatGraph:
    @staticmethod
    def create_app():
        @tool
        def get_time() -> str:
            """当需要查询精确时间时，调用此函数。返回格式为：[年-月-日 时:分:秒]"""
            return localtime(now()).strftime("%Y-%m-%d %H:%M:%S")

        @tool
        def search_knowledge_base(query: str) -> str:
            """当用户问到任何关于文档、文件、资料、知识相关的问题时，必须调用此函数搜索知识库。
            比如用户问"文档里说了什么"、"我上传的文件里有什么"、"知识库里有没有关于X的内容"等，
            都应该用这个函数查询。输入为要查询的问题，输出为知识库中检索到的相关内容。"""
            lancedb_path = os.path.join(settings.BASE_DIR, 'web', 'documents', 'lancedb_storage')
            db = lancedb.connect(lancedb_path)
            if 'my_knowledge_base' not in db.table_names():
                return '知识库中暂无文档，请先上传文档。'
            embeddings = CustomEmbeddings()
            vector_db = LanceDB(
                connection=db,
                embedding=embeddings,
                table_name='my_knowledge_base',
            )
            docs = vector_db.similarity_search(query, k=3)
            if not docs:
                return '未在知识库中找到与问题相关的内容。'
            context = '\n\n'.join([f'内容片段：{i + 1}\n{doc.page_content}' for i, doc in enumerate(docs)])
            return f'从知识库中找到以下相关信息：\n\n{context}\n'

        tools = [get_time, search_knowledge_base]

        llm = ChatOpenAI(
            model='deepseek-v3.2',
            openai_api_key=os.getenv('API_KEY'),
            openai_api_base=os.getenv('API_BASE'),
            streaming=True,
            model_kwargs={
                "stream_options": {
                    "include_usage": True,  # 输出token消耗数量
                }
            }
        ).bind_tools(tools)

        class AgentState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], add_messages]

        def model_call(state: AgentState) ->AgentState:
            res = llm.invoke(state['messages'])
            return {'messages':[res]}

        def should_continue(state: AgentState) -> str:
            last_message = state['messages'][-1]
            if last_message.tool_calls:
                return "tools"
            return "end"

        tool_node = ToolNode(tools)

        graph = StateGraph(AgentState)
        graph.add_node('agent', model_call)
        graph.add_node('tools', tool_node)

        graph.add_edge(START, 'agent')
        graph.add_conditional_edges(
            'agent',
            should_continue,
            {
                'tools': 'tools',
                'end': END,
            }
        )
        graph.add_edge('tools', 'agent')

        return graph.compile()