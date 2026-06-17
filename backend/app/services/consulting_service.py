from typing import Tuple, List
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    CaseInfo,
    RetrievedLaw,
    GuideQuestion,
    Message,
    MessageRole,
)
from app.services.dialog_manager import dialog_manager
from app.services.prompt_builder import prompt_builder
from app.services.llm_service import llm_service
from app.rag.milvus_store import milvus_service
from app.core.logging import logger


class LegalConsultingService:

    @staticmethod
    def _retrieve_relevant_laws(
        case_info: CaseInfo,
        user_message: str,
    ) -> List[RetrievedLaw]:
        query = prompt_builder.build_case_summary_query(case_info, user_message)
        logger.info(f"RAG 检索查询: {query[:80]}...")
        laws = milvus_service.search_laws(query)
        for law in laws:
            logger.debug(f"检索命中: {law.title} {law.article} (相似度={law.similarity:.3f})")
        return laws

    @staticmethod
    def _extract_references(laws: List[RetrievedLaw]) -> List[str]:
        refs = []
        seen = set()
        for law in laws:
            key = f"{law.title}|{law.article}"
            if key not in seen:
                seen.add(key)
                chapter_str = f" {law.chapter}" if law.chapter else ""
                refs.append(f"《{law.title}》{chapter_str}{law.article}")
        return refs

    @classmethod
    async def process_chat(cls, request: ChatRequest) -> ChatResponse:
        session_id = request.session_id
        user_message = request.user_message.strip()

        logger.info(f"[会话 {session_id}] 收到咨询请求: {user_message[:50]}...")

        current_case = request.case_info or CaseInfo()
        history = request.history or []

        case_info, next_question, is_completed = dialog_manager.process_user_message(
            session_id=session_id,
            user_message=user_message,
            current_case_info=current_case,
        )

        retrieved_laws = cls._retrieve_relevant_laws(case_info, user_message)

        messages = prompt_builder.build_messages(
            case_info=case_info,
            retrieved_laws=retrieved_laws,
            history=history,
            current_user_message=user_message,
            is_completed=is_completed,
        )

        try:
            answer = llm_service.chat(messages, temperature=0.2)
        except Exception as e:
            logger.error(f"大模型调用异常: {e}")
            answer = "抱歉，当前法律咨询服务暂时不可用，请稍后重试或直接拨打法律援助热线 12348。"

        references = cls._extract_references(retrieved_laws)

        response = ChatResponse(
            session_id=session_id,
            answer=answer,
            guide_next=next_question,
            case_info=case_info,
            retrieved_laws=retrieved_laws,
            is_completed=is_completed,
            references=references,
        )

        logger.info(
            f"[会话 {session_id}] 处理完成 | "
            f"步骤: {next_question.step.value if next_question else '完成'}, "
            f"检索法条: {len(retrieved_laws)}条, "
            f"回答长度: {len(answer)}字符"
        )
        return response


legal_consulting_service = LegalConsultingService()
