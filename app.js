/* ── DATA ─────────────────────────────────────────────────── */

const CANCERS = [
  { icon: '🧠', name: 'Brain Tumor',      model: 'ResNet50',        input: 'MRI Scan',          acc: '98.2%', color: '#7c3aed' },
  { icon: '🫁', name: 'Lung Cancer',      model: 'EfficientNet-B0', input: 'CT Scan / X-Ray',   acc: '97.4%', color: '#3b9eff' },
  { icon: '🍶', name: 'Breast Cancer',    model: 'VGG19',           input: 'Mammogram',         acc: '96.8%', color: '#ec4899' },
  { icon: '🫀', name: 'Colorectal',       model: 'EfficientNet-B0', input: 'Histopathology',    acc: '97.1%', color: '#06d6a0' },
  { icon: '🧬', name: 'Cervical Cancer',  model: 'DenseNet121',     input: 'Pap Smear Image',   acc: '99.1%', color: '#fbbf24' },
  { icon: '🩺', name: 'Skin Cancer',      model: 'CNN (Custom)',    input: 'Dermoscopy',        acc: '95.6%', color: '#f87171' },
  { icon: '🔬', name: 'Kidney Cancer',    model: 'ResNet50',        input: 'CT Scan',           acc: '96.3%', color: '#38bdf8' },
  { icon: '🫘', name: 'Oral Cancer',      model: 'CNN (Custom)',    input: 'Clinical Image',    acc: '94.8%', color: '#a78bfa' },
  { icon: '💊', name: 'Symptom Analysis', model: 'BERT + LLaMA',   input: 'Text Description',  acc: '93.5%', color: '#34d399' },
];

const ARCH_LAYERS = [
  { num: 'Layer 1', title: 'Presentation Layer', bg: 'rgba(59,158,255,0.07)', items: ['Web Application (Next.js 14)', 'Mobile Interface', 'Patient Dashboard', 'Specialist Dashboard', 'OTP Authentication UI'] },
  { num: 'Layer 2', title: 'Application Layer',  bg: 'rgba(124,58,237,0.07)', items: ['Flask REST API', 'Image Upload Handler', 'Symptom NLP Module', 'Chatbot Interface', 'Secure Messaging'] },
  { num: 'Layer 3', title: 'AI / ML Layer',      bg: 'rgba(6,214,160,0.07)',  items: ['9× Cancer CNN Models', 'Grad-CAM Engine', 'LIME Explainer', 'LLaMA-3.1-70B Chatbot', 'BERT Symptom Classifier'] },
  { num: 'Layer 4', title: 'Security Layer',      bg: 'rgba(251,191,36,0.07)', items: ['AI-based IDS (Scapy)', 'Firewall', 'JWT Session Mgmt', 'AES-256 Encryption', 'RBAC'] },
  { num: 'Layer 5', title: 'Data Layer',          bg: 'rgba(248,113,113,0.07)', items: ['Firebase Encrypted DB', 'Patient Records', 'Model Weights Store', 'Audit Logs', 'DPDPA 2023 Compliance'] },
];

const PHASES = [
  { badge: 'Phase 1', color: '#3b9eff', bg: 'rgba(59,158,255,0.12)', title: 'Data Collection & Preprocessing', desc: 'Download 9 public datasets. Clean, resize, normalise, augment images. Apply 80:10:10 stratified split. Handle class imbalance via weighted samplers.' },
  { badge: 'Phase 2', color: '#7c3aed', bg: 'rgba(124,58,237,0.12)', title: 'Model Development & Training',     desc: 'Train 9 CNN models independently with ImageNet pre-trained weights (transfer learning). Fine-tune classification heads. Evaluate on held-out test sets.' },
  { badge: 'Phase 3', color: '#06d6a0', bg: 'rgba(6,214,160,0.12)',  title: 'XAI Integration',                  desc: 'Register Grad-CAM hooks on final conv layers. Integrate LIME as post-hoc superpixel explainer. Validate heatmap accuracy with clinicians.' },
  { badge: 'Phase 4', color: '#fbbf24', bg: 'rgba(251,191,36,0.12)', title: 'NLP Symptom Module',               desc: 'Fine-tune BERT for symptom-to-cancer text classification. Configure LLaMA-3.1-70B chatbot with cancer-specific prompt engineering and RAG.' },
  { badge: 'Phase 5', color: '#f87171', bg: 'rgba(248,113,113,0.12)', title: 'Web Application Development',     desc: 'Build Next.js 14 frontend with Tailwind CSS. Implement Flask REST backend. Integrate Firebase. Dockerise all microservices. Deploy on cloud.' },
  { badge: 'Phase 6', color: '#a78bfa', bg: 'rgba(167,139,250,0.12)', title: 'Security & Testing',              desc: 'Train AI-IDS on NSL-KDD dataset. Penetration testing. Integration testing for auth, encryption and RBAC. Final deployment and performance benchmarking.' },
];

const TECH_LAYERS = [
  { title: 'Frontend',        desc: 'User interface & experience', chips: ['Next.js 14', 'Tailwind CSS', 'React', 'TypeScript', 'Axios'] },
  { title: 'Backend API',     desc: 'Server-side logic & routing',  chips: ['Python 3.11', 'Flask', 'REST API', 'JWT', 'Firebase Admin SDK'] },
  { title: 'AI / ML',         desc: 'Deep learning models & XAI',   chips: ['PyTorch', 'TensorFlow', 'Keras', 'EfficientNet-B0', 'ResNet50', 'VGG19', 'DenseNet121', 'Grad-CAM', 'LIME'] },
  { title: 'NLP / Chatbot',   desc: 'Language understanding',        chips: ['LLaMA 3.1-70B', 'BERT', 'HuggingFace Transformers', 'Groq API'] },
  { title: 'Database',        desc: 'Storage & encryption',          chips: ['Firebase Firestore', 'Firebase Storage', 'AES-256', 'TLS 1.3'] },
  { title: 'Security',        desc: 'Threat detection & compliance', chips: ['Scapy', 'NSL-KDD IDS', 'OTP (Twilio)', 'DPDPA 2023', 'RBAC'] },
  { title: 'DevOps',          desc: 'Deployment & scalability',      chips: ['Docker', 'Docker Compose', 'GitHub Actions', 'Google Cloud Run', 'Nginx'] },
];

const DATASETS = [
  ['1', 'Brain Tumor',      'Brain Tumor Classification – Kaggle (Bhuvaji et al.)',     '3,264',  'ResNet50'],
  ['2', 'Lung Cancer',      'IQ-OTH/NCCD Lung Cancer CT Dataset – Kaggle',              '1,190',  'EfficientNet-B0'],
  ['3', 'Breast Cancer',    'Breast Ultrasound Images Dataset (BUSI) – Kaggle',          '780',    'VGG19'],
  ['4', 'Colorectal',       'NCT-CRC-HE-100K Histopathology – Zenodo',                  '100,000','EfficientNet-B0'],
  ['5', 'Cervical Cancer',  'Cervical Cancer Risk Classification – Kaggle',              '858',    'DenseNet121'],
  ['6', 'Skin Cancer',      'HAM10000 (ISIC 2018) – Harvard Dataverse',                  '10,015', 'CNN Custom'],
  ['7', 'Kidney Cancer',    'CT Kidney Dataset – Kaggle',                                '12,446', 'ResNet50'],
  ['8', 'Oral Cancer',      'Oral Cancer Image Dataset – Kaggle',                        '1,335',  'CNN Custom'],
  ['9', 'Symptom/NLP',      'Symptom-to-Disease Text Dataset – Kaggle',                  '4,920',  'BERT + LLaMA'],
];

const GANTT = [
  { label: 'Phase 1 – Data Collection',     start: 0, dur: 1.5, color: '#3b9eff' },
  { label: 'Phase 2 – Model Training',       start: 1, dur: 2,   color: '#7c3aed' },
  { label: 'Phase 3 – XAI Integration',      start: 2, dur: 1,   color: '#06d6a0' },
  { label: 'Phase 4 – NLP Module',           start: 2.5, dur: 1.5, color: '#fbbf24' },
  { label: 'Phase 5 – Web App Development',  start: 3, dur: 2,   color: '#f87171' },
  { label: 'Phase 6 – Security & Testing',   start: 4.5, dur: 1.5, color: '#a78bfa' },
];
const TOTAL_MONTHS = 6;
const MONTH_LABELS = ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6'];

const OUTCOMES = [
  { icon: '🎯', title: 'High Diagnostic Accuracy', metric: '94 – 99%', desc: 'All 9 models achieve validation accuracies consistent with published benchmarks, with high sensitivity and specificity across all cancer types.' },
  { icon: '📱', title: 'Dual-Input Coverage',       metric: 'Image + Text', desc: 'Both medical image uploads and plain-text symptom descriptions are supported, extending AI diagnostics to patients without imaging access.' },
  { icon: '🔍', title: 'Explainable Predictions',  metric: 'Grad-CAM + LIME', desc: 'Every image prediction includes a Grad-CAM heatmap and LIME explanation, enabling confident, auditable clinical decisions.' },
  { icon: '🔒', title: 'Secure Data Management',   metric: 'DPDPA 2023', desc: 'All patient data encrypted at rest and in transit. AI-IDS detects and blocks intrusion attempts in real time.' },
  { icon: '⚡', title: 'Fast Inference',            metric: '< 2 seconds', desc: 'AI inference per image targeted under 2 seconds — reducing time from upload to preliminary diagnosis from hours to near-instant.' },
  { icon: '🤖', title: '24/7 AI Chatbot',           metric: 'LLaMA 3.1-70B', desc: 'Patients receive round-the-clock support, cancer-specific information, report analysis, and specialist guidance via the NLP chatbot.' },
];

/* ── RENDER FUNCTIONS ───────────────────────────────────────── */

function renderCancers() {
  const el = document.getElementById('cancerGrid');
  el.innerHTML = CANCERS.map(c => `
    <div class="cancer-card" style="--c:${c.color}">
      <div class="cancer-icon">${c.icon}</div>
      <div class="cancer-name">${c.name}</div>
      <div class="cancer-model">${c.model}</div>
      <div class="cancer-input">${c.input}</div>
      <div class="cancer-acc">${c.acc} accuracy</div>
    </div>`).join('');
}

function renderArch() {
  const el = document.getElementById('archLayers');
  el.innerHTML = ARCH_LAYERS.map(l => `
    <div class="arch-layer" style="background:${l.bg}">
      <span class="arch-layer-num">${l.num}</span>
      <span class="arch-layer-title">${l.title}</span>
      <div class="arch-layer-items">
        ${l.items.map(i => `<span class="arch-tag">${i}</span>`).join('')}
      </div>
    </div>`).join('');
}

function renderPhases() {
  const el = document.getElementById('phasesTimeline');
  el.innerHTML = PHASES.map(p => `
    <div class="phase-row">
      <span class="phase-badge" style="background:${p.bg};color:${p.color}">${p.badge}</span>
      <div><h4>${p.title}</h4><p>${p.desc}</p></div>
    </div>`).join('');
}

function renderTech() {
  const el = document.getElementById('techLayers');
  el.innerHTML = TECH_LAYERS.map(t => `
    <div class="tech-layer-row">
      <div class="tech-layer-head">
        <h4>${t.title}</h4>
        <span class="tech-layer-desc">— ${t.desc}</span>
      </div>
      <div class="tech-chips">
        ${t.chips.map(c => `<span class="chip">${c}</span>`).join('')}
      </div>
    </div>`).join('');
}

function renderDatasets() {
  const tb = document.getElementById('datasetsBody');
  tb.innerHTML = DATASETS.map(r => `
    <tr>
      <td>${r[0]}</td>
      <td>${r[1]}</td>
      <td>${r[2]}</td>
      <td class="ds-count">${r[3]}</td>
      <td class="ds-arch">${r[4]}</td>
    </tr>`).join('');
}

function renderGantt() {
  const wrap = document.getElementById('ganttChart');
  const monthsHtml = `
    <div class="gantt-months">
      ${MONTH_LABELS.map(m => `<div class="gantt-month">${m}</div>`).join('')}
    </div>`;
  const rowsHtml = GANTT.map(g => {
    const leftPct  = (g.start / TOTAL_MONTHS) * 100;
    const widthPct = (g.dur  / TOTAL_MONTHS) * 100;
    const hue = g.color;
    return `
      <div class="gantt-row">
        <div class="gantt-label">${g.label}</div>
        <div class="gantt-bar-wrap">
          <div class="gantt-bar"
               style="margin-left:${leftPct}%;width:${widthPct}%;background:linear-gradient(90deg,${hue}cc,${hue}88)">
            ${g.dur >= 1.5 ? Math.round(g.dur * 4) + ' wks' : ''}
          </div>
        </div>
      </div>`;
  }).join('');
  wrap.innerHTML = monthsHtml + rowsHtml;
}

function renderOutcomes() {
  const el = document.getElementById('outcomesGrid');
  el.innerHTML = OUTCOMES.map(o => `
    <div class="outcome-card">
      <div class="outcome-icon">${o.icon}</div>
      <h3>${o.title}</h3>
      <p>${o.desc}</p>
      <div class="outcome-metric">${o.metric}</div>
    </div>`).join('');
}

/* ── NAV SCROLL EFFECT ──────────────────────────────────────── */
window.addEventListener('scroll', () => {
  document.getElementById('navbar').style.boxShadow =
    window.scrollY > 40 ? '0 4px 30px rgba(0,0,0,0.4)' : 'none';
});

/* ── INTERSECTION OBSERVER (fade-in) ────────────────────────── */
const fadeEls = document.querySelectorAll('section');
const io = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.05, rootMargin: '0px 0px -40px 0px' });
fadeEls.forEach(el => {
  el.classList.add('fade-section');
  io.observe(el);
});

/* ── BOOT ────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  renderCancers();
  renderArch();
  renderPhases();
  renderTech();
  renderDatasets();
  renderGantt();
  renderOutcomes();
  initDragDrop();
});

/* ══════════════════════════════════════════════════════════════
   LIVE DEMO — state & helpers
══════════════════════════════════════════════════════════════ */
const API = 'http://localhost:5000/api';
let chatHistory = [];   // [{role, content}]

function toggleSetup() {
  const p = document.getElementById('setupPanel');
  p.style.display = p.style.display === 'none' ? 'block' : 'none';
}

async function saveKeys() {
  const hf   = document.getElementById('hfToken').value.trim();
  const groq = document.getElementById('groqKey').value.trim();
  const st   = document.getElementById('connStatus');
  st.textContent = '⏳ Testing…';
  try {
    const r = await fetch(`${API}/health`);
    const d = await r.json();
    if (d.status === 'ok') {
      st.innerHTML = '<span style="color:#06d6a0">✓ Backend connected</span>';
      document.getElementById('apiBanner').style.background = 'rgba(6,214,160,0.08)';
    }
  } catch {
    st.innerHTML = '<span style="color:#f87171">✗ Backend not running — start it first (see README)</span>';
  }
}

function switchTab(tab, btn) {
  document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
  document.querySelectorAll('.demo-tab').forEach(b => b.classList.remove('active'));
  document.getElementById(`tab-${tab}`).style.display = 'block';
  btn.classList.add('active');
}

/* ── Image upload ─────────────────────────────────────────── */
function handleImageSelect(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    const prev = document.getElementById('previewImg');
    prev.src = ev.target.result;
    prev.style.display = 'block';
    document.getElementById('uploadPlaceholder').style.display = 'none';
    document.getElementById('analyzeBtn').disabled = false;
    document.getElementById('resultPanel').style.display = 'none';
    document.getElementById('resultPlaceholder').style.display = 'block';
  };
  reader.readAsDataURL(file);
}

function initDragDrop() {
  const zone = document.getElementById('uploadZone');
  if (!zone) return;
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault(); zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) { document.getElementById('imgInput').files = e.dataTransfer.files; handleImageSelect({ target: { files: [file] } }); }
  });
}

async function analyzeImage() {
  const input      = document.getElementById('imgInput');
  const cancerType = document.getElementById('cancerTypeSelect').value;
  const btn        = document.getElementById('analyzeBtn');
  const btnText    = document.getElementById('analyzeBtnText');
  if (!input.files[0]) return;

  btn.disabled = true;
  btnText.innerHTML = 'Analysing… <span class="loading-spin"></span>';

  const form = new FormData();
  form.append('image', input.files[0]);
  form.append('cancer_type', cancerType);

  try {
    const res  = await fetch(`${API}/predict`, { method: 'POST', body: form });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    renderResults(data);
  } catch (err) {
    alert('Error: ' + err.message + '\n\nMake sure the Flask backend is running:\n  cd backend && python app.py');
  } finally {
    btn.disabled = false;
    btnText.textContent = 'Analyse Image';
  }
}

function renderResults(data) {
  document.getElementById('resultPlaceholder').style.display = 'none';
  const panel = document.getElementById('resultPanel');
  panel.style.display = 'flex';

  // Risk badge
  const badge = document.getElementById('riskBadge');
  badge.textContent = data.risk_level === 'HIGH' ? '⚠ HIGH RISK' : '✓ LOW RISK';
  badge.className = `risk-badge ${data.risk_level}`;

  document.getElementById('topLabel').textContent = data.top_label.replace(/_/g, ' ');
  document.getElementById('topScore').textContent = `${data.top_score}%`;

  // Confidence bars
  const bars = document.getElementById('confBars');
  bars.innerHTML = data.predictions.map(p => `
    <div class="conf-row">
      <span class="conf-name">${p.label.replace(/_/g,' ')}</span>
      <div class="conf-bar-wrap">
        <div class="conf-bar-fill" style="width:${p.score}%"></div>
      </div>
      <span class="conf-pct">${p.score}%</span>
    </div>`).join('');

  // Grad-CAM
  if (data.gradcam) {
    document.getElementById('gradcamImg').src = `data:image/png;base64,${data.gradcam}`;
    document.getElementById('gradcamBlock').style.display = 'flex';
  }
  document.getElementById('modelTag').textContent = `Model: ${data.model_used}`;
}

/* ── Symptom Checker ─────────────────────────────────────── */
async function checkSymptoms() {
  const txt     = document.getElementById('symptomsInput').value.trim();
  const btnText = document.getElementById('symptomBtnText');
  if (!txt) return alert('Please describe your symptoms first.');

  btnText.innerHTML = 'Analysing… <span class="loading-spin"></span>';

  try {
    const res  = await fetch(`${API}/symptom-check`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symptoms: txt })
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    renderSymptomResult(data);
  } catch (err) {
    alert('Error: ' + err.message);
  } finally {
    btnText.textContent = 'Analyse Symptoms';
  }
}

function renderSymptomResult(data) {
  const el = document.getElementById('symptomResult');
  el.style.display = 'block';

  const risks = (data.cancer_risks || []).map(r => `
    <div class="sym-risk-card">
      <span class="sym-risk-level ${r.risk_level}">${r.risk_level}</span>
      <span class="sym-cancer-name">${r.cancer_type}</span>
      <span class="sym-reason">${r.reason || ''}</span>
    </div>`).join('');

  const urgClass = data.urgency || 'Routine';
  el.innerHTML = `
    <h4 style="color:#fff;margin-bottom:0.5rem">Symptom Analysis Results</h4>
    <div class="sym-risk-cards">${risks}</div>
    <div>
      <span class="sym-urgency ${urgClass}">Urgency: ${urgClass}</span>
    </div>
    <p class="sym-recommendation">${data.recommendation || ''}</p>
    <p class="sym-disclaimer">⚠️ ${data.disclaimer || 'This is not a medical diagnosis. Consult a qualified doctor.'}</p>`;
}

/* ── Chatbot ─────────────────────────────────────────────── */
function toggleChat() {
  const panel = document.getElementById('chatPanel');
  const badge = document.getElementById('chatBadge');
  panel.classList.toggle('open');
  badge.style.display = 'none';
  if (panel.classList.contains('open')) {
    setTimeout(() => document.getElementById('chatInput').focus(), 300);
  }
}

async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text  = input.value.trim();
  if (!text) return;
  input.value = '';

  appendMsg('user', text);
  chatHistory.push({ role: 'user', content: text });

  const typingEl = appendMsg('bot', '●●●', true);

  try {
    const res  = await fetch(`${API}/chat`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: chatHistory })
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    typingEl.remove();
    appendMsg('bot', data.reply);
    chatHistory.push({ role: 'assistant', content: data.reply });
  } catch (err) {
    typingEl.remove();
    appendMsg('bot', `⚠️ Error: ${err.message}\n\nMake sure the Flask backend is running and your GROQ_API_KEY is set in backend/.env`);
  }
}

function appendMsg(role, text, isTyping = false) {
  const msgs = document.getElementById('chatMessages');
  const div  = document.createElement('div');
  div.className = `chat-msg ${role}${isTyping ? ' msg-typing' : ''}`;
  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.textContent = isTyping ? '' : text;
  div.appendChild(bubble);
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return div;
}
