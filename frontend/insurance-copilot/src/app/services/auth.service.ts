import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, map, catchError, of, switchMap } from 'rxjs';
import { AuthRequest, AuthResponse, User, RegisterRequest } from '@/app/shared/models/types';
import { Router } from '@angular/router';
import { environment } from '@/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private apiUrl = environment.apiUrl + '/auth';

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

  getMe(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/me`);
  }

  login(credentials: AuthRequest): Observable<AuthResponse> {

    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    return this.http.post<any>(`${this.apiUrl}/token`, formData).pipe(
      map(response => {
        const authResponse: AuthResponse = {
          token: response.access_token,
          user: {} as User,
          expiresIn: 1800
        };
        return authResponse;
      }),
      tap((response) => {
        this.setSession(response);
      }),
      switchMap(authResponse => {
        return this.getMe().pipe(
          map(user => {
            authResponse.user = user;
            return authResponse;
          }),
          catchError(() => of(authResponse))
        );
      })
    );
  }

  register(data: RegisterRequest): Observable<User> {

    const payload = {
      email: data.email,
      password: data.password,
      username: data.company || data.email.split('@')[0],
      role: 'broker'
    };

    return this.http.post<User>(`${this.apiUrl}/register`, payload);
  }

  private setSession(authResult: AuthResponse) {
    localStorage.setItem('auth_token', authResult.token);
    if (authResult.refresh_token) {
      localStorage.setItem('auth_refresh_token', authResult.refresh_token);
    }

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
        const currentUser = this.getCurrentUser();
        const authResponse: AuthResponse = {
          token: response.access_token,
          refresh_token: response.refresh_token,
          user: currentUser!,
          expiresIn: 1800
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
