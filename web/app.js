const form = document.querySelector("#run-form");
const request = document.querySelector("#request");
const result = document.querySelector("#result");

function renderRun(run, detail) {
  result.classList.remove("empty");
  const cost = run.cost_estimate ? `${run.cost_estimate} CNY / 米` : "未计算";
  const functions = detail?.parsed_requirements?.required_functions?.join(" · ") || "待解析";
  const design = detail?.process_design;
  const materials = design?.fibers?.map((fiber) => `${fiber.material_id} ${fiber.percentage}%`).join(" · ") || "待设计";
  result.innerHTML = `<div class="card-head"><div><span class="step">02 · 结果</span><h2>一条可追溯的设计链</h2></div><span class="pill">${run.status === "completed" ? "已完成" : run.status}</span></div><div class="metric"><span>目标功能</span><strong>${functions}</strong></div><div class="metric"><span>推荐配方</span><strong>${materials}</strong></div><div class="metric"><span>预估成本</span><strong>${cost}</strong></div><div class="metric"><span>修订次数</span><strong>${run.revision_count} / ${run.max_revisions}</strong></div><p class="privacy">成本来自标记为 mock 的离线费率，仅用于方案比较。</p>`;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = form.querySelector("button");
  button.disabled = true;
  button.textContent = "设计中…";
  try {
    const response = await fetch("/api/v1/runs", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({user_request: request.value})});
    const body = await response.json();
    if (!response.ok) throw new Error(body.error?.message || "请求失败");
    const detailResponse = await fetch(`/api/v1/runs/${body.run_id}`);
    const detail = detailResponse.ok ? await detailResponse.json() : null;
    renderRun(body, detail);
  } catch (error) {
    result.classList.remove("empty");
    result.innerHTML = `<div class="error">${error.message}</div>`;
  } finally { button.disabled = false; button.innerHTML = "开始设计 <span>→</span>"; }
});
