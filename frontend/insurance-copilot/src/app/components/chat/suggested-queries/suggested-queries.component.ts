import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

const SUGGESTED_QUERIES = [
  'Cotiza una Toyota Hilux 2023 en Rimac y Pacífico',
  'Compara coberturas de daño total vs terceros',
  '¿Qué aseguradora tiene mejor cobertura para robo?',
  'Análisis de deducibles y primas para autos de 5 años',
];

@Component({
  selector: 'app-suggested-queries',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="space-y-3">
      <p class="text-sm font-semibold text-muted-foreground">Consultas sugeridas</p>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
        <button
          *ngFor="let query of suggestedQueries"
          (click)="onQuerySelect.emit(query)"
          class="text-left px-4 py-3 rounded-lg border border-border bg-card hover:bg-primary/5 hover:border-primary transition-all duration-200 text-sm text-foreground hover:text-primary cursor-pointer group"
        >
          <span class="flex items-center gap-2">
            <span class="text-muted-foreground group-hover:text-primary transition-colors">→</span>
            <span class="text-pretty">{{ query }}</span>
          </span>
        </button>
      </div>
    </div>
  `,
})
export class SuggestedQueriesComponent {
  @Output() onQuerySelect = new EventEmitter<string>();

  suggestedQueries = SUGGESTED_QUERIES;
}
