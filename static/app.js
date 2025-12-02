const MAP_CENTER = [39.8283, -98.5795]; // center of USA
const MAP_ZOOM = 4;

let map = L.map('map').setView(MAP_CENTER, MAP_ZOOM);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '© OpenStreetMap'
}).addTo(map);

let markers = L.markerClusterGroup();
map.addLayer(markers);

let allFeatures = null;

async function fetchAnyJson(candidates){
  for (const u of candidates){
    try{
      const res = await fetch(u);
      if (!res.ok) continue;
      const contentType = res.headers.get('content-type') || '';
      if (contentType.includes('application/json') || contentType.includes('application/geo+json') || u.endsWith('.geojson')){
        return await res.json();
      }
      // try parsing regardless
      return await res.json();
    }catch(e){
      // try next
      continue;
    }
  }
  throw new Error('Failed to fetch any candidate JSON');
}

async function fetchPlayers(){
  // If an embedded JSON blob is present in the page (fallback for file://), use it first
  const embedded = document.getElementById('players-data');
  if (embedded){
    try{
      const fc = JSON.parse(embedded.textContent || embedded.innerText || '{}');
      allFeatures = (fc && fc.features) ? fc.features : fc || [];
      renderFeatures(allFeatures);
      return;
    }catch(e){
      console.warn('Failed to parse embedded players JSON, falling back to network fetch', e);
    }
  }

  const candidates = [
    '/players.geojson',
    'players.geojson',
    './players.geojson',
    '../players.geojson'
  ];
  const fc = await fetchAnyJson(candidates);
  allFeatures = (fc && fc.features) ? fc.features : fc || [];
  renderFeatures(allFeatures);
}

function renderFeatures(features){
  markers.clearLayers();
  features.forEach(f => {
    if (!f || !f.geometry || !f.geometry.coordinates) return;
    const [lon, lat] = f.geometry.coordinates;
    if (typeof lat !== 'number' || typeof lon !== 'number') return;
    const p = f.properties || {};
    const marker = L.marker([lat, lon]);
    const html = `<b>${escapeHtml(p.name)}</b><br>${escapeHtml(p.position || '')}<br>${escapeHtml(p.college || '')}<br><i>${escapeHtml(p.team_status || '')}</i>`;
    marker.bindPopup(html);
    markers.addLayer(marker);
  });
  if (features.length) {
    const group = markers.getBounds();
    if (group.isValid()) map.fitBounds(group, {maxZoom: 8});
  }
}

function colorFromString(s){
  // placeholder preserved in case we re-enable coloring later
  return '#3388ff';
}

function escapeHtml(s){
  if (!s) return '';
  return s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
}

let timeout = null;
const searchInput = document.getElementById('search');
if (searchInput){
  searchInput.addEventListener('input', (e) => {
    clearTimeout(timeout);
    timeout = setTimeout(()=>{
      const q = e.target.value.trim().toLowerCase();
      if (!allFeatures) {
        // if data not loaded yet, load then filter
        fetchPlayers().then(()=> filterAndRender(q)).catch(err => {
          console.error(err);
          alert('Failed to load players.geojson. Run generate_players_geojson.py first.');
        });
      } else {
        filterAndRender(q);
      }
    }, 250);
  });
}

function filterAndRender(q){
  if (!q) return renderFeatures(allFeatures);
  const filtered = allFeatures.filter(f => {
    const p = (f.properties || {});
    return ['name','college','position','team_status'].some(k => (p[k]||'').toString().toLowerCase().includes(q));
  });
  renderFeatures(filtered);
}

// initial load
fetchPlayers().catch(err => {
  console.error(err);
  // don't spam alert on missing file; show console notice
});

// Report dropdown behavior
const reportBtn = document.getElementById('reportBtn');
const reportPanel = document.getElementById('reportPanel');
const reportContent = document.getElementById('reportContent');

const chatsBtn = document.getElementById('chatsBtn');
const chatsPanel = document.getElementById('chatsPanel');
const chatsContent = document.getElementById('chatsContent');

async function fetchAnyText(candidates){
  for (const u of candidates){
    try{
      const res = await fetch(u);
      if (!res.ok) continue;
      return await res.text();
    }catch(e){
      continue;
    }
  }
  throw new Error('Failed to fetch any candidate text');
}

async function loadHtmlFile(pathCandidates, el){
  try{
    const txt = await fetchAnyText(pathCandidates);
    el.innerHTML = txt;
  }catch(err){
    el.innerHTML = '<div class="load-error">Failed to load file.</div>';
  }
}

reportBtn.addEventListener('click', ()=>{
  const hidden = reportPanel.hasAttribute('hidden');
  reportPanel.toggleAttribute('hidden', !hidden);
  chatsPanel.setAttribute('hidden', '');
  if (hidden) loadHtmlFile(['/report.html','report.html','/static/report.html','../report.html'], reportContent);
});

chatsBtn.addEventListener('click', ()=>{
  const hidden = chatsPanel.hasAttribute('hidden');
  chatsPanel.toggleAttribute('hidden', !hidden);
  reportPanel.setAttribute('hidden', '');
  if (hidden) loadHtmlFile(['/copilot_chats.html','copilot_chats.html','/static/copilot_chats.html','../copilot_chats.html'], chatsContent);
});

// close panels when clicking outside
document.addEventListener('click', (e)=>{
  const path = e.composedPath ? e.composedPath() : (e.path || []);
  if (!path.some(node => node && node.id === 'reportPanel') && !path.some(node=> node && node.id === 'reportBtn')){
    reportPanel.setAttribute('hidden','');
  }
  if (!path.some(node => node && node.id === 'chatsPanel') && !path.some(node=> node && node.id === 'chatsBtn')){
    chatsPanel.setAttribute('hidden','');
  }
});
