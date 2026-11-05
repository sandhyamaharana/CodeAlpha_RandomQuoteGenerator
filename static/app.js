const copyButton = document.querySelector("#copy-button");
const copyStatus = document.querySelector("#copy-status");

copyButton?.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(copyButton.dataset.quote || "");
    copyStatus.textContent = "Copied to clipboard.";
  } catch {
    copyStatus.textContent = "Clipboard access is unavailable in this browser.";
  }
});
