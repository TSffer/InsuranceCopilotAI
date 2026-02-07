import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { delay, tap } from 'rxjs/operators';
import { AuthRequest, AuthResponse, User } from '../shared/models/types';
import { mockUsers } from '../shared/data/mock-data';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  private tokenSubject = new BehaviorSubject<string | null>(null);
  public token$ = this.tokenSubject.asObservable();

  private isLoadingSubject = new BehaviorSubject(true);
  public isLoading$ = this.isLoadingSubject.asObservable();

  constructor() {
    this.initializeAuth();
  }

  private initializeAuth(): void {
    const token = localStorage.getItem('auth_token');
    const user = localStorage.getItem('auth_user');

    if (token && user) {
      this.tokenSubject.next(token);
      this.currentUserSubject.next(JSON.parse(user));
    }

    this.isLoadingSubject.next(false);
  }

  login(credentials: AuthRequest): Observable<AuthResponse> {
    // Mock authentication - in real app, call API
    const user = mockUsers.broker1;
    const token = 'mock-token-' + Date.now();

    return of({
      token,
      user,
      expiresIn: 3600,
    }).pipe(
      delay(800),
      tap((response) => {
        localStorage.setItem('auth_token', response.token);
        localStorage.setItem('auth_user', JSON.stringify(response.user));
        this.tokenSubject.next(response.token);
        this.currentUserSubject.next(response.user);
      })
    );
  }

  register(email: string, password: string, firstName: string, lastName: string): Observable<AuthResponse> {
    const user: User = {
      id: 'user-' + Date.now(),
      email,
      firstName,
      lastName,
      createdAt: new Date(),
      role: 'broker',
    };
    const token = 'mock-token-' + Date.now();

    return of({
      token,
      user,
      expiresIn: 3600,
    }).pipe(
      delay(800),
      tap((response) => {
        localStorage.setItem('auth_token', response.token);
        localStorage.setItem('auth_user', JSON.stringify(response.user));
        this.tokenSubject.next(response.token);
        this.currentUserSubject.next(response.user);
      })
    );
  }

  logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    this.tokenSubject.next(null);
    this.currentUserSubject.next(null);
  }

  isLoggedIn(): boolean {
    return !!this.tokenSubject.value;
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  getToken(): string | null {
    return this.tokenSubject.value;
  }
}
