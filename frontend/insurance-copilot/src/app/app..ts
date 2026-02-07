import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthPageComponent } from './components/auth/auth-page/auth-page.component';
import { ChatInterfaceComponent } from './components/chat/chat-interface/chat-interface.component';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, AuthPageComponent, ChatInterfaceComponent],
  template: `
    <div class="min-h-screen">
      <app-auth-page
        *ngIf="!(isLoggedIn$ | async)"
      ></app-auth-page>
      <app-chat-interface
        *ngIf="(isLoggedIn$ | async)"
      ></app-chat-interface>
    </div>
  `,
})
export class App implements OnInit {
  isLoggedIn$;

  constructor(private authService: AuthService) {
    this.isLoggedIn$ = this.authService.currentUser$;
  }

  ngOnInit(): void {
    // Component initialization if needed
  }
}
