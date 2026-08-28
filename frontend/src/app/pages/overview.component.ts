import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { ApiService } from '../api.service';
import { ChartSeries, ExcelChartComponent } from '../charts/excel-chart.component';
import { DomainInfo, HourlyRow, Metrics, RunInfo } from '../models';

@Component({
  selector: 'app-overview',
  standalone: true,
  imports: [CommonModule, FormsModule, ExcelChartComponent],
  templateUrl: './overview.component.html',
  styleUrl: './overview.component.scss',
})
export class OverviewComponent implements OnInit {
  domains: DomainInfo[] = [];
  domain = 'trade';
  sourcePath = '';
  category: 'Agency' | 'SLT' = 'Agency';
  run: RunInfo | null = null;
  metrics: Metrics | null = null;
  error = '';
  loading = false;
  samplePath = '';
  parserScript = '';
  usingLocalParser = false;

  constructor(
    private readonly api: ApiService,
    private readonly router: Router
  ) {}

  ngOnInit(): void {
    this.api.listDomains().subscribe({
      next: (domains) => (this.domains = domains),
      error: () => (this.error = 'Could not load domains'),
    });
    this.api.health().subscribe({
      next: (health) => {
        this.samplePath = health.samplePath;
        this.parserScript = health.parserScript ?? '';
        this.usingLocalParser = Boolean(health.usingLocalParser);
      },
      error: () => undefined,
    });
    this.api.latestRun().subscribe({
      next: (run) => {
        this.run = run;
        this.refreshMetrics();
      },
      error: () => undefined,
    });
  }

  useSample(): void {
    this.runAction(() => this.api.loadSample());
  }

  analyze(): void {
    if (!this.sourcePath.trim()) {
      this.error = 'Enter a log folder path';
      return;
    }
    this.runAction(() => this.api.createRun(this.domain, this.sourcePath.trim()));
  }

  setCategory(category: 'Agency' | 'SLT'): void {
    this.category = category;
    if (this.run) {
      this.refreshMetrics();
    }
  }

  openHour(row: HourlyRow): void {
    if (row.started <= 0) {
      return;
    }
    void this.router.navigate(['/events'], { queryParams: { category: this.category, hour: row.hour } });
  }

  openDeal(groupId: string): void {
    void this.router.navigate(['/events'], { queryParams: { category: this.category, dealId: groupId } });
  }

  openIssue(eventId: string): void {
    void this.router.navigate(['/events', eventId]);
  }

  hours(): HourlyRow[] {
    return this.metrics?.hourly ?? [];
  }

  hourLabels(): string[] {
    return this.hours().map((row) => row.hour);
  }

  throughputSeries(): ChartSeries[] {
    return [
      { name: 'Started', color: '#5b9bd5', values: this.hours().map((row) => row.started) },
      { name: 'Completed', color: '#c45911', values: this.hours().map((row) => row.completed) },
    ];
  }

  durationSeries(): ChartSeries[] {
    return [{ name: 'Avg sec', color: '#c45911', values: this.hours().map((row) => row.avgDurationSeconds) }];
  }

  matchSeries(): ChartSeries[] {
    return [{ name: 'Match rate', color: '#5b9bd5', values: this.hours().map((row) => row.matchRate) }];
  }

  statusRows(): { label: string; count: number }[] {
    if (!this.metrics) {
      return [];
    }
    return [
      { label: 'Unmatched', count: this.metrics.kpis.unmatchedCount },
      { label: 'Matched', count: this.metrics.kpis.completedResponses },
    ];
  }

  statusLabels(): string[] {
    return this.statusRows().map((row) => row.label);
  }

  statusSeries(): ChartSeries[] {
    return [{ name: 'Trades', color: '#5b9bd5', values: this.statusRows().map((row) => row.count) }];
  }

  requestTypeLabels(): string[] {
    return (this.metrics?.requestTypes ?? []).map((row) => row.requestType);
  }

  requestTypeSeries(): ChartSeries[] {
    return [{ name: '% of requests', color: '#5b9bd5', values: (this.metrics?.requestTypes ?? []).map((row) => row.percent) }];
  }

  peak() {
    const hours = this.hours();
    if (!hours.length) {
      return null;
    }
    const started = hours.reduce((best, row) => (row.started > best.started ? row : best));
    const completed = hours.reduce((best, row) => (row.completed > best.completed ? row : best));
    return {
      peakStarted: started.started,
      peakCompleted: completed.completed,
      startedHour: started.hour,
      completedHour: completed.hour,
    };
  }

  peakLabels(): string[] {
    return ['Peak Completed', 'Peak Started'];
  }

  peakSeries(): ChartSeries[] {
    const peak = this.peak();
    return [{ name: 'Trades', color: '#548235', values: [peak?.peakCompleted ?? 0, peak?.peakStarted ?? 0] }];
  }

  narrative(): string {
    const active = this.hours().filter((row) => row.started > 0);
    const peak = this.peak();
    if (!active.length || !peak) {
      return '';
    }
    return `Activity spans ${active[0].hour} to ${active[active.length - 1].hour}. Peak starts: ${peak.peakStarted} at ${peak.startedHour}; peak completions: ${peak.peakCompleted} at ${peak.completedHour}.`;
  }

  private runAction(action: () => ReturnType<ApiService['loadSample']>): void {
    this.loading = true;
    this.error = '';
    action().subscribe({
      next: (run) => {
        this.run = run;
        this.loading = false;
        this.refreshMetrics();
      },
      error: (err: { error?: { message?: string } }) => {
        this.loading = false;
        this.error = err.error?.message ?? 'Analyze failed';
      },
    });
  }

  private refreshMetrics(): void {
    this.api.metrics(this.category).subscribe({
      next: (metrics) => (this.metrics = metrics),
      error: () => (this.error = 'Could not load metrics'),
    });
  }
}
