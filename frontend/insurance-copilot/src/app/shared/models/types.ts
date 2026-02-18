export interface AuthRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  refresh_token?: string;
  user: User;
  expiresIn: number;
}

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  createdAt: Date;
  role: 'broker' | 'admin' | 'user';
}

export interface RegisterRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  company?: string;
}

// ============ CHAT ============

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
  metadata?: {
    type?: 'text' | 'table' | 'quote' | 'analysis';
    data?: unknown;
  };
}

export interface ChatSession {
  id: string;
  userId: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messages: Message[];
}

export interface ChatMessageRequest {
  message: string;
  sessionId?: string;
  history?: Array<{ role: 'user' | 'assistant'; content: string }>;
}

export interface ChatMessageResponse {
  id: string;
  content: string;
  timestamp: Date;
  analysisResult?: QueryAnalysis;
  comparisonResult?: ComparisonResult;
}

// ============ ANÁLISIS DE QUERY ============

export interface QueryAnalysis {
  intent: 'quote' | 'conditions' | 'comparison' | 'general';
  confidence: number;
  extractedParameters: {
    vehicle?: {
      brand?: string;
      model?: string;
      type?: string;
      usage?: string;
      year?: number;
    };
    insurers?: string[];
    clauses?: string[];
    otherParams?: Record<string, unknown>;
  };
}

// ============ COTIZACIONES ============

export interface InsuranceQuote {
  id: string;
  insurer: string;
  premium: number;
  currency: string;
  coverage: {
    type: string;
    limit: string;
    description: string;
  };
  clausesHighlight?: string;
  metadata?: {
    responseTime: number;
    dataSource: 'database' | 'document';
  };
  link?: string;
}

export interface QuoteRequest {
  vehicle: {
    brand: string;
    model: string;
    year: number;
    type: string;
  };
  insurers?: string[];
  coverageType?: string;
}

export interface QuoteResponse {
  quotes: InsuranceQuote[];
  processingTime: number;
}

// ============ COMPARACIONES ============

export interface ComparisonTableRow {
  insurer: string;
  premium: string;
  coverage: string;
  specialClause: string;
  advantages: string[];
  disadvantages: string[];
  responsiveness: string;
}

export interface ComparisonResult {
  id: string;
  query: string;
  quotes: InsuranceQuote[];
  comparativeTable?: ComparisonTableRow[];
  analysis?: string;
  timestamp: Date;
  sourceDocuments?: SourceDocument[];
  metadata?: {
    processingTime: number;
    vectorSimilarity: number;
    dataQuality: number;
  };
}

export interface ComparisonRequest {
  query: string;
  insurers?: string[];
  includeAnalysis?: boolean;
}

// ============ DOCUMENTOS ============

export interface SourceDocument {
  id: string;
  insurer: string;
  documentType: 'policy' | 'clause' | 'coverage_map' | 'conditions';
  title: string;
  relevantClause: string;
  pageReference?: string;
  similarity?: number;
  extractedAt: Date;
}

// ============ SESIONES ============

export interface SessionRequest {
  title: string;
}

export interface SessionResponse {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
}

// ============ RESPUESTAS API ============

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  metadata?: {
    processingTime: number;
    timestamp: Date;
    requestId: string;
  };
}

export interface PaginationParams {
  page: number;
  limit: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}
