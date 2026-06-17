export interface SafetyResult {
  safe: boolean;
  matched?: string[];
  reason?: string;
}

const PROMPT_INJECTION_REGEX: Array<{ pattern: RegExp; label: string }> = [
  {
    pattern:
      /(忽略|无视|忘掉|跳过|暂停|停止|解除|删除|重置).{0,20}(之前的|以上的|上述的|前面的|系统的|所有的|原来的|初始的).{0,20}(指令|规则|设定|设置|prompt|角色|身份|限制)/i,
    label: '身份/规则绕过尝试',
  },
  {
    pattern:
      /(现在起|从现在开始|假设|假装|扮演|想象你是|你现在是|你其实是|换个身份|作为|充当).{0,30}(不再是|不是|不要做|别做|而非|而不是).{0,20}(法律|律师|ai|助手|咨询)/i,
    label: '身份替换诱导',
  },
  {
    pattern:
      /(扮演|假设|假装|你是|你现在是|作为|充当).{0,30}(黑客|入侵者|破解者|攻击者|罪犯|骗子|小偷|毒贩|军师|走私犯)/i,
    label: '非法身份诱导',
  },
  {
    pattern:
      /(请|给我|告诉我|输出|显示|打印|泄露|透露|重复|复述).{0,15}(系统提示|system prompt|系统指令|初始指令|隐藏指令|prompt原文|你的设定|你的规则|内部指令)/i,
    label: '系统提示泄露探测',
  },
  {
    pattern: /(完成以上任务后|回答完后|之后|接下来|然后|与此同时).{0,20}(请你|帮我|告诉我|回答).{0,30}(忽略|无视|忘记|改变).{0,15}(规则|身份|限制)/i,
    label: '多轮攻击尝试',
  },
];

const ILLEGAL_KEYWORDS: Array<{ words: string[]; label: string }> = [
  {
    words: [
      '偷税漏税', '逃税', '避税方法', '怎么逃税', '怎么偷税', '虚开发票', '做假账',
      '账外账', '公转私避税', '拆分工资', '虚报成本', '费用套现',
    ],
    label: '税务违法',
  },
  {
    words: [
      '诈骗方法', '怎么诈骗', '电信诈骗', '杀猪盘', '套路贷', '高利贷', '非法集资',
      '庞氏骗局', '传销模式', '刷单诈骗', '钓鱼网站', '伪造证件', '办假证', '刻假章',
    ],
    label: '诈骗与伪造',
  },
  {
    words: [
      '黑客技术', '入侵网站', '破解密码', '盗号方法', 'ddos攻击', '注入漏洞',
      'webshell', '提权', '内网渗透', '脱库', '撞库', '盗刷', '外挂',
    ],
    label: '网络黑客',
  },
  {
    words: ['毒品制作', '制毒配方', '吸毒方法', '贩毒渠道', '怎么贩毒'],
    label: '毒品违法',
  },
  {
    words: ['怎么杀人', '杀人方法', '报复社会', '恐怖袭击', '爆炸物制作', '自制武器', '枪支制造', '雇凶杀人', '买凶'],
    label: '严重暴力犯罪',
  },
  {
    words: ['盗窃技巧', '怎么偷东西', '入室盗窃', '扒窃方法', '撬锁教程', '抢劫方法', '碰瓷技巧', '敲诈勒索'],
    label: '财产犯罪',
  },
  {
    words: ['赌博方法', '出千技巧', '作弊方法', '赌球技巧', '百家乐赢钱'],
    label: '赌博相关',
  },
  {
    words: ['怎么不被抓', '逃避侦查', '反侦察技巧', '销毁证据', '跑路方法', '偷渡', '洗钱方法', '资金外逃', '串供方法', '作伪证'],
    label: '逃避法律制裁',
  },
  {
    words: ['自杀方法', '怎么自残', '自残教程'],
    label: '自残倾向',
  },
  {
    words: ['钻法律空子', '规避法律', '打法律擦边球', '合法伤害权', '合法报复', '恶心人不犯法'],
    label: '诱导利用法律漏洞',
  },
];

const CONTEXT_SAFE_KEYWORDS = [
  '法律咨询', '律师', '法院', '起诉', '诉讼', '仲裁', '赔偿', '合同', '劳动',
  '工伤', '离婚', '交通事故', '遗产', '继承', '侵权', '消费者', '证据', '法律援助',
  '违法吗', '合法吗', '犯法吗', '犯罪吗', '会被抓吗',
];

export function checkInputSafety(text: string): SafetyResult {
  if (!text || !text.trim()) {
    return { safe: true };
  }
  const normalized = text.replace(/\s+/g, '').toLowerCase();
  const matched: string[] = [];

  for (const { pattern, label } of PROMPT_INJECTION_REGEX) {
    if (pattern.test(text) || pattern.test(normalized)) {
      matched.push(label);
    }
  }

  for (const { words, label } of ILLEGAL_KEYWORDS) {
    for (const w of words) {
      if (text.includes(w) || normalized.includes(w)) {
        matched.push(`${label}:${w}`);
        break;
      }
    }
  }

  if (matched.length > 0) {
    const contextSafe = CONTEXT_SAFE_KEYWORDS.some((k) => text.includes(k));
    if (contextSafe && matched.length <= 1) {
      return { safe: true };
    }
    return {
      safe: false,
      matched: Array.from(new Set(matched)),
      reason: '输入内容包含违规或越界信息，请规范表述您的法律问题。',
    };
  }

  return { safe: true };
}
