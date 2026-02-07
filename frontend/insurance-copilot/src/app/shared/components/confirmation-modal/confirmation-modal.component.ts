import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-confirmation-modal',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div *ngIf="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fadeIn">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity" (click)="onCancel.emit()"></div>

      <!-- Modal Card -->
      <div class="relative w-full max-w-sm bg-card text-card-foreground rounded-2xl shadow-2xl border border-white/10 overflow-hidden transform transition-all scale-100">
        <!-- Header -->
        <div class="p-6 pb-2">
          <h3 class="text-lg font-heading font-semibold text-foreground tracking-tight flex items-center gap-2">
            <span class="text-destructive">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            </span>
            {{ title }}
          </h3>
        </div>

        <!-- Body -->
        <div class="px-6 py-2">
          <p class="text-sm text-muted-foreground leading-relaxed">
            {{ message }}
          </p>
        </div>

        <!-- Footer -->
        <div class="p-6 flex justify-end gap-3">
          <button
            (click)="onCancel.emit()"
            class="px-4 py-2 rounded-xl text-sm font-medium text-foreground hover:bg-muted transition-colors"
          >
            {{ cancelText }}
          </button>
          <button
            (click)="onConfirm.emit()"
            class="px-4 py-2 rounded-xl text-sm font-medium bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-lg shadow-destructive/20 transition-all"
          >
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  `,
    styles: [`
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    .animate-fadeIn {
      animation: fadeIn 0.2s ease-out;
    }
  `]
})
export class ConfirmationModalComponent {
    @Input() isOpen = false;
    @Input() title = 'Confirmar acción';
    @Input() message = '¿Estás seguro de que deseas continuar?';
    @Input() confirmText = 'Confirmar';
    @Input() cancelText = 'Cancelar';

    @Output() onConfirm = new EventEmitter<void>();
    @Output() onCancel = new EventEmitter<void>();
}
