import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { delay } from 'rxjs/operators';
import { InsuranceQuote, QuoteRequest, QuoteResponse } from '@/app/shared/models/types';
import { mockQuotes } from '@/app/shared/data/mock-data';

@Injectable({
  providedIn: 'root',
})
export class QuoteService {
  getQuotes(request: QuoteRequest): Observable<QuoteResponse> {
    // Mock API call - in real app, call actual backend
    return of({
      quotes: mockQuotes,
      processingTime: 1200,
    }).pipe(delay(1200));
  }

  getQuoteById(id: string): Observable<InsuranceQuote | undefined> {
    const quote = mockQuotes.find((q) => q.id === id);
    return of(quote).pipe(delay(300));
  }

  getAllQuotes(): Observable<InsuranceQuote[]> {
    return of(mockQuotes).pipe(delay(500));
  }
}
