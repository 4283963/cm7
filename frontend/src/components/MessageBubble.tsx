import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, Bot, Loader2, BookOpen, Link2 } from 'lucide-react';
import { Tooltip } from 'antd';
import dayjs from 'dayjs';
import type { DisplayMessage } from '@/types';
import { GuideQuestionCard } from './GuideQuestionCard';

interface MessageBubbleProps {
  message: DisplayMessage;
  onSelectOption?: (value: string) => void;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onSelectOption }) => {
  const isUser = message.role === 'user';
  const isTyping = message.isTyping;

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center shadow-sm ${
          isUser
            ? 'bg-gradient-to-br from-primary-500 to-primary-700 text-white'
            : 'bg-gradient-to-br from-law-gold to-amber-600 text-white'
        }`}
      >
        {isUser ? (
          <User className="w-5 h-5" strokeWidth={2.2} />
        ) : (
          <Bot className="w-5 h-5" strokeWidth={2.2} />
        )}
      </div>

      <div className={`flex flex-col gap-1 max-w-[80%] ${isUser ? 'items-end' : 'items-start'} flex-1`}>
        <div
          className={`rounded-2xl px-4 py-3 shadow-sm ${
            isTyping ? 'bg-white/70 border border-dashed border-gray-300' : ''
          } ${
            isUser
              ? 'bg-gradient-to-br from-primary-600 to-primary-700 text-white rounded-tr-sm'
              : 'bg-white border border-gray-100 text-gray-800 rounded-tl-sm'
          }`}
        >
          {isTyping ? (
            <div className="flex items-center gap-2 text-gray-500">
              <Loader2 className="w-4 h-4 animate-spin text-primary-500" />
              <span className="text-sm">{message.content}</span>
            </div>
          ) : isUser ? (
            <div className="text-sm whitespace-pre-wrap leading-relaxed">
              {message.content}
            </div>
          ) : (
            <div className="markdown-body">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h3: ({ children }) => (
                    <h3 className="!text-[15px] !font-bold !text-primary-700 !border-l-4 !border-primary-500 !pl-2 !mt-4 !mb-2 first:!mt-0">
                      {children}
                    </h3>
                  ),
                  p: ({ children }) => <p className="!my-2 !leading-7">{children}</p>,
                  ul: ({ children }) => (
                    <ul className="!my-2 !pl-5 list-disc space-y-0.5">{children}</ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="!my-2 !pl-5 list-decimal space-y-0.5">{children}</ol>
                  ),
                  li: ({ children }) => <li className="!leading-7">{children}</li>,
                  strong: ({ children }) => (
                    <strong className="!text-primary-700 !font-semibold">{children}</strong>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className="!border-l-4 !border-law-gold/60 !bg-amber-50/60 !pl-3 !py-1.5 !my-2 !rounded-r-md text-gray-600 italic">
                      {children}
                    </blockquote>
                  ),
                  code: ({ children }) => (
                    <code className="bg-gray-100 px-1.5 py-0.5 rounded text-primary-700 text-[13px] font-mono">
                      {children}
                    </code>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {!isTyping && !isUser && message.references && message.references.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5 mt-1 px-1">
            <Tooltip title="本回答依据的法律条文">
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <BookOpen className="w-3.5 h-3.5" />
                <span>引用法条：</span>
              </div>
            </Tooltip>
            {message.references.map((ref, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1 text-[11px] bg-gray-50 text-gray-600 border border-gray-200 px-2 py-0.5 rounded-md hover:bg-primary-50 hover:border-primary-200 hover:text-primary-700 transition cursor-help"
              >
                <Link2 className="w-3 h-3 opacity-60" />
                {ref}
              </span>
            ))}
          </div>
        )}

        {!isTyping && !isUser && message.guideQuestion && (
          <div className="w-full mt-2">
            <GuideQuestionCard
              guide={message.guideQuestion}
              onSelect={onSelectOption}
              compact
            />
          </div>
        )}

        <Tooltip title={dayjs(message.timestamp).format('YYYY-MM-DD HH:mm:ss')}>
          <span className="text-[11px] text-gray-400 px-1">
            {dayjs(message.timestamp).format('HH:mm')}
          </span>
        </Tooltip>
      </div>
    </div>
  );
};
