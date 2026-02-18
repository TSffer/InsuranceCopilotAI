import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, map, catchError, of } from 'rxjs';
import { AuthRequest, AuthResponse, User, RegisterRequest } from '@/app/shared/models/types';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api/v1/auth'; // Adjust if environment config available
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  private tokenSubject = new BehaviorSubject<string | null>(null);
  public token$ = this.tokenSubject.asObservable();

  private isLoadingSubject = new BehaviorSubject(true);
  public isLoading$ = this.isLoadingSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {
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
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    return this.http.post<any>(`${this.apiUrl}/token`, formData).pipe(
      map(response => {
        //Backend returns Token model: { access_token, token_type }
        // We need to fetch user details or construct partial user. 
        // For now, let's decode token or just store it. 
        // Since backend doesn't return User object on login yet (only token), 
        // we might need a /me endpoint or update login response.
        // BUT, for speed, let's assume we can derive or fetch user. 
        // Actually, let's update backend to return User info if possible? 
        // No, standard OAuth2 returns token.
        // Let's decode token (if JWT) or just set a dummy user state until we have /me.

        const authResponse: AuthResponse = {
          token: response.access_token,
          user: {
            id: '0',
            email: credentials.email,
            firstName: 'User',
            lastName: '',
            role: 'broker',
            createdAt: new Date()
          }, // Placeholder until we fetch real user
          expiresIn: 1800
        };
        return authResponse;
      }),
      tap((response) => {
        this.setSession(response);
      })
    );
  }

  register(data: RegisterRequest): Observable<User> {
    // Backend expects UserCreate: { email, password, username, role }
    const payload = {
      email: data.email,
      password: data.password,
      username: data.company || data.email.split('@')[0], // Fallback username
      role: 'broker' // Default role
    };

    return this.http.post<User>(`${this.apiUrl}/register`, payload);
  }

  private setSession(authResult: AuthResponse) {
    localStorage.setItem('auth_token', authResult.token);
    if (authResult.refresh_token) {
      localStorage.setItem('auth_refresh_token', authResult.refresh_token);
    }
    // Persist user info if available
    localStorage.setItem('auth_user', JSON.stringify(authResult.user));

    this.tokenSubject.next(authResult.token);
    this.currentUserSubject.next(authResult.user);
  }

  logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_refresh_token');
    localStorage.removeItem('auth_user');
    this.tokenSubject.next(null);
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
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

  getRefreshToken(): string | null {
    return localStorage.getItem('auth_refresh_token');
  }

  refreshToken(): Observable<AuthResponse> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      this.logout();
      return of(null as any);
    }

    return this.http.post<any>(`${this.apiUrl}/refresh`, { refresh_token: refreshToken }).pipe(
      map(response => {
        // response matches Token schema from backend: { access_token, refresh_token, token_type }
        // We need to map it to AuthResponse format expected by setSession or just update token
        // But setSession expects AuthResponse which includes User. 
        // The refresh endpoint only returns Token. 
        // So we need to reconstruct AuthResponse reusing current user.

        const currentUser = this.getCurrentUser();
        const authResponse: AuthResponse = {
          token: response.access_token,
          refresh_token: response.refresh_token, // Update refresh token if rotated
          user: currentUser!,
          expiresIn: 1800 // default
        };
        return authResponse;
      }),
      tap(response => this.setSession(response)),
      catchError(err => {
        this.logout();
        throw err;
      })
    );
  }
}
