import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { ApiService } from '../api.service';
import { EventItem, Hop } from '../models';

@Component({
  selector: 'app-event-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './event-detail.component.html',
  styleUrl: './event-detail.component.scss',
})
export class EventDetailComponent implements OnInit {
  event: EventItem | null = null;
  hops: Hop[] = [];
  openHop: number | null = null;
  error = '';

  constructor(
    private readonly api: ApiService,
    private readonly route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    const eventId = this.route.snapshot.paramMap.get('eventId');
    if (!eventId) {
      this.error = 'Missing event id';
      return;
    }
    this.api.event(eventId).subscribe({
      next: (event) => (this.event = event),
      error: () => (this.error = 'Event not found'),
    });
    this.api.timeline(eventId).subscribe({
      next: (result) => (this.hops = result.hops),
      error: () => (this.error = this.error || 'Timeline unavailable'),
    });
  }

  toggleHop(index: number): void {
    this.openHop = this.openHop === index ? null : index;
  }
}
