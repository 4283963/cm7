import React, { useMemo } from 'react';
import { useChat } from '@/hooks/useChat';
import { Header } from '@/components/Header';
import { CaseInfoPanel } from '@/components/CaseInfoPanel';
import { MessageList } from '@/components/MessageList';
import { ChatInput } from '@/components/ChatInput';
import { Alert } from 'antd';
import { Info } from 'lucide-react';

const App: React.FC = () => {
  const {
    messages,
    caseInfo,
    isLoading,
    isCompleted,
    currentGuide,
    sendMessage,
    resetChat,
    messagesEndRef,
  } = useChat();

  const currentStep = useMemo(() => {
    if (isCompleted) return 'completed';
    return currentGuide?.step || null;
  }, [currentGuide, isCompleted]);

  return (
    <div className="h-full flex flex-col bg-slate-50/60">
      <Header onReset={resetChat} isCompleted={isCompleted} />

      {isCompleted && (
        <div className="max-w-7xl w-full mx-auto px-4 pt-4">
          <Alert
            type="success"
            showIcon
            icon={<Info className="w-4 h-4 mt-0.5" />}
            message="案情信息已收集完成"
            description="以上法律分析基于您提供的信息生成。如信息有变动，可随时补充告知。如需进一步帮助，建议携带材料前往当地法律援助中心面询。"
            className="!rounded-xl !shadow-sm"
            closable
          />
        </div>
      )}

      <main className="flex-1 flex overflow-hidden max-w-7xl w-full mx-auto px-4 py-4">
        <div className="flex-1 flex flex-col lg:flex-row gap-6 overflow-hidden">
          <div className="flex-1 flex flex-col bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <MessageList
              messages={messages}
              onSelectOption={sendMessage}
              ref={messagesEndRef}
            />
            <ChatInput
              onSend={sendMessage}
              isLoading={isLoading}
              currentGuide={currentGuide}
            />
          </div>

          <aside className="hidden lg:block w-[360px] flex-shrink-0 overflow-y-auto scrollbar-thin -mr-2 pr-2">
            <CaseInfoPanel caseInfo={caseInfo} currentStep={currentStep} />
          </aside>
        </div>
      </main>
    </div>
  );
};

export default App;
