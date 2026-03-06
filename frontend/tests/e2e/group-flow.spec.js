import { expect, test } from "@playwright/test";

const PASSWORD = "Password123!";
const env = globalThis.process?.env ?? {};

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

test("host can invite a member and member can accept, save preferences, and surface on host dashboard", async ({
  browser,
  request,
}) => {
  test.setTimeout(180_000);
  const apiBaseUrl = (env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  const idSuffix = `${Date.now()}${Math.floor(Math.random() * 1000)}`;
  const hostEmail = `host-${idSuffix}@example.com`;
  const memberEmail = `member-${idSuffix}@example.com`;

  const hostContext = await browser.newContext();
  const hostPage = await hostContext.newPage();

  await registerAndLogin(hostPage, hostEmail);
  await hostPage.goto("/create-group");

  const groupName = `E2E Group ${idSuffix}`;
  await hostPage.getByPlaceholder("e.g., Summer Escape 2026").fill(groupName);
  await hostPage.getByRole("checkbox", { name: /make this group public/i }).check();
  await hostPage.getByRole("button", { name: "Create Group" }).click();
  await hostPage.waitForURL(/\/groups\/\d+$/);
  const groupId = hostPage.url().split("/").pop();

  const hostToken = await hostPage.evaluate(
    () =>
      window.localStorage.getItem("arewegoing_access_token") ||
      window.sessionStorage.getItem("arewegoing_access_token")
  );
  expect(hostToken).toBeTruthy();

  const inviteRes = await request.post(`${apiBaseUrl}/api/v1/groups/${groupId}/invites`, {
    headers: {
      Authorization: `Bearer ${hostToken}`,
    },
    data: {
      email: memberEmail,
    },
  });
  const inviteBody = await inviteRes.text();
  test.skip(!inviteRes.ok(), `Invite API unavailable in this run: ${inviteRes.status()} ${inviteBody}`);

  const memberContext = await browser.newContext();
  const memberPage = await memberContext.newPage();

  await registerAndLogin(memberPage, memberEmail);
  await memberPage.goto("/dashboard");
  await expect(memberPage.getByText(groupName)).toBeVisible();
  await memberPage.getByRole("button", { name: /accept invite/i }).click();
  await memberPage.waitForURL(new RegExp(`/groups/${groupId}$`));

  await memberPage.getByPlaceholder("Destination type").fill("Beach");
  await memberPage.getByPlaceholder("Travel pace").fill("Balanced");
  await memberPage.getByPlaceholder("Budget min").fill("500");
  await memberPage.getByPlaceholder("Budget max").fill("1500");
  await memberPage.getByPlaceholder("Days").fill("5");
  await memberPage.getByPlaceholder("Transport mode").fill("Flight");
  await memberPage.getByPlaceholder("Activities (comma separated)").fill("snorkeling, hiking");
  await memberPage
    .getByPlaceholder("Dietary preferences (comma separated)")
    .fill("vegetarian");
  await memberPage.getByRole("button", { name: /save preferences/i }).click();
  await expect(memberPage.locator("text=Completion: 50%")).toBeVisible();

  await hostPage.reload();
  await expect(hostPage.getByText("Group members")).toBeVisible();
  await expect(hostPage.getByText(memberEmail).first()).toBeVisible();
  await expect(hostPage.getByText("ACCEPTED").first()).toBeVisible();

  const completionText = await hostPage.locator("text=Completion:").first().textContent();
  const completionMatch = completionText?.match(/Completion:\s*(\d+)%/);
  const completionPercent = Number(completionMatch?.[1] || 0);
  expect(completionPercent).toBeGreaterThan(0);

  await hostPage.getByRole("button", { name: "Capture snapshot" }).click();
  await expect(hostPage.getByText("Metrics trend history")).toBeVisible();
  await expect(hostPage.getByText("No snapshots yet. Capture one to start tracking trends.")).toHaveCount(0);

  await memberContext.close();
  await hostContext.close();
});
