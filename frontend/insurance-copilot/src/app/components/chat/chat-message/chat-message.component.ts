import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Message, ComparisonTableRow } from '@/app/shared/models/types';
import { MarkdownModule } from 'ngx-markdown';
import { ChatService } from '@/app/services/chat.service';

@Component({
  selector: 'app-chat-message',
  standalone: true,
  imports: [CommonModule, MarkdownModule],
  template: `
    <div class="flex gap-4 animate-fadeIn group" [ngClass]="message.role === 'user' ? 'justify-end' : 'justify-start'">
      <!-- Assistant Avatar -->
      <div
        *ngIf="message.role === 'assistant'"
        class="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-white to-white/50 border border-white/20 shadow-sm flex items-center justify-center mt-auto"
      >
        <span class="text-sm select-none">🤖</span>
      </div>

      <!-- Message bubble -->
      <div
        class="flex-1 max-w-[85%] md:max-w-md lg:max-w-2xl shadow-sm relative group"
        [ngClass]="
          message.role === 'user'
            ? 'bg-primary text-primary-foreground rounded-2xl rounded-tr-sm ml-auto'
            : 'bg-white/80 dark:bg-card/80 backdrop-blur-sm border border-border/50 text-foreground rounded-2xl rounded-tl-sm shadow-sm'
        "
      >
        <div class="px-5 py-3.5">
          <markdown 
            [data]="message.content" 
            class="markdown-body block"
          ></markdown>

          <!-- Fuentes consultadas (Collapsible) -->
          <div *ngIf="message.sources && message.sources.length > 0" class="mt-2 border-t border-border/40 pt-2">
            <button 
              (click)="showSources = !showSources" 
              class="flex items-center gap-1.5 text-[10px] font-medium text-muted-foreground hover:text-primary transition-colors focus:outline-none"
            >
              <span>{{ showSources ? '▼' : '▶' }}</span>
              <span> Fuentes ({{ message.sources.length }})</span>
            </button>

            <div *ngIf="showSources" class="flex flex-wrap gap-1.5 mt-2 animate-fadeIn">
              <div *ngFor="let source of message.sources" class="relative hover:z-50 source-chip-wrapper">
                <!-- Chip Compacto -->
                <div class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-secondary/30 hover:bg-secondary/80 border border-border/50 hover:border-border text-xs cursor-help transition-all">
                  <span class="text-[9px] opacity-70">📄</span>
                  <span class="max-w-[120px] truncate leading-none text-[10px]">{{ source.title }}</span>
                </div>
                
                <!-- Custom Tooltip (Ajustado con Scroll) -->
                <div class="source-tooltip invisible opacity-0 transition-all duration-200 absolute bottom-full left-0 mb-1 w-72 p-0 bg-popover text-popover-foreground text-[10px] rounded-md shadow-xl border border-border z-50 pointer-events-auto flex flex-col overflow-hidden">
                   <div class="p-2 border-b border-border/10 bg-muted/20">
                     <div class="font-semibold truncate text-primary">{{ source.title }}</div>
                   </div>
                   <div class="p-2 max-h-48 overflow-y-auto custom-scrollbar bg-card/50">
                     <p class="text-muted-foreground leading-relaxed whitespace-pre-wrap">{{ source.content }}</p>
                   </div>
                   <div class="p-1 bg-muted/20 text-[9px] text-center text-muted-foreground/50 border-t border-border/10">
                     Relevancia: {{ (source.score || 0) | number:'1.2-2' }}
                   </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div *ngIf="message.role === 'assistant'" class="absolute -bottom-5 left-2 opacity-0 group-hover:opacity-100 transition-opacity text-[10px] text-muted-foreground">
           InsuroBot
        </div>
        <div *ngIf="message.role === 'user'" class="absolute -bottom-5 right-2 opacity-0 group-hover:opacity-100 transition-opacity text-[10px] text-muted-foreground">
           Tú
        </div>
      </div>

      <!-- User Avatar -->
      <div
        *ngIf="message.role === 'user'"
        class="flex-shrink-0 w-8 h-8 rounded-lg bg-primary shadow-lg shadow-primary/20 flex items-center justify-center mt-auto text-white"
      >
        <span class="text-sm font-semibold select-none">Tú</span>
      </div>

      <!-- Actions (Assistant Only) -->
      <div *ngIf="message.role === 'assistant'" class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
        <button 
          (click)="downloadPdf()" 
          class="p-1 hover:bg-secondary rounded text-muted-foreground hover:text-primary transition-colors"
          title="Descargar PDF"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        </button>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
    }
    .source-chip-wrapper:hover .source-tooltip {
      visibility: visible;
      opacity: 1;
    }
    .custom-scrollbar::-webkit-scrollbar {
      width: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
      background: transparent;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
      background: rgba(156, 163, 175, 0.3);
      border-radius: 2px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
      background: rgba(156, 163, 175, 0.5);
    }
  `]
})
export class ChatMessageComponent {
  @Input() message!: Message;
  showSources = false;

  constructor(private chatService: ChatService) { }

  get tableData(): ComparisonTableRow[] | null {
    if (this.message.metadata?.type === 'table' && Array.isArray(this.message.metadata?.data)) {
      return this.message.metadata.data as ComparisonTableRow[];
    }
    return null;
  }

  downloadPdf() {
    const title = this.tableData ? 'Comparativa de Seguros' : 'Resumen de Consulta';
    const content = this.message.content;
    const tableData = this.tableData;

    this.chatService.downloadSlip(title, content, tableData).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `slip-${Date.now()}.pdf`;
        link.click();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => console.error('Error downloading PDF', err)
    });
  }
}
