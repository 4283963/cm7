import React from 'react';
import { Sparkles, ChevronRight } from 'lucide-react';
import { Tag, Divider } from 'antd';
import type { GuideQuestion } from '@/types';

interface GuideQuestionCardProps {
  guide: GuideQuestion | null | undefined;
  onSelect?: (value: string) => void;
  onUseText?: () => void;
  compact?: boolean;
}

const DISPUTE_ICONS: Record<string, string> = {
  劳动纠纷: '💼',
  合同纠纷: '📄',
  房产纠纷: '🏠',
  婚姻家庭: '👨‍👩‍👧',
  继承纠纷: '📜',
  侵权纠纷: '🛡️',
  交通事故: '🚗',
  刑事案件: '⚖️',
  行政纠纷: '🏛️',
  其他纠纷: '❓',
};

export const GuideQuestionCard: React.FC<GuideQuestionCardProps> = ({
  guide,
  onSelect,
  compact = false,
}) => {
  if (!guide) return null;

  const isDisputeType = guide.step === 'dispute_type';

  return (
    <div
      className={`mt-3 rounded-xl border-2 border-dashed border-primary-200 bg-gradient-to-br from-primary-50/80 to-white overflow-hidden transition ${
        compact ? 'p-3' : 'p-4'
      }`}
    >
      <div className="flex items-start gap-2.5 mb-3">
        <div className="p-1.5 rounded-lg bg-primary-100 text-primary-700 mt-0.5 flex-shrink-0">
          <Sparkles className="w-4 h-4" />
        </div>
        <div className="flex-1">
          <div className="text-xs font-semibold text-primary-700 mb-0.5 flex items-center gap-1">
            AI 引导提问 <ChevronRight className="w-3 h-3" />
          </div>
          <div className="text-sm text-gray-800 leading-relaxed">
            {guide.question}
          </div>
          {guide.required && (
            <Tag color="red" className="!mt-1.5 !mx-0 !text-[10px] !py-0.5">
              必填项
            </Tag>
          )}
        </div>
      </div>

      {guide.options && guide.options.length > 0 && (
        <>
          <Divider className="!my-3" plain>
            <span className="text-xs text-gray-400 font-medium">
              点击下方选项快速选择
            </span>
          </Divider>
          <div
            className={`grid gap-2 ${
              isDisputeType
                ? 'grid-cols-2 sm:grid-cols-3 md:grid-cols-5'
                : 'grid-cols-2 sm:grid-cols-3'
            }`}
          >
            {guide.options.map((opt, idx) => {
              const icon = DISPUTE_ICONS[opt];
              return (
                <button
                  key={idx}
                  onClick={() => onSelect?.(opt)}
                  className={`group text-left p-2.5 rounded-lg border transition-all hover:-translate-y-0.5 ${
                    isDisputeType
                      ? 'bg-white hover:bg-primary-50 border-gray-200 hover:border-primary-300 hover:shadow-md'
                      : 'bg-white hover:bg-blue-50 border-gray-200 hover:border-blue-300'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    {isDisputeType && (
                      <span className="text-lg flex-shrink-0">{icon}</span>
                    )}
                    <span
                      className={`text-sm ${
                        isDisputeType
                          ? 'font-medium text-gray-700 group-hover:text-primary-700'
                          : 'text-gray-700 group-hover:text-blue-700'
                      }`}
                    >
                      {opt}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};
