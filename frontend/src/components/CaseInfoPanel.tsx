import React from 'react';
import {
  FileText,
  Calendar,
  MapPin,
  Users,
  AlertCircle,
  FolderCheck,
  Tag,
  ChevronRight,
  CheckCircle2,
  Clock,
} from 'lucide-react';
import { Card, Tag as AntTag, Empty, Divider } from 'antd';
import type { CaseInfo, GuideStep } from '@/types';

interface CaseInfoPanelProps {
  caseInfo: CaseInfo;
  currentStep: GuideStep | null;
}

const STEP_ORDER: GuideStep[] = [
  'dispute_type',
  'time',
  'location',
  'parties',
  'details',
  'completed',
];

const STEP_LABELS: Record<GuideStep, string> = {
  greeting: '欢迎',
  dispute_type: '纠纷类型',
  time: '事件时间',
  location: '发生地点',
  parties: '当事人信息',
  details: '案情详情',
  completed: '已完成',
};

const progressPct = (step: GuideStep | null) => {
  const idx = step ? STEP_ORDER.indexOf(step) : 0;
  return Math.round(((idx < 0 ? 0 : idx) / (STEP_ORDER.length - 1)) * 100);
};

export const CaseInfoPanel: React.FC<CaseInfoPanelProps> = ({ caseInfo, currentStep }) => {
  const progress = progressPct(currentStep || null);
  const pct = Math.min(progress, 100);

  const FieldItem: React.FC<{
    icon: React.ReactNode;
    label: string;
    value?: string | null;
    highlight?: boolean;
  }> = ({ icon, label, value, highlight }) => (
    <div
      className={`flex gap-2.5 p-3 rounded-lg transition ${
        highlight ? 'bg-primary-50 border border-primary-100' : 'bg-gray-50'
      }`}
    >
      <div
        className={`mt-0.5 ${highlight ? 'text-primary-600' : 'text-gray-400'}`}
      >
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-xs font-medium text-gray-500 mb-0.5">{label}</div>
        {value ? (
          <div className="text-sm text-gray-800 break-words leading-relaxed">
            {value}
          </div>
        ) : (
          <div className="text-xs text-gray-400 italic">待补充...</div>
        )}
      </div>
      {value && <CheckCircle2 className="w-4 h-4 text-green-500 mt-1 flex-shrink-0" />}
    </div>
  );

  const tags: { label: string; color?: string }[] = [];
  if (caseInfo.dispute_type) {
    tags.push({ label: caseInfo.dispute_type, color: 'blue' });
  }

  return (
    <Card
      className="!rounded-xl !shadow-sm border-0 sticky top-4"
      title={
        <div className="flex items-center gap-2">
          <FolderCheck className="w-5 h-5 text-primary-600" />
          <span className="font-semibold text-gray-800">案情档案</span>
        </div>
      }
      extra={
        <span className="text-xs font-medium text-primary-600 bg-primary-50 px-2 py-0.5 rounded-full">
          {pct}% 完成
        </span>
      }
    >
      <div className="mb-5">
        <div className="flex justify-between text-xs text-gray-500 mb-1.5">
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" /> 信息收集进度
          </span>
          <span>{STEP_LABELS[currentStep || 'greeting']}</span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary-500 to-law-gold rounded-full transition-all duration-500"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {tags.length > 0 && (
        <div className="mb-4 flex flex-wrap gap-1.5">
          {tags.map((t, i) => (
            <AntTag key={i} color={t.color} className="!m-0">
              <Tag className="w-3 h-3 inline mr-0.5 -mt-0.5" />
              {t.label}
            </AntTag>
          ))}
        </div>
      )}

      <div className="space-y-2.5">
        <FieldItem
          icon={<AlertCircle className="w-4 h-4" />}
          label="纠纷类型"
          value={caseInfo.dispute_type}
          highlight={currentStep === 'dispute_type'}
        />
        <FieldItem
          icon={<Calendar className="w-4 h-4" />}
          label="事件时间"
          value={caseInfo.incident_time}
          highlight={currentStep === 'time'}
        />
        <FieldItem
          icon={<MapPin className="w-4 h-4" />}
          label="发生地点"
          value={caseInfo.incident_location}
          highlight={currentStep === 'location'}
        />
        <FieldItem
          icon={<Users className="w-4 h-4" />}
          label="当事人信息"
          value={caseInfo.parties}
          highlight={currentStep === 'parties'}
        />
        <FieldItem
          icon={<FileText className="w-4 h-4" />}
          label="案情详情"
          value={caseInfo.details}
          highlight={currentStep === 'details'}
        />
      </div>

      <Divider className="my-5" />

      <div>
        <div className="text-xs font-semibold text-gray-500 mb-2.5 flex items-center gap-1.5">
          <ChevronRight className="w-3 h-3" /> 收集流程
        </div>
        <ol className="space-y-1.5">
          {STEP_ORDER.slice(0, -1).map((step) => {
            const stepIdx = STEP_ORDER.indexOf(step);
            const curIdx = currentStep ? STEP_ORDER.indexOf(currentStep) : -1;
            const state =
              stepIdx < curIdx || currentStep === 'completed'
                ? 'done'
                : step === currentStep
                ? 'active'
                : 'todo';
            return (
              <li key={step} className="flex items-center gap-2 text-sm">
                <div
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    state === 'done'
                      ? 'bg-green-500 text-white'
                      : state === 'active'
                      ? 'bg-primary-600 text-white ring-2 ring-primary-100'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {state === 'done' ? '✓' : stepIdx + 1}
                </div>
                <span
                  className={
                    state === 'active'
                      ? 'font-medium text-primary-700'
                      : state === 'done'
                      ? 'text-gray-600 line-through/40'
                      : 'text-gray-400'
                  }
                >
                  {STEP_LABELS[step]}
                </span>
              </li>
            );
          })}
        </ol>
      </div>

      {!caseInfo.dispute_type && !caseInfo.incident_time && !caseInfo.details && (
        <div className="mt-5">
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={
              <span className="text-xs text-gray-400">
                通过对话引导完善案情
              </span>
            }
            className="!py-3"
          />
        </div>
      )}
    </Card>
  );
};
