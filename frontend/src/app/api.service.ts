import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { DomainInfo, EventItem, EventQuery, HealthInfo, Metrics, RunInfo, TimelineResult } from './models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private readonly http: HttpClient) {}

  health(): Observable<HealthInfo> {
    return this.http.get<HealthInfo>('/api/health');
  }

  listDomains(): Observable<DomainInfo[]> {
    return this.http.get<DomainInfo[]>('/api/domains');
  }

  loadSample(): Observable<RunInfo> {
    return this.http.post<RunInfo>('/api/runs/sample', {});
  }

  createRun(domain: string, sourcePath: string): Observable<RunInfo> {
    return this.http.post<RunInfo>('/api/runs', { domain, sourcePath });
  }

  latestRun(): Observable<RunInfo> {
    return this.http.get<RunInfo>('/api/runs/latest');
  }

  metrics(category?: string): Observable<Metrics> {
    let params = new HttpParams();
    if (category) {
      params = params.set('category', category);
    }
    return this.http.get<Metrics>('/api/runs/latest/metrics', { params });
  }

  events(query: EventQuery = {}): Observable<{ items: EventItem[]; total: number }> {
    let params = new HttpParams();
    Object.entries(query).forEach(([key, value]) => {
      if (value) {
        params = params.set(key, value);
      }
    });
    return this.http.get<{ items: EventItem[]; total: number }>('/api/runs/latest/events', { params });
  }

  event(eventId: string): Observable<EventItem> {
    return this.http.get<EventItem>(`/api/runs/latest/events/${encodeURIComponent(eventId)}`);
  }

  timeline(eventId: string): Observable<TimelineResult> {
    return this.http.get<TimelineResult>(`/api/runs/latest/events/${encodeURIComponent(eventId)}/timeline`);
  }
}
