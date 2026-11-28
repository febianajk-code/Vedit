'use strict';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const uid = () => Math.random().toString(36).slice(2, 9) + Date.now().toString(36);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const DB_KEY = 'sverfile.db.v1';
const DEFAULT_SETTINGS = { ui: 'material', mode: 'dark', accent: '#3b82f6', bgKind: 'color', bgValue: '#0b1220', blur: 16, alpha: 55, fontScale: 100 };

const TYPES = {
  txt: { label: 'Teks', icon: '📄', tpl: '' },
  md: { label: 'Markdown', icon: '📝', tpl: '# Judul\n\nTulis sesuatu di sini…\n' },
  html: { label: 'HTML', icon: '🌐', tpl: '<!doctype html>\n<html lang="id">\n<head>\n  <meta charset="utf-8">\n  <title>Halaman Baru</title>\n</head>\n<body>\n  <h1>Halo Sver</h1>\n</body>\n</html>\n' },
  css: { label: 'CSS', icon: '🎨', tpl: ':root {\n  --warna: #3b82f6;\n}\n\nbody {\n  margin: 0;\n  font-family: system-ui, sans-serif;\n}\n' },
  js: { label: 'JavaScript', icon: '⚡', tpl: "'use strict';\n\nconsole.log('Halo Sver');\n" },
  json: { label: 'JSON', icon: '🧩', tpl: '{\n  "nama": "sver-file",\n  "versi": "1.0"\n}\n' },
  xml: { label: 'XML', icon: '🗂️', tpl: '<?xml version="1.0" encoding="UTF-8"?>\n<root>\n</root>\n' },
  csv: { label: 'CSV', icon: '📊', tpl: 'kolom_a,kolom_b\n1,2\n' },
  py: { label: 'Python', icon: '🐍', tpl: 'def main():\n    print("Halo Sver")\n\n\nif __name__ == "__main__":\n    main()\n' },
  java: { label: 'Java', icon: '☕', tpl: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Halo Sver");\n    }\n}\n' },
  c: { label: 'C', icon: '🔧', tpl: '#include <stdio.h>\n\nint main(void) {\n    printf("Halo Sver\\n");\n    return 0;\n}\n' },
  cpp: { label: 'C++', icon: '➕', tpl: '#include <iostream>\n\nint main() {\n    std::cout << "Halo Sver" << std::endl;\n    return 0;\n}\n' },
  cs: { label: 'C#', icon: '🟣', tpl: 'using System;\n\nclass Program {\n    static void Main() {\n        Console.WriteLine("Halo Sver");\n    }\n}\n' },
  php: { label: 'PHP', icon: '🐘', tpl: '<?php\necho "Halo Sver";\n' },
  sh: { label: 'Shell', icon: '🐚', tpl: '#!/bin/sh\necho "Halo Sver"\n' },
  yaml: { label: 'YAML', icon: '⚙️', tpl: 'nama: sver-file\nversi: "1.0"\n' },
  ini: { label: 'INI', icon: '🛠️', tpl: '[pengaturan]\nmode=gelap\n' },
  sql: { label: 'SQL', icon: '🗄️', tpl: 'SELECT * FROM sver;\n' },
  svg: { label: 'SVG', icon: '🖼️', tpl: '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"></svg>\n' },
  log: { label: 'Log', icon: '🧾', tpl: '[INFO] Sver File siap.\n' }
};

const ACCENTS = ['#3b82f6', '#8b5cf6', '#ec4899', '#ef4444', '#f59e0b', '#22c55e', '#14b8a6', '#e2e8f0'];
const BG_PRESETS = [
  { name: 'Navy', css: 'linear-gradient(160deg,#0b1220,#12203f)' },
  { name: 'Aurora', css: 'linear-gradient(150deg,#0f172a,#1e3a5f,#312e81)' },
  { name: 'Sunset', css: 'linear-gradient(150deg,#1f1130,#7c2d55,#b45309)' },
  { name: 'Mint', css: 'linear-gradient(150deg,#052e26,#065f46,#0ea5e9)' },
  { name: 'Candy', css: 'linear-gradient(150deg,#fdf2f8,#e0e7ff,#cffafe)' },
  { name: 'Carbon', css: 'linear-gradient(160deg,#0a0a0a,#27272a)' }
];

let DB = loadDB();
const state = { view: 'files', currentFolder: 'all', currentFile: null, dirName: null, pickedExt: 'txt', pendingBackup: null };
const ed = { stack: [], idx: -1, lastPush: 0 };
let editor, saveTimer, persistSettingsTimer;

function loadDB() {
  try {
    const raw = localStorage.getItem(DB_KEY);
    if (raw) {
      const d = JSON.parse(raw);
      d.folders = Array.isArray(d.folders) && d.folders.length ? d.folders : [{ id: 'root', name: 'Project Utama', createdAt: Date.now() }];
      d.files = Array.isArray(d.files) ? d.files : [];
      d.history = Array.isArray(d.history) ? d.history : [];
      d.settings = Object.assign({}, DEFAULT_SETTINGS, d.settings || {});
      d.onboarded = !!d.onboarded;
      return d;
    }
  } catch (e) { console.warn('DB rusak, mulai baru', e); }
  return {
    folders: [{ id: 'root', name: 'Project Utama', createdAt: Date.now() }],
    files: [],
    history: [],
    settings: Object.assign({}, DEFAULT_SETTINGS),
    onboarded: false
  };
}

function persist() {
  try { localStorage.setItem(DB_KEY, JSON.stringify(DB)); setSaveState('tersimpan ✓'); }
  catch (e) { toast('⚠️ Penyimpanan penuh — hapus file/gambar latar'); setSaveState('gagal menyimpan'); }
}

function setSaveState(t) { const el = $('#save-state'); if (el) el.textContent = t; }

function getSettings() { return DB.settings; }
function getFolder(id) { return DB.folders.find(f => f.id === id); }
function getFile(id) { return DB.files.find(f => f.id === id); }
function folderName(id) { const f = getFolder(id); return f ? f.name : '?'; }

function applySettings() {
  const s = getSettings();
  const r = document.documentElement.style;
  r.setProperty('--accent', s.accent);
  r.setProperty('--glass-blur', s.blur + 'px');
  r.setProperty('--panel-alpha', (s.alpha / 100).toFixed(2));
  r.setProperty('--fs', (s.fontScale / 100).toFixed(2));
  document.body.dataset.ui = s.ui;
  document.body.dataset.mode = s.mode;
  $('#btn-mode').textContent = s.mode === 'dark' ? '🌙' : '☀️';
  const bgEl = $('#bgimage');
  if (s.bgKind === 'image' && s.bgValue) {
    bgEl.style.backgroundImage = 'url(' + s.bgValue + ')';
    bgEl.style.display = 'block';
  } else {
    bgEl.style.backgroundImage = '';
    bgEl.style.display = 'none';
    document.body.style.background = s.bgKind === 'gradient' ? s.bgValue : s.bgValue;
  }
  $$('.ui-card').forEach(c => c.classList.toggle('sel', c.id === 'ui-' + s.ui));
  $$('.seg-btn').forEach(b => b.classList.toggle('active', b.dataset.mode === s.mode));
  $$('#accent-swatches .swatch').forEach(b => b.classList.toggle('sel', b.dataset.c === s.accent));
  $$('#bg-swatches .swatch').forEach(b => b.classList.toggle('sel', s.bgKind === 'gradient' && b.dataset.g === s.bgValue));
  const vb = $('#val-blur'); if (vb) vb.textContent = s.blur + 'px';
  const va = $('#val-alpha'); if (va) va.textContent = s.alpha + '%';
  const vf = $('#val-font'); if (vf) vf.textContent = s.fontScale + '%';
}

function saveSettingsDebounced() {
  clearTimeout(persistSettingsTimer);
  persistSettingsTimer = setTimeout(persist, 300);
}

function toast(msg) {
  const t = $('#toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => t.classList.remove('show'), 1900);
}

function timeAgo(ts) {
  const m = Math.floor((Date.now() - ts) / 60000);
  if (m < 1) return 'baru saja';
  if (m < 60) return m + ' mnt lalu';
  const h = Math.floor(m / 60);
  if (h < 24) return h + ' jam lalu';
  const d = Math.floor(h / 24);
  if (d < 7) return d + ' hari lalu';
  return new Date(ts).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });
}

function fileIcon(ext) { return (TYPES[ext] || { icon: '📄' }).icon; }

function switchView(name) {
  state.view = name;
  $$('.view').forEach(v => v.classList.toggle('active', v.id === 'view-' + name));
  $$('.nav-btn').forEach(b => b.classList.toggle('active', b.dataset.view === name));
  if (name === 'files') renderFiles();
  if (name === 'history') renderHistory();
  if (name === 'settings') renderSettings();
  if (name === 'editor' && !state.currentFile) renderEditorEmpty();
}

function renderFiles() {
  const chips = $('#folder-chips');
  chips.innerHTML = '';
  const all = document.createElement('button');
  all.className = 'chip' + (state.currentFolder === 'all' ? ' active' : '');
  all.innerHTML = '<span>📂 Semua</span>';
  all.addEventListener('click', () => { state.currentFolder = 'all'; renderFiles(); });
  chips.appendChild(all);
  DB.folders.forEach(f => {
    const b = document.createElement('button');
    b.className = 'chip' + (state.currentFolder === f.id ? ' active' : '');
    b.innerHTML = '<span>📁 ' + esc(f.name) + '</span>';
    b.addEventListener('click', () => { state.currentFolder = f.id; renderFiles(); });
    b.addEventListener('contextmenu', ev => { ev.preventDefault(); folderSheet(f.id); });
    chips.appendChild(b);
  });

  const list = $('#filelist');
  list.innerHTML = '';
  const files = DB.files
    .filter(f => state.currentFolder === 'all' || f.folderId === state.currentFolder)
    .sort((a, b) => b.updatedAt - a.updatedAt);
  $('#files-empty').hidden = files.length > 0;
  files.forEach((f, i) => {
    const item = document.createElement('div');
    item.className = 'file-item';
    item.style.animationDelay = Math.min(i * 0.04, 0.4) + 's';
    item.innerHTML =
      '<span class="fi-icon">' + fileIcon(f.ext) + '</span>' +
      '<div><strong>' + esc(f.name + '.' + f.ext) + '</strong>' +
      '<small>' + esc(folderName(f.folderId)) + ' • ' + timeAgo(f.updatedAt) + '</small></div>';
    const kebab = document.createElement('button');
    kebab.className = 'fi-btn';
    kebab.textContent = '⋮';
    kebab.setAttribute('aria-label', 'Opsi file');
    kebab.addEventListener('click', ev => { ev.stopPropagation(); fileSheet(f.id); });
    item.appendChild(kebab);
    item.addEventListener('click', () => openEditor(f.id));
    list.appendChild(item);
  });
}

function renderHistory() {
  const list = $('#histlist');
  list.innerHTML = '';
  $('#hist-empty').hidden = DB.history.length > 0;
  DB.history.forEach((h, i) => {
    const f = getFile(h.fileId);
    const item = document.createElement('div');
    item.className = 'file-item';
    item.style.animationDelay = Math.min(i * 0.04, 0.4) + 's';
    const icon = f ? fileIcon(f.ext) : '🗑️';
    const meta = f ? (folderName(h.folderId) + ' • ' + timeAgo(h.at)) : ('terhapus • ' + timeAgo(h.at));
    item.innerHTML =
      '<span class="fi-icon">' + icon + '</span>' +
      '<div><strong>' + esc(h.name) + '</strong><small>' + esc(meta) + '</small></div>';
    const act = document.createElement('button');
    act.className = 'fi-btn';
    act.textContent = f ? '↗' : '✕';
    act.setAttribute('aria-label', f ? 'Buka file' : 'Hapus dari riwayat');
    act.addEventListener('click', ev => {
      ev.stopPropagation();
      if (f) openEditor(f.id);
      else { DB.history = DB.history.filter(x => x.fileId !== h.fileId); persist(); renderHistory(); }
    });
    item.appendChild(act);
    if (f) item.addEventListener('click', () => openEditor(f.id));
    list.appendChild(item);
  });
}

function renderSettings() {
  const s = getSettings();
  $('#perm-state').textContent = 'Status izin: ' + permStateText() + (state.dirName ? ' • Folder proyek: ' + state.dirName : '');
  $('#accent-custom').value = s.accent;
  $('#bg-custom').value = s.bgKind === 'color' ? s.bgValue : '#0b1220';
  $('#set-blur').value = s.blur;
  $('#set-alpha').value = s.alpha;
  $('#set-font').value = s.fontScale;
  $('#val-blur').textContent = s.blur + 'px';
  $('#val-alpha').textContent = s.alpha + '%';
  $('#val-font').textContent = s.fontScale + '%';
}

function permStateText() {
  if (!DB.onboarded) return 'belum diizinkan';
  if (navigator.storage && navigator.storage.persisted) return 'aktif (lokal)';
  return 'aktif';
}

function renderEditorEmpty() {
  state.currentFile = null;
  $('#ed-name').textContent = 'Belum ada file';
  $('#ed-folder').textContent = 'Buat atau buka file dari Beranda';
  $('#ed-icon').textContent = '🗂️';
  editor.value = '';
  editor.disabled = true;
  ed.stack = []; ed.idx = -1;
  updateStats();
}

function openEditor(id) {
  const f = getFile(id);
  if (!f) return;
  state.currentFile = id;
  editor.disabled = false;
  $('#ed-name').textContent = f.name + '.' + f.ext;
  $('#ed-folder').textContent = '📁 ' + folderName(f.folderId) + ' • diubah ' + timeAgo(f.updatedAt);
  $('#ed-icon').textContent = fileIcon(f.ext);
  editor.value = f.content;
  ed.stack = [{ v: f.content, s: 0, e: 0 }];
  ed.idx = 0;
  updateStats();
  setSaveState('tersimpan ✓');
  switchView('editor');
  setTimeout(() => { editor.focus(); editor.setSelectionRange(f.content.length, f.content.length); }, 60);
}

function markEdited() {
  const f = getFile(state.currentFile);
  if (!f) return;
  f.content = editor.value;
  f.updatedAt = Date.now();
  addHistory(f);
  setSaveState('menyimpan…');
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => { persist(); refreshMeta(); }, 700);
}

function refreshMeta() {
  const f = getFile(state.currentFile);
  if (f) {
    $('#ed-folder').textContent = '📁 ' + folderName(f.folderId) + ' • diubah ' + timeAgo(f.updatedAt);
    $('#ed-name').textContent = f.name + '.' + f.ext;
  }
}

function addHistory(f) {
  DB.history = DB.history.filter(h => h.fileId !== f.id);
  DB.history.unshift({ fileId: f.id, name: f.name + '.' + f.ext, folderId: f.folderId, at: Date.now() });
  DB.history = DB.history.slice(0, 50);
}

function snap() { return { v: editor.value, s: editor.selectionStart, e: editor.selectionEnd }; }

function pushHistory() {
  const now = Date.now();
  const top = ed.stack[ed.idx];
  if (top && top.v === editor.value) { top.s = editor.selectionStart; top.e = editor.selectionEnd; return; }
  if (now - ed.lastPush < 400 && top) {
    ed.stack[ed.idx] = snap();
  } else {
    ed.stack = ed.stack.slice(0, ed.idx + 1);
    ed.stack.push(snap());
    if (ed.stack.length > 300) ed.stack.shift();
    ed.idx = ed.stack.length - 1;
  }
  ed.lastPush = now;
}

function applySnap(s) {
  editor.value = s.v;
  try { editor.setSelectionRange(s.s, s.e); } catch (e) {}
  updateStats();
  markEdited();
}

function undo() {
  if (ed.idx <= 0) { toast('Tidak ada lagi yang bisa di-undo'); return; }
  ed.idx--;
  applySnap(ed.stack[ed.idx]);
}

function redo() {
  if (ed.idx >= ed.stack.length - 1) { toast('Tidak ada lagi yang bisa di-redo'); return; }
  ed.idx++;
  applySnap(ed.stack[ed.idx]);
}

function updateStats() {
  const v = editor.value;
  const lines = v.split('\n').length;
  $('#st-lines').textContent = lines + ' baris';
  $('#st-chars').textContent = v.length + ' karakter';
  const before = v.slice(0, editor.selectionStart);
  const ln = before.split('\n').length;
  const col = before.length - before.lastIndexOf('\n');
  $('#st-cur').textContent = 'Ln ' + ln + ', Col ' + col;
}

function selText() { return editor.value.slice(editor.selectionStart, editor.selectionEnd); }

async function copySel() {
  const t = selText() || editor.value;
  try { await navigator.clipboard.writeText(t); toast('✓ Tersalin'); }
  catch (e) { legacyCopy(t); }
}

function legacyCopy(t) {
  const ta = document.createElement('textarea');
  ta.value = t;
  ta.style.cssText = 'position:fixed;opacity:0';
  document.body.appendChild(ta);
  ta.select();
  try { document.execCommand('copy'); toast('✓ Tersalin'); }
  catch (e) { toast('⚠️ Gagal menyalin'); }
  ta.remove();
}

async function cutSel() {
  if (!selText()) editor.setSelectionRange(0, editor.value.length);
  const t = selText();
  if (!t) return;
  try { await navigator.clipboard.writeText(t); toast('✂ Dipotong'); }
  catch (e) { toast('✂ Dipotong (clipboard diblokir)'); }
  replaceSelection('');
}

async function pasteClip() {
  try {
    const t = await navigator.clipboard.readText();
    if (!t) { manualPaste(); return; }
    replaceSelection(t);
    toast('📋 Ditempel');
  } catch (e) { manualPaste(); }
}

function manualPaste() {
  openModal(
    '<h3>Tempel Manual</h3>' +
    '<p class="hint">Browser memblokir akses clipboard. Tekan-lama di kotak lalu pilih Tempel.</p>' +
    '<div class="field"><textarea id="paste-box" placeholder="Tempel di sini…"></textarea></div>' +
    '<div class="modal-foot"><button class="btn ghost" data-close>Batal</button>' +
    '<button class="btn primary" id="paste-go">Tempel ke Editor</button></div>');
  $('#paste-go').addEventListener('click', () => {
    const t = $('#paste-box').value;
    if (t) replaceSelection(t);
    closeModal();
    toast('📋 Ditempel');
  });
}

function replaceSelection(text) {
  const s = editor.selectionStart, e = editor.selectionEnd;
  editor.setRangeText(text, s, e, 'end');
  editor.focus();
  pushHistory();
  updateStats();
  markEdited();
}

function selectAll() { editor.focus(); editor.setSelectionRange(0, editor.value.length); updateStats(); }

function clearAll() {
  if (!editor.value) return;
  confirmModal('Kosongkan seluruh isi editor?', () => {
    editor.setSelectionRange(0, editor.value.length);
    replaceSelection('');
  });
}

function downloadBlob(name, text) {
  if (window.AndroidBlob && window.AndroidBlob.save) {
    try {
      window.AndroidBlob.save(name, btoa(unescape(encodeURIComponent(text))));
      return;
    } catch (e) {}
  }
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}

function downloadFile() {
  const f = getFile(state.currentFile);
  const name = f ? (f.name + '.' + f.ext) : 'sver-file.txt';
  downloadBlob(name, editor.value);
  toast('⬇ Diunduh: ' + name);
}

function saveNow() {
  const f = getFile(state.currentFile);
  if (!f) { toast('Buka file dulu dari Beranda'); return; }
  f.content = editor.value;
  f.updatedAt = Date.now();
  addHistory(f);
  persist();
  refreshMeta();
  toast('💾 Tersimpan');
}

function openNewFileModal() {
  state.pickedExt = 'txt';
  const grid = Object.entries(TYPES).map(([ext, t]) =>
    '<button class="type-btn' + (ext === 'txt' ? ' sel' : '') + '" data-ext="' + ext + '">' +
    '<i>' + t.icon + '</i>' + t.label + '</button>').join('');
  const folders = DB.folders.map(f =>
    '<option value="' + f.id + '"' + (f.id === (state.currentFolder === 'all' ? 'root' : state.currentFolder) ? ' selected' : '') + '>' + esc(f.name) + '</option>').join('');
  openModal(
    '<h3>Buat File Baru</h3>' +
    '<div class="field"><span>Nama file</span><input id="nf-name" placeholder="tanpa-nama" maxlength="60" autocomplete="off"></div>' +
    '<div class="field"><span>Folder proyek</span><select id="nf-folder">' + folders + '</select></div>' +
    '<div class="field"><span>Jenis file (' + Object.keys(TYPES).length + ' pilihan)</span></div>' +
    '<div class="typegrid" id="nf-grid">' + grid + '</div>' +
    '<div class="modal-foot"><button class="btn ghost" data-close>Batal</button>' +
    '<button class="btn primary" id="nf-go">＋ Buat</button></div>');
  $('#nf-grid').addEventListener('click', e => {
    const b = e.target.closest('.type-btn');
    if (!b) return;
    $$('#nf-grid .type-btn').forEach(x => x.classList.remove('sel'));
    b.classList.add('sel');
    state.pickedExt = b.dataset.ext;
  });
  $('#nf-go').addEventListener('click', () => createNewFile());
  $('#nf-name').focus();
}

function sanitizeName(n) {
  n = (n || '').trim().replace(/[\\/:*?"<>|]/g, '').replace(/\s+/g, ' ');
  return n || 'tanpa-nama';
}

function createNewFile() {
  const base = sanitizeName($('#nf-name').value);
  const ext = state.pickedExt;
  const folderId = $('#nf-folder').value;
  let name = base, n = 2;
  while (DB.files.some(f => f.folderId === folderId && f.name === name && f.ext === ext)) name = base + ' (' + n++ + ')';
  const file = { id: uid(), name, ext, folderId, content: TYPES[ext].tpl, createdAt: Date.now(), updatedAt: Date.now() };
  DB.files.push(file);
  addHistory(file);
  persist();
  closeModal();
  state.currentFolder = folderId;
  openEditor(file.id);
  toast('✨ ' + name + '.' + ext + ' dibuat');
}

function openNewFolderModal() {
  openModal(
    '<h3>Folder Proyek Baru</h3>' +
    '<div class="field"><span>Nama folder</span><input id="fd-name" placeholder="misal: Proyek Kuliah" maxlength="40" autocomplete="off"></div>' +
    '<div class="modal-foot"><button class="btn ghost" data-close>Batal</button>' +
    '<button class="btn primary" id="fd-go">＋ Buat Folder</button></div>');
  $('#fd-go').addEventListener('click', () => {
    const name = sanitizeName($('#fd-name').value);
    if (DB.folders.some(f => f.name.toLowerCase() === name.toLowerCase())) { toast('⚠️ Nama folder sudah dipakai'); return; }
    DB.folders.push({ id: uid(), name, createdAt: Date.now() });
    persist();
    state.currentFolder = DB.folders[DB.folders.length - 1].id;
    closeModal();
    renderFiles();
    toast('📁 Folder "' + name + '" dibuat');
  });
  $('#fd-name').focus();
}

function openModal(html) { $('#modal-card').innerHTML = html; $('#modal').classList.add('open'); }
function closeModal() { $('#modal').classList.remove('open'); }
function openSheet(html) { $('#sheet-card').innerHTML = html; $('#sheet').classList.add('open'); }
function closeSheet() { $('#sheet').classList.remove('open'); }

function fileSheet(id) {
  const f = getFile(id);
  if (!f) return;
  openSheet(
    '<h3>' + fileIcon(f.ext) + ' ' + esc(f.name + '.' + f.ext) + '</h3>' +
    '<div class="sheet-opts">' +
    '<button class="sheet-opt" data-act="open">✏️ Buka di Editor</button>' +
    '<button class="sheet-opt" data-act="rename">✏️ Ganti Nama</button>' +
    '<button class="sheet-opt" data-act="move">📁 Pindahkan Folder</button>' +
    '<button class="sheet-opt" data-act="download">⬇ Unduh</button>' +
    '<button class="sheet-opt danger" data-act="delete">🗑️ Hapus</button>' +
    '<button class="sheet-opt" data-close>Batal</button>' +
    '</div>');
  $('#sheet-card').addEventListener('click', e => {
    const b = e.target.closest('[data-act]');
    if (!b) return;
    closeSheet();
    const act = b.dataset.act;
    if (act === 'open') openEditor(id);
    if (act === 'rename') renameModal(f);
    if (act === 'move') moveModal(f);
    if (act === 'download') downloadAny(f);
    if (act === 'delete') confirmModal('Hapus "' + f.name + '.' + f.ext + '"? Tindakan ini tidak bisa dibatalin.', () => {
      DB.files = DB.files.filter(x => x.id !== id);
      DB.history = DB.history.filter(h => h.fileId !== id);
      if (state.currentFile === id) renderEditorEmpty();
      persist(); renderFiles();
      toast('🗑️ File dihapus');
    });
  }, { once: true });
}

function folderSheet(id) {
  const f = getFolder(id);
  if (!f) return;
  openSheet(
    '<h3>📁 ' + esc(f.name) + '</h3>' +
    '<div class="sheet-opts">' +
    '<button class="sheet-opt" data-act="rename">✏️ Ganti Nama Folder</button>' +
    '<button class="sheet-opt danger" data-act="delete">🗑️ Hapus Folder</button>' +
    '<button class="sheet-opt" data-close>Batal</button>' +
    '</div>');
  $('#sheet-card').addEventListener('click', e => {
    const b = e.target.closest('[data-act]');
    if (!b) return;
    closeSheet();
    if (b.dataset.act === 'rename') {
      openModal(
        '<h3>Ganti Nama Folder</h3>' +
        '<div class="field"><span>Nama baru</span><input id="fr-name" maxlength="40" value="' + esc(f.name) + '"></div>' +
        '<div class="modal-foot"><button class="btn ghost" data-close>Batal</button><button class="btn primary" id="fr-go">Simpan</button></div>');
      $('#fr-go').addEventListener('click', () => {
        f.name = sanitizeName($('#fr-name').value);
        persist(); closeModal(); renderFiles(); toast('✓ Folder diubah');
      });
    }
    if (b.dataset.act === 'delete') {
      confirmModal('Hapus folder "' + f.name + '"? Semua file di dalamnya pindah ke Project Utama.', () => {
        DB.files.forEach(x => { if (x.folderId === id) x.folderId = 'root'; });
        DB.history.forEach(h => { if (h.folderId === id) h.folderId = 'root'; });
        DB.folders = DB.folders.filter(x => x.id !== id);
        if (state.currentFolder === id) state.currentFolder = 'all';
        persist(); renderFiles();
        toast('🗑️ Folder dihapus');
      });
    }
  }, { once: true });
}

function renameModal(f) {
  openModal(
    '<h3>Ganti Nama File</h3>' +
    '<div class="field"><span>Nama (tanpa .' + esc(f.ext) + ')</span><input id="rn-name" maxlength="60" value="' + esc(f.name) + '"></div>' +
    '<div class="modal-foot"><button class="btn ghost" data-close>Batal</button><button class="btn primary" id="rn-go">Simpan</button></div>');
  $('#rn-go').addEventListener('click', () => {
    f.name = sanitizeName($('#rn-name').value);
    f.updatedAt = Date.now();
    addHistory(f);
    persist(); closeModal(); renderFiles(); renderHistory();
    if (state.currentFile === f.id) refreshMeta();
    toast('✓ Nama diubah');
  });
}

function moveModal(f) {
  const opts = DB.folders.map(x =>
    '<button class="sheet-opt" data-fid="' + x.id + '">📁 ' + esc(x.name) + (x.id === f.folderId ? ' •' : '') + '</button>').join('');
  openSheet('<h3>Pindahkan ke…</h3><div class="sheet-opts">' + opts +
    '<button class="sheet-opt" data-close>Batal</button></div>');
  $('#sheet-card').addEventListener('click', e => {
    const b = e.target.closest('[data-fid]');
    if (!b) return;
    closeSheet();
    f.folderId = b.dataset.fid;
    f.updatedAt = Date.now();
    addHistory(f);
    persist(); renderFiles(); renderHistory();
    if (state.currentFile === f.id) refreshMeta();
    toast('📁 Dipindah ke ' + folderName(f.folderId));
  }, { once: true });
}

function downloadAny(f) {
  downloadBlob(f.name + '.' + f.ext, f.content);
  toast('⬇ Diunduh');
}

function confirmModal(msg, onYes) {
  openModal(
    '<h3>Yakin?</h3><p class="hint">' + esc(msg) + '</p>' +
    '<div class="modal-foot"><button class="btn ghost" data-close>Batal</button>' +
    '<button class="btn danger" id="cf-yes">Ya, Lanjut</button></div>');
  $('#cf-yes').addEventListener('click', () => { closeModal(); onYes(); });
}

function importFromDevice(files) {
  [...files].forEach(file => {
    const dot = file.name.lastIndexOf('.');
    const ext = dot > 0 ? file.name.slice(dot + 1).toLowerCase() : 'txt';
    const reader = new FileReader();
    reader.onload = () => {
      const knownExt = TYPES[ext] ? ext : 'txt';
      let name = dot > 0 ? file.name.slice(0, dot) : file.name;
      name = sanitizeName(name);
      const folderId = state.currentFolder === 'all' ? 'root' : state.currentFolder;
      let fname = name, n = 2;
      while (DB.files.some(f => f.folderId === folderId && f.name === fname && f.ext === knownExt)) fname = name + ' (' + n++ + ')';
      DB.files.push({ id: uid(), name: fname, ext: knownExt, folderId, content: String(reader.result), createdAt: Date.now(), updatedAt: Date.now() });
      const nf = DB.files[DB.files.length - 1];
      addHistory(nf);
      persist();
      renderFiles();
      toast('📂 Diimpor: ' + fname + '.' + knownExt);
    };
    reader.readAsText(file);
  });
}

function setBackgroundImage(file) {
  const img = new Image();
  const reader = new FileReader();
  reader.onload = () => {
    img.onload = () => {
      const max = 1280;
      const sc = Math.min(1, max / Math.max(img.width, img.height));
      const c = document.createElement('canvas');
      c.width = Math.round(img.width * sc);
      c.height = Math.round(img.height * sc);
      c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
      const s = getSettings();
      try {
        s.bgKind = 'image';
        s.bgValue = c.toDataURL('image/jpeg', 0.72);
        applySettings(); persist();
        toast('🖼️ Latar belakang dipasang');
      } catch (e) { toast('⚠️ Gambar terlalu besar'); }
    };
    img.src = reader.result;
  };
  reader.readAsDataURL(file);
}

async function requestStorage() {
  const parts = [];
  try {
    if (navigator.storage && navigator.storage.persist) {
      const ok = await navigator.storage.persist();
      parts.push(ok ? 'penyimpanan persisten: aktif' : 'penyimpanan persisten: ditolak browser');
    } else parts.push('penyimpanan lokal: aktif (localStorage)');
  } catch (e) { parts.push('izin penyimpanan: error'); }
  return parts.join(' • ');
}

async function connectFolder() {
  if (!window.showDirectoryPicker) { toast('⚠️ Browser tidak mendukung akses folder nyata'); return; }
  try {
    const h = await window.showDirectoryPicker({ mode: 'readwrite' });
    state.dirName = h.name;
    toast('📁 Terhubung: ' + h.name);
    renderSettings();
  } catch (e) { if (e && e.name !== 'AbortError') toast('⚠️ Gagal menghubungkan folder'); }
}

function exportBackup() {
  downloadBlob('sver-file-backup.json', JSON.stringify(DB, null, 2));
  toast('⬇ Cadangan dibuat');
}

function importBackup(file) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const d = JSON.parse(String(reader.result));
      if (!d || !Array.isArray(d.folders)) throw new Error('format salah');
      localStorage.setItem(DB_KEY, JSON.stringify(d));
      DB = loadDB();
      applySettings(); renderAll();
      toast('✓ Cadangan dipulihkan');
    } catch (e) { toast('⚠️ File cadangan tidak valid'); }
  };
  reader.readAsText(file);
}

function renderAll() {
  renderFiles();
  renderHistory();
  renderSettings();
  if (state.view === 'editor' && !state.currentFile) renderEditorEmpty();
}

function bindEvents() {
  editor = $('#editor');

  $$('.nav-btn').forEach(b => b.addEventListener('click', () => switchView(b.dataset.view)));

  const newFile = () => { switchView('files'); openNewFileModal(); };
  ['btn-new', 'btn-new2', 'btn-new3'].forEach(id => $('#' + id).addEventListener('click', newFile));
  $('#btn-newfolder').addEventListener('click', openNewFolderModal);
  $('#btn-opendevice').addEventListener('click', () => $('#file-import').click());
  $('#file-import').addEventListener('change', e => { importFromDevice(e.target.files); e.target.value = ''; });

  editor.addEventListener('input', () => { pushHistory(); updateStats(); markEdited(); });
  document.addEventListener('selectionchange', () => { if (document.activeElement === editor) updateStats(); });

  $('#toolbar').addEventListener('click', e => {
    const b = e.target.closest('[data-cmd]');
    if (!b) return;
    const cmd = b.dataset.cmd;
    if (cmd === 'undo') undo();
    if (cmd === 'redo') redo();
    if (cmd === 'cut') cutSel();
    if (cmd === 'copy') copySel();
    if (cmd === 'paste') pasteClip();
    if (cmd === 'selall') selectAll();
    if (cmd === 'clear') clearAll();
    if (cmd === 'download') downloadFile();
  });

  $('#btn-save').addEventListener('click', saveNow);
  $('#btn-close-ed').addEventListener('click', () => { saveNow(); switchView('files'); });

  document.addEventListener('keydown', e => {
    if (state.view !== 'editor') return;
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'z') { e.preventDefault(); undo(); }
    else if ((e.ctrlKey || e.metaKey) && (e.key.toLowerCase() === 'y' || (e.shiftKey && e.key.toLowerCase() === 'z'))) { e.preventDefault(); redo(); }
    else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') { e.preventDefault(); saveNow(); }
  });

  $('#btn-mode').addEventListener('click', () => {
    const s = getSettings();
    s.mode = s.mode === 'dark' ? 'light' : 'dark';
    applySettings(); saveSettingsDebounced();
  });

  $('#ui-material').addEventListener('click', () => { getSettings().ui = 'material'; applySettings(); saveSettingsDebounced(); toast('🧱 Material Style'); });
  $('#ui-glass').addEventListener('click', () => { getSettings().ui = 'glass'; applySettings(); saveSettingsDebounced(); toast('🫧 Liquid Glass Style'); });
  $$('.seg-btn').forEach(b => b.addEventListener('click', () => { getSettings().mode = b.dataset.mode; applySettings(); saveSettingsDebounced(); }));

  const sw = $('#accent-swatches');
  ACCENTS.forEach(c => {
    const b = document.createElement('button');
    b.className = 'swatch';
    b.style.background = c;
    b.dataset.c = c;
    b.setAttribute('aria-label', 'Warna aksen ' + c);
    b.addEventListener('click', () => { getSettings().accent = c; applySettings(); saveSettingsDebounced(); });
    sw.appendChild(b);
  });
  $('#accent-custom').addEventListener('input', e => { getSettings().accent = e.target.value; applySettings(); saveSettingsDebounced(); });

  const bsw = $('#bg-swatches');
  BG_PRESETS.forEach(p => {
    const b = document.createElement('button');
    b.className = 'swatch';
    b.style.background = p.css;
    b.dataset.g = p.css;
    b.title = p.name;
    b.setAttribute('aria-label', 'Latar ' + p.name);
    b.addEventListener('click', () => { const s = getSettings(); s.bgKind = 'gradient'; s.bgValue = p.css; applySettings(); saveSettingsDebounced(); });
    bsw.appendChild(b);
  });
  $('#bg-custom').addEventListener('input', e => { const s = getSettings(); s.bgKind = 'color'; s.bgValue = e.target.value; applySettings(); saveSettingsDebounced(); });
  $('#btn-bgimg').addEventListener('click', () => $('#file-bg').click());
  $('#file-bg').addEventListener('change', e => { if (e.target.files[0]) setBackgroundImage(e.target.files[0]); e.target.value = ''; });
  $('#btn-bgrm').addEventListener('click', () => {
    const s = getSettings();
    s.bgKind = 'color';
    s.bgValue = s.mode === 'dark' ? '#0b1220' : '#eef2f8';
    applySettings(); saveSettingsDebounced();
    toast('Gambar latar dihapus');
  });

  $('#set-blur').addEventListener('input', e => { getSettings().blur = +e.target.value; $('#val-blur').textContent = e.target.value + 'px'; applySettings(); saveSettingsDebounced(); });
  $('#set-alpha').addEventListener('input', e => { getSettings().alpha = +e.target.value; $('#val-alpha').textContent = e.target.value + '%'; applySettings(); saveSettingsDebounced(); });
  $('#set-font').addEventListener('input', e => { getSettings().fontScale = +e.target.value; $('#val-font').textContent = e.target.value + '%'; applySettings(); saveSettingsDebounced(); });

  $('#btn-perm2').addEventListener('click', async () => { toast('⏳ Memeriksa izin…'); toast(await requestStorage()); renderSettings(); });
  $('#btn-dir').addEventListener('click', connectFolder);
  $('#btn-export').addEventListener('click', exportBackup);
  $('#btn-import').addEventListener('click', () => $('#file-backup').click());
  $('#file-backup').addEventListener('change', e => { if (e.target.files[0]) importBackup(e.target.files[0]); e.target.value = ''; });
  $('#btn-reset').addEventListener('click', () => confirmModal('Semua file, folder, riwayat, dan pengaturan akan dihapus permanen. Lanjut?', () => {
    localStorage.removeItem(DB_KEY);
    location.reload();
  }));

  $('#btn-clearhist').addEventListener('click', () => {
    if (!DB.history.length) { toast('Riwayat sudah kosong'); return; }
    confirmModal('Bersihkan semua riwayat edit?', () => { DB.history = []; persist(); renderHistory(); toast('🧹 Riwayat dibersihkan'); });
  });

  document.addEventListener('click', e => {
    if (e.target.closest('[data-close]')) { closeModal(); closeSheet(); }
    if (e.target.id === 'modal') closeModal();
    if (e.target.id === 'sheet') closeSheet();
  });

  document.addEventListener('pointerdown', e => {
    const btn = e.target.closest('.btn,.nav-btn,.chip,.type-btn,.icon-btn,.ui-card,.swatch,.file-item,.sheet-opt');
    if (!btn || document.body.dataset.ui !== 'material') return;
    const r = btn.getBoundingClientRect();
    const d = Math.max(r.width, r.height) * 1.15;
    const span = document.createElement('span');
    span.className = 'ripple';
    span.style.width = span.style.height = d + 'px';
    span.style.left = (e.clientX - r.left - d / 2) + 'px';
    span.style.top = (e.clientY - r.top - d / 2) + 'px';
    btn.appendChild(span);
    setTimeout(() => span.remove(), 600);
  });

  window.addEventListener('beforeunload', e => {
    const f = getFile(state.currentFile);
    if (f && f.content !== editor.value) { e.preventDefault(); e.returnValue = ''; }
  });
}

function initOnboard() {
  if (DB.onboarded) return;
  $('#onboard').classList.add('open');
  $('#btn-perm').addEventListener('click', async () => {
    $('#perm-status').textContent = '⏳ Meminta izin…';
    const res = await requestStorage();
    $('#perm-status').textContent = '✓ ' + res;
    DB.onboarded = true;
    persist();
    setTimeout(() => $('#onboard').classList.remove('open'), 900);
  });
  $('#btn-skip').addEventListener('click', () => {
    DB.onboarded = true;
    persist();
    $('#onboard').classList.remove('open');
    toast('Izin bisa diaktifkan kapan saja di Pengaturan');
  });
}

function registerSW() {
  if (!('serviceWorker' in navigator)) return;
  if (location.protocol !== 'https:' && !['localhost', '127.0.0.1'].includes(location.hostname)) return;
  navigator.serviceWorker.register('sw.js').catch(() => {});
}

const t0 = Date.now();
window.addEventListener('load', () => {
  if (window.__sverInit) return;
  window.__sverInit = true;
  bindEvents();
  applySettings();
  renderAll();
  initOnboard();
  registerSW();
  const wait = Math.max(0, 1600 - (Date.now() - t0));
  setTimeout(() => {
    const l = $('#loader');
    l.classList.add('done');
    setTimeout(() => l.remove(), 700);
  }, wait);
});
