import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoginComponent } from '@/app/components/auth/login/login.component';
import { RegisterComponent } from '@/app/components/auth/register/register.component';

@Component({
  selector: 'app-auth-page',
  standalone: true,
  imports: [CommonModule, LoginComponent, RegisterComponent],
  template: `
    <div class="min-h-screen bg-gradient-to-br from-background to-muted/20 flex items-center justify-center p-4">
      <div class="w-full max-w-md">
        <div class="flex justify-center mb-8">
          <div class="text-center">
            <h1 class="text-4xl font-bold text-foreground mb-2">Copilot de Seguros</h1>
            <p class="text-muted-foreground">Análisis Inteligente de Cotizaciones de Seguros</p>
          </div>
        </div>

        <div class="bg-card rounded-xl border border-border p-8 shadow-lg">
          @if (!isRegister) {
            <app-login (onSwitchToRegister)="isRegister = true"></app-login>
          } @else {
            <app-register (onSwitchToLogin)="isRegister = false"></app-register>
          }
        </div>
      </div>
    </div>
  `,
})
export class AuthPageComponent {
  @Output() onAuthSuccess = new EventEmitter<void>();

  isRegister = false;
}
