import { ComponentFixture, TestBed } from '@angular/core/testing';
import { convertToParamMap } from '@angular/router';
import { ActivatedRoute, provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';

import { ApiService } from '../api.service';
import { EventItem } from '../models';
import { WorkbookComponent } from './workbook.component';

const item: EventItem = {
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
  requestPayload: null,
  responsePayload: null,
};

describe('WorkbookComponent', () => {
  let fixture: ComponentFixture<WorkbookComponent>;
  let api: jasmine.SpyObj<ApiService>;

  async function setup(category: string, items$ = of({ items: [item], total: 1 })) {
    api = jasmine.createSpyObj('ApiService', ['events']);
    api.events.and.returnValue(items$);
    await TestBed.resetTestingModule();
    await TestBed.configureTestingModule({
      imports: [WorkbookComponent],
      providers: [
        provideRouter([]),
        { provide: ApiService, useValue: api },
        { provide: ActivatedRoute, useValue: { paramMap: of(convertToParamMap({ category })) } },
      ],
    }).compileComponents();
    fixture = TestBed.createComponent(WorkbookComponent);
    fixture.detectChanges();
  }

  it('renders SLT sheet columns and trade id link', async () => {
    await setup('SLT');
    expect(fixture.nativeElement.querySelector('[data-testid="sheet-title"]').textContent).toContain('SLT');
    expect(fixture.nativeElement.textContent).toContain('Workflow');
    expect(fixture.nativeElement.textContent).toContain('786712011');
    expect(fixture.nativeElement.textContent).toContain('Request Payload');
    expect(fixture.nativeElement.textContent).toContain('Response Payload');
    expect(fixture.nativeElement.textContent).toContain('Outcome');
    expect(api.events).toHaveBeenCalledWith({ category: 'SLT' });
  });

  it('shows request response and outcome from the parser row', async () => {
    const filled = {
      ...item,
      requestPayload: '{"settlementTradeId":"786712011"}',
      responsePayload: '{"success":"true"}',
      outcome: 'SUCCESS',
    };
    await setup('SLT', of({ items: [filled], total: 1 }));
    const table = fixture.nativeElement.querySelector('[data-testid="sheet-table"]').textContent;
    expect(table).toContain('settlementTradeId');
    expect(table).toContain('"success":"true"');
    expect(table).toContain('SUCCESS');
    expect(fixture.componentInstance.payloadText(null)).toBe('—');
    expect(fixture.componentInstance.payloadText('  ')).toBe('—');
  });

  it('renders Agency sheet without workflow column', async () => {
    await setup('Agency');
    expect(fixture.nativeElement.querySelector('[data-testid="sheet-title"]').textContent).toContain('Agency');
    expect(fixture.nativeElement.textContent).not.toContain('Workflow');
  });

  it('asks the user to run the parser when the API fails', async () => {
    await setup('Agency', throwError(() => new Error('none')));
    expect(fixture.nativeElement.textContent).toContain('Run the parser first');
  });

  it('colours fail retry unmatched and matched rows like the workbook', async () => {
    await setup('SLT');
    const component = fixture.componentInstance;
    expect(component.rowClass({ ...item, outcome: 'FAIL' })).toBe('fail');
    expect(component.rowClass({ ...item, requestCount: 2 })).toBe('retry');
    expect(component.rowClass({ ...item, status: 'Unmatched', outcome: null })).toBe('unmatched');
    expect(component.rowClass(item)).toBe('matched');
    expect(component.fileLabel(['/tmp/ldtl-trading-2026-08-24.0.log'])).toBe('ldtl-trading-2026-08-24.0.log');
    expect(component.fileLabel([])).toBe('—');
    expect(
      component.fileLabel([
        'C:\\Users\\example\\Desktop\\logs\\ldtl-trading-2026-08-24.0.log.gz',
      ])
    ).toBe('ldtl-trading-2026-08-24.0.log.gz');
  });

  it('renders only the log file name in source-file cells', async () => {
    const windowsItem = {
      ...item,
      requestFiles: [
        'C:\\Users\\example\\Desktop\\logs\\ldtl-trading-2026-08-24.2.log.gz',
      ],
      responseFiles: [
        'C:\\Users\\example\\Desktop\\logs\\ldtl-trading-2026-08-24.2.log.gz',
      ],
    };
    await setup('SLT', of({ items: [windowsItem], total: 1 }));
    const table = fixture.nativeElement.querySelector('[data-testid="sheet-table"]').textContent;
    expect(table).toContain('ldtl-trading-2026-08-24.2.log.gz');
    expect(table).not.toContain('C:\\Users');
    expect(table).toContain('786712011');
    expect(table).toContain('SUCCESS');
  });
});
