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

test("public join request appears for host and can be approved", async ({ browser }) => {
  test.setTimeout(180_000);

  const idSuffix = `${Date.now()}${Math.floor(Math.random() * 1000)}`;
  const hostEmail = `host-request-${idSuffix}@example.com`;
  const requesterEmail = `requester-${idSuffix}@example.com`;
  const groupName = `Public Request ${idSuffix}`;

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
  await expect(pendingPanel).toBeVisible();
  const pendingRow = pendingPanel.locator('[data-testid^="pending-request-"]').filter({ hasText: requesterEmail }).first();
  await expect(pendingRow).toBeVisible();
  await pendingRow.getByRole("button", { name: "Approve" }).click();
  await expect(pendingPanel.locator('[data-testid^="pending-request-"]').filter({ hasText: requesterEmail })).toHaveCount(0);

  const membersPanel = hostPage.getByTestId("group-members-panel");
  await expect(membersPanel.getByText(requesterEmail)).toBeVisible();
  await expect(membersPanel.getByText("MEMBER / ACTIVE")).toBeVisible();

  await requesterPage.goto("/dashboard");
  const tripCard = requesterPage.locator("a.trip-card").filter({ hasText: groupName }).first();
  await expect(tripCard).toBeVisible();
  await expect(tripCard.getByText("MEMBER / ACTIVE")).toBeVisible();

  await requesterContext.close();
  await hostContext.close();
});
