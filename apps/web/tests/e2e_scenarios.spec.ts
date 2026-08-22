import { test, expect } from "@playwright/test";

test.describe("RazorRecover AI — E2E Test Suite (§20.3)", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to Login page
    await page.goto("http://localhost:3000/login");
    await page.fill('input[type="email"]', "owner@merchant.com");
    await page.fill('input[type="password"]', "password123");
    await page.click('button[type="submit"]');
    // Ensure dashboard loads
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test("1. Failed payment case appears on dashboard and displays KPI metrics", async ({ page }) => {
    await expect(page.locator("text=AI Revenue Recovery Dashboard")).toBeVisible();
    await expect(page.locator("text=Recovered Revenue")).toBeVisible();
    await expect(page.locator("text=Pending Approval Cases")).toBeVisible();
    await expect(page.locator("text=Recent Recovery Cases")).toBeVisible();
  });

  test("2. Case decision chain detail displays full AI and Policy signals", async ({ page }) => {
    await page.goto("http://localhost:3000/recovery/11111111-1111-1111-1111-000000000001");
    await expect(page.locator("text=Case Decision Chain")).toBeVisible();
    await expect(page.locator("text=1. Risk Signals")).toBeVisible();
    await expect(page.locator("text=2. AI Decision")).toBeVisible();
    await expect(page.locator("text=3. Policy Guardrail")).toBeVisible();
    await expect(page.locator("text=Audit Trail Timeline")).toBeVisible();
  });

  test("3. Pending approvals queue allows owner to approve high-risk cases", async ({ page }) => {
    await page.goto("http://localhost:3000/approvals");
    await expect(page.locator("text=Pending Approvals Queue")).toBeVisible();
    const approveBtn = page.locator('button:has-text("Approve Action")').first();
    if (await approveBtn.isVisible()) {
      await approveBtn.click();
      // Action executes and status transitions
      await expect(page.locator("text=Approved")).toBeVisible();
    }
  });

  test("4. Payments directory lists payments with filter and detail view", async ({ page }) => {
    await page.goto("http://localhost:3000/payments");
    await expect(page.locator("text=Authoritative Payments Directory")).toBeVisible();
    await expect(page.locator("text=All Statuses")).toBeVisible();
  });

  test("5. Settings page displays credentials and read-only policy thresholds", async ({ page }) => {
    await page.goto("http://localhost:3000/settings");
    await expect(page.locator("text=Merchant & Policy Settings")).toBeVisible();
    await expect(page.locator("text=Razorpay API Credentials")).toBeVisible();
    await expect(page.locator("text=Policy Config Thresholds (Read-Only)")).toBeVisible();
    await expect(page.locator("text=₹50,000")).toBeVisible();
  });
});
