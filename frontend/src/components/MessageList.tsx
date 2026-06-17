import React, { forwardRef } from 'react';
import type { DisplayMessage } from '@/types';
import { MessageBubble } from './MessageBubble';

interface MessageListProps {
  messages: DisplayMessage[];
  onSelectOption?: (value: string) => void;
  messagesEndRef: React.RefObject<HTMLDivElement>;
}

export const MessageList = forwardRef<HTMLDivElement, MessageListProps>(
  ({ messages, onSelectOption }, ref) => {
    return (
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-6">
          {messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              onSelectOption={onSelectOption}
            />
          ))}
          <div ref={ref} />
        </div>
      </div>
    );
  },
);

MessageList.displayName = 'MessageList';
