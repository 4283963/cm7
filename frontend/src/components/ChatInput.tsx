import React, { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Send, Paperclip, Info, Loader2 } from 'lucide-react';
import { Button, Input, Tooltip } from 'antd';
import type { GuideQuestion } from '@/types';
import { GuideQuestionCard } from './GuideQuestionCard';

const { TextArea } = Input;

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  currentGuide: GuideQuestion | null;
  disabled?: boolean;
}

const QUICK_SUGGESTIONS = [
  '公司拖欠工资怎么办？',
  '老公出轨我想离婚财产怎么分？',
  '被车撞了对方不赔偿怎么处理？',
  '房东不退押金找哪个部门？',
];

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  isLoading,
  currentGuide,
  disabled,
}) => {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [value]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || isLoading || disabled) return;
    onSend(trimmed);
    setValue('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleQuickSuggest = (text: string) => {
    if (isLoading || disabled) return;
    setValue(text);
    setTimeout(() => textareaRef.current?.focus(), 0);
  };

  const handleSelectOption = (opt: string) => {
    if (isLoading || disabled) return;
    onSend(opt);
  };

  return (
    <div className="border-t border-gray-200 bg-gradient-to-b from-white to-gray-50/50 px-4 sm:px-6 py-4">
      {currentGuide && (
        <div className="mb-3 max-w-4xl mx-auto">
          <GuideQuestionCard
            guide={currentGuide}
            onSelect={handleSelectOption}
          />
        </div>
      )}

      {!currentGuide && (
        <div className="mb-3 max-w-4xl mx-auto flex flex-wrap gap-2">
          <Tooltip title="点击快速填入咨询示例">
            <span className="inline-flex items-center gap-1 text-xs text-gray-500">
              <Info className="w-3 h-3" /> 快捷提问：
            </span>
          </Tooltip>
          {QUICK_SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              onClick={() => handleQuickSuggest(s)}
              disabled={isLoading}
              className="text-xs bg-white border border-gray-200 text-gray-600 px-2.5 py-1 rounded-full hover:bg-primary-50 hover:border-primary-200 hover:text-primary-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="max-w-4xl mx-auto">
        <div className="flex items-end gap-3 bg-white rounded-2xl border border-gray-200 focus-within:border-primary-400 focus-within:ring-4 focus-within:ring-primary-50 transition shadow-sm p-2">
          <Button
            type="text"
            icon={<Paperclip className="w-4 h-4 text-gray-400" />}
            disabled
            title="附件功能开发中"
            className="!border-0 !flex-shrink-0"
          />

          <TextArea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="请详细描述您的法律问题... (Enter 发送 / Shift+Enter 换行)"
            autoSize={false}
            rows={1}
            disabled={isLoading || disabled}
            className="!border-0 !shadow-none !resize-none !text-sm !leading-6 !focus:ring-0 !p-2 scrollbar-thin max-h-44"
          />

          <Tooltip title={value.trim() ? '发送咨询' : '请输入内容'}>
            <Button
              type="primary"
              onClick={handleSend}
              disabled={!value.trim() || isLoading || disabled}
              icon={
                isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )
              }
              size="large"
              className="!rounded-xl !px-5 !h-10 !flex-shrink-0"
            >
              {isLoading ? '处理中' : '发送'}
            </Button>
          </Tooltip>
        </div>

        <p className="text-[11px] text-gray-400 mt-2.5 text-center">
          ⚠️ 本系统基于 AI 大模型与中国现行法律条文提供咨询建议，仅供参考，不构成正式法律意见。
          具体案件请携带材料前往当地法律援助中心或拨打 12348。
        </p>
      </div>
    </div>
  );
};
