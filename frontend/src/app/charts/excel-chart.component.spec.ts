import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExcelChartComponent } from './excel-chart.component';

describe('ExcelChartComponent', () => {
  let fixture: ComponentFixture<ExcelChartComponent>;
  let component: ExcelChartComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ExcelChartComponent],
    }).compileComponents();
    fixture = TestBed.createComponent(ExcelChartComponent);
    component = fixture.componentInstance;
    component.title = 'Started vs Completed Throughput';
    component.yLabel = 'Trades per hour';
    component.testId = 'chart-throughput';
    component.xLabels = ['05:00', '06:00', '07:00'];
    component.series = [
      { name: 'Started', color: '#5b9bd5', values: [627, 0, 12] },
      { name: 'Completed', color: '#c45911', values: [626, 0, 12] },
    ];
    fixture.detectChanges();
  });

  it('renders an SVG line chart with series, markers, and 24-hour style labels', () => {
    const root = fixture.nativeElement.querySelector('[data-testid="chart-throughput"]');
    expect(root.textContent).toContain('Started vs Completed Throughput');
    expect(root.textContent).toContain('Started');
    expect(root.textContent).toContain('Completed');
    expect(root.querySelectorAll('svg').length).toBe(1);
    expect(root.querySelectorAll('[data-testid="series-line"]').length).toBe(2);
    expect(root.querySelectorAll('[data-testid="marker"]').length).toBe(6);
    expect(root.textContent).toContain('05:00');
  });

  it('breaks the line on idle (null) hours instead of dropping to 0%', () => {
    component.chartType = 'line';
    component.series = [{ name: 'Match rate', color: '#5b9bd5', values: [100, null, 99.8] }];
    fixture.detectChanges();
    const path = fixture.nativeElement.querySelector('[data-testid="series-line"]').getAttribute('d');
    expect(path.split('M').length - 1).toBe(2);
    expect(path).not.toContain('100,0');
  });

  it('renders duration columns only where there is a value', () => {
    component.chartType = 'column';
    component.title = 'Average Completion Duration';
    component.testId = 'chart-duration';
    component.series = [{ name: 'Avg sec', color: '#c45911', values: [33.5, null, 81.2] }];
    fixture.detectChanges();
    const root = fixture.nativeElement.querySelector('[data-testid="chart-duration"]');
    expect(root.textContent).toContain('Average Completion Duration');
    expect(root.querySelectorAll('[data-testid="column"]').length).toBe(2);
  });

  it('covers scale, label-step, and tick format branches', () => {
    component.series = [{ name: 'Empty', color: '#000', values: [null, 0] }];
    expect(component.yMax()).toBe(1);
    component.xLabels = Array.from({ length: 24 }, (_, i) => `${i}:00`);
    expect(component.showLabel(0)).toBeTrue();
    expect(component.showLabel(1)).toBeFalse();
    expect(component.showLabel(23)).toBeTrue();
    component.xLabels = Array.from({ length: 10 }, (_, i) => String(i));
    expect(component.showLabel(1)).toBeFalse();
    component.yLabel = 'Match rate %';
    expect(component.yMax()).toBe(120);
    expect(component.formatTick(99.8)).toBe('100%');
    component.series = [{ name: 'Over', color: '#000', values: [140] }];
    expect(component.yMax()).toBeCloseTo(161);
    component.yLabel = 'Trades per hour';
    expect(component.formatTick(627)).toBe('627');
    expect(component.formatTick(12.4)).toBe('12');
    expect(component.formatTick(3.2)).toBe('3.2');
    component.chartType = 'bar';
    expect(component.padL()).toBe(148);
    component.series = [];
    expect(component.columns()).toEqual([]);
    component.xLabels = ['A'];
    expect(component.bars()[0].value).toBe(0);
  });

  it('renders a horizontal status bar with labels', () => {
    component.chartType = 'bar';
    component.title = 'Status Breakdown';
    component.testId = 'chart-status';
    component.yLabel = 'Trades';
    component.xLabels = ['Unmatched', 'Matched'];
    component.series = [{ name: 'Trades', color: '#5b9bd5', values: [1, 1215] }];
    fixture.detectChanges();
    const root = fixture.nativeElement.querySelector('[data-testid="chart-status"]');
    expect(root.textContent).toContain('Unmatched');
    expect(root.textContent).toContain('Matched');
    expect(root.querySelectorAll('[data-testid="hbar"]').length).toBe(2);
    expect(root.textContent).toContain('1215');
  });
});
