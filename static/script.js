const historyKey = "cyberGuardianHistory";
const $ = (id) => document.getElementById(id);
const escapeHtml = (value) =>
  String(value).replace(
    /[&<>"']/g,
    (character) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      })[character],
  );

function setStatus(resultId, scoreId, tipId, data) {
  const result = $(resultId);
  result.textContent = data.result;
  result.className =
    data.score >= 75 ? "safe" : data.score >= 50 ? "caution" : "danger";
  $(scoreId).textContent = `${data.score} / 100`;
  $(tipId).textContent = data.tip;
}

function saveHistory(type, value, result, score) {
  const history = JSON.parse(localStorage.getItem(historyKey) || "[]");
  history.unshift({
    type,
    value: value.slice(0, 48),
    result,
    score,
    time: Date.now(),
  });
  localStorage.setItem(historyKey, JSON.stringify(history.slice(0, 8)));
  renderHistory();
}

function renderHistory() {
  const history = JSON.parse(localStorage.getItem(historyKey) || "[]");
  $("scanCount").textContent =
    `${history.length} scan${history.length === 1 ? "" : "s"} today`;
  $("historyList").innerHTML = history.length
    ? history
        .map(
          (item) =>
            `<div class="history-item"><span class="history-type">${escapeHtml(item.type)}</span><span class="history-value">${escapeHtml(item.value)}</span><strong class="${item.score >= 75 ? "safe" : item.score >= 50 ? "caution" : "danger"}">${escapeHtml(item.result)}</strong></div>`,
        )
        .join("")
    : '<p class="empty-state">Your recent checks will appear here.</p>';
}

async function analyze(endpoint, payload, ids, type, value, onData) {
  $(ids[0]).textContent = "Checking...";
  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    setStatus(ids[0], ids[1], ids[2], data);
    if (onData) onData(data);
    saveHistory(type, value, data.result, data.score);
    if (data.score < 50)
      $(ids[0]).animate([{ opacity: 0.45 }, { opacity: 1 }], { duration: 450 });
  } catch (error) {
    $(ids[0]).textContent = "Unable to check right now";
  }
}

$("passwordButton").addEventListener("click", () =>
  analyze(
    "/check_password",
    { password: $("password").value },
    ["result1", "passwordScore", "passwordTip"],
    "Password",
    "Private value",
  ),
);
$("urlButton").addEventListener("click", () =>
  analyze(
    "/check_url",
    { url: $("url").value },
    ["result2", "urlScore", "urlTip"],
    "URL",
    $("url").value,
  ),
);
$("emailButton").addEventListener("click", () =>
  analyze(
    "/check_email",
    { email: $("email").value },
    ["result3", "emailScore", "emailTip"],
    "Email",
    $("email").value,
  ),
);
$("phoneButton").addEventListener("click", () =>
  analyze(
    "/check_phone",
    { number: $("phone").value },
    ["result4", "phoneScore", "phoneTip"],
    "Phone",
    "Private value",
    (data) => {
      $("phoneMeta").textContent = data.country
        ? `${data.country} · ${data.region} · ${data.line_type}`
        : "";
    },
  ),
);
$("password").addEventListener("input", () => {
  const length = $("password").value.length;
  $("passwordMeter").style.width = `${Math.min(length * 10, 100)}%`;
});
$("clearHistory").addEventListener("click", () => {
  localStorage.removeItem(historyKey);
  renderHistory();
});
$("chatButton").addEventListener("click", async () => {
  const msg = $("chatInput").value.trim();
  if (!msg) return;
  const response = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ msg }),
  });
  $("chatResult").textContent = (await response.json()).reply;
  $("chatInput").value = "";
});
$("chatInput").addEventListener("keydown", (event) => {
  if (event.key === "Enter") $("chatButton").click();
});
$("themeToggle").addEventListener("click", () => {
  document.body.classList.toggle("light-mode");
  localStorage.setItem(
    "lightMode",
    document.body.classList.contains("light-mode"),
  );
});
if (localStorage.getItem("lightMode") === "true")
  document.body.classList.add("light-mode");
renderHistory();
