const api = "/api/students";
const rows = document.getElementById("studentRows");
const form = document.getElementById("studentForm");
const backdrop = document.getElementById("modalBackdrop");
const notice = document.getElementById("notice");
const searchInput = document.getElementById("searchInput");
let allStudents = [];
let editingId = null;

function showNotice(message, type = "success") {
  notice.textContent = message;
  notice.className = `notice ${type}`;
  window.clearTimeout(showNotice.timer);
  showNotice.timer = window.setTimeout(() => notice.classList.add("hidden"), 4500);
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "Request failed. Please try again.");
  return data;
}

function initials(name) {
  return name.trim().split(/\s+/).slice(0, 2).map(part => part[0] || "").join("").toUpperCase();
}

function yearLabel(year) {
  const labels = {"1":"1st Year", "2":"2nd Year", "3":"3rd Year", "4":"4th Year"};
  return labels[String(year)] || `Year ${year}`;
}

function safeText(value) {
  return String(value ?? "").replace(/[&<>"']/g, character => ({
    "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
  })[character]);
}

function updateStats(list) {
  document.getElementById("totalStudents").textContent = list.length;
  document.getElementById("totalDepartments").textContent =
    new Set(list.map(student => (student.department || "").trim().toLowerCase()).filter(Boolean)).size;
}

function renderStudents() {
  const term = searchInput.value.trim().toLowerCase();
  const filtered = allStudents.filter(student =>
    [student.name, student.department, student.email, yearLabel(student.year)]
      .some(value => String(value || "").toLowerCase().includes(term))
  );

  updateStats(allStudents);
  document.getElementById("recordCount").textContent =
    `Showing ${filtered.length} of ${allStudents.length} student${allStudents.length === 1 ? "" : "s"}`;

  if (!filtered.length) {
    rows.innerHTML = `<tr><td colspan="5" class="empty-state">${term ? "No matching students found." : "No students yet. Click “Add Student” to create your first record."}</td></tr>`;
    return;
  }

  rows.innerHTML = filtered.map(student => `
    <tr>
      <td><div class="student-cell"><div class="student-avatar">${safeText(initials(student.name || "?"))}</div><span>${safeText(student.name)}</span></div></td>
      <td><span class="department-pill">${safeText(student.department)}</span></td>
      <td><span class="year-pill">${safeText(yearLabel(student.year))}</span></td>
      <td>${safeText(student.email || "—")}</td>
      <td><div class="row-actions">
        <button class="icon-btn edit" data-action="edit" data-id="${safeText(student._id)}" aria-label="Edit ${safeText(student.name)}">✎ Edit</button>
        <button class="icon-btn delete" data-action="delete" data-id="${safeText(student._id)}" aria-label="Delete ${safeText(student.name)}">⌫ Delete</button>
      </div></td>
    </tr>
  `).join("");
}

async function loadStudents() {
  rows.innerHTML = `<tr><td colspan="5" class="empty-state">Loading student records…</td></tr>`;
  try {
    allStudents = await requestJson(api);
    document.getElementById("dbStatus").textContent = "Connected";
    document.getElementById("dbCaption").textContent = "MongoDB Atlas is reachable";
    renderStudents();
  } catch (error) {
    allStudents = [];
    updateStats(allStudents);
    document.getElementById("dbStatus").textContent = "Offline";
    document.getElementById("dbCaption").textContent = "Check Atlas connection";
    rows.innerHTML = `<tr><td colspan="5" class="empty-state">${safeText(error.message)}</td></tr>`;
    document.getElementById("recordCount").textContent = "Unable to load records";
  }
}

function openModal(student = null) {
  editingId = student ? student._id : null;
  form.reset();
  document.getElementById("modalTitle").textContent = student ? "Edit Student" : "Add Student";
  document.getElementById("saveButton").textContent = student ? "Save Changes" : "Save Student";
  document.getElementById("name").value = student?.name || "";
  document.getElementById("department").value = student?.department || "";
  document.getElementById("year").value = student ? String(student.year) : "";
  document.getElementById("email").value = student?.email || "";
  backdrop.classList.remove("hidden");
  document.getElementById("name").focus();
}

function closeModal() {
  backdrop.classList.add("hidden");
  editingId = null;
}

document.getElementById("addButton").addEventListener("click", () => openModal());
document.getElementById("closeModal").addEventListener("click", closeModal);
document.getElementById("cancelButton").addEventListener("click", closeModal);
document.getElementById("refreshButton").addEventListener("click", loadStudents);
searchInput.addEventListener("input", renderStudents);
backdrop.addEventListener("click", event => {
  if (event.target === backdrop) closeModal();
});
document.addEventListener("keydown", event => {
  if (event.key === "Escape") closeModal();
});

form.addEventListener("submit", async event => {
  event.preventDefault();
  const data = {
    name: document.getElementById("name").value.trim(),
    department: document.getElementById("department").value.trim(),
    year: document.getElementById("year").value,
    email: document.getElementById("email").value.trim()
  };
  const wasEditing = Boolean(editingId);
  const saveButton = document.getElementById("saveButton");
  saveButton.disabled = true;
  saveButton.textContent = "Saving…";
  try {
    const url = editingId ? `${api}/${encodeURIComponent(editingId)}` : api;
    await requestJson(url, {
      method: editingId ? "PUT" : "POST",
      body: JSON.stringify(data)
    });
    closeModal();
    await loadStudents();
    showNotice(wasEditing ? "Student updated successfully." : "Student added successfully.");
  } catch (error) {
    showNotice(error.message, "error");
  } finally {
    saveButton.disabled = false;
    saveButton.textContent = wasEditing ? "Save Changes" : "Save Student";
  }
});

rows.addEventListener("click", async event => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const student = allStudents.find(item => item._id === button.dataset.id);
  if (!student) return;

  if (button.dataset.action === "edit") {
    openModal(student);
    return;
  }

  if (button.dataset.action === "delete") {
    if (!window.confirm(`Delete ${student.name}'s record? This cannot be undone.`)) return;
    button.disabled = true;
    try {
      await requestJson(`${api}/${encodeURIComponent(student._id)}`, { method: "DELETE" });
      await loadStudents();
      showNotice("Student deleted successfully.");
    } catch (error) {
      showNotice(error.message, "error");
      button.disabled = false;
    }
  }
});

loadStudents();
