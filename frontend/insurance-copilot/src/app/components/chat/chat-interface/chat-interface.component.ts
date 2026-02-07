import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ChatService } from '../../../services/chat.service';
import { AuthService } from '../../../services/auth.service';
import { ChatMessageComponent } from '../chat-message/chat-message.component';
import { SuggestedQueriesComponent } from '../suggested-queries/suggested-queries.component';
import { SessionsListComponent } from '../sessions-list/sessions-list.component';
import { ChatSession, Message } from '../../../shared/models/types';

@Component({
  selector: 'app-chat-interface',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ChatMessageComponent,
    SuggestedQueriesComponent,
    SessionsListComponent,
  ],
  template: `
    <div class="flex h-screen bg-background text-foreground font-sans overflow-hidden">
      <!-- Sidebar (Desktop) -->
      <div class="hidden md:flex md:flex-col w-80 glass border-r border-border/50 shadow-2xl z-10 relative">
        <div class="p-6 border-b border-white/10 flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center shadow-lg shadow-primary/20">
             <span class="text-white font-bold text-lg">I</span>
          </div>
          <h1 class="text-xl font-heading font-bold bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
            InsuroBot
          </h1>
        </div>
        
        <div class="flex-1 overflow-hidden">
           <app-sessions-list
            [sessions]="(sessions$ | async) || []"
            [currentSessionId]="currentSessionId$ | async"
            (onSessionSelect)="loadSession($event)"
            (onNewSession)="createSession()"
            (onDeleteSession)="deleteSession($event)"
          ></app-sessions-list>
        </div>

        <div class="p-4 border-t border-white/10 bg-white/5 backdrop-blur-sm">
          <button
            (click)="logout()"
            class="w-full group flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-destructive/10 text-destructive hover:bg-destructive hover:text-destructive-foreground transition-all duration-300 font-medium text-sm"
          >
            <span>Cerrar Sesión</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 transition-transform group-hover:translate-x-1"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
          </button>
        </div>
      </div>

      <!-- Main chat area -->
      <div class="flex-1 flex flex-col relative bg-gradient-to-tr from-background via-background to-secondary/30">
        <!-- Header (Mobile/Tablet) -->
        <div class="md:hidden flex items-center justify-between p-4 glass border-b border-border/50 sticky top-0 z-20">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
               <span class="text-white font-bold">I</span>
            </div>
            <h2 class="text-lg font-heading font-semibold">{{ currentSessionTitle }}</h2>
          </div>
          <button
            class="p-2 rounded-lg hover:bg-muted transition-colors"
            (click)="toggleSidebar()"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
          </button>
        </div>

        <!-- Header (Desktop) -->
        <div class="hidden md:flex items-center justify-between px-8 py-6 border-b border-border/40 backdrop-blur-sm bg-background/50 sticky top-0 z-10">
          <h2 class="text-2xl font-heading font-semibold text-foreground/80 tracking-tight">{{ currentSessionTitle }}</h2>
          <div class="flex items-center gap-2">
             <div class="h-2 w-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)] animate-pulse"></div>
             <span class="text-xs font-medium text-muted-foreground uppercase tracking-wider">Online</span>
          </div>
        </div>

        <!-- Messages area -->
        <div
          #messagesContainer
          class="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-8 scroll-smooth"
        >
          <div *ngIf="currentSession$ | async as session" class="max-w-4xl mx-auto w-full space-y-8 pb-4">
            <div *ngIf="session.messages.length === 0" class="flex flex-col items-center justify-center h-full min-h-[400px] animate-fadeIn">
               <div class="w-24 h-24 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center mb-6 shadow-inner">
                  <span class="text-4xl text-primary">👋</span>
               </div>
               <h3 class="text-3xl font-heading font-bold text-center mb-3 text-foreground">¿En qué puedo ayudarte?</h3>
               <p class="text-muted-foreground text-center mb-10 max-w-md text-lg text-balance">Tu asistente inteligente de seguros. Pregúntame sobre pólizas, coberturas o comparativas.</p>
              
               <div class="w-full max-w-2xl">
                <app-suggested-queries
                  (onQuerySelect)="handleQuery($event)"
                ></app-suggested-queries>
               </div>
            </div>

            <app-chat-message
              *ngFor="let message of session.messages"
              [message]="message"
            ></app-chat-message>
          </div>

          <div
            *ngIf="isLoading"
            class="flex gap-4 justify-start max-w-4xl mx-auto w-full animate-fadeIn pl-2 md:pl-0"
          >
             <div class="w-10 h-10 rounded-full bg-white shadow-sm border border-border flex items-center justify-center">
              <span class="text-lg">🤖</span>
            </div>
            <div class="flex items-center gap-2 p-4 rounded-2xl rounded-tl-none bg-card border border-border shadow-sm">
                <div class="flex space-x-1">
                   <div class="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style="animation-delay: 0s"></div>
                   <div class="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style="animation-delay: 0.15s"></div>
                   <div class="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style="animation-delay: 0.3s"></div>
                </div>
            </div>
          </div>
        </div>

        <!-- Input area -->
        <div class="p-4 md:p-6 bg-gradient-to-t from-background via-background to-transparent sticky bottom-0 z-20">
          <div class="max-w-4xl mx-auto w-full relative">
            <form (ngSubmit)="sendMessage()" class="relative flex items-end gap-2 p-2 rounded-2xl glass-card transition-all duration-300 focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary/50">
              
              <input
                [(ngModel)]="messageInput"
                name="messageInput"
                type="text"
                placeholder="Escribe tu mensaje..."
                [disabled]="isLoading"
                class="flex-1 px-4 py-3 bg-transparent text-foreground placeholder:text-muted-foreground/70 focus:outline-none text-base resize-none max-h-32 disabled:opacity-50"
                autocomplete="off"
              />
              
              <button
                type="submit"
                [disabled]="isLoading || !messageInput.trim()"
                class="p-3 rounded-xl bg-primary text-primary-foreground transition-all hover:bg-primary/90 hover:scale-105 hover:shadow-lg disabled:opacity-50 disabled:hover:scale-100 disabled:hover:shadow-none disabled:cursor-not-allowed group"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              </button>
            </form>
             <p class="text-center text-xs text-muted-foreground mt-3 font-medium">InsuroBot puede cometer errores. Verifica la información importante.</p>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      @keyframes fadeIn {
        from {
          opacity: 0;
          transform: translateY(10px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
      :host ::ng-deep .animate-fadeIn {
        animation: fadeIn 0.3s ease-out;
      }
    `,
  ],
})
export class ChatInterfaceComponent implements OnInit, AfterViewChecked {
  @ViewChild('messagesContainer') messagesContainer!: ElementRef;

  messageInput = '';
  isLoading = false;

  currentSession$ = new Observable<ChatSession | null>();
  sessions$ = new Observable<ChatSession[]>();
  currentSessionId$ = new Observable<string | null>(); // New observable
  currentSessionTitle = 'Nueva Sesión';

  private shouldScroll = false;

  constructor(
    private chatService: ChatService,
    private authService: AuthService
  ) { }

  ngOnInit(): void {
    this.initializeChat();
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  private initializeChat(): void {
    this.currentSession$ = this.chatService.currentSession$;
    this.sessions$ = this.chatService.sessions$;

    // Create the derived observable
    this.currentSessionId$ = this.currentSession$.pipe(
      map(session => session ? session.id : null)
    );

    this.currentSession$.subscribe((session) => {
      if (session) {
        this.currentSessionTitle = session.title;
        this.shouldScroll = true;
      }
    });
  }

  sendMessage(): void {
    if (!this.messageInput.trim()) return;

    this.isLoading = true;
    const message = this.messageInput;
    this.messageInput = '';

    this.chatService.sendMessage({ message }).subscribe({
      next: () => {
        this.isLoading = false;
        this.shouldScroll = true;
      },
      error: () => {
        this.isLoading = false;
      },
    });
  }

  handleQuery(query: string): void {
    this.messageInput = query;
    this.sendMessage();
  }

  loadSession(sessionId: string): void {
    this.chatService.loadSession(sessionId);
  }

  createSession(): void {
    this.chatService.createSession('Nueva Sesión').subscribe({
      next: () => {
        this.messageInput = '';
      },
    });
  }

  deleteSession(sessionId: string): void {
    this.chatService.deleteSession(sessionId).subscribe();
  }

  logout(): void {
    this.authService.logout();
    window.location.reload();
  }

  toggleSidebar(): void {
    // Implement sidebar toggle for mobile
  }

  private scrollToBottom(): void {
    try {
      this.messagesContainer.nativeElement.scrollTop =
        this.messagesContainer.nativeElement.scrollHeight;
    } catch (err) { }
  }

  // extractId helper is no longer needed in template but good to keep if needed logic later, 
  // though for now we are using the observable pipe
}

