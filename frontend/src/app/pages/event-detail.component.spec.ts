import { ComponentFixture, TestBed } from '@angular/core/testing';
import { convertToParamMap } from '@angular/router';
import { ActivatedRoute, provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';

import { ApiService } from '../api.service';
import { EventItem, Hop } from '../models';
import { EventDetailComponent } from './event-detail.component';

const event: EventItem = {
  id: 'trade:SLT:SL_ALTER_TRADE:786712011',
  domain: 'trade',
  displayId: '786712011',
  groupId: 'HH0Y9V9',
  category: 'SLT',
  workflow: 'SL_ALTER_TRADE',
  requestType: 'SLT Trade Settlement',
  status: 'Matched',
  outcome: 'SUCCESS',
  start: '2026-08-24 13:04:47',
  end: '2026-08-24 13:06:04',
  durationSeconds: 76.576,
  requestCount: 1,
  responseCount: 1,
  requestFiles: [],
  responseFiles: [],
  requestPayload: '{}',
  responsePayload: 'success="true"',
};

const hop: Hop = {
  timestamp: '2026-08-24 13:04:47',
  thread: 'EMT-1',
  service: 'com.example.service.EMTService',
  workflow: 'SL_ALTER_TRADE',
  level: 'LDTLINFO',
  summary: 'sendEMTMessage() EMT Request Message',
  payload: '{"eventId":"ALTER_TRADE_786712011_1"}',
  sourceFile: 'a.log',
  gapSeconds: null,
  lines: ['line1 {"eventId":"ALTER_TRADE_786712011_1"}'],
};

describe('EventDetailComponent', () => {
  let fixture: ComponentFixture<EventDetailComponent>;
  let api: jasmine.SpyObj<ApiService>;

  async function setup(eventId: string | null, event$ = of(event), hops$ = of({ eventId: event.id, hops: [hop] })) {
    api = jasmine.createSpyObj('ApiService', ['event', 'timeline']);
    api.event.and.returnValue(event$);
    api.timeline.and.returnValue(hops$);
    await TestBed.resetTestingModule();
    await TestBed.configureTestingModule({
      imports: [EventDetailComponent],
      providers: [
        provideRouter([]),
        { provide: ApiService, useValue: api },
        {
          provide: ActivatedRoute,
          useValue: { snapshot: { paramMap: convertToParamMap(eventId ? { eventId } : {}) } },
        },
      ],
    }).compileComponents();
    fixture = TestBed.createComponent(EventDetailComponent);
    fixture.detectChanges();
    return fixture;
  }

  it('renders verdict and expands hop payload', async () => {
    await setup(event.id);
    expect(fixture.nativeElement.querySelector('[data-testid="event-title"]').textContent).toContain('786712011');
    expect(fixture.nativeElement.textContent).toContain('EMTService');
    expect(fixture.nativeElement.querySelector('[data-testid="event-request"]').textContent).toContain('{}');
    expect(fixture.nativeElement.querySelector('[data-testid="event-response"]').textContent).toContain('success="true"');
    expect(fixture.nativeElement.querySelector('[data-testid="verdict"]').textContent).toContain('SUCCESS');
    fixture.nativeElement.querySelector('.hops button').click();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[data-testid="hop-payload"]').textContent).toContain('ALTER_TRADE');
    fixture.nativeElement.querySelector('.hops button').click();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[data-testid="hop-payload"]')).toBeNull();
  });

  it('previews ten hop lines then shows the rest', async () => {
    const long: Hop = { ...hop, lines: Array.from({ length: 12 }, (_, i) => `L${i + 1}`) };
    await setup(event.id, of(event), of({ eventId: event.id, hops: [long] }));
    fixture.nativeElement.querySelector('.hops button').click();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[data-testid="hop-payload"]').textContent).toContain('L1');
    expect(fixture.nativeElement.querySelector('[data-testid="hop-payload"]').textContent).not.toContain('L12');
    fixture.nativeElement.querySelector('[data-testid="hop-more"]').click();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[data-testid="hop-payload"]').textContent).toContain('L12');
  });

  it('still shows request and response blocks when payloads are empty', async () => {
    const empty = { ...event, requestPayload: null, responsePayload: null, outcome: null };
    await setup(event.id, of(empty), of({ eventId: event.id, hops: [hop], requestPayload: null, responsePayload: null, outcome: null }));
    expect(fixture.nativeElement.querySelector('[data-testid="event-request"]').textContent).toContain('—');
    expect(fixture.nativeElement.querySelector('[data-testid="event-response"]').textContent).toContain('—');
    expect(fixture.nativeElement.querySelector('[data-testid="verdict"]').textContent).toContain('—');
  });

  it('shows missing id and load errors', async () => {
    await setup(null);
    expect(fixture.nativeElement.textContent).toContain('Missing event id');
    await setup('x', throwError(() => new Error('missing')), throwError(() => new Error('tl')));
    expect(fixture.nativeElement.textContent).toContain('Event not found');
  });
});
