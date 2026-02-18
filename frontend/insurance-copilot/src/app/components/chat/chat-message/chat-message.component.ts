import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Message, ComparisonTableRow } from '@/app/shared/models/types';
import { MarkdownModule } from 'ngx-markdown';

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
        <!-- Text/Markdown content -->
        <div class="px-5 py-3.5">
          <markdown 
            [data]="message.content" 
            class="markdown-body block"
          ></markdown>
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
    </div>
  `,
  styles: [`
    :host {
      display: block;
    }
  `]
})
export class ChatMessageComponent {
  @Input() message!: Message;

  get tableData(): ComparisonTableRow[] | null {
    if (this.message.metadata?.type === 'table' && Array.isArray(this.message.metadata?.data)) {
      return this.message.metadata.data as ComparisonTableRow[];
    }
    return null;
  }
}
