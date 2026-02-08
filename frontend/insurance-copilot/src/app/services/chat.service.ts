import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, map, of, switchMap } from 'rxjs';
import {
  ChatSession,
  ChatMessageRequest,
  ChatMessageResponse,
} from '@/app/shared/models/types';

@Injectable({
  providedIn: 'root',
})
export class ChatService {
  private apiUrl = 'http://localhost:8000/api/v1'; // Base API URL

  private currentSessionSubject = new BehaviorSubject<ChatSession | null>(null);
  public currentSession$ = this.currentSessionSubject.asObservable();

  private sessionsSubject = new BehaviorSubject<ChatSession[]>([]);
  public sessions$ = this.sessionsSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadSessions();
  }

  loadSessions(): void {
    this.http.get<any[]>(`${this.apiUrl}/threads`).subscribe({
      next: (threads) => {
        // Map backend threads to ChatSession
        const sessions: ChatSession[] = threads.map(t => ({
          id: t.id,
          userId: 'current-user', // Backend handles user context
          title: t.title,
          createdAt: new Date(t.created_at),
          updatedAt: new Date(t.updated_at),
          messages: [] // Messages loaded on demand
        }));
        this.sessionsSubject.next(sessions);

        // Load first session if none selected
        if (sessions.length > 0 && !this.currentSessionSubject.value) {
          this.loadSession(sessions[0].id);
        }
      },
      error: (err) => console.error('Failed to load threads', err)
    });
  }

  getCurrentSession(): ChatSession | null {
    return this.currentSessionSubject.value;
  }

  createSession(title: string): Observable<ChatSession> {
    return this.http.post<any>(`${this.apiUrl}/threads`, { title }).pipe(
      map(t => ({
        id: t.id,
        userId: 'current-user',
        title: t.title,
        createdAt: new Date(t.created_at),
        updatedAt: new Date(t.updated_at),
        messages: []
      })),
      tap((session) => {
        const sessions = this.sessionsSubject.value;
        sessions.unshift(session);
        this.sessionsSubject.next([...sessions]);
        this.currentSessionSubject.next(session);
      })
    );
  }

  sendMessage(request: ChatMessageRequest): Observable<ChatMessageResponse> {
    const currentSession = this.currentSessionSubject.value;
    let threadId = currentSession?.id;

    // If no session exists, create one first? 
    // Ideally UI should handle this, but let's assume session exists or thread_id is null for new.
    // However, our backend /chat endpoint takes thread_id.

    // Optimistic UI update for User Message
    const userMsg = {
      id: 'temp-user-' + Date.now(),
      content: request.message,
      role: 'user' as const,
      timestamp: new Date(),
      status: 'sending' as const,
    };

    // Update local state immediately
    if (currentSession) {
      currentSession.messages = [...currentSession.messages, userMsg];
      this.currentSessionSubject.next({ ...currentSession });
    }

    const payload = {
      message: request.message,
      thread_id: threadId
    };

    return this.http.post<any>(`${this.apiUrl}/chat`, payload).pipe(
      map(response => {
        // Return formatted response
        return {
          id: 'msg-' + Date.now(),
          content: response.answer,
          timestamp: new Date(),
          // Comparison/Table data parsing if needed
          comparisonResult: undefined // TODO: Parse sources/data_table if backend sends it
        } as ChatMessageResponse;
      }),
      tap((msg) => {
        // Update Session with Assistant Message
        const session = this.currentSessionSubject.value;
        if (session) {
          // Update user msg status
          session.messages = session.messages.map(m => m.id === userMsg.id ? { ...m, status: 'sent' } : m);

          const assistantMsg = {
            id: msg.id,
            content: msg.content,
            role: 'assistant' as const,
            timestamp: msg.timestamp,
            status: 'sent' as const,
            // metadata...
          };

          session.messages.push(assistantMsg);
          this.currentSessionSubject.next({ ...session });

          // Refresh threads list order logic if needed
        } else {
          // Case where we started without a session (if supported)
          // We should reload sessions to get the new one created by backend if we passed null thread_id
          this.loadSessions();
        }
      })
    );
  }

  loadSession(sessionId: string): void {
    // Check if we have messages loaded? 
    // Always fetch latest messages
    this.http.get<any[]>(`${this.apiUrl}/threads/${sessionId}/messages`).subscribe({
      next: (msgs) => {
        const session = this.sessionsSubject.value.find(s => s.id === sessionId);
        if (session) {
          session.messages = msgs.map(m => ({
            id: m.id,
            content: m.content,
            role: m.role as 'user' | 'assistant',
            timestamp: new Date(m.created_at),
            status: 'sent'
          }));
          this.currentSessionSubject.next({ ...session });
        }
      },
      error: (err) => console.error('Error loading messages', err)
    });
  }

  getSessions(): ChatSession[] {
    return this.sessionsSubject.value;
  }

  deleteSession(sessionId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/threads/${sessionId}`).pipe(
      tap(() => {
        const sessions = this.sessionsSubject.value.filter((s) => s.id !== sessionId);
        this.sessionsSubject.next([...sessions]);

        const currentSession = this.currentSessionSubject.value;
        if (currentSession?.id === sessionId) {
          this.currentSessionSubject.next(sessions.length > 0 ? sessions[0] : null);
          if (sessions.length > 0) {
            this.loadSession(sessions[0].id);
          }
        }
      })
    );
  }

  renameSession(sessionId: string, newTitle: string): Observable<void> {
    return this.http.put<void>(`${this.apiUrl}/threads/${sessionId}`, { title: newTitle }).pipe(
      tap(() => {
        const sessions = this.sessionsSubject.value.map((s) => {
          if (s.id === sessionId) {
            return { ...s, title: newTitle, updatedAt: new Date() };
          }
          return s;
        });
        this.sessionsSubject.next([...sessions]);

        const currentSession = this.currentSessionSubject.value;
        if (currentSession?.id === sessionId) {
          this.currentSessionSubject.next({ ...currentSession, title: newTitle });
        }
      })
    );
  }
}
