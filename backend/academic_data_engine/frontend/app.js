/**
 * app.js – RNSIT Academic Data Engine Frontend
 * Wizard: Student → Semester → Add Subjects (PDF/Manual) → Review → Enter Marks → Summary
 * CIE and SEE only — no SGPA/CGPA.
 */

const API = "";  // same-origin

// ── Global state ─────────────────────────────────────────────────
let state = {
  studentId: null,
  semesterId: null,
  subjects: [],      // [{id, subject_code, subject_name, subject_type, credits, is_mandatory, is_chosen}]
  marks: {},         // {subj_id: {cie_final, see_raw, see_reduced, is_detained, is_absent, status, components}}
  mode: "manual",    // "manual" | "pdf"
  currentStep: 1,
};

// ── Navigation ───────────────────────────────────────────────────
const STEP_LABELS = ["Student", "Semester", "Subjects", "Review", "Marks", "Summary"];

function buildStepper() {
  const box = document.getElementById("stepper");
  box.innerHTML = STEP_LABELS.map((l, i) =>
    `<div class="step-dot" title="${l}" onclick="tryGotoStep(${i + 1})">${i + 1}</div>`
  ).join("");
}
buildStepper();

function updateStepper(active) {
  document.querySelectorAll(".step-dot").forEach((d, i) => {
    d.className = "step-dot" + (i + 1 < active ? " done" : i + 1 === active ? " active" : "");
  });
}

function gotoStep(n) {
  document.querySelectorAll(".step").forEach(s => s.classList.remove("active"));
  document.getElementById(`step${n}`).classList.add("active");
  state.currentStep = n;
  updateStepper(n);
  window.scrollTo(0, 0);

  if (n === 4) renderReview();
  if (n === 5) renderMarksList();
  if (n === 6) renderSummary();
}

function tryGotoStep(n) {
  // Only allow going back freely; going forward requires completing current
  if (n <= state.currentStep) gotoStep(n);
}

// ── Toasts ───────────────────────────────────────────────────────
function toast(msg, type = "info") {
  const box = document.getElementById("toast-box");
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.textContent = msg;
  box.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

// ── API helpers ──────────────────────────────────────────────────
async function apiFetch(method, url, body) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res = await fetch(API + url, opts);
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try { detail = (await res.json()).detail || detail; } catch { }
    throw new Error(detail);
  }
  if (res.status === 204) return {};
  return res.json();
}

// ── STEP 1: Create Student ────────────────────────────────────────
document.getElementById("f1").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = document.getElementById("btn1");
  btn.disabled = true;
  btn.textContent = "Creating…";
  try {
    const fd = new FormData(e.target);
    const data = {
      name: fd.get("name").trim(),
      usn: fd.get("usn").trim().toUpperCase(),
      branch: e.target.querySelector("select[name=branch]").value,
      scheme: "2024",
    };
    const s = await apiFetch("POST", "/students/", data);
    state.studentId = s.id;
    toast(`Student "${s.name}" created (USN: ${s.usn})`, "success");
    gotoStep(2);
  } catch (err) {
    toast(err.message, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Create Profile →";
  }
});

// ── STEP 2: Create Semester ───────────────────────────────────────
document.getElementById("f2").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    const payload = {
      semester_number: parseInt(fd.get("sem_num")),
      academic_year: fd.get("acad_year").trim(),
    };
    const sem = await apiFetch("POST", `/students/${state.studentId}/semesters/`, payload);
    state.semesterId = sem.id;
    state.subjects = [];
    toast(`Semester ${sem.semester_number} created`, "success");
    gotoStep(3);
  } catch (err) {
    toast(err.message, "error");
  }
});

// ── STEP 3: Add Subjects ──────────────────────────────────────────

// Mode toggle
document.querySelectorAll(".mode-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("on"));
    btn.classList.add("on");
    state.mode = btn.dataset.mode;
    document.getElementById("manual-panel").style.display = state.mode === "manual" ? "" : "none";
    document.getElementById("pdf-panel").style.display = state.mode === "pdf" ? "" : "none";
  });
});

// Manual add
document.getElementById("btn-add-subj").addEventListener("click", async () => {
  const code = document.getElementById("m-code").value.trim().toUpperCase();
  const name = document.getElementById("m-name").value.trim();
  const type = document.getElementById("m-type").value;
  const credits = parseFloat(document.getElementById("m-credits").value) || 0;
  const ltp = document.getElementById("m-ltp").value.trim() || null;
  const bucket = document.getElementById("m-bucket").value.trim() || null;

  if (!code || !name) { toast("Code and Name are required", "error"); return; }

  try {
    const subj = await apiFetch("POST", `/semesters/${state.semesterId}/subjects/`, {
      subject_code: code,
      subject_name: name,
      subject_type: type,
      credits: credits,
      ltp_hours: ltp,
      is_mandatory: type === "mc",
      option_group: bucket,
      is_chosen: true,
    });
    state.subjects.push(subj);
    document.getElementById("m-code").value = "";
    document.getElementById("m-name").value = "";
    document.getElementById("m-credits").value = "";
    document.getElementById("m-ltp").value = "";
    document.getElementById("m-bucket").value = "";
    renderManualList();
    toast(`${code} added`, "success");
  } catch (err) {
    toast(err.message, "error");
  }
});

function renderManualList() {
  const list = document.getElementById("manual-list");
  if (!state.subjects.length) { list.innerHTML = ""; return; }
  list.innerHTML = `<div class="subj-entry-list">${state.subjects.map((s, idx) => `
    <div class="subj-entry-item">
      <span class="code">${s.subject_code}</span>
      <span class="name">${s.subject_name}</span>
      <span class="type-badge type-${s.subject_type}">${s.subject_type.toUpperCase()}</span>
      <span style="color:var(--muted);font-size:.78rem">${s.credits} cr</span>
      <button class="del-btn" onclick="removeSubject(${idx}, ${s.id})">✕</button>
    </div>`).join("")}
  </div>`;
}

async function removeSubject(idx, id) {
  try {
    await apiFetch("DELETE", `/subjects/${id}`);
    state.subjects.splice(idx, 1);
    renderManualList();
    toast("Subject removed", "info");
  } catch (err) {
    toast(err.message, "error");
  }
}

// PDF Upload
const pdfZone = document.getElementById("pdf-zone");
const pdfInput = document.getElementById("pdf-input");

pdfZone.addEventListener("click", () => pdfInput.click());

pdfZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  pdfZone.style.borderColor = "var(--primary)";
});
pdfZone.addEventListener("dragleave", () => {
  pdfZone.style.borderColor = "";
});
pdfZone.addEventListener("drop", (e) => {
  e.preventDefault();
  pdfZone.style.borderColor = "";
  const file = e.dataTransfer.files[0];
  if (file) handlePdfUpload(file);
});

pdfInput.addEventListener("change", (e) => {
  if (e.target.files[0]) handlePdfUpload(e.target.files[0]);
});

async function handlePdfUpload(file) {
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    toast("Only PDF files are accepted", "error"); return;
  }
  const statusEl = document.getElementById("pdf-status");
  statusEl.innerHTML = `<div class="alert alert-info">⏳ Uploading and extracting subjects…</div>`;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API}/upload-syllabus/${state.semesterId}`, {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);

    // Fetch the subjects now stored in DB
    const subjects = await apiFetch("GET", `/semesters/${state.semesterId}/subjects/`);
    state.subjects = subjects;

    let html = `<div class="alert alert-success">
      ✅ Extracted <strong>${data.subjects_extracted}</strong> subjects, 
      stored <strong>${data.subjects_stored}</strong>.
    </div>`;

    if (data.warnings && data.warnings.length) {
      html += `<div class="alert alert-warning" style="margin-top:8px">
        <strong>Warnings:</strong><br>${data.warnings.map(w => `• ${w}`).join("<br>")}
      </div>`;
    }
    if (data.subjects_stored > 0) {
      html += `<div class="subj-entry-list" style="margin-top:12px">
        ${state.subjects.map(s => `
          <div class="subj-entry-item">
            <span class="code">${s.subject_code}</span>
            <span class="name">${s.subject_name}</span>
            <span class="type-badge type-${s.subject_type}">${s.subject_type.toUpperCase()}</span>
            <span style="color:var(--muted);font-size:.78rem">${s.credits} cr</span>
          </div>`).join("")}
      </div>`;
      html += `<div class="alert alert-info" style="margin-top:10px">
        ℹ️ Subject types were auto-detected. You can correct them in the next step.
      </div>`;
    }
    statusEl.innerHTML = html;
    toast(`${data.subjects_stored} subjects extracted from PDF`, "success");
  } catch (err) {
    statusEl.innerHTML = `<div class="alert alert-danger">❌ ${err.message}</div>`;
    toast(err.message, "error");
  }
}

// Done button for Step 3
document.getElementById("btn-subj-done").addEventListener("click", async () => {
  if (!state.subjects.length) {
    // Try fetching subjects (might have been added via PDF before state was updated)
    const subjects = await apiFetch("GET", `/semesters/${state.semesterId}/subjects/`);
    state.subjects = subjects;
  }
  if (!state.subjects.length) {
    toast("Please add at least one subject", "error"); return;
  }
  gotoStep(4);
});

// ── STEP 4: Review Subjects ───────────────────────────────────────
const TYPE_INFO = {
  pcc: "Theory — IA avg→30/50 + CCE→20 = 50 CIE",
  ipcc: "Theory+Lab — IA→20 + CCE→10 + Lab Rec→12 + Lab Test→8 = 50 CIE",
  pccl: "Pure Lab — Lab Rec→30 + Lab Test(scaled)→20 = 50 CIE",
  esc: "Elective Science — PCC-style CIE",
  aec: "Ability Enhancement — PCC-style CIE",
  mc: "Mandatory Course — CIE /100 only, no SEE",
  uhv: "Universal Human Values — PCC-style CIE",
  other: "Other — PCC-style CIE",
};

function renderReview() {
  const container = document.getElementById("review-container");
  if (!state.subjects.length) {
    container.innerHTML = `<div class="alert alert-warning">No subjects found. Go back and add subjects.</div>`;
    return;
  }
  container.innerHTML = `
    <table class="review-table">
      <thead><tr>
        <th>Code</th><th>Name</th><th>Type</th><th>Cr</th><th>Enrolled</th>
      </tr></thead>
      <tbody id="review-tbody">
        ${state.subjects.map((s, idx) => `
          <tr>
            <td><code style="color:var(--primary)">${s.subject_code}</code></td>
            <td style="font-size:.8rem">${s.subject_name}</td>
            <td>
              <select onchange="updateSubjectType(${idx}, ${s.id}, this.value)" style="min-width:90px">
                ${Object.keys(TYPE_INFO).map(t =>
    `<option value="${t}" ${s.subject_type === t ? 'selected' : ''}>${t.toUpperCase()}</option>`
  ).join("")}
              </select>
            </td>
            <td style="color:var(--muted)">${s.credits}</td>
            <td><input type="checkbox" ${s.is_chosen ? 'checked' : ''} onchange="updateChosenFlag(${idx}, ${s.id}, this.checked)"/></td>
          </tr>`).join("")}
      </tbody>
    </table>
    <div class="alert alert-info" style="margin-top:14px;font-size:.78rem">
      💡 <strong>Note:</strong><br>
      ${Object.entries(TYPE_INFO).map(([k, v]) => `<strong>${k.toUpperCase()}</strong>: ${v}`).join("<br>")}
    </div>`;
}

async function updateSubjectType(idx, id, newType) {
  try {
    const updated = await apiFetch("PUT", `/subjects/${id}`, {
      subject_type: newType
    });
    state.subjects[idx] = updated;
    toast(`${updated.subject_code} → ${newType.toUpperCase()}`, "info");
  } catch (err) {
    toast(err.message, "error");
  }
}

async function updateChosenFlag(idx, id, chosen) {
  try {
    const updated = await apiFetch("PUT", `/subjects/${id}`, { is_chosen: chosen });
    state.subjects[idx] = updated;
  } catch (err) {
    toast(err.message, "error");
  }
}

// ── STEP 5: Enter Marks ───────────────────────────────────────────
function renderMarksList() {
  const chosen = state.subjects.filter(s => s.is_chosen);
  const list = document.getElementById("marks-subject-list");
  list.innerHTML = `<div class="marks-list">${chosen.map(s => {
    const m = state.marks[s.id] || {};
    const cieText = m.cie_final != null ? `CIE: ${m.cie_final}/${s.is_mandatory ? 100 : 50}` : "CIE: —";
    const seeText = s.is_mandatory ? "No SEE" : (m.see_raw != null ? `SEE: ${m.see_raw}/100 → ${m.see_reduced}/50` : "SEE: —");
    const statusCls = getStatusClass(m.status);
    return `
      <div class="marks-row" onclick="openMarksModal(${s.id})">
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px">
            <span class="mr-code">${s.subject_code}</span>
            <span class="type-badge type-${s.subject_type}">${s.subject_type.toUpperCase()}</span>
          </div>
          <div class="mr-name">${s.subject_name}</div>
        </div>
        <div style="text-align:right">
          <div style="font-size:.78rem;color:var(--muted)">${cieText}</div>
          <div style="font-size:.78rem;color:var(--muted)">${seeText}</div>
          <span class="mr-status ${statusCls}">${m.status || "Pending"}</span>
        </div>
      </div>`;
  }).join("")}</div>`;
}

function getStatusClass(status) {
  if (!status || status === "Pending") return "status-pending";
  if (status === "CIE Only") return "status-cie-only";
  if (status === "Complete") return "status-complete";
  if (status === "Detained") return "status-detained";
  if (status === "Absent") return "status-absent";
  return "status-pending";
}

// ── Marks Modal ───────────────────────────────────────────────────
let _modalSubjId = null;

document.getElementById("btn-modal-close").addEventListener("click", closeModal);
document.getElementById("modal-marks").addEventListener("click", (e) => {
  if (e.target === document.getElementById("modal-marks")) closeModal();
});

function closeModal() {
  document.getElementById("modal-marks").style.display = "none";
  _modalSubjId = null;
}

function openMarksModal(subjId) {
  const subj = state.subjects.find(s => s.id === subjId);
  if (!subj) return;
  _modalSubjId = subjId;

  document.getElementById("modal-title").textContent = `${subj.subject_code} Marks`;
  document.getElementById("modal-sub").textContent = subj.subject_name;
  document.getElementById("modal-form-area").innerHTML = buildMarksForm(subj);
  document.getElementById("modal-computed").textContent = "";

  const m = state.marks[subjId] || {};
  // Restore saved values
  restoreFormValues(subj, m);
  // Live preview
  attachLiveCompute(subj);

  document.getElementById("modal-marks").style.display = "flex";
}

function buildMarksForm(subj) {
  const t = subj.subject_type;
  const m = state.marks[subj.id] || {};

  const numInput = (id, label, placeholder, max, val) =>
    `<div class="group">
       <label>${label} ${max ? `<em style="font-weight:400;text-transform:none">(/${max})</em>` : ""}</label>
       <input type="number" id="${id}" min="0" max="${max || 9999}" step="0.5" placeholder="${placeholder}" value="${val != null ? val : ''}"/>
     </div>`;

  let html = "";

  if (t === "mc") {
    html += `<div class="marks-section-label">Mandatory Course — CIE only</div>
      <div class="marks-form-grid col1">
        ${numInput("f-direct", "Direct CIE Marks", "0–100", 100, m.direct_cie_marks)}
      </div>`;
  } else if (t === "pccl") {
    html += `<div class="marks-section-label">Lab Components — PCCL</div>
      <div class="marks-form-grid">
        ${numInput("f-lab-rec", "Lab Record", "0–30", 30, m.lab_record_marks)}
        ${numInput("f-lt1", "Lab Test (/100)", "0–100", 100, m.lab_test1_raw)}
      </div>`;
  } else if (t === "ipcc") {
    html += `<div class="marks-section-label">Theory — IA Tests (IPCC)</div>
      <div class="marks-form-grid">
        ${numInput("f-ia1", "IA Test 1", "0–50", 50, m.ia_test1_raw)}
        ${numInput("f-ia2", "IA Test 2", "0–50", 50, m.ia_test2_raw)}
      </div>
      <div class="marks-section-label">CCE</div>
      <div class="marks-form-grid">
        ${numInput("f-cce", "CCE Marks", "0–10", 10, m.cce_marks)}
      </div>
      <div class="marks-section-label">Lab Components</div>
      <div class="marks-form-grid">
        ${numInput("f-lab-rec", "Lab Record", "0–12", 12, m.lab_record_marks)}
        ${numInput("f-lt1", "Lab Test 1 (/100)", "0–100", 100, m.lab_test1_raw)}
        ${numInput("f-lt2", "Lab Test 2 (/100)", "0–100", 100, m.lab_test2_raw)}
      </div>`;
  } else {
    // PCC / ESC / AEC / UHV / other
    html += `<div class="marks-section-label">IA Tests</div>
      <div class="marks-form-grid">
        ${numInput("f-ia1", "IA Test 1", "0–50", 50, m.ia_test1_raw)}
        ${numInput("f-ia2", "IA Test 2", "0–50", 50, m.ia_test2_raw)}
      </div>
      <div class="marks-section-label">CCE</div>
      <div class="marks-form-grid">
        ${numInput("f-cce", "CCE Marks", "0–20", 20, m.cce_marks)}
      </div>`;
  }

  // SEE (not for MC)
  if (t !== "mc") {
    html += `<div class="marks-section-label">SEE — Semester End Exam</div>
      <div class="marks-form-grid">
        ${numInput("f-see", "SEE Raw Score", "0–100", 100, m.see_raw)}
      </div>
      <div class="tick-row">
        <input type="checkbox" id="f-absent" ${m.is_absent ? 'checked' : ''}/>
        <label for="f-absent" style="text-transform:none;letter-spacing:0;color:var(--text);cursor:pointer">Mark as <strong>Absent</strong> in SEE</label>
      </div>`;
  }

  html += `<div id="live-preview"></div>`;
  return html;
}

function restoreFormValues(subj, m) {
  // Values are already set in numInput via value="" attribute, nothing extra needed
}

function attachLiveCompute(subj) {
  const area = document.getElementById("modal-form-area");
  area.querySelectorAll("input").forEach(inp => {
    inp.addEventListener("input", () => livePreview(subj));
  });
  livePreview(subj);
}

function livePreview(subj) {
  const t = subj.subject_type;
  const gv = (id) => { const el = document.getElementById(id); return el ? parseFloat(el.value) || null : null; };
  let cieFinal = null;

  if (t === "mc") {
    const direct = gv("f-direct");
    if (direct != null) cieFinal = Math.min(direct, 100);
  } else if (t === "pccl") {
    const rec = gv("f-lab-rec");
    const lt1 = gv("f-lt1");
    const ltSc = lt1 != null ? +(lt1 * 20 / 100).toFixed(2) : 0;
    cieFinal = +((rec || 0) + ltSc).toFixed(2);
    cieFinal = Math.min(cieFinal, 50);
  } else if (t === "ipcc") {
    const ia1 = gv("f-ia1"), ia2 = gv("f-ia2");
    const tests = [ia1, ia2].filter(v => v != null);
    const iasc = tests.length ? +((tests.reduce((a, b) => a + b, 0) / tests.length) * 20 / 50).toFixed(2) : 0;
    const cce = gv("f-cce") || 0;
    const rec = gv("f-lab-rec") || 0;
    const lts = [gv("f-lt1"), gv("f-lt2")].filter(v => v != null);
    const ltsc = lts.length ? +((lts.reduce((a, b) => a + b, 0) / lts.length) * 8 / 100).toFixed(2) : 0;
    cieFinal = Math.min(+(iasc + cce + rec + ltsc).toFixed(2), 50);
  } else {
    const ia1 = gv("f-ia1"), ia2 = gv("f-ia2");
    const tests = [ia1, ia2].filter(v => v != null);
    const iasc = tests.length ? +((tests.reduce((a, b) => a + b, 0) / tests.length) * 30 / 50).toFixed(2) : 0;
    const cce = gv("f-cce") || 0;
    cieFinal = Math.min(+(iasc + cce).toFixed(2), 50);
  }

  const detained = t !== "mc" && cieFinal != null && cieFinal < 20;
  const seeRaw = t !== "mc" ? gv("f-see") : null;
  const absent = document.getElementById("f-absent")?.checked || false;
  const seeReduced = seeRaw != null && !absent ? +(seeRaw / 2).toFixed(2) : null;

  const prev = document.getElementById("live-preview");
  if (!prev) return;

  let html = `<div class="computed-row">`;
  if (t !== "mc") {
    html += `<div class="computed-item"><div class="ci-label">Final CIE</div><div class="ci-val" style="${detained ? 'color:var(--danger)' : ''}">${cieFinal ?? "—"}/50</div></div>`;
    if (seeReduced != null) {
      html += `<div class="computed-item"><div class="ci-label">SEE (reduced)</div><div class="ci-val">${seeReduced}/50</div></div>`;
      html += `<div class="computed-item"><div class="ci-label">Total</div><div class="ci-val">${+((cieFinal || 0) + (seeReduced || 0)).toFixed(2)}/100</div></div>`;
    }
    if (detained) html += `<div class="computed-item"><div class="ci-label">Status</div><div class="ci-val" style="color:var(--danger)">DETAINED</div></div>`;
  } else {
    html += `<div class="computed-item"><div class="ci-label">CIE (MC)</div><div class="ci-val">${cieFinal ?? "—"}/100</div></div>`;
  }
  html += `</div>`;
  prev.innerHTML = html;
}

// Save marks
document.getElementById("btn-modal-save").addEventListener("click", async () => {
  const subjId = _modalSubjId;
  if (!subjId) return;
  const subj = state.subjects.find(s => s.id === subjId);
  if (!subj) return;

  const btn = document.getElementById("btn-modal-save");
  btn.disabled = true;
  btn.textContent = "Saving…";

  const t = subj.subject_type;
  const gv = (id) => { const el = document.getElementById(id); return el ? (el.value !== "" ? parseFloat(el.value) : null) : null; };

  try {
    // Build CIE payload
    let ciePayload = {};
    if (t === "mc") {
      ciePayload = { direct_cie_marks: gv("f-direct") };
    } else if (t === "pccl") {
      ciePayload = { lab_record_marks: gv("f-lab-rec"), lab_test1_raw: gv("f-lt1") };
    } else if (t === "ipcc") {
      ciePayload = {
        ia_test1_raw: gv("f-ia1"), ia_test2_raw: gv("f-ia2"),
        cce_marks: gv("f-cce"),
        lab_record_marks: gv("f-lab-rec"),
        lab_test1_raw: gv("f-lt1"), lab_test2_raw: gv("f-lt2"),
      };
    } else {
      ciePayload = { ia_test1_raw: gv("f-ia1"), ia_test2_raw: gv("f-ia2"), cce_marks: gv("f-cce") };
    }

    const cieResult = await apiFetch("POST", `/subjects/${subjId}/cie`, ciePayload);

    let seeResult = null;
    if (t !== "mc") {
      const isAbsent = document.getElementById("f-absent")?.checked || false;
      seeResult = await apiFetch("POST", `/subjects/${subjId}/see`, {
        raw_scored: isAbsent ? null : gv("f-see"),
        is_absent: isAbsent,
      });
    }

    // Determine status
    let status = "Pending";
    if (cieResult.is_detained) {
      status = "Detained";
    } else if (t === "mc") {
      status = cieResult.final_cie != null ? "Complete" : "Pending";
    } else if (seeResult) {
      if (seeResult.is_absent) status = "Absent";
      else if (cieResult.final_cie != null && seeResult.reduced_scored != null) status = "Complete";
      else if (cieResult.final_cie != null) status = "CIE Only";
    } else {
      status = cieResult.final_cie != null ? "CIE Only" : "Pending";
    }

    // Save to state
    state.marks[subjId] = {
      cie_final: cieResult.final_cie,
      is_detained: cieResult.is_detained,
      ia_test1_raw: cieResult.ia_test1_raw,
      ia_test2_raw: cieResult.ia_test2_raw,
      ia_scaled: cieResult.ia_scaled,
      cce_marks: cieResult.cce_marks,
      lab_record_marks: cieResult.lab_record_marks,
      lab_test1_raw: cieResult.lab_test1_raw,
      lab_test2_raw: cieResult.lab_test2_raw,
      lab_test_scaled: cieResult.lab_test_scaled,
      direct_cie_marks: cieResult.direct_cie_marks,
      see_raw: seeResult?.raw_scored ?? null,
      see_reduced: seeResult?.reduced_scored ?? null,
      is_absent: seeResult?.is_absent ?? false,
      status,
    };

    closeModal();
    renderMarksList();
    toast(`Marks saved for ${subj.subject_code}`, "success");
  } catch (err) {
    toast(err.message, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Save Marks";
  }
});

// ── STEP 6: Summary ───────────────────────────────────────────────
async function renderSummary() {
  const cardsEl = document.getElementById("sum-cards");
  const jsonEl = document.getElementById("jsonOut");

  cardsEl.innerHTML = "<div style='color:var(--muted)'>Loading…</div>";

  try {
    const data = await apiFetch("GET", `/semesters/${state.semesterId}/marks-summary`);

    if (!data.subjects || !data.subjects.length) {
      cardsEl.innerHTML = `<div class="alert alert-warning">No subjects with marks found. Go back and enter marks.</div>`;
      jsonEl.textContent = JSON.stringify(data, null, 2);
      return;
    }

    // Update local state from server
    data.subjects.forEach(s => {
      state.marks[s.subject_id] = {
        cie_final: s.final_cie,
        is_detained: s.is_detained,
        ia_test1_raw: s.ia_test1_raw,
        ia_test2_raw: s.ia_test2_raw,
        ia_scaled: s.ia_scaled,
        cce_marks: s.cce_marks,
        lab_record_marks: s.lab_record_marks,
        lab_test1_raw: s.lab_test1_raw,
        lab_test2_raw: s.lab_test2_raw,
        lab_test_scaled: s.lab_test_scaled,
        direct_cie_marks: s.direct_cie_marks,
        see_raw: s.see_raw,
        see_reduced: s.see_reduced,
        is_absent: s.is_absent,
        status: s.status,
      };
    });

    cardsEl.innerHTML = `<div class="sum-grid">${data.subjects.map(s => {
      const statusColor = s.status === "Complete" ? "var(--success)"
        : s.status === "Detained" ? "var(--danger)"
          : s.status === "CIE Only" ? "var(--warning)"
            : "var(--muted)";

      const cieMax = s.is_mandatory ? 100 : 50;
      const cieDisp = s.final_cie != null ? `${s.final_cie}` : "—";
      const seeDisp = s.see_raw != null ? `${s.see_raw}` : (s.is_absent ? "Absent" : "—");
      const seeRedDisp = s.see_reduced != null ? `→ ${s.see_reduced}/50` : "";
      const total = !s.is_mandatory && s.final_cie != null && s.see_reduced != null
        ? +((s.final_cie + s.see_reduced).toFixed(2)) : null;

      return `<div class="sum-card">
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
            <span class="sc-code">${s.subject_code}</span>
            <span class="type-badge type-${s.subject_type}">${s.subject_type.toUpperCase()}</span>
          </div>
          <div class="sc-name">${s.subject_name} &nbsp;·&nbsp; ${s.credits} credits</div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:8px">
          <span class="sum-status" style="background:${statusColor}18;color:${statusColor}">${s.status}</span>
          <div class="sc-marks">
            <div class="sum-mark-item">
              <span class="sm-label">Final CIE</span>
              <span class="sm-val" style="${s.is_detained ? 'color:var(--danger)' : ''}">${cieDisp}</span>
              <span class="sm-max">/ ${cieMax}</span>
            </div>
            ${!s.is_mandatory ? `
            <div class="sum-mark-item">
              <span class="sm-label">SEE Raw</span>
              <span class="sm-val">${seeDisp}</span>
              <span class="sm-max">/ 100 ${seeRedDisp}</span>
            </div>` : ""}
            ${total != null ? `
            <div class="sum-mark-item">
              <span class="sm-label">Total</span>
              <span class="sm-val">${total}</span>
              <span class="sm-max">/ 100</span>
            </div>` : ""}
          </div>
        </div>
      </div>`;
    }).join("")}</div>`;

    jsonEl.textContent = JSON.stringify(data, null, 2);

    // Download button
    document.getElementById("btn-dl-json").onclick = () => {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `marks_sem${data.semester_number}_${data.academic_year}.json`.replace(/\s/g, "_");
      a.click();
    };

    // Auto-Redirect to Analyzer
    toast("Data Saved! Launching Performance Analyzer...", "success");
    setTimeout(() => {
      const usn = document.getElementById('s-usn').value;
      window.open('http://localhost:9002/dashboard/analyzer?usn=' + encodeURIComponent(usn), '_top');
    }, 2500);

  } catch (err) {
    cardsEl.innerHTML = `<div class="alert alert-danger">❌ ${err.message}</div>`;
    jsonEl.textContent = "Error fetching data.";
    toast(err.message, "error");
  }
}

// ── Restart ───────────────────────────────────────────────────────
document.getElementById("btn-restart").addEventListener("click", () => {
  state = { studentId: null, semesterId: null, subjects: [], marks: {}, mode: "manual", currentStep: 1 };
  document.getElementById("f1").reset();
  document.getElementById("f2").reset();
  document.getElementById("manual-list").innerHTML = "";
  document.getElementById("pdf-status").innerHTML = "";
  document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("on"));
  document.querySelector(".mode-btn[data-mode=manual]").classList.add("on");
  document.getElementById("manual-panel").style.display = "";
  document.getElementById("pdf-panel").style.display = "none";
  gotoStep(1);
});

// ── Init ──────────────────────────────────────────────────────────
gotoStep(1);
