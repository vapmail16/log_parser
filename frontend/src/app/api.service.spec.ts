import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ApiService } from './api.service';

describe('ApiService', () => {
  let service: ApiService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(ApiService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('lists domains and loads sample', () => {
    service.health().subscribe((h) => expect(h.samplePath).toContain('demo'));
    http.expectOne('/api/health').flush({ status: 'ok', samplePath: '/tmp/demo' });

    service.listDomains().subscribe((rows) => expect(rows[0].id).toBe('trade'));
    http.expectOne('/api/domains').flush([{ id: 'trade', label: 'Trade', status: 'ready' }]);

    service.loadSample().subscribe((run) => expect(run.eventCount).toBe(2));
    http.expectOne('/api/runs/sample').flush({ id: 'sample', eventCount: 2 });
  });

  it('creates a run and fetches metrics/events/timeline', () => {
    service.createRun('trade', '/logs').subscribe((run) => expect(run.domain).toBe('trade'));
    const create = http.expectOne('/api/runs');
    expect(create.request.body).toEqual({ domain: 'trade', sourcePath: '/logs' });
    create.flush({ domain: 'trade' });

    service.latestRun().subscribe((run) => expect(run.id).toBe('r1'));
    http.expectOne('/api/runs/latest').flush({ id: 'r1' });

    service.metrics('SLT').subscribe((m) => expect(m.category).toBe('SLT'));
    const metrics = http.expectOne((req) => req.url === '/api/runs/latest/metrics');
    expect(metrics.request.params.get('category')).toBe('SLT');
    metrics.flush({ category: 'SLT' });

    service.events({ status: 'Unmatched', q: '289' }).subscribe((res) => expect(res.total).toBe(1));
    const events = http.expectOne((req) => req.url === '/api/runs/latest/events');
    expect(events.request.params.get('status')).toBe('Unmatched');
    events.flush({ items: [], total: 1 });

    service.event('abc').subscribe((event) => expect(event.id).toBe('abc'));
    http.expectOne('/api/runs/latest/events/abc').flush({ id: 'abc' });

    service.timeline('abc').subscribe((res) => expect(res.hops.length).toBe(1));
    http.expectOne('/api/runs/latest/events/abc/timeline').flush({ eventId: 'abc', hops: [{}] });
  });
});
