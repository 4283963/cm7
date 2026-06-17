import React, { useState } from 'react';
import {
  FileText,
  Building2,
  MapPin,
  CalendarDays,
  Gavel,
  Scale,
  ExternalLink,
  X,
  BookOpen,
  Award,
  AlertTriangle,
} from 'lucide-react';
import { Tag, Button, Modal, Empty, Divider, Progress, Tooltip } from 'antd';
import type { SimilarCase } from '@/types';

interface Props {
  cases: SimilarCase[];
}

const similarityLevel = (score: number) => {
  if (score >= 0.75) return { color: '#16a34a', label: '高度相似', percent: Math.round(score * 100) };
  if (score >= 0.55) return { color: '#0284c7', label: '较为相似', percent: Math.round(score * 100) };
  return { color: '#ca8a04', label: '参考案例', percent: Math.round(score * 100) };
};

const CaseCard: React.FC<{ item: SimilarCase; index: number; onClick: () => void }> = ({
  item,
  index,
  onClick,
}) => {
  const level = similarityLevel(item.similarity_score);
  return (
    <button
      onClick={onClick}
      className="w-full text-left rounded-xl border border-gray-200 bg-white p-3.5 hover:border-primary-300 hover:shadow-md hover:-translate-y-0.5 transition-all group"
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <div
            className="w-6 h-6 rounded-md flex items-center justify-center text-[11px] font-bold text-white flex-shrink-0"
            style={{ background: level.color }}
          >
            #{index + 1}
          </div>
          <div className="min-w-0">
            <div className="text-xs font-bold text-gray-800 truncate group-hover:text-primary-700">
              {item.title}
            </div>
            <div className="text-[10px] text-gray-500 truncate">{item.case_number}</div>
          </div>
        </div>
        <Tooltip title={`相似度 ${level.percent}%`}>
          <Progress
            type="circle"
            size={36}
            percent={level.percent}
            strokeColor={level.color}
            format={() => <span className="text-[9px] font-bold" style={{ color: level.color }}>{level.percent}%</span>}
            showInfo
            className="!m-0 flex-shrink-0"
          />
        </Tooltip>
      </div>

      {item.summary && (
        <p className="text-[11px] text-gray-600 leading-relaxed line-clamp-2 mb-2">
          {item.summary}
        </p>
      )}

      <div className="flex flex-wrap gap-1">
        {item.dispute_type && (
          <Tag color="blue" className="!m-0 !text-[10px] !py-0 !px-1.5">
            {item.dispute_type}
          </Tag>
        )}
        {item.amount_involved && (
          <Tag color="gold" className="!m-0 !text-[10px] !py-0 !px-1.5">
            金额：{item.amount_involved}
          </Tag>
        )}
        {item.has_written_evidence && (
          <Tag color={item.has_written_evidence === '有' ? 'green' : 'orange'} className="!m-0 !text-[10px] !py-0 !px-1.5">
            证据：{item.has_written_evidence}
          </Tag>
        )}
      </div>
    </button>
  );
};

const CaseDetailModal: React.FC<{
  open: boolean;
  item: SimilarCase | null;
  onClose: () => void;
}> = ({ open, item, onClose }) => {
  if (!item) return null;
  const level = similarityLevel(item.similarity_score);

  return (
    <Modal
      open={open}
      onCancel={onClose}
      title={null}
      footer={[
        <Button key="close" onClick={onClose}>
          关闭
        </Button>,
      ]}
      width={720}
      destroyOnClose
      closeIcon={<X className="w-4 h-4" />}
      className="case-detail-modal"
    >
      <div className="-mx-6 -mt-6 px-6 py-4 bg-gradient-to-r from-law-navy via-primary-700 to-primary-600 text-white rounded-t-lg mb-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <Tag color={level.color} className="!m-0 !text-[11px]">
                {level.label} · {level.percent}% 匹配
              </Tag>
              <Tag color="rgba(255,255,255,0.2)" className="!m-0 !text-[11px] !text-white !border-white/30">
                {item.case_level || '一审'}
              </Tag>
            </div>
            <h3 className="text-lg font-bold leading-snug">{item.title}</h3>
            <div className="text-xs text-white/70 mt-1 font-mono">{item.case_number}</div>
          </div>
          <div className="text-center">
            <Progress
              type="dashboard"
              size={72}
              percent={level.percent}
              strokeColor="#fbbf24"
              trailColor="rgba(255,255,255,0.2)"
              format={(p) => <span className="text-xl font-bold text-law-gold">{p}%</span>}
            />
            <div className="text-[10px] text-white/70 -mt-2">整体相似度</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-5">
        <div className="flex items-start gap-2 p-3 rounded-lg bg-gray-50">
          <Building2 className="w-4 h-4 text-primary-600 mt-0.5 flex-shrink-0" />
          <div>
            <div className="text-[11px] text-gray-500">审理法院</div>
            <div className="text-sm font-medium text-gray-800">{item.court_name || '—'}</div>
          </div>
        </div>
        <div className="flex items-start gap-2 p-3 rounded-lg bg-gray-50">
          <CalendarDays className="w-4 h-4 text-primary-600 mt-0.5 flex-shrink-0" />
          <div>
            <div className="text-[11px] text-gray-500">审理日期</div>
            <div className="text-sm font-medium text-gray-800">{item.trial_date || '—'}</div>
          </div>
        </div>
        <div className="flex items-start gap-2 p-3 rounded-lg bg-gray-50">
          <MapPin className="w-4 h-4 text-primary-600 mt-0.5 flex-shrink-0" />
          <div>
            <div className="text-[11px] text-gray-500">审理地区</div>
            <div className="text-sm font-medium text-gray-800">
              {[item.province, item.city].filter(Boolean).join(' ') || '—'}
            </div>
          </div>
        </div>
        <div className="flex items-start gap-2 p-3 rounded-lg bg-gray-50">
          <Scale className="w-4 h-4 text-primary-600 mt-0.5 flex-shrink-0" />
          <div>
            <div className="text-[11px] text-gray-500">纠纷类型</div>
            <div className="text-sm font-medium text-gray-800">{item.dispute_type || '—'}</div>
          </div>
        </div>
      </div>

      {(item.amount_involved || item.has_written_evidence || item.limitation_period) && (
        <div className="mb-5 p-3 rounded-lg border border-amber-200 bg-amber-50/60">
          <div className="flex items-center gap-1.5 text-xs font-bold text-amber-800 mb-2">
            <Gavel className="w-3.5 h-3.5" /> 案情要素
          </div>
          <div className="flex flex-wrap gap-2">
            {item.amount_involved && (
              <Tag color="gold">涉案金额：{item.amount_involved}</Tag>
            )}
            {item.has_written_evidence && (
              <Tag color={item.has_written_evidence === '有' ? 'green' : 'orange'}>
                书面证据：{item.has_written_evidence}
              </Tag>
            )}
            {item.limitation_period && (
              <Tag color={item.limitation_period === '未过' ? 'green' : item.limitation_period === '已过' ? 'red' : 'orange'}>
                诉讼时效：{item.limitation_period}
              </Tag>
            )}
          </div>
        </div>
      )}

      {item.tags && item.tags.length > 0 && (
        <div className="mb-5">
          <div className="flex items-center gap-1.5 text-xs font-bold text-gray-700 mb-2">
            <Award className="w-3.5 h-3.5 text-law-gold" /> 案件标签
          </div>
          <div className="flex flex-wrap gap-1.5">
            {item.tags.map((t, i) => (
              <Tag key={i} color="blue" className="!m-0">
                {t}
              </Tag>
            ))}
          </div>
        </div>
      )}

      {item.facts && (
        <div className="mb-5">
          <div className="flex items-center gap-1.5 text-xs font-bold text-gray-700 mb-2">
            <FileText className="w-3.5 h-3.5 text-primary-600" /> 案件事实
          </div>
          <div className="text-sm text-gray-700 leading-7 p-3.5 rounded-lg bg-gray-50 whitespace-pre-wrap">
            {item.facts}
          </div>
        </div>
      )}

      {item.judgment_result && (
        <div className="mb-5">
          <div className="flex items-center gap-1.5 text-xs font-bold text-gray-700 mb-2">
            <Gavel className="w-3.5 h-3.5 text-law-red" /> 裁判结果
          </div>
          <div className="text-sm text-gray-800 leading-7 p-3.5 rounded-lg border-l-4 border-primary-500 bg-primary-50/60 whitespace-pre-wrap font-medium">
            {item.judgment_result}
          </div>
        </div>
      )}

      {item.applicable_laws && item.applicable_laws.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 text-xs font-bold text-gray-700 mb-2">
            <BookOpen className="w-3.5 h-3.5 text-law-gold" /> 适用法条
          </div>
          <div className="space-y-1.5">
            {item.applicable_laws.map((law, i) => (
              <div
                key={i}
                className="flex items-start gap-2 text-sm p-2 rounded-md bg-white border border-gray-100 hover:bg-amber-50/60 hover:border-amber-200 transition"
              >
                <ExternalLink className="w-3.5 h-3.5 text-gray-400 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">{law}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <Divider className="!my-4" />

      <div className="flex items-start gap-2 p-3 rounded-lg bg-red-50/60 border border-red-100">
        <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
        <div className="text-xs text-red-700 leading-6">
          <span className="font-bold">免责声明：</span>
          本判例仅作为相似案例参考，不构成对您案件的法律意见或判决预测。
          具体案件需结合实际证据和情况判断，建议携带材料前往当地法律援助中心或咨询执业律师。
        </div>
      </div>
    </Modal>
  );
};

export const SimilarCasesPanel: React.FC<Props> = ({ cases }) => {
  const [selected, setSelected] = useState<SimilarCase | null>(null);

  if (!cases || cases.length === 0) return null;

  return (
    <>
      <div className="rounded-xl border border-primary-200 bg-gradient-to-br from-primary-50/60 to-white shadow-sm overflow-hidden">
        <div className="px-4 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Scale className="w-4 h-4 text-law-gold" strokeWidth={2.2} />
            <div>
              <div className="text-sm font-bold">相似法院判例</div>
              <div className="text-[11px] text-white/70">基于案情要素智能匹配</div>
            </div>
          </div>
          <Tag color="gold" className="!m-0">
            共 {cases.length} 条
          </Tag>
        </div>

        <div className="p-3 space-y-2.5">
          {cases.map((item, index) => (
            <CaseCard
              key={item.case_number + index}
              item={item}
              index={index}
              onClick={() => setSelected(item)}
            />
          ))}
        </div>

        <div className="px-3 pb-3">
          <div className="text-[10px] text-gray-400 text-center leading-5">
            💡 点击卡片查看完整判例详情
            <br />
            判例仅供参考，具体案件请以法院生效判决为准
          </div>
        </div>
      </div>

      <CaseDetailModal
        open={!!selected}
        item={selected}
        onClose={() => setSelected(null)}
      />
    </>
  );
};

export const CasesEmpty: React.FC = () => (
  <div className="rounded-xl border border-dashed border-gray-200 bg-gray-50/50 p-5">
    <Empty
      image={Empty.PRESENTED_IMAGE_SIMPLE}
      description={
        <div className="text-center">
          <div className="text-sm text-gray-500 mb-1">暂未匹配到相似判例</div>
          <div className="text-[11px] text-gray-400">
            完善案情信息后，系统将自动为您检索相关判例
          </div>
        </div>
      }
      className="!py-2"
    />
  </div>
);
