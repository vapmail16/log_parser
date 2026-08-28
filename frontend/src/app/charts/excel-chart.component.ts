import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

export interface ChartSeries {
  name: string;
  color: string;
  values: Array<number | null>;
}

@Component({
  selector: 'app-excel-chart',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './excel-chart.component.html',
  styleUrl: './excel-chart.component.scss',
})
export class ExcelChartComponent {
  @Input() chartType: 'line' | 'column' | 'bar' = 'line';
  @Input() title = '';
  @Input() xLabels: string[] = [];
  @Input() series: ChartSeries[] = [];
  @Input() yLabel = '';
  @Input() testId = 'excel-chart';

  readonly width = 720;
  readonly height = 300;
  readonly pad = { r: 18, t: 18, b: 42 };

  padL(): number {
    return this.chartType === 'bar' ? 148 : 56;
  }

  plotWidth(): number {
    return this.width - this.padL() - this.pad.r;
  }

  plotHeight(): number {
    return this.height - this.pad.t - this.pad.b;
  }

  yMax(): number {
    const values = this.series.flatMap((row) => row.values.filter((value): value is number => value != null));
    const peak = Math.max(0, ...values);
    if (this.isPercent()) {
      return peak > 100 ? peak * 1.15 : 120;
    }
    return peak === 0 ? 1 : peak * 1.15;
  }

  isPercent(): boolean {
    return this.yLabel.toLowerCase().includes('rate') || this.yLabel.includes('%');
  }

  xAt(index: number): number {
    const last = Math.max(this.xLabels.length - 1, 1);
    return this.padL() + (index / last) * this.plotWidth();
  }

  yAt(value: number): number {
    return this.pad.t + this.plotHeight() - (value / this.yMax()) * this.plotHeight();
  }

  ticks(): number[] {
    const max = this.yMax();
    return [0, 1, 2, 3, 4].map((step) => (max * step) / 4);
  }

  showLabel(index: number): boolean {
    const step = this.xLabels.length > 16 ? 3 : this.xLabels.length > 8 ? 2 : 1;
    return index % step === 0 || index === this.xLabels.length - 1;
  }

  linePath(values: Array<number | null>): string {
    const parts: string[] = [];
    let drawing = false;
    values.forEach((value, index) => {
      if (value == null) {
        drawing = false;
        return;
      }
      const command = drawing ? 'L' : 'M';
      parts.push(`${command}${this.xAt(index).toFixed(1)},${this.yAt(value).toFixed(1)}`);
      drawing = true;
    });
    return parts.join(' ');
  }

  markers(values: Array<number | null>): { x: number; y: number }[] {
    return values
      .map((value, index) => (value == null ? null : { x: this.xAt(index), y: this.yAt(value) }))
      .filter((point): point is { x: number; y: number } => point != null);
  }

  columns(): { x: number; y: number; width: number; height: number; value: number }[] {
    const values = this.series[0]?.values ?? [];
    const slot = this.plotWidth() / Math.max(this.xLabels.length, 1);
    const width = slot * 0.55;
    return values.flatMap((value, index) => {
      if (value == null) {
        return [];
      }
      const height = (value / this.yMax()) * this.plotHeight();
      return [
        {
          x: this.padL() + index * slot + (slot - width) / 2,
          y: this.pad.t + this.plotHeight() - height,
          width,
          height,
          value,
        },
      ];
    });
  }

  bars(): { y: number; width: number; label: string; value: number }[] {
    const values = this.series[0]?.values ?? [];
    const slot = this.plotHeight() / Math.max(this.xLabels.length, 1);
    const max = this.yMax();
    return this.xLabels.map((label, index) => {
      const value = values[index] ?? 0;
      return {
        y: this.pad.t + index * slot + slot * 0.2,
        width: (value / max) * this.plotWidth(),
        label,
        value,
      };
    });
  }

  barHeight(): number {
    return (this.plotHeight() / Math.max(this.xLabels.length, 1)) * 0.55;
  }

  axisTitleTransform(): string {
    return `rotate(-90 14 ${this.height / 2})`;
  }

  formatTick(value: number): string {
    if (this.isPercent()) {
      return `${Math.round(value)}%`;
    }
    if (value >= 100) {
      return String(Math.round(value));
    }
    return value.toFixed(value >= 10 ? 0 : 1);
  }
}
