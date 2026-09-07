import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { ApiService } from '../api.service';
import { EventItem, Hop } from '../models';

const LINE_PREVIEW = 10;

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
  expandedLines = new Set<number>();
  timelineRequest = '';
  timelineResponse = '';
  timelineOutcome = '';
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
      next: (result) => {
        this.hops = result.hops;
        this.timelineRequest = result.requestPayload ?? '';
        this.timelineResponse = result.responsePayload ?? '';
        this.timelineOutcome = result.outcome ?? '';
      },
      error: () => (this.error = this.error || 'Timeline unavailable'),
    });
  }

  requestText(): string {
    return this.event?.requestPayload || this.timelineRequest;
  }

  responseText(): string {
    return this.event?.responsePayload || this.timelineResponse;
  }

  outcomeText(): string {
    return this.event?.outcome || this.timelineOutcome || '—';
  }

  hopLines(hop: Hop): string[] {
    if (hop.lines?.length) {
      return hop.lines;
    }
    return hop.payload ? [hop.payload] : [];
  }

  visibleLines(hop: Hop, index: number): string[] {
    const lines = this.hopLines(hop);
    if (this.expandedLines.has(index) || lines.length <= LINE_PREVIEW) {
      return lines;
    }
    return lines.slice(0, LINE_PREVIEW);
  }

  hiddenCount(hop: Hop, index: number): number {
    const extra = this.hopLines(hop).length - LINE_PREVIEW;
    return this.expandedLines.has(index) || extra <= 0 ? 0 : extra;
  }

  toggleHop(index: number): void {
    this.openHop = this.openHop === index ? null : index;
  }

  showAllLines(index: number): void {
    this.expandedLines = new Set([...this.expandedLines, index]);
  }
}
