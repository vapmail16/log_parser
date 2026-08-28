import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { ApiService } from '../api.service';
import { EventItem } from '../models';

@Component({
  selector: 'app-workbook',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './workbook.component.html',
  styleUrl: './workbook.component.scss',
})
export class WorkbookComponent implements OnInit {
  category = 'Agency';
  items: EventItem[] = [];
  error = '';

  constructor(
    private readonly api: ApiService,
    private readonly route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe((params) => {
      this.category = params.get('category') === 'SLT' ? 'SLT' : 'Agency';
      this.error = '';
      this.api.events({ category: this.category }).subscribe({
        next: (result) => (this.items = result.items),
        error: () => (this.error = 'Run the parser first, then open this sheet.'),
      });
    });
  }

  rowClass(item: EventItem): string {
    if (item.outcome === 'FAIL') {
      return 'fail';
    }
    if (item.requestCount > 1) {
      return 'retry';
    }
    if (item.status === 'Unmatched') {
      return 'unmatched';
    }
    return item.status === 'Matched' ? 'matched' : '';
  }

  fileLabel(paths: string[]): string {
    return paths.map((path) => path.split('/').pop() || path).join(', ') || '—';
  }
}
