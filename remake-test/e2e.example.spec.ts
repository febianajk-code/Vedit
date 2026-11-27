// Example Playwright spec for remake-test, shaped after the recon map's
// flows. Replace the selectors and URLs with the remake's real ones.
import { expect, test } from "@playwright/test";

test.describe("F01 guest books a session", () => {
  test("happy path books a slot", async ({ page }) => {
    await page.goto("/book/evt_demo");
    await expect(page.getByRole("heading", { name: /pick a time/i })).toBeVisible();
    await page.getByRole("button", { name: /10:00/ }).first().click();
    await page.getByLabel("Your name").fill("Ada Tester");
    await page.getByLabel("Your email").fill("ada@example.com");
    await page.getByRole("button", { name: /confirm/i }).click();
    await expect(page.getByText(/booked/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /10:00/ })).toBeDisabled();
  });

  test("edge: taken slot cannot be double-booked", async ({ page }) => {
    await page.goto("/book/evt_demo");
    await page.getByRole("button", { name: /10:00/ }).first().click();
    await page.getByLabel("Your name").fill("Second Guest");
    await page.getByLabel("Your email").fill("guest@example.com");
    await page.getByRole("button", { name: /confirm/i }).click();
    await expect(page.getByText(/no longer available/i)).toBeVisible();
  });
});
