import { expect, test } from '@playwright/test';

test('sample data shows Agency metrics then drills into an event timeline', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Trade log analysis' })).toBeVisible();

  await page.getByTestId('sample').click();
  await expect(page.getByTestId('kpis')).toBeVisible();
  await expect(page.getByTestId('unmatched-count')).toHaveText('1');
  await expect(page.getByTestId('issues')).toContainText('unmatched');
  await expect(page.getByTestId('hourly')).toContainText('05:00');
  await page.getByTestId('hour-filter').selectOption('active');
  await expect(page.getByTestId('hourly')).toContainText('05:00');
  await expect(page.getByTestId('chart-throughput')).toContainText('Started vs Completed Throughput');
  await expect(page.getByTestId('chart-throughput').locator('svg')).toBeVisible();
  await expect(page.getByTestId('chart-duration')).toContainText('Average Completion Duration');
  await expect(page.getByTestId('chart-match')).toContainText('Hourly Match Rate');
  await expect(page.getByTestId('chart-status')).toContainText('Status Breakdown');
  await expect(page.getByTestId('chart-status')).toContainText('Unmatched');

  await page.getByTestId('tab-slt').click();
  await expect(page.getByTestId('request-types')).toContainText('SLT Trade Settlement');
  await expect(page.getByTestId('kpis')).toContainText('Total requests');

  await page.getByTestId('tab-agency').click();
  await page.getByRole('button', { name: /unmatched · 2890940/i }).click();
  await expect(page.getByTestId('event-title')).toContainText('2890940');
  await expect(page.getByTestId('verdict')).toContainText('Unmatched');

  await page.goto('/');
  await page.getByTestId('sample').click();
  await page.getByTestId('tab-slt').click();
  await page.getByRole('button', { name: /FAILDEAL|999000|slow|fail|retry/i }).first().click();
});

test('Agency and SLT sheets match the parser workbook and open event detail', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('sample').click();
  await expect(page.getByTestId('kpis')).toBeVisible();

  await page.getByRole('link', { name: 'Agency' }).click();
  await expect(page.getByTestId('sheet-title')).toContainText('Agency');
  await expect(page.getByTestId('sheet-table')).toContainText('2890940');
  await expect(page.getByTestId('sheet-table')).not.toContainText('Workflow');
  await page.getByTestId('event-2890940').click();
  await expect(page.getByTestId('event-title')).toContainText('2890940');
  await expect(page.getByTestId('verdict')).toContainText('Unmatched');

  await page.getByRole('link', { name: 'SLT' }).click();
  await expect(page.getByTestId('sheet-title')).toContainText('SLT');
  await expect(page.getByTestId('sheet-table')).toContainText('Workflow');
  await expect(page.getByTestId('sheet-table')).toContainText('786712011');
  await page.getByTestId('event-786712011').click();
  await expect(page.getByTestId('event-title')).toContainText('786712011');
  await expect(page.getByTestId('hops')).toContainText('EMTService');
});

test('SLT event timeline shows hops from the source log', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('sample').click();
  await page.getByTestId('tab-slt').click();
  await page.getByRole('link', { name: 'Events' }).click();
  await page.getByTestId('event-786712011').click();
  await expect(page.getByTestId('event-title')).toContainText('786712011');
  await expect(page.getByTestId('hops')).toContainText('EMTService');
  await page.getByRole('button', { name: /sendEMTMessage/i }).click();
  await expect(page.getByTestId('hop-payload')).toContainText('ALTER_TRADE');
  await expect(page.getByTestId('event-request').or(page.getByTestId('hop-payload'))).toBeVisible();
});
