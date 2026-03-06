import { expect, test } from "@playwright/test";

const PASSWORD = "Password123!";

async function registerAndLogin(page, email) {
  await page.goto("/signup");
  await page.locator("#register-email").fill(email);
  await page.locator("#register-password").fill(PASSWORD);
  await page.locator("#register-confirm-password").fill(PASSWORD);
  await page.getByRole("button", { name: "Create Account" }).click();

  await page.waitForURL("**/login");
  await page.locator("#email").fill(email);
  await page.locator("#password").fill(PASSWORD);
  await page.getByRole("button", { name: "Sign In" }).click();
  await page.waitForURL("**/landing");
}

test("host can approve all pending join requests in one action", async ({ browser }) => {
  test.setTimeout(240_000);

  const idSuffix = `${Date.now()}${Math.floor(Math.random() * 1000)}`;
  const hostEmail = `host-bulk-${idSuffix}@example.com`;
  const requesterOneEmail = `requester-a-${idSuffix}@example.com`;
  const requesterTwoEmail = `requester-b-${idSuffix}@example.com`;
  const groupName = `Bulk Request ${idSuffix}`;

  const hostContext = await browser.newContext();
  const hostPage = await hostContext.newPage();
  await registerAndLogin(hostPage, hostEmail);
  await hostPage.goto("/create-group");
  await hostPage.getByPlaceholder("e.g., Summer Escape 2026").fill(groupName);
  await hostPage.getByRole("checkbox", { name: /make this group public/i }).check();
  await hostPage.getByRole("button", { name: "Create Group" }).click();
  await hostPage.waitForURL(/\/groups\/\d+$/);

  const requesterOneContext = await browser.newContext();
  const requesterOnePage = await requesterOneContext.newPage();
  await registerAndLogin(requesterOnePage, requesterOneEmail);
  await requesterOnePage.goto("/join-group");
  const publicCardOne = requesterOnePage.locator('[data-testid="public-group-card"]').filter({ hasText: groupName }).first();
  await expect(publicCardOne).toBeVisible();
  await publicCardOne.getByRole("button", { name: "Request join" }).click();
  await expect(publicCardOne.getByRole("button", { name: "Requested" })).toBeVisible();

  const requesterTwoContext = await browser.newContext();
  const requesterTwoPage = await requesterTwoContext.newPage();
  await registerAndLogin(requesterTwoPage, requesterTwoEmail);
  await requesterTwoPage.goto("/join-group");
  const publicCardTwo = requesterTwoPage.locator('[data-testid="public-group-card"]').filter({ hasText: groupName }).first();
  await expect(publicCardTwo).toBeVisible();
  await publicCardTwo.getByRole("button", { name: "Request join" }).click();
  await expect(publicCardTwo.getByRole("button", { name: "Requested" })).toBeVisible();

  await hostPage.reload();
  const pendingPanel = hostPage.getByTestId("pending-requests-panel");
  await expect(pendingPanel).toBeVisible();
  await expect(pendingPanel.getByText(requesterOneEmail)).toBeVisible();
  await expect(pendingPanel.getByText(requesterTwoEmail)).toBeVisible();
  await pendingPanel.getByRole("button", { name: "Approve all" }).click();
  await expect(pendingPanel.getByText("No pending requests.")).toBeVisible();

  await requesterOnePage.goto("/dashboard");
  const tripCardOne = requesterOnePage.locator("a.trip-card").filter({ hasText: groupName }).first();
  await expect(tripCardOne).toBeVisible();
  await expect(tripCardOne.getByText("MEMBER / ACTIVE")).toBeVisible();

  await requesterTwoPage.goto("/dashboard");
  const tripCardTwo = requesterTwoPage.locator("a.trip-card").filter({ hasText: groupName }).first();
  await expect(tripCardTwo).toBeVisible();
  await expect(tripCardTwo.getByText("MEMBER / ACTIVE")).toBeVisible();

  await requesterOneContext.close();
  await requesterTwoContext.close();
  await hostContext.close();
});
