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

test("requester sees rejected state after host rejects public join request", async ({ browser }) => {
  test.setTimeout(180_000);

  const idSuffix = `${Date.now()}${Math.floor(Math.random() * 1000)}`;
  const hostEmail = `host-reject-${idSuffix}@example.com`;
  const requesterEmail = `requester-reject-${idSuffix}@example.com`;
  const groupName = `Reject Request ${idSuffix}`;

  const hostContext = await browser.newContext();
  const hostPage = await hostContext.newPage();
  await registerAndLogin(hostPage, hostEmail);
  await hostPage.goto("/create-group");
  await hostPage.getByPlaceholder("e.g., Summer Escape 2026").fill(groupName);
  await hostPage.getByRole("checkbox", { name: /make this group public/i }).check();
  await hostPage.getByRole("button", { name: "Create Group" }).click();
  await hostPage.waitForURL(/\/groups\/\d+$/);

  const requesterContext = await browser.newContext();
  const requesterPage = await requesterContext.newPage();
  await registerAndLogin(requesterPage, requesterEmail);
  await requesterPage.goto("/join-group");
  const publicCard = requesterPage.locator('[data-testid="public-group-card"]').filter({ hasText: groupName }).first();
  await expect(publicCard).toBeVisible();
  await publicCard.getByRole("button", { name: "Request join" }).click();
  await expect(publicCard.getByRole("button", { name: "Requested" })).toBeVisible();

  await hostPage.reload();
  const pendingPanel = hostPage.getByTestId("pending-requests-panel");
  const pendingRow = pendingPanel.locator('[data-testid^="pending-request-"]').filter({ hasText: requesterEmail }).first();
  await expect(pendingRow).toBeVisible();
  await pendingRow.getByRole("button", { name: "Reject" }).click();
  await expect(pendingPanel.locator('[data-testid^="pending-request-"]').filter({ hasText: requesterEmail })).toHaveCount(0);

  await requesterPage.goto("/dashboard");
  const rejectedCard = requesterPage.locator("div.trip-card").filter({ hasText: groupName }).first();
  await expect(rejectedCard).toBeVisible();
  await expect(rejectedCard.getByText("MEMBER / REJECTED")).toBeVisible();
  await expect(rejectedCard.getByText("Request declined by host")).toBeVisible();
  await expect(requesterPage.locator("a.trip-card").filter({ hasText: groupName })).toHaveCount(0);

  await requesterContext.close();
  await hostContext.close();
});
