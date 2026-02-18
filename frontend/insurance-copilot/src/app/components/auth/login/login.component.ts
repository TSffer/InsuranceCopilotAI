import { Component, Output, EventEmitter, ChangeDetectorRef } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '@/app/services/auth.service';
import { AuthRequest } from '@/app/shared/models/types';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="w-full max-w-md space-y-6">
      <div class="space-y-2 text-center">
        <h2 class="text-3xl font-bold text-foreground">Bienvenido</h2>
        <p class="text-muted-foreground">
          Accede a tu cuenta de broker de seguros
        </p>
      </div>

      <form (ngSubmit)="handleSubmit()" class="space-y-4">
        <div class="space-y-2">
          <label for="email" class="text-sm font-medium text-foreground">
            Correo Electrónico
          </label>
          <input
            id="email"
            type="email"
            [(ngModel)]="email"
            name="email"
            placeholder="tu@email.com"
            class="w-full px-4 py-3 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            required
          />
        </div>

        <div class="space-y-2">
          <label for="password" class="text-sm font-medium text-foreground">
            Contraseña
          </label>
          <input
            id="password"
            type="password"
            [(ngModel)]="password"
            name="password"
            placeholder="••••••••"
            class="w-full px-4 py-3 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            required
          />
        </div>
      
        @if(error) {
          <div class="p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-sm text-destructive">
            {{ error }}
          </div>
        }

        <button
          type="submit"
          [disabled]="loading"
          class="w-full py-3 px-4 rounded-lg bg-primary text-primary-foreground font-semibold transition-all hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ loading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}
        </button>
      </form>

      <div class="relative">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-border"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-2 bg-background text-muted-foreground">
            ¿No tienes cuenta?
          </span>
        </div>
      </div>

      <button (click)="onSwitchToRegister.emit()"
        class="w-full py-3 px-4 rounded-lg border border-primary bg-transparent text-primary font-semibold hover:bg-primary/5 transition-colors"
      >
        Crear Nueva Cuenta
      </button>

      <div class="mt-6 p-4 rounded-lg bg-muted/30 border border-border">
        <p class="text-xs text-muted-foreground mb-2 font-semibold">
          Demo - Credenciales de prueba:
        </p>
        <p class="text-xs text-muted-foreground">
          <span class="font-mono">broker@seguros.com</span>
          <br />
          <span class="font-mono">password123</span>
        </p>
      </div>
    </div>
  `,
})
export class LoginComponent {
  @Output() onSwitchToRegister = new EventEmitter<void>();

  email = 'broker@seguros.com';
  password = 'password123';
  loading = false;
  error: string | null = null;

  constructor(private authService: AuthService, private router: Router, private cdr: ChangeDetectorRef) { }

  handleSubmit(): void {
    this.loading = true;
    this.error = null;

    this.authService
      .login({
        email: this.email,
        password: this.password,
      } as AuthRequest)
      .subscribe({
        next: () => {
          this.loading = false;
          this.router.navigate(['/chat']); // Adjust route as needed
        },
        error: (err: any) => {
          console.error('Login error:', err);
          this.error = err.error?.detail || 'Error al iniciar sesión';
          this.loading = false;
          this.cdr.detectChanges();
        },
      });
  }
}
