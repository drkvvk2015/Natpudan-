import { test, expect } from '@playwright/test'

test('landing route loads', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveTitle(/Natpudan|Vite|Medical/i)
})
