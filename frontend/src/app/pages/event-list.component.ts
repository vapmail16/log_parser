import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { ApiService } from '../api.service';
import { EventItem } from '../models';

@Component({
  selector: 'app-event-list',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './event-list.component.html',
  styleUrl: './event-list.component.scss',
})
export class EventListComponent implements OnInit {
  items: EventItem[] = [];
  error = '';

  constructor(
    private readonly api: ApiService,
    private readonly route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.route.queryParamMap.subscribe((params) => {
      this.api
        .events({
          category: params.get('category') ?? undefined,
          status: params.get('status') ?? undefined,
          dealId: params.get('dealId') ?? undefined,
          hour: params.get('hour') ?? undefined,
          q: params.get('q') ?? undefined,
        })
        .subscribe({
          next: (result) => (this.items = result.items),
          error: () => (this.error = 'Could not load events'),
        });
    });
  }
}
