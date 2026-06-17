import { useState, useCallback, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { message as antdMessage } from 'antd';
import { consultingApi } from '@/services/api';
import { checkInputSafety } from '@/services/safety';
import type {
  DisplayMessage,
  CaseInfo,
  ChatMessage,
  GuideQuestion,
  MessageRole,
  CaseKeyFactors,
  SimilarCase,
} from '@/types';

const STORAGE_KEY = 'legal_ai_session';

export interface ChatState {
  sessionId: string;
  messages: DisplayMessage[];
  caseInfo: CaseInfo;
  isLoading: boolean;
  isCompleted: boolean;
  currentGuide: GuideQuestion | null;
  keyFactors: CaseKeyFactors | null;
  similarCases: SimilarCase[];
}

function loadStoredSession(): Partial<ChatState> | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function saveSession(state: ChatState) {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        sessionId: state.sessionId,
        caseInfo: state.caseInfo,
        keyFactors: state.keyFactors,
        similarCases: state.similarCases,
      }),
    );
  } catch {}
}

export function useChat() {
  const stored = loadStoredSession();

  const [sessionId] = useState<string>(stored?.sessionId || uuidv4());
  const [messages, setMessages] = useState<DisplayMessage[]>([
    {
      id: uuidv4(),
      role: 'assistant',
      content:
        '您好，欢迎使用**法律援助中心 AI 法律咨询系统**。\n\n我是您的专属法律助手，将通过几个简单问题帮助您梳理案情，并结合真实法律条文提供专业建议。\n\n请先告诉我，您遇到的是哪一类法律纠纷？',
      timestamp: new Date(),
      guideQuestion: {
        step: 'dispute_type',
        question: '请选择您遇到的纠纷类型：',
        options: [
          '劳动纠纷',
          '合同纠纷',
          '房产纠纷',
          '婚姻家庭',
          '继承纠纷',
          '侵权纠纷',
          '交通事故',
          '刑事案件',
          '行政纠纷',
          '其他纠纷',
        ],
        required: true,
      },
    },
  ]);
  const [caseInfo, setCaseInfo] = useState<CaseInfo>(stored?.caseInfo || {});
  const [isLoading, setIsLoading] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [currentGuide, setCurrentGuide] = useState<GuideQuestion | null>(null);
  const [keyFactors, setKeyFactors] = useState<CaseKeyFactors | null>(
    stored?.keyFactors || null,
  );
  const [similarCases, setSimilarCases] = useState<SimilarCase[]>(
    stored?.similarCases || [],
  );

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  useEffect(() => {
    saveSession({
      sessionId,
      messages,
      caseInfo,
      isLoading,
      isCompleted,
      currentGuide,
      keyFactors,
      similarCases,
    });
  }, [sessionId, caseInfo, isCompleted, currentGuide, keyFactors, similarCases]);

  const toHistoryMessages = (list: DisplayMessage[]): ChatMessage[] =>
    list
      .filter((m) => !m.isTyping && m.role !== 'system')
      .slice(-20)
      .map((m) => ({
        role: m.role as MessageRole,
        content: m.content,
        timestamp: m.timestamp.toISOString(),
      }));

  const addUserMessage = useCallback((content: string) => {
    const msg: DisplayMessage = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, msg]);
    return msg;
  }, []);

  const addAssistantMessage = useCallback(
    (
      content: string,
      options: {
        references?: string[];
        guideQuestion?: GuideQuestion | null;
        isTyping?: boolean;
      } = {},
    ) => {
      const msg: DisplayMessage = {
        id: uuidv4(),
        role: 'assistant',
        content,
        timestamp: new Date(),
        references: options.references,
        guideQuestion: options.guideQuestion || null,
        isTyping: options.isTyping,
      };
      setMessages((prev) => [...prev, msg]);
      return msg;
    },
    [],
  );

  const updateLastAssistant = useCallback(
    (updates: Partial<DisplayMessage>) => {
      setMessages((prev) => {
        const lastIdx = [...prev].reverse().findIndex((m) => m.role === 'assistant');
        if (lastIdx === -1) return prev;
        const realIdx = prev.length - 1 - lastIdx;
        const newList = [...prev];
        newList[realIdx] = { ...newList[realIdx], ...updates };
        return newList;
      });
    },
    [],
  );

  const sendMessage = useCallback(
    async (userInput: string) => {
      const trimmed = userInput.trim();
      if (!trimmed || isLoading) return;

      const safety = checkInputSafety(trimmed);
      if (!safety.safe) {
        antdMessage.warning({
          content: safety.reason || '输入内容存在安全风险，请规范表述。',
          duration: 4,
        });
        console.warn('[前端安全拦截]', safety.matched);
        return;
      }

      addUserMessage(trimmed);
      setIsLoading(true);
      setCurrentGuide(null);

      addAssistantMessage('正在分析案情并检索相关法条...', { isTyping: true });

      try {
        const history = toHistoryMessages(messages);
        const response = await consultingApi.chat({
          session_id: sessionId,
          user_message: trimmed,
          case_info: caseInfo || null,
          history,
        });

        setCaseInfo(response.case_info);
        setIsCompleted(response.is_completed);
        setCurrentGuide(response.guide_next || null);
        if (response.key_factors) {
          setKeyFactors(response.key_factors);
        }
        if (response.similar_cases && response.similar_cases.length > 0) {
          setSimilarCases(response.similar_cases);
        }

        updateLastAssistant({
          content: response.answer,
          isTyping: false,
          references: response.references,
          guideQuestion: response.guide_next || null,
        });
      } catch (err: any) {
        const errorMsg =
          err?.response?.data?.detail ||
          err?.message ||
          '抱歉，咨询服务暂时不可用，请稍后重试或拨打法律援助热线 12348。';
        updateLastAssistant({
          content: `❌ ${errorMsg}`,
          isTyping: false,
        });
      } finally {
        setIsLoading(false);
      }
    },
    [
      sessionId,
      caseInfo,
      isLoading,
      messages,
      addUserMessage,
      addAssistantMessage,
      updateLastAssistant,
    ],
  );

  const resetChat = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    window.location.reload();
  }, []);

  return {
    sessionId,
    messages,
    caseInfo,
    isLoading,
    isCompleted,
    currentGuide,
    keyFactors,
    similarCases,
    sendMessage,
    resetChat,
    messagesEndRef,
  };
}
