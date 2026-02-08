import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatSession } from '@/app/shared/models/types';
import { ConfirmationModalComponent } from '@/app/shared/components/confirmation-modal/confirmation-modal.component';

@Component({
  selector: 'app-sessions-list',
  standalone: true,
  imports: [CommonModule, FormsModule, ConfirmationModalComponent],
  template: `
    <div class="flex-1 overflow-y-auto custom-scrollbar relative">
      <div class="p-4 space-y-3">
        <button
          (click)="onNewSession.emit()"
          class="w-full px-4 py-3 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 hover:shadow-lg transition-all duration-300 font-semibold text-sm flex items-center justify-center gap-2 group"
        >
          <span class="text-lg font-light transition-transform group-hover:rotate-90">+</span> Nueva Sesión
        </button>

        <div class="space-y-1 mt-6">
          <p class="px-4 text-[10px] font-bold text-muted-foreground uppercase tracking-widest opacity-70 mb-2">
            Historial
          </p>
          <div class="space-y-1">
            <div
                *ngFor="let session of sessions"
                class="group relative"
            >
                <button
                    (click)="onSessionSelect.emit(session.id)"
                    [ngClass]="
                    session.id === currentSessionId
                        ? 'bg-primary/10 text-primary font-medium border-primary/20 shadow-sm'
                        : 'text-muted-foreground hover:bg-white/5 hover:text-foreground border-transparent'
                    "
                    class="w-full text-left px-4 py-3 rounded-xl border transition-all duration-200 text-sm truncate flex items-center gap-2 relative overflow-hidden pr-16"
                >
                    <div class="w-1 h-1 rounded-full bg-current opacity-50 flex-shrink-0"></div>
                    
                    <ng-container *ngIf="editingSessionId !== session.id; else editMode">
                        <span class="truncate relative z-10">{{ session.title }}</span>
                    </ng-container>
                    
                    <ng-template #editMode>
                        <input
                            type="text"
                            [(ngModel)]="editTitle"
                            (click)="$event.stopPropagation()"
                            (keydown.enter)="saveTitle($event)"
                            (keydown.escape)="cancelEditing()"
                            (blur)="cancelEditing()"
                            class="w-full bg-transparent border-b border-primary/50 text-foreground focus:outline-none px-1 py-0.5"
                            autofocus
                        />
                    </ng-template>

                    <div *ngIf="session.id === currentSessionId" class="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent pointer-events-none"></div>
                </button>
                
                <div class="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all duration-200 z-20">
                    <button
                        *ngIf="editingSessionId !== session.id"
                        (click)="startEditing($event, session)"
                        class="p-1.5 rounded-lg text-muted-foreground hover:text-primary hover:bg-primary/10"
                        title="Renombrar"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.85 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>
                    </button>
                    <button
                        (click)="openDeleteModal($event, session.id)"
                        class="p-1.5 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                        title="Eliminar"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                    </button>
                </div>
            </div>
          </div>
        </div>
      </div>
      
      <app-confirmation-modal
        [isOpen]="isModalOpen"
        title="Eliminar conversación"
        message="¿Estás seguro de que deseas eliminar esta conversación? Esta acción no se puede deshacer."
        confirmText="Eliminar"
        cancelText="Cancelar"
        (onConfirm)="confirmDelete()"
        (onCancel)="cancelDelete()"
      ></app-confirmation-modal>
    </div>
  `,
})
export class SessionsListComponent {
  @Input() sessions: ChatSession[] | null = [];
  @Input() currentSessionId: string | null = null;
  @Output() onSessionSelect = new EventEmitter<string>();
  @Output() onNewSession = new EventEmitter<void>();
  @Output() onDeleteSession = new EventEmitter<string>();
  @Output() onRenameSession = new EventEmitter<{ id: string, newTitle: string }>();

  isModalOpen = false;
  sessionToDelete: string | null = null;

  editingSessionId: string | null = null;
  editTitle = '';

  openDeleteModal(event: Event, sessionId: string): void {
    event.stopPropagation();
    this.sessionToDelete = sessionId;
    this.isModalOpen = true;
  }

  confirmDelete(): void {
    if (this.sessionToDelete) {
      this.onDeleteSession.emit(this.sessionToDelete);
      this.cancelDelete();
    }
  }

  cancelDelete(): void {
    this.isModalOpen = false;
    this.sessionToDelete = null;
  }

  startEditing(event: Event, session: ChatSession): void {
    event.stopPropagation();
    this.editingSessionId = session.id;
    this.editTitle = session.title;
  }

  saveTitle(event: Event): void {
    event.stopPropagation();
    if (this.editingSessionId && this.editTitle.trim()) {
      this.onRenameSession.emit({
        id: this.editingSessionId,
        newTitle: this.editTitle.trim()
      });
      this.cancelEditing();
    }
  }

  cancelEditing(): void {
    this.editingSessionId = null;
    this.editTitle = '';
  }

  handleKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      this.saveTitle(event);
    } else if (event.key === 'Escape') {
      this.cancelEditing();
    }
  }
}
