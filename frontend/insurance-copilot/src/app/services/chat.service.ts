import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, map, of, switchMap, catchError, throwError } from 'rxjs';
import {
  ChatSession,
  ChatMessageRequest,
  ChatMessageResponse,
} from '@/app/shared/models/types';

@Injectable({
  providedIn: 'root',
})
export class ChatService {
  private apiUrl = 'http://localhost:8000/api/v1';

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
        const sessions: ChatSession[] = threads.map(t => ({
          id: t.id,
          userId: 'current-user',
          title: t.title,
          createdAt: new Date(t.created_at),
          updatedAt: new Date(t.updated_at),
          messages: []
        }));
        this.sessionsSubject.next(sessions);

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

    const userMsg = {
      id: 'temp-user-' + Date.now(),
      content: request.message,
      role: 'user' as const,
      timestamp: new Date(),
      status: 'sending' as const,
    };

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
        return {
          id: 'msg-' + Date.now(),
          content: response.answer,
          timestamp: new Date(),
          comparisonResult: undefined,
          sources: response.sources
        } as ChatMessageResponse;
      }),
      tap((msg) => {
        const session = this.currentSessionSubject.value;
        if (session) {
          session.messages = session.messages.map(m => m.id === userMsg.id ? { ...m, status: 'sent' } : m);

          const assistantMsg = {
            id: msg.id,
            content: msg.content,
            role: 'assistant' as const,
            timestamp: msg.timestamp,
            status: 'sent' as const,
            sources: msg.sources
          };

          session.messages.push(assistantMsg);
          this.currentSessionSubject.next({ ...session });
        } else {
          this.loadSessions();
        }
      }),
      catchError((error) => {
        console.error('Chat API Error:', error);

        const session = this.currentSessionSubject.value;
        if (session) {
          session.messages = session.messages.map(m => m.id === userMsg.id ? { ...m, status: 'error' } : m);

          const errorMsg = {
            id: 'err-' + Date.now(),
            content: "❌ Lo siento, ocurrió un error en el servidor. Por favor intenta más tarde o reformula tu pregunta.",
            role: 'assistant' as const,
            timestamp: new Date(),
            status: 'error' as const
          };

          session.messages.push(errorMsg);
          this.currentSessionSubject.next({ ...session });
        }

        return throwError(() => error);
      })
    );
  }

  loadSession(sessionId: string): void {
    this.http.get<any[]>(`${this.apiUrl}/threads/${sessionId}/messages`).subscribe({
      next: (msgs) => {
        const session = this.sessionsSubject.value.find(s => s.id === sessionId);
        if (session) {
          session.messages = msgs.map(m => ({
            id: m.id,
            content: m.content,
            role: m.role as 'user' | 'assistant',
            timestamp: new Date(m.created_at),
            status: 'sent',
            sources: m.metadata_json?.sources || []
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

  downloadSlip(title: string, content: string, tableData: any = null): Observable<Blob> {
    const url = `${this.apiUrl}/files/pdf/slip`;
    const body = { title, content, table_data: tableData };
    return this.http.post(url, body, { responseType: 'blob' });
  }
}
