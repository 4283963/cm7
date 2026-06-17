import React from 'react';
import {
  Gavel,
  MapPin,
  CalendarDays,
  Users,
  Scale,
  FileText,
  AlertCircle,
  Hash,
} from 'lucide-react';
import { Tag } from 'antd';
import type { CaseKeyFactors } from '@/types';

interface Props {
  factors: CaseKeyFactors | null | undefined;
}

const Row: React.FC<{ icon: React.ReactNode; label: string; value?: string | null }> = ({
  icon,
  label,
  value,
}) => (
  <div className="flex items-start gap-2">
    <div className="mt-0.5 text-primary-500">{icon}</div>
    <div className="flex-1 min-w-0">
      <div className="text-[11px] text-gray-500">{label}</div>
      <div className="text-sm text-gray-800 font-medium break-words">
        {value || <span className="text-gray-400 italic font-normal">识别中...</span>}
      </div>
    </div>
  </div>
);

export const KeyFactorsCard: React.FC<Props> = ({ factors }) => {
  if (!factors) return null;

  const hasAny = Object.values(factors).some(
    (v) => v !== undefined && v !== null && v !== '' && (typeof v !== 'object' || Object.keys(v).length > 0),
  );
  if (!hasAny) return null;

  const limitationColor: Record<string, string> = {
    未过: 'green',
    已过: 'red',
    待查: 'orange',
  };

  return (
    <div className="rounded-xl border border-amber-200 bg-gradient-to-br from-amber-50/70 to-white p-4 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <div className="p-1.5 rounded-lg bg-law-gold/20">
          <Gavel className="w-4 h-4 text-law-red" strokeWidth={2.2} />
        </div>
        <div>
          <div className="text-sm font-bold text-gray-800">AI 提炼核心要素</div>
          <div className="text-[11px] text-gray-500">基于案情描述自动识别</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Row
          icon={<Scale className="w-3.5 h-3.5" />}
          label="纠纷类型"
          value={factors.dispute_type}
        />
        <Row
          icon={<Hash className="w-3.5 h-3.5" />}
          label="涉案金额"
          value={factors.amount_involved}
        />
        <Row
          icon={<FileText className="w-3.5 h-3.5" />}
          label="书面证据"
          value={factors.has_written_evidence}
        />
        <div className="flex items-start gap-2">
          <div className="mt-0.5 text-primary-500">
            <CalendarDays className="w-3.5 h-3.5" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-[11px] text-gray-500">诉讼时效</div>
            <div>
              {factors.limitation_period ? (
                <Tag color={limitationColor[factors.limitation_period] || 'default'} className="!m-0 !text-xs">
                  {factors.limitation_period}
                </Tag>
              ) : (
                <span className="text-gray-400 italic text-sm">识别中...</span>
              )}
            </div>
          </div>
        </div>
        {factors.party_relationship && (
          <Row
            icon={<Users className="w-3.5 h-3.5" />}
            label="当事人关系"
            value={factors.party_relationship}
          />
        )}
        {factors.location && (
          <Row
            icon={<MapPin className="w-3.5 h-3.5" />}
            label="发生地"
            value={factors.location}
          />
        )}
      </div>

      {factors.extra_factors && Object.keys(factors.extra_factors).length > 0 && (
        <div className="mt-3 pt-3 border-t border-dashed border-amber-200">
          <div className="text-[11px] text-gray-500 mb-1.5 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" /> 其他识别要素
          </div>
          <div className="flex flex-wrap gap-1">
            {Object.entries(factors.extra_factors).map(([k, v]) => (
              <Tag key={k} color="blue" className="!m-0 !text-[11px]">
                {k}: {String(v)}
              </Tag>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
