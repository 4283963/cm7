from typing import Optional, Tuple, Dict, Any, List
from app.schemas.chat import (
    CaseInfo,
    GuideStep,
    GuideQuestion,
    DisputeType,
    Message,
    MessageRole,
)
from app.core.logging import logger
import re


class DialogManager:
    GUIDE_FLOW = [
        GuideStep.GREETING,
        GuideStep.DISPUTE_TYPE,
        GuideStep.TIME,
        GuideStep.LOCATION,
        GuideStep.PARTIES,
        GuideStep.DETAILS,
        GuideStep.COMPLETED,
    ]

    STEP_QUESTIONS: Dict[GuideStep, GuideQuestion] = {
        GuideStep.GREETING: GuideQuestion(
            step=GuideStep.GREETING,
            question="您好，欢迎使用法律援助中心AI咨询系统。我将帮助您梳理案情并提供专业法律建议。请先告诉我您遇到的是哪一类纠纷？",
            options=[d.value for d in DisputeType],
            required=True,
        ),
        GuideStep.DISPUTE_TYPE: GuideQuestion(
            step=GuideStep.DISPUTE_TYPE,
            question="请选择您遇到的纠纷类型：",
            options=[d.value for d in DisputeType],
            required=True,
        ),
        GuideStep.TIME: GuideQuestion(
            step=GuideStep.TIME,
            question="请问纠纷事件发生的时间是什么时候？（例如：2024年3月、去年6月左右、具体日期等）",
            required=True,
        ),
        GuideStep.LOCATION: GuideQuestion(
            step=GuideStep.LOCATION,
            question="请问事件发生在什么地点？（例如：北京市朝阳区、某公司办公场所内等）",
            required=True,
        ),
        GuideStep.PARTIES: GuideQuestion(
            step=GuideStep.PARTIES,
            question="请介绍一下纠纷涉及的当事人有哪些？各方是什么关系？（例如：我是员工，对方是XX公司；我和对方是邻居等）",
            required=True,
        ),
        GuideStep.DETAILS: GuideQuestion(
            step=GuideStep.DETAILS,
            question="请详细描述一下纠纷的具体经过、您目前掌握的证据，以及您希望达到的诉求是什么？",
            required=True,
        ),
    }

    def __init__(self):
        self._step_state: Dict[str, GuideStep] = {}

    def _infer_dispute_type(self, text: str) -> Optional[DisputeType]:
        keywords = {
            DisputeType.LABOR: ["工资", "加班", "劳动", "劳动合同", "辞退", "解雇", "工伤", "社保", "公积金", "离职", "员工", "公司辞退"],
            DisputeType.CONTRACT: ["合同", "违约", "协议", "定金", "违约金", "履行合同", "解除合同", "签订合同"],
            DisputeType.PROPERTY: ["房产", "房屋", "买房", "卖房", "交房", "房产证", "物业", "开发商", "二手房", "房租", "租房"],
            DisputeType.MARRIAGE: ["离婚", "结婚", "夫妻", "孩子", "抚养权", "财产分割", "家暴", "出轨", "配偶", "婚姻"],
            DisputeType.INHERITANCE: ["继承", "遗产", "遗嘱", "继承人", "遗赠", "房产继承", "遗产分割"],
            DisputeType.TORT: ["侵权", "赔偿", "损害", "名誉", "隐私", "肖像权", "知识产权", "专利", "商标", "著作权"],
            DisputeType.TRAFFIC: ["交通事故", "车祸", "撞车", "肇事", "交警", "酒驾", "保险理赔", "交通事故认定书"],
            DisputeType.CRIMINAL: ["刑事", "报案", "诈骗", "盗窃", "公安", "派出所", "刑事拘留", "取保候审", "判刑"],
            DisputeType.ADMINISTRATIVE: ["行政", "政府部门", "复议", "诉讼", "行政处罚", "行政许可", "公务员"],
        }

        for dtype, kws in keywords.items():
            for kw in kws:
                if kw in text:
                    return dtype
        return None

    def _extract_field_from_text(self, step: GuideStep, text: str, case_info: CaseInfo) -> CaseInfo:
        if step == GuideStep.DISPUTE_TYPE:
            inferred = self._infer_dispute_type(text)
            if inferred:
                case_info.dispute_type = inferred
            else:
                for d in DisputeType:
                    if d.value in text:
                        case_info.dispute_type = d
                        break

        elif step == GuideStep.TIME:
            case_info.incident_time = text.strip()

        elif step == GuideStep.LOCATION:
            case_info.incident_location = text.strip()

        elif step == GuideStep.PARTIES:
            case_info.parties = text.strip()

        elif step == GuideStep.DETAILS:
            case_info.details = text.strip()

        return case_info

    def get_current_step(self, session_id: str) -> GuideStep:
        return self._step_state.get(session_id, GuideStep.GREETING)

    def set_step(self, session_id: str, step: GuideStep):
        self._step_state[session_id] = step

    def _next_step(self, current: GuideStep) -> GuideStep:
        try:
            idx = self.GUIDE_FLOW.index(current)
            if idx + 1 < len(self.GUIDE_FLOW):
                return self.GUIDE_FLOW[idx + 1]
            return GuideStep.COMPLETED
        except ValueError:
            return GuideStep.COMPLETED

    def is_step_complete(self, step: GuideStep, case_info: CaseInfo) -> bool:
        checks = {
            GuideStep.GREETING: True,
            GuideStep.DISPUTE_TYPE: case_info.dispute_type is not None,
            GuideStep.TIME: bool(case_info.incident_time),
            GuideStep.LOCATION: bool(case_info.incident_location),
            GuideStep.PARTIES: bool(case_info.parties),
            GuideStep.DETAILS: bool(case_info.details),
            GuideStep.COMPLETED: True,
        }
        return checks.get(step, True)

    def process_user_message(
        self,
        session_id: str,
        user_message: str,
        current_case_info: Optional[CaseInfo],
    ) -> Tuple[CaseInfo, Optional[GuideQuestion], bool]:
        case_info = current_case_info or CaseInfo()
        current_step = self.get_current_step(session_id)

        logger.info(f"[{session_id}] 当前步骤: {current_step.value}, 用户消息: {user_message[:50]}...")

        if current_step == GuideStep.GREETING:
            case_info = self._extract_field_from_text(GuideStep.DISPUTE_TYPE, user_message, case_info)
            if self.is_step_complete(GuideStep.DISPUTE_TYPE, case_info):
                current_step = self._next_step(GuideStep.DISPUTE_TYPE)
                self.set_step(session_id, current_step)
            else:
                current_step = GuideStep.DISPUTE_TYPE
                self.set_step(session_id, current_step)
        else:
            case_info = self._extract_field_from_text(current_step, user_message, case_info)

        if self.is_step_complete(current_step, case_info):
            next_s = current_step
            while self.is_step_complete(next_s, case_info) and next_s != GuideStep.COMPLETED:
                next_s = self._next_step(next_s)
                self.set_step(session_id, next_s)
            current_step = next_s

        is_completed = current_step == GuideStep.COMPLETED
        next_question = None
        if not is_completed and current_step in self.STEP_QUESTIONS:
            next_question = self.STEP_QUESTIONS[current_step]

        logger.info(f"[{session_id}] 下一步: {current_step.value}, 是否完成: {is_completed}")
        return case_info, next_question, is_completed


dialog_manager = DialogManager()
