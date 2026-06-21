const API = 'http://localhost:8000';
let token = localStorage.getItem('token') || null;
let categories = [];
let expenses = [];
let currentUser = null;

// ─── INIT ────────────────────────────────────────────────────
window.onload = () => {
  if (token) initApp();
};

async function initApp() {
  try {
    const me = await api('/auth/me');
    currentUser = me;
    document.getElementById('sidebar-user-email').textContent = me.email;
    document.getElementById('auth-page').style.display = 'none';
    document.getElementById('app-page').style.display = 'block';
    await Promise.all([loadCategories(), loadExpenses()]);
    renderDashboard();
  } catch {
    token = null;
    localStorage.removeItem('token');
  }
}

// ─── API HELPER ───────────────────────────────────────────────
async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(API + path, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Request failed');
  }
  if (res.status === 204) return null;
  return res.json();
}

// ─── AUTH ─────────────────────────────────────────────────────
function switchTab(tab) {
  document.querySelectorAll('.auth-tab').forEach((t, i) => {
    t.classList.toggle('active', (i === 0 && tab === 'login') || (i === 1 && tab === 'register'));
  });
  document.getElementById('login-form').style.display = tab === 'login' ? '' : 'none';
  document.getElementById('register-form').style.display = tab === 'register' ? '' : 'none';
  hideAlert('auth-alert');
}

async function handleLogin(e) {
  e.preventDefault();
  const btn = document.getElementById('login-btn');
  btn.innerHTML = '<span class="spinner"></span> Signing in…';
  btn.disabled = true;
  try {
    const data = await api('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email: document.getElementById('login-email').value,
        password: document.getElementById('login-password').value
      })
    });
    token = data.access_token;
    localStorage.setItem('token', token);
    await initApp();
  } catch (err) {
    showAlert('auth-alert', err.message, 'danger');
  } finally {
    btn.innerHTML = 'Sign in';
    btn.disabled = false;
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const btn = document.getElementById('register-btn');
  btn.innerHTML = '<span class="spinner"></span> Creating account…';
  btn.disabled = true;
  try {
    await api('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        username: document.getElementById('reg-username').value,
        email: document.getElementById('reg-email').value,
        password: document.getElementById('reg-password').value
      })
    });
    showAlert('auth-alert', 'Account created! Please sign in.', 'success');
    switchTab('login');
    document.getElementById('login-email').value = document.getElementById('reg-email').value;
  } catch (err) {
    showAlert('auth-alert', err.message, 'danger');
  } finally {
    btn.innerHTML = 'Create account';
    btn.disabled = false;
  }
}

function logout() {
    // clear all cached data
    token = null;
    currentUser = null;
    categories = [];
    expenses = [];

    localStorage.removeItem('token');

    // reset UI back to empty state
    document.getElementById('stat-total').textContent = '—';
    document.getElementById('stat-month').textContent = '—';
    document.getElementById('stat-cats').textContent = '—';
    document.getElementById('stat-count').textContent = '—';
    document.getElementById('category-breakdown').innerHTML = '';
    document.getElementById('recent-expenses').innerHTML = '';
    document.getElementById('categories-list').innerHTML = '';
    document.getElementById('expenses-table-wrap').innerHTML = '';

    document.getElementById('app-page').style.display = 'none';
    document.getElementById('auth-page').style.display = 'flex';
}

// ─── NAVIGATION ───────────────────────────────────────────────
function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  const navIndex = ['dashboard', 'categories', 'expenses'].indexOf(name);
  document.querySelectorAll('.nav-item')[navIndex].classList.add('active');
  if (name === 'dashboard') renderDashboard();
  if (name === 'categories') renderCategories();
  if (name === 'expenses') renderExpenses();
}

// ─── CATEGORIES ───────────────────────────────────────────────
async function loadCategories() {
  categories = await api('/categories/');
  populateCategorySelects();
}

function populateCategorySelects() {
  const selects = ['exp-category', 'expense-filter-cat'];
  selects.forEach(id => {
    const sel = document.getElementById(id);
    const val = sel.value;
    while (sel.options.length > 1) sel.remove(1);
    categories.forEach(c => {
      const opt = new Option(c.name, c.id);
      sel.add(opt);
    });
    if (val) sel.value = val;
  });
}

function renderCategories() {
  const wrap = document.getElementById('categories-list');
  if (!categories.length) {
    wrap.innerHTML = '<div class="empty-state">No categories yet. Create one!</div>';
    return;
  }
  wrap.innerHTML = categories.map(c => `
    <div class="chip">
      <span>${escHtml(c.name)}</span>
      <button onclick="confirmDeleteCategory(${c.id}, '${escHtml(c.name)}')" title="Delete">&times;</button>
    </div>
  `).join('');
}

function openCategoryModal() {
  document.getElementById('cat-name').value = '';
  hideAlert('cat-alert');
  openModal('cat-modal');
}

async function handleCreateCategory(e) {
  e.preventDefault();
  const btn = document.getElementById('cat-submit-btn');
  btn.innerHTML = '<span class="spinner"></span>';
  btn.disabled = true;
  try {
    const cat = await api('/categories/', {
      method: 'POST',
      body: JSON.stringify({ name: document.getElementById('cat-name').value })
    });
    categories.push(cat);
    populateCategorySelects();
    closeModal('cat-modal');
    renderCategories();
  } catch (err) {
    showAlert('cat-alert', err.message, 'danger');
  } finally {
    btn.innerHTML = 'Create';
    btn.disabled = false;
  }
}

function confirmDeleteCategory(id, name) {
  document.getElementById('delete-msg').textContent = `Delete category "${name}"? All its expenses will also be removed.`;
  document.getElementById('delete-confirm-btn').onclick = () => deleteCategory(id);
  openModal('delete-modal');
}

async function deleteCategory(id) {
  try {
    await api('/categories/' + id, { method: 'DELETE' });
    categories = categories.filter(c => c.id !== id);
    expenses = expenses.filter(e => e.category_id !== id);
    populateCategorySelects();
    renderCategories();
    renderExpenses();
    closeModal('delete-modal');
  } catch (err) {
    alert(err.message);
  }
}

// ─── EXPENSES ─────────────────────────────────────────────────
async function loadExpenses() {
  const catId = document.getElementById('expense-filter-cat')?.value;
  const qs = catId ? `?category_id=${catId}` : '';
  expenses = await api('/expenses/' + qs);
}

function renderExpenses() {
  const wrap = document.getElementById('expenses-table-wrap');
  if (!expenses.length) {
    wrap.innerHTML = '<div class="empty-state">No expenses yet. Add your first one!</div>';
    return;
  }
  wrap.innerHTML = `<table>
    <thead>
      <tr>
        <th>Title</th>
        <th>Category</th>
        <th>Amount</th>
        <th>Date</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      ${expenses.map(e => {
        const cat = categories.find(c => c.id === e.category_id);
        const date = new Date(e.created_at).toLocaleDateString('en-US', { month:'short', day:'numeric', year:'numeric'});
        return `<tr>
          <td>
            <div style="font-weight:500;">${escHtml(e.title)}</div>
            ${e.description ? `<div style="font-size:12px; color:var(--text3);">${escHtml(e.description)}</div>` : ''}
          </td>
          <td>${cat ? `<span class="badge badge-blue">${escHtml(cat.name)}</span>` : '—'}</td>
          <td class="amount">PKR ${Number(e.amount).toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
          <td style="color:var(--text2); font-size:13px;">${date}</td>
          <td style="white-space:nowrap;">
            <button class="btn btn-sm" onclick="openEditExpense(${e.id})" style="margin-right:4px;">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="confirmDeleteExpense(${e.id}, '${escHtml(e.title)}')">Delete</button>
          </td>
        </tr>`;
      }).join('')}
    </tbody>
  </table>`;
}

function openExpenseModal() {
  document.getElementById('expense-modal-title').textContent = 'Add expense';
  document.getElementById('exp-title').value = '';
  document.getElementById('exp-amount').value = '';
  document.getElementById('exp-category').value = '';
  document.getElementById('exp-desc').value = '';
  document.getElementById('exp-editing-id').value = '';
  hideAlert('exp-alert');
  openModal('expense-modal');
}

function openEditExpense(id) {
  const exp = expenses.find(e => e.id === id);
  if (!exp) return;
  document.getElementById('expense-modal-title').textContent = 'Edit expense';
  document.getElementById('exp-title').value = exp.title;
  document.getElementById('exp-amount').value = exp.amount;
  document.getElementById('exp-category').value = exp.category_id;
  document.getElementById('exp-desc').value = exp.description || '';
  document.getElementById('exp-editing-id').value = exp.id;
  hideAlert('exp-alert');
  openModal('expense-modal');
}

async function handleSaveExpense(e) {
  e.preventDefault();
  const btn = document.getElementById('exp-submit-btn');
  btn.innerHTML = '<span class="spinner"></span>';
  btn.disabled = true;
  const editingId = document.getElementById('exp-editing-id').value;
  const body = {
    title: document.getElementById('exp-title').value,
    amount: parseFloat(document.getElementById('exp-amount').value),
    category_id: parseInt(document.getElementById('exp-category').value),
    description: document.getElementById('exp-desc').value || null
  };
  try {
    if (editingId) {
      const updated = await api('/expenses/' + editingId, { method: 'PUT', body: JSON.stringify(body) });
      const idx = expenses.findIndex(e => e.id === parseInt(editingId));
      if (idx !== -1) expenses[idx] = updated;
    } else {
      const created = await api('/expenses/', { method: 'POST', body: JSON.stringify(body) });
      expenses.unshift(created);
    }
    closeModal('expense-modal');
    renderExpenses();
    renderDashboard();
  } catch (err) {
    showAlert('exp-alert', err.message, 'danger');
  } finally {
    btn.innerHTML = 'Save';
    btn.disabled = false;
  }
}

function confirmDeleteExpense(id, title) {
  document.getElementById('delete-msg').textContent = `Delete "${title}"?`;
  document.getElementById('delete-confirm-btn').onclick = () => deleteExpense(id);
  openModal('delete-modal');
}

async function deleteExpense(id) {
  try {
    await api('/expenses/' + id, { method: 'DELETE' });
    expenses = expenses.filter(e => e.id !== id);
    renderExpenses();
    renderDashboard();
    closeModal('delete-modal');
  } catch (err) {
    alert(err.message);
  }
}

// ─── DASHBOARD ────────────────────────────────────────────────
function renderDashboard() {
  const total = expenses.reduce((s, e) => s + e.amount, 0);
  const now = new Date();
  const monthTotal = expenses
    .filter(e => {
      const d = new Date(e.created_at);
      return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
    })
    .reduce((s, e) => s + e.amount, 0);

  document.getElementById('stat-total').textContent = 'PKR ' + total.toLocaleString('en-US', {maximumFractionDigits:0});
  document.getElementById('stat-month').textContent = 'PKR ' + monthTotal.toLocaleString('en-US', {maximumFractionDigits:0});
  document.getElementById('stat-cats').textContent = categories.length;
  document.getElementById('stat-count').textContent = expenses.length;

  // Category breakdown
  const bycat = {};
  expenses.forEach(e => {
    if (!bycat[e.category_id]) bycat[e.category_id] = 0;
    bycat[e.category_id] += e.amount;
  });
  const breakdown = document.getElementById('category-breakdown');
  if (!Object.keys(bycat).length) {
    breakdown.innerHTML = '<div class="empty-state" style="padding:1.5rem;">No data yet.</div>';
  } else {
    const sorted = Object.entries(bycat).sort((a,b) => b[1] - a[1]);
    const max = sorted[0][1];
    breakdown.innerHTML = sorted.map(([catId, amount]) => {
      const cat = categories.find(c => c.id == catId);
      const pct = Math.round((amount / total) * 100);
      const barW = Math.round((amount / max) * 100);
      return `<div style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;">
          <span>${cat ? escHtml(cat.name) : 'Unknown'}</span>
          <span style="color:var(--text2);">PKR ${amount.toLocaleString('en-US', {maximumFractionDigits:0})} <span style="color:var(--text3);">(${pct}%)</span></span>
        </div>
        <div style="height:6px; background:var(--surface2); border-radius:3px; overflow:hidden;">
          <div style="height:100%; width:${barW}%; background:var(--accent); border-radius:3px;"></div>
        </div>
      </div>`;
    }).join('');
  }

  // Recent expenses
  const recent = document.getElementById('recent-expenses');
  const last5 = expenses.slice(0, 5);
  if (!last5.length) {
    recent.innerHTML = '<div class="empty-state" style="padding:1.5rem;">No expenses yet.</div>';
    return;
  }
  recent.innerHTML = `<table>
    <thead><tr><th>Title</th><th>Category</th><th>Amount</th></tr></thead>
    <tbody>
      ${last5.map(e => {
        const cat = categories.find(c => c.id === e.category_id);
        return `<tr>
          <td>${escHtml(e.title)}</td>
          <td>${cat ? `<span class="badge badge-blue">${escHtml(cat.name)}</span>` : '—'}</td>
          <td class="amount">PKR ${Number(e.amount).toLocaleString('en-US', {minimumFractionDigits:2,maximumFractionDigits:2})}</td>
        </tr>`;
      }).join('')}
    </tbody>
  </table>`;
}

// ─── MODAL HELPERS ────────────────────────────────────────────
function openModal(id) { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }

document.querySelectorAll('.modal-overlay').forEach(m => {
  m.addEventListener('click', e => { if (e.target === m) m.classList.remove('open'); });
});

// ─── ALERT HELPERS ────────────────────────────────────────────
function showAlert(id, msg, type) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.className = `alert alert-${type} show`;
}
function hideAlert(id) {
  const el = document.getElementById(id);
  el.className = 'alert';
}

// ─── ESCAPE HTML ─────────────────────────────────────────────
function escHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}