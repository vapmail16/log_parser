import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';

import { ApiService } from '../api.service';
import { EventItem } from '../models';
import { EventListComponent } from './event-list.component';

const item: EventItem = {
  id: 'trade:Agency:AGY_TRADE:2890940',
  domain: 'trade',
  displayId: '2890940',
  groupId: 'UVGMWGKV',
  category: 'Agency',
  workflow: 'AGY_TRADE',
  requestType: 'Agency Trade',
  status: 'Unmatched',
  outcome: null,
  start: '2026-08-24 05:10:00',
  end: null,
  durationSeconds: null,
  requestCount: 1,
  responseCount: 0,
  requestFiles: [],
  responseFiles: [],
  requestPayload: null,
  responsePayload: null,
};

describe('EventListComponent', () => {
  let fixture: ComponentFixture<EventListComponent>;
  let api: jasmine.SpyObj<ApiService>;

  beforeEach(async () => {
    api = jasmine.createSpyObj('ApiService', ['events']);
    api.events.and.returnValue(of({ items: [item], total: 1 }));
    await TestBed.configureTestingModule({
      imports: [EventListComponent],
      providers: [provideRouter([]), { provide: ApiService, useValue: api }],
    }).compileComponents();
    fixture = TestBed.createComponent(EventListComponent);
    fixture.detectChanges();
  });

  it('renders events from the API', () => {
    expect(fixture.nativeElement.textContent).toContain('2890940');
    expect(fixture.nativeElement.textContent).toContain('Unmatched');
  });

  it('shows an error when the API fails', () => {
    api.events.and.returnValue(throwError(() => new Error('nope')));
    fixture = TestBed.createComponent(EventListComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Could not load events');
  });
});
