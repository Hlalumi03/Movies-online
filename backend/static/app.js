const moviesEl = document.getElementById('movies');
const btnSearch = document.getElementById('btnSearch');
const searchInput = document.getElementById('search');
const categorySelect = document.getElementById('category');
const yearInput = document.getElementById('year');

async function loadCategories(){
  const res = await fetch('/api/movies');
  const items = await res.json();
  const cats = new Set();
  items.forEach(m=> m.categories.forEach(c=> cats.add(c.name)));
  cats.forEach(name=>{
    const o = document.createElement('option'); o.value=name; o.textContent=name; categorySelect.appendChild(o);
  });
}

function movieCard(m){
  const div = document.createElement('div');
  div.className = 'bg-white/5 p-4 rounded-lg';
  div.innerHTML = `
    <h2 class="text-xl font-semibold">${m.title} <span class="text-sm text-indigo-200">(${m.year||'—'})</span></h2>
    <p class="mt-2 text-indigo-200">${m.description||''}</p>
    <div class="mt-3 flex items-center justify-between">
      <div class="text-sm text-yellow-300">⭐ ${m.avg_rating.toFixed(1)}</div>
      <div class="text-sm text-indigo-200">${m.categories.map(c=>c.name).join(', ')}</div>
    </div>
  `;
  return div;
}

async function search(){
  const q = encodeURIComponent(searchInput.value.trim());
  const cat = encodeURIComponent(categorySelect.value);
  const year = yearInput.value;
  let url = `/api/movies?per_page=50`;
  if(q) url += `&q=${q}`;
  if(cat) url += `&category=${cat}`;
  if(year) url += `&year=${year}`;
  const res = await fetch(url);
  const items = await res.json();
  moviesEl.innerHTML = '';
  if(items.length===0){
    moviesEl.innerHTML = '<div class="text-center text-indigo-200">No movies found.</div>';
    return;
  }
  items.forEach(m=> moviesEl.appendChild(movieCard(m)));
}

btnSearch.addEventListener('click', search);
searchInput.addEventListener('keydown', (e)=>{ if(e.key==='Enter') search(); });

window.addEventListener('load', async ()=>{ await loadCategories(); await search(); });
