import React from 'react';
import { Scale, RefreshCw, Phone } from 'lucide-react';
import { Button, Tooltip } from 'antd';

interface HeaderProps {
  onReset: () => void;
  isCompleted: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onReset, isCompleted }) => {
  return (
    <header className="bg-gradient-to-r from-law-navy via-primary-700 to-primary-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-white/15 p-2 rounded-lg backdrop-blur-sm">
            <Scale className="w-7 h-7 text-law-gold" strokeWidth={2.2} />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-wide">法律援助中心 AI 咨询系统</h1>
            <p className="text-xs text-white/70 mt-0.5">
              Legal Aid AI Consulting · 基于真实法条的智能咨询
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Tooltip title="法律援助热线">
            <div className="hidden sm:flex items-center gap-1.5 bg-white/10 px-3 py-1.5 rounded-full backdrop-blur-sm">
              <Phone className="w-4 h-4 text-law-gold" />
              <span className="text-sm font-medium">12348</span>
            </div>
          </Tooltip>

          {isCompleted && (
            <span className="hidden md:inline-block bg-law-gold/90 text-law-navy px-3 py-1 rounded-full text-xs font-semibold">
              ✓ 案情收集完成
            </span>
          )}

          <Tooltip title="开始新的咨询">
            <Button
              type="text"
              onClick={onReset}
              icon={<RefreshCw className="w-4 h-4" />}
              className="!text-white hover:!bg-white/15 !border-0"
              size="small"
            >
              新咨询
            </Button>
          </Tooltip>
        </div>
      </div>
    </header>
  );
};
