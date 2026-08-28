import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { AppComponent } from './app.component';

describe('AppComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [provideRouter([])],
    }).compileComponents();
  });

  it('renders brand title', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Log parser');
    expect(fixture.nativeElement.textContent).toContain('Agency');
    expect(fixture.nativeElement.textContent).toContain('SLT');
    expect(fixture.nativeElement.textContent).toContain('Events');
  });
});
