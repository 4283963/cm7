export type MessageRole = 'user' | 'assistant' | 'system';

export type GuideStep =
  | 'greeting'
  | 'dispute_type'
  | 'time'
  | 'location'
  | 'details'
  | 'parties'
  | 'completed';

export type DisputeType =
  | '劳动纠纷'
  | '合同纠纷'
  | '房产纠纷'
  | '婚姻家庭'
  | '继承纠纷'
  | '侵权纠纷'
  | '交通事故'
  | '刑事案件'
  | '行政纠纷'
  | '其他纠纷';

export interface CaseInfo {
  dispute_type?: DisputeType | null;
  incident_time?: string | null;
  incident_location?: string | null;
  parties?: string | null;
  details?: string | null;
  evidence?: string | null;
  demands?: string | null;
  extra_fields?: Record<string, any>;
}

export interface ChatMessage {
  role: MessageRole;
  content: string;
  timestamp: string;
}

export interface GuideQuestion {
  step: GuideStep;
  question: string;
  options?: string[];
  required: boolean;
}

export interface RetrievedLaw {
  law_id: string;
  title: string;
  chapter?: string | null;
  article: string;
  content: string;
  similarity: number;
  law_source?: string | null;
}

export interface CaseKeyFactors {
  dispute_type?: string | null;
  amount_involved?: string | null;
  has_written_evidence?: string | null;
  limitation_period?: string | null;
  party_relationship?: string | null;
  location?: string | null;
  extra_factors?: Record<string, any>;
}

export interface SimilarCase {
  id?: number | null;
  case_number: string;
  title: string;
  dispute_type: string;
  court_name?: string | null;
  province?: string | null;
  city?: string | null;
  trial_date?: string | null;
  case_level?: string | null;
  facts?: string | null;
  judgment_result?: string | null;
  applicable_laws?: string[] | null;
  key_factors?: Record<string, any> | null;
  amount_involved?: string | null;
  has_written_evidence?: string | null;
  limitation_period?: string | null;
  tags?: string[] | null;
  summary?: string | null;
  similarity_score: number;
}

export interface ChatRequest {
  session_id: string;
  user_message: string;
  case_info?: CaseInfo | null;
  history?: ChatMessage[];
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  guide_next?: GuideQuestion | null;
  case_info: CaseInfo;
  retrieved_laws: RetrievedLaw[];
  is_completed: boolean;
  references: string[];
  key_factors?: CaseKeyFactors | null;
  similar_cases: SimilarCase[];
}

export interface DisplayMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  isTyping?: boolean;
  references?: string[];
  guideQuestion?: GuideQuestion | null;
}
