import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { delay, tap } from 'rxjs/operators';
import {
  ChatSession,
  ChatMessageRequest,
  ChatMessageResponse,
  ComparisonResult,
} from '../shared/models/types';
import { mockChatSession, mockComparisonResult, mockSessions } from '../shared/data/mock-data';
import { MockResponse, directResponses, comparisonResponses, quotationResponses } from '../shared/data/mock-responses';

@Injectable({
  providedIn: 'root',
})
export class ChatService {
  private currentSessionSubject = new BehaviorSubject<ChatSession | null>(null);
  public currentSession$ = this.currentSessionSubject.asObservable();

  private sessionsSubject = new BehaviorSubject<ChatSession[]>(mockSessions);
  public sessions$ = this.sessionsSubject.asObservable();

  constructor() {
    this.loadDefaultSession();
  }

  private loadDefaultSession(): void {
    if (mockSessions.length > 0) {
      this.currentSessionSubject.next(mockSessions[0]);
    }
  }

  getCurrentSession(): ChatSession | null {
    return this.currentSessionSubject.value;
  }

  createSession(title: string): Observable<ChatSession> {
    const newSession: ChatSession = {
      id: 'session-' + Date.now(),
      userId: 'user-001',
      title,
      createdAt: new Date(),
      updatedAt: new Date(),
      messages: [],
    };

    return of(newSession).pipe(
      delay(300),
      tap((session) => {
        const sessions = this.sessionsSubject.value;
        sessions.unshift(session);
        this.sessionsSubject.next([...sessions]);
        this.currentSessionSubject.next(session);
      })
    );
  }

  sendMessage(request: ChatMessageRequest): Observable<ChatMessageResponse> {
    // Mock response logic based on keywords
    const lowerMessage = request.message.toLowerCase();
    let selectedResponse: MockResponse;

    if (lowerMessage.includes('cotiz') || lowerMessage.includes('precio') || lowerMessage.includes('costo')) {
      selectedResponse = quotationResponses[Math.floor(Math.random() * quotationResponses.length)];
    } else if (lowerMessage.includes('compar') || lowerMessage.includes('diferencia') || lowerMessage.includes('vs')) {
      selectedResponse = comparisonResponses[Math.floor(Math.random() * comparisonResponses.length)];
    } else if (lowerMessage.includes('cobert') || lowerMessage.includes('cubre') || lowerMessage.includes('exclu')) {
      // Mix of direct text answers or comparison tables for coverage/exclusions
      const options = [...directResponses, ...comparisonResponses];
      selectedResponse = options[Math.floor(Math.random() * options.length)];
    } else {
      // Default to a direct text answer if no specific keyword
      selectedResponse = directResponses[Math.floor(Math.random() * directResponses.length)];
    }

    const response: ChatMessageResponse = {
      id: 'msg-' + Date.now(),
      content: selectedResponse.content,
      timestamp: new Date(),
      comparisonResult: selectedResponse.type === 'table' ? {
        id: 'comp-' + Date.now(),
        query: request.message,
        timestamp: new Date(),
        quotes: [],
        comparativeTable: selectedResponse.tableData
      } : undefined,
    };

    return of(response).pipe(
      delay(1200),
      tap((msg) => {
        const session = this.currentSessionSubject.value;
        if (session) {
          const userMsg = {
            id: 'msg-user-' + Date.now(),
            content: request.message,
            role: 'user' as const,
            timestamp: new Date(),
            status: 'sent' as const,
          };

          const assistantMsg = {
            id: msg.id,
            content: msg.content,
            role: 'assistant' as const,
            timestamp: msg.timestamp,
            status: 'sent' as const,
            metadata: {
              type: selectedResponse.type,
              data: selectedResponse.tableData,
            },
          };

          session.messages = [...session.messages, userMsg, assistantMsg];
          session.updatedAt = new Date();
          this.currentSessionSubject.next({ ...session });

          const sessions = this.sessionsSubject.value.map((s) =>
            s.id === session.id ? session : s
          );
          this.sessionsSubject.next([...sessions]);
        }
      })
    );
  }

  loadSession(sessionId: string): void {
    const session = this.sessionsSubject.value.find((s) => s.id === sessionId);
    if (session) {
      this.currentSessionSubject.next(session);
    }
  }

  getSessions(): ChatSession[] {
    return this.sessionsSubject.value;
  }

  deleteSession(sessionId: string): Observable<void> {
    return of(void 0).pipe(
      tap(() => {
        const sessions = this.sessionsSubject.value.filter((s) => s.id !== sessionId);
        this.sessionsSubject.next([...sessions]);

        const currentSession = this.currentSessionSubject.value;
        if (currentSession?.id === sessionId) {
          this.currentSessionSubject.next(sessions.length > 0 ? sessions[0] : null);
        }
      })
    );
  }
}
