import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '@/app/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="w-full max-w-md space-y-6">
      <div class="space-y-2 text-center">
        <h2 class="text-3xl font-bold text-foreground">Crear Cuenta</h2>
        <p class="text-muted-foreground">
          Regístrate para acceder a InsuroBot
        </p>
      </div>

      <form (ngSubmit)="handleSubmit()" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <label for="firstName" class="text-sm font-medium text-foreground">
              Nombre
            </label>
            <input
              id="firstName"
              type="text"
              [(ngModel)]="firstName"
              name="firstName"
              placeholder="Juan"
              class="w-full px-4 py-3 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              required
            />
          </div>

          <div class="space-y-2">
            <label for="lastName" class="text-sm font-medium text-foreground">
              Apellido
            </label>
            <input
              id="lastName"
              type="text"
              [(ngModel)]="lastName"
              name="lastName"
              placeholder="Pérez"
              class="w-full px-4 py-3 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              required
            />
          </div>
        </div>

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
          {{ loading ? 'Creando cuenta...' : 'Crear Cuenta' }}
        </button>
      </form>

      <button
        (click)="onSwitchToLogin.emit()"
        class="w-full py-3 px-4 rounded-lg border border-border bg-transparent text-foreground font-semibold hover:bg-muted/50 transition-colors"
      >
        Volver al Inicio de Sesión
      </button>
    </div>
  `,
})
export class RegisterComponent {
  @Output() onSwitchToLogin = new EventEmitter<void>();

  firstName = '';
  lastName = '';
  email = '';
  password = '';
  loading = false;
  error: string | null = null;

  constructor(private authService: AuthService) { }

  handleSubmit(): void {
    if (!this.firstName || !this.lastName || !this.email || !this.password) {
      this.error = 'Por favor completa todos los campos';
      return;
    }

    this.loading = true;
    this.error = null;

    const registerData = {
      email: this.email,
      password: this.password,
      firstName: this.firstName,
      lastName: this.lastName
    };

    this.authService.register(registerData).subscribe({
      next: () => {
        this.loading = false;
        this.onSwitchToLogin.emit();
      },
      error: (err: any) => {
        this.error = err.error?.detail || 'Error al crear la cuenta';
        this.loading = false;
      },
    });
  }
}
