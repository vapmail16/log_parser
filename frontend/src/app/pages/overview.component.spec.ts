import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';

import { ApiService } from '../api.service';
import { Metrics, RunInfo } from '../models';
import { OverviewComponent } from './overview.component';

const run: RunInfo = {
  id: 'sample',
  domain: 'trade',
  sourcePath: '/demo',
  status: 'completed',
  createdAt: '2026-08-24',
  eventCount: 6,
};

const metrics: Metrics = {
  category: 'Agency',
  kpis: {
    totalRequests: 2,
    completedResponses: 1,
    unmatchedCount: 1,
    matchRate: 50,
    avgDurationSeconds: 17.3,
    p95DurationSeconds: 17.3,
    maxDurationSeconds: 17.3,
  },
  hourly: [
    { hour: '05:00', started: 2, completed: 1, avgDurationSeconds: 17.3, matchRate: 50, completionGap: -1 },
    { hour: '08:00', started: 0, completed: 0, avgDurationSeconds: null, matchRate: null, completionGap: 0 },
  ],
  requestTypes: [{ requestType: 'Agency Trade', count: 2, percent: 100 }],
  perDeal: [
    { groupId: 'WNGH58WU', tradeCount: 1, minDurationSeconds: 17.3, maxDurationSeconds: 17.3, avgDurationSeconds: 17.3 },
  ],
  issues: [{ kind: 'unmatched', eventId: 'e1', displayId: '2890940', summary: 'No matching response' }],
};

describe('OverviewComponent', () => {
  let fixture: ComponentFixture<OverviewComponent>;
  let api: jasmine.SpyObj<ApiService>;
  let router: Router;

  beforeEach(async () => {
    api = jasmine.createSpyObj('ApiService', [
      'listDomains',
      'health',
      'loadSample',
      'createRun',
      'metrics',
      'latestRun',
    ]);
    api.listDomains.and.returnValue(of([{ id: 'trade', label: 'Trade processing', status: 'ready' }]));
    api.health.and.returnValue(
      of({
        status: 'ok',
        samplePath: '/tmp/demo',
        parserScript: '/tmp/trade_analysis_demo.py',
        usingLocalParser: false,
      })
    );
    api.loadSample.and.returnValue(of(run));
    api.createRun.and.returnValue(of(run));
    api.metrics.and.returnValue(of(metrics));
    api.latestRun.and.returnValue(throwError(() => ({ status: 404 })));

    await TestBed.configureTestingModule({
      imports: [OverviewComponent],
      providers: [provideRouter([]), provideHttpClient(), { provide: ApiService, useValue: api }],
    }).compileComponents();

    fixture = TestBed.createComponent(OverviewComponent);
    router = TestBed.inject(Router);
    spyOn(router, 'navigate');
    fixture.detectChanges();
  });

  it('loads sample and shows Excel-style KPIs, tables, and SVG charts', () => {
    expect(fixture.nativeElement.querySelector('[data-testid="parser-script"]').textContent).toContain('demo');
    fixture.nativeElement.querySelector('[data-testid="sample"]').click();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[data-testid="unmatched-count"]').textContent).toContain('1');
    expect(fixture.nativeElement.querySelector('[data-testid="hourly"]').textContent).toContain('05:00');
    expect(fixture.nativeElement.querySelector('[data-testid="hourly"]').textContent).toContain('08:00');
    expect(fixture.nativeElement.querySelector('[data-testid="hourly"]').textContent).toContain('—');
    expect(fixture.nativeElement.querySelector('[data-testid="narrative"]').textContent).toContain('Peak starts: 2 at 05:00');
    expect(fixture.nativeElement.querySelector('[data-testid="chart-throughput"] svg')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('[data-testid="chart-throughput"]').textContent).toContain(
      'Started vs Completed Throughput'
    );
    expect(fixture.nativeElement.querySelector('[data-testid="chart-duration"]').textContent).toContain(
      'Average Completion Duration'
    );
    expect(fixture.nativeElement.querySelector('[data-testid="chart-match"]').textContent).toContain('Hourly Match Rate');
    expect(fixture.nativeElement.querySelector('[data-testid="chart-status"]').textContent).toContain('Status Breakdown');
    expect(fixture.nativeElement.querySelectorAll('[data-testid="series-line"]').length).toBeGreaterThan(0);
    expect(fixture.nativeElement.querySelector('[data-testid="issues"]').textContent).toContain('unmatched (1)');
    fixture.componentInstance.hourFilter = 'active';
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[data-testid="hourly"]').textContent).toContain('05:00');
    expect(fixture.nativeElement.querySelector('[data-testid="hourly"]').textContent).not.toContain('08:00');
    fixture.componentInstance.hourFilter = 'gaps';
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[data-testid="hourly"]').textContent).toContain('05:00');
    fixture.componentInstance.toggleIssueKind('unmatched');
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[data-testid="issues"]').textContent).not.toContain('2890940');
  });

  it('requires a folder path before analyze', () => {
    fixture.nativeElement.querySelector('[data-testid="analyze"]').click();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[data-testid="error"]').textContent).toContain('Enter a log folder');
    expect(api.createRun).not.toHaveBeenCalled();
  });

  it('analyzes a folder and can switch to SLT', () => {
    const slt = {
      ...metrics,
      category: 'SLT',
      requestTypes: [{ requestType: 'SLT Trade Settlement', count: 3, percent: 82.9 }],
    };
    api.metrics.and.returnValue(of(slt));
    fixture.componentInstance.sourcePath = '/logs';
    fixture.detectChanges();
    fixture.nativeElement.querySelector('[data-testid="analyze"]').click();
    fixture.detectChanges();
    fixture.nativeElement.querySelector('[data-testid="tab-slt"]').click();
    fixture.detectChanges();
    expect(api.metrics).toHaveBeenCalledWith('SLT');
    expect(fixture.nativeElement.textContent).toContain('SLT Trade Settlement');
  });

  it('surfaces analyze errors', () => {
    api.loadSample.and.returnValue(throwError(() => ({ error: { message: 'boom' } })));
    fixture.nativeElement.querySelector('[data-testid="sample"]').click();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[data-testid="error"]').textContent).toContain('boom');
  });

  it('navigates from hour deal and issue', () => {
    const component = fixture.componentInstance;
    component.run = run;
    component.metrics = metrics;
    component.openHour(metrics.hourly[0]);
    component.openHour(metrics.hourly[1]);
    component.openDeal('WNGH58WU');
    component.openIssue('e1');
    expect(router.navigate).toHaveBeenCalledTimes(3);
    expect(component.narrative()).toContain('05:00');
    expect(component.peakSeries()[0].values).toEqual([1, 2]);
  });

  it('handles empty metrics helpers and load errors', () => {
    const component = fixture.componentInstance;
    expect(component.statusRows()).toEqual([]);
    expect(component.narrative()).toBe('');
    expect(component.peak()).toBeNull();
    expect(component.peakSeries()[0].values).toEqual([0, 0]);
    component.setCategory('SLT');
    expect(api.metrics).not.toHaveBeenCalledWith('SLT');
    api.listDomains.and.returnValue(throwError(() => new Error('domains')));
    api.health.and.returnValue(throwError(() => new Error('health')));
    api.metrics.and.returnValue(throwError(() => new Error('metrics')));
    fixture = TestBed.createComponent(OverviewComponent);
    fixture.detectChanges();
    fixture.nativeElement.querySelector('[data-testid="sample"]').click();
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Could not load');
  });
});

describe('OverviewComponent latest run', () => {
  it('hydrates KPIs from the latest parser run', async () => {
    const api = jasmine.createSpyObj('ApiService', [
      'listDomains',
      'health',
      'loadSample',
      'createRun',
      'metrics',
      'latestRun',
    ]);
    api.listDomains.and.returnValue(of([{ id: 'trade', label: 'Trade processing', status: 'ready' }]));
    api.health.and.returnValue(
      of({
        status: 'ok',
        samplePath: '/tmp/demo',
        parserScript: '/tmp/trade_analysis_v2.py',
        usingLocalParser: true,
      })
    );
    api.latestRun.and.returnValue(of(run));
    api.metrics.and.returnValue(of(metrics));
    await TestBed.resetTestingModule();
    await TestBed.configureTestingModule({
      imports: [OverviewComponent],
      providers: [provideRouter([]), provideHttpClient(), { provide: ApiService, useValue: api }],
    }).compileComponents();
    const fixture = TestBed.createComponent(OverviewComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[data-testid="parser-script"]').textContent).toContain('local');
    expect(fixture.nativeElement.querySelector('[data-testid="unmatched-count"]').textContent).toContain('1');
    expect(api.metrics).toHaveBeenCalledWith('Agency');
  });
});
