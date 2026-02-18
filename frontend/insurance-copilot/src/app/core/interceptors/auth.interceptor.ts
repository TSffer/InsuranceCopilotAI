import { HttpInterceptorFn, HttpErrorResponse, HttpRequest, HttpHandlerFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { catchError, switchMap, throwError, BehaviorSubject, filter, take } from 'rxjs';

let isRefreshing = false;
const refreshTokenSubject = new BehaviorSubject<string | null>(null);

export const authInterceptor: HttpInterceptorFn = (req, next) => {
	const authService = inject(AuthService);
	const token = authService.getToken() || localStorage.getItem('auth_token');

	let request = req;
	if (token) {
		request = req.clone({
			setHeaders: {
				Authorization: `Bearer ${token}`
			}
		});
	}

	return next(request).pipe(
		catchError((error) => {
			if (error instanceof HttpErrorResponse && error.status === 401 && !request.url.includes('auth/token') && !request.url.includes('auth/refresh')) {
				return handle401Error(request, next, authService);
			}
			return throwError(() => error);
		})
	);
};

function handle401Error(request: HttpRequest<unknown>, next: HttpHandlerFn, authService: AuthService) {
	if (!isRefreshing) {
		isRefreshing = true;
		refreshTokenSubject.next(null);

		return authService.refreshToken().pipe(
			switchMap((authResponse) => {
				isRefreshing = false;
				refreshTokenSubject.next(authResponse.token);
				return next(request.clone({
					setHeaders: { Authorization: `Bearer ${authResponse.token}` }
				}));
			}),
			catchError((err) => {
				isRefreshing = false;
				authService.logout();
				return throwError(() => err);
			})
		);
	} else {
		return refreshTokenSubject.pipe(
			filter(token => token !== null),
			take(1),
			switchMap((token) => {
				return next(request.clone({
					setHeaders: { Authorization: `Bearer ${token}` }
				}));
			})
		);
	}
}
