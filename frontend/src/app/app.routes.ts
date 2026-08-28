import { Routes } from '@angular/router';

import { EventDetailComponent } from './pages/event-detail.component';
import { EventListComponent } from './pages/event-list.component';
import { OverviewComponent } from './pages/overview.component';
import { WorkbookComponent } from './pages/workbook.component';

export const routes: Routes = [
  { path: '', component: OverviewComponent },
  { path: 'sheets/:category', component: WorkbookComponent },
  { path: 'events', component: EventListComponent },
  { path: 'events/:eventId', component: EventDetailComponent },
];
