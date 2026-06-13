/* ═══════════════════════════════════════════════════════
   KALA VASTRA — Frontend App
   Connects to Flask backend at http://localhost:5000/api
   Falls back to local data if API is offline.
═══════════════════════════════════════════════════════ */

const API = 'http://localhost:5000/api';

// Unique session ID for server-side cart
const SESSION_ID = (() => {
  let id = localStorage.getItem('kv_session');
  if (!id) { id = 'kv_' + Date.now() + '_' + Math.random().toString(36).slice(2); localStorage.setItem('kv_session', id); }
  return id;
})();

// ── Fallback product data (used when API is offline) ──
const FALLBACK_PRODUCTS = [
  { id:1, name:'Peacock Hand-Painted Silk Saree', category:'saree', price:4800,
    image_url:'https://i.pinimg.com/736x/2d/5f/1d/2d5f1d1c2cee71cd1d6174f3c1b73dad.jpg',
    description:'Inspired by Rajasthan, this hand-painted silk saree is a wearable canvas. Every motif is hand-drawn with fabric-safe pigments on pure Kanjivaram silk.',
    tags:['100% Silk','Hand-painted','Custom Colors','Includes Blouse Piece'], badge:'Bestseller' },
  { id:2, name:'Banarasi Floral Saree', category:'saree', price:3200,
    image_url:'https://i.pinimg.com/736x/2d/5f/1d/2d5f1d1c2cee71cd1d6174f3c1b73dad.jpg',
    description:'A timeless Banarasi silk saree with intricate floral motifs in gold zari. Perfect for weddings.',
    tags:['Silk','Gold Zari','Bridal'], badge:null },
  { id:3, name:'Chiffon Rose Garden Saree', category:'saree', price:2800,
    image_url:'https://i.pinimg.com/736x/2d/5f/1d/2d5f1d1c2cee71cd1d6174f3c1b73dad.jpg',
    description:'Delicate rose motifs hand-painted on soft chiffon. Lightweight and perfect for summer festivals.',
    tags:['Chiffon','Hand-painted','Summer Wear'], badge:'New' },
  { id:4, name:'Painted Anarkali Kurti', category:'kurti', price:1850,
    image_url:'https://i.pinimg.com/736x/fa/88/cb/fa88cb4a8906246b645f3365f508c82a.jpg',
    description:'Hand-painted floral patterns on soft georgette in a graceful Anarkali silhouette.',
    tags:['Georgette','Hand-painted','Anarkali'], badge:null },
  { id:5, name:'Straight Cotton Kurti', category:'kurti', price:1200,
    image_url:'https://i.pinimg.com/736x/fa/88/cb/fa88cb4a8906246b645f3365f508c82a.jpg',
    description:'Comfortable everyday cotton kurti with block-print border. A daily-wear essential.',
    tags:['Cotton','Block Print','Everyday Wear'], badge:null },
  { id:6, name:'A-Line Embroidered Kurti', category:'kurti', price:1650,
    image_url:'https://i.pinimg.com/736x/fa/88/cb/fa88cb4a8906246b645f3365f508c82a.jpg',
    description:'Subtle embroidery meets contemporary A-line silhouette. Pairs well with palazzo or jeans.',
    tags:['Embroidered','A-Line','Semi-Formal'], badge:'Trending' },
  { id:7, name:'Lotus Bloom Shirt', category:'mens_shirt', price:2100,
    image_url:'https://i.pinimg.com/736x/1b/13/4f/1b134fbdd190ab80f181114be41a0f63.jpg',
    description:'Delicate lotus motifs hand-painted on pure cotton. A wearable canvas of Indian art.',
    tags:['Pure Cotton','Hand-painted','Lotus Motif'], badge:null },
  { id:8, name:'Krishna Art Shirt', category:'mens_shirt', price:2500,
    image_url:'https://i.pinimg.com/736x/1b/13/4f/1b134fbdd190ab80f181114be41a0f63.jpg',
    description:'Stunning hand-painted Krishna artwork on premium fabric. One-of-a-kind artisan masterpiece.',
    tags:['Premium Fabric','Hand-painted','Krishna Art'], badge:'Artisan' },
  { id:9, name:'Tiger Spirit Shirt', category:'mens_shirt', price:1800,
    image_url:'https://i.pinimg.com/736x/1b/13/4f/1b134fbdd190ab80f181114be41a0f63.jpg',
    description:'Bold tiger motif hand-painted on black premium cotton. Raw power meets artisan craft.',
    tags:['Black Cotton','Hand-painted','Tiger Motif'], badge:null },
];

// ── State ──────────────────────────────────────────────
let cart = JSON.parse(localStorage.getItem('kv_cart') || '[]');
let allWomensProducts = [];
let currentFilter = 'all';
let apiOnline = false;

// ══════════════════════════════════════════════════════
// PRODUCTS
// ══════════════════════════════════════════════════════

async function loadWomensProducts(category = 'all') {
  const grid = document.getElementById('women-grid');
  grid.innerHTML = `<div class="loading-placeholder"><div class="spinner"></div><p>Loading…</p></div>`;

  try {
    const url = category === 'all'
      ? `${API}/products?category=all`
      : `${API}/products?category=${category}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('API error');
    const json = await res.json();
    apiOnline = true;
    const women = json.data.filter(p => p.category === 'saree' || p.category === 'kurti');
    allWomensProducts = women;
    renderWomensGrid(women);
  } catch {
    apiOnline = false;
    showApiNotice(grid);
    const women = FALLBACK_PRODUCTS.filter(p => p.category === 'saree' || p.category === 'kurti');
    allWomensProducts = category === 'all' ? women : women.filter(p => p.category === category);
    renderWomensGrid(allWomensProducts);
  }
}

function showApiNotice(container) {
  const notice = document.createElement('div');
  notice.className = 'api-notice';
  notice.style.gridColumn = '1/-1';
  notice.textContent = '⚠️ Running in offline mode. Start the backend (python app.py) to sync with database.';
  container.prepend(notice);
}

function renderWomensGrid(products) {
  const grid = document.getElementById('women-grid');
  if (!products.length) {
    grid.innerHTML = '<p class="no-results">No products found.</p>';
    return;
  }
  grid.innerHTML = products.map((p, i) => `
    <div class="product-card" data-cat="${p.category}" onclick="openModal(${i}, 'womens')">
      <div class="product-img">
        <img src="${p.image_url}" alt="${p.name}" loading="lazy"/>
        <button class="wishlist" onclick="toggleWish(event,this)" aria-label="Wishlist">♡</button>
        <div class="product-quick">Quick View</div>
      </div>
      <div class="product-label">${p.category === 'saree' ? 'Sarees' : 'Kurtis'}</div>
      <div class="product-name">${p.name}</div>
      <div class="product-price">
        ₹${p.price.toLocaleString('en-IN')}
        <span class="custom">Custom</span>
      </div>
      <button class="add-btn" onclick="event.stopPropagation();addToCart(${p.id}, '${p.name}', ${p.price}, '${p.image_url}')">+ Add to Bag</button>
    </div>
  `).join('');
}

async function loadMensProducts() {
  const grid = document.getElementById('mens-grid');
  let mens = [];

  try {
    const res = await fetch(`${API}/products?category=mens_shirt`);
    if (!res.ok) throw new Error();
    const json = await res.json();
    mens = json.data;
  } catch {
    mens = FALLBACK_PRODUCTS.filter(p => p.category === 'mens_shirt');
  }

  if (!mens.length) { grid.innerHTML = '<p class="no-results" style="color:#fff;">No products found.</p>'; return; }

  const [left, center, right] = [mens[0], mens[1] || mens[0], mens[2] || mens[0]];

  grid.innerHTML = [
    cardMens(left, 0),
    `<div class="mens-card mens-center">${mensInner(center, 1)}</div>`,
    cardMens(right, 2)
  ].join('');
}

function cardMens(p, i) {
  return `<div class="mens-card">${mensInner(p, i)}</div>`;
}

function mensInner(p, i) {
  return `
    <img src="${p.image_url}" alt="${p.name}" loading="lazy"/>
    <div class="mens-card-body">
      <h3>${p.name}</h3>
      <p>${p.description ? p.description.slice(0,90) + '…' : ''}</p>
      <div class="mens-price-row">
        <div class="price">₹${p.price.toLocaleString('en-IN')}</div>
        <button class="add-btn-dark" onclick="addToCart(${p.id},'${p.name}',${p.price},'${p.image_url}')">+ Bag</button>
      </div>
    </div>
  `;
}

// Filter tabs
function filterProducts(cat) {
  currentFilter = cat;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.toggle('active', b.dataset.filter === cat));
  const filtered = cat === 'all' ? allWomensProducts : allWomensProducts.filter(p => p.category === cat);
  renderWomensGrid(filtered);
}

function filterAndScroll(cat) {
  filterProducts(cat);
  document.getElementById('womens').scrollIntoView({ behavior: 'smooth' });
}

function handleSearch(q) {
  const lower = q.toLowerCase();
  const filtered = allWomensProducts.filter(p =>
    (currentFilter === 'all' || p.category === currentFilter) &&
    (p.name.toLowerCase().includes(lower) || (p.description || '').toLowerCase().includes(lower))
  );
  renderWomensGrid(filtered);
}

// ══════════════════════════════════════════════════════
// CART
// ══════════════════════════════════════════════════════

function addToCart(id, name, price, img) {
  const existing = cart.find(i => i.id === id);
  if (existing) { existing.qty = (existing.qty || 1) + 1; }
  else { cart.push({ id, name, price, img: img || '', qty: 1 }); }
  saveCart();
  renderCart();
  updateBadge();
  showToast(`Added "${name}" to bag!`);
  if (!document.getElementById('cart-sidebar').classList.contains('open')) toggleCart();

  // Also tell server if online
  if (apiOnline) {
    fetch(`${API}/cart`, { method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ session_id: SESSION_ID, product_id: id, quantity: 1 }) }).catch(() => {});
  }
}

function addToCartById(id) {
  const p = FALLBACK_PRODUCTS.find(x => x.id === id) || allWomensProducts.find(x => x.id === id);
  if (p) addToCart(p.id, p.name, p.price, p.image_url);
}

function removeFromCart(id) {
  cart = cart.filter(i => i.id !== id);
  saveCart(); renderCart(); updateBadge();
}

function renderCart() {
  const el = document.getElementById('cart-items');
  const total = cart.reduce((s, i) => s + i.price * (i.qty || 1), 0);
  document.getElementById('cart-total').textContent = '₹' + total.toLocaleString('en-IN');
  document.getElementById('cart-count').textContent = cart.reduce((s, i) => s + (i.qty || 1), 0);

  if (!cart.length) { el.innerHTML = '<p class="cart-empty">Your bag is empty.</p>'; return; }

  el.innerHTML = cart.map(item => `
    <div class="cart-item">
      <img class="cart-item-img" src="${item.img || 'https://i.pinimg.com/736x/2d/5f/1d/2d5f1d1c2cee71cd1d6174f3c1b73dad.jpg'}" alt="${item.name}"/>
      <div class="cart-item-info">
        <h4>${item.name}</h4>
        <div class="cart-item-price">₹${item.price.toLocaleString('en-IN')} × ${item.qty || 1}</div>
        <button class="remove-item" onclick="removeFromCart(${item.id})">Remove</button>
      </div>
    </div>
  `).join('');

  // Build WhatsApp message
  const lines = cart.map(i => `• ${i.name} (₹${i.price.toLocaleString('en-IN')} × ${i.qty||1})`).join('%0A');
  const msg = `Hi Kala Vastra! I want to order:%0A${lines}%0ATotal: ₹${total.toLocaleString('en-IN')}`;
  document.getElementById('whatsapp-checkout').href = `https://wa.me/919876543210?text=${msg}`;
}

function saveCart() { localStorage.setItem('kv_cart', JSON.stringify(cart)); }
function updateBadge() {
  const n = cart.reduce((s, i) => s + (i.qty || 1), 0);
  document.getElementById('nav-badge').textContent = n;
}

function toggleCart() {
  document.getElementById('cart-sidebar').classList.toggle('open');
  document.getElementById('cart-overlay').classList.toggle('open');
}

// ══════════════════════════════════════════════════════
// MODAL
// ══════════════════════════════════════════════════════

function openModal(index, section) {
  const products = section === 'womens' ? allWomensProducts : FALLBACK_PRODUCTS.filter(p => p.category === 'mens_shirt');
  const p = products[index];
  if (!p) return;

  document.getElementById('modal-img').src = p.image_url;
  document.getElementById('modal-img').alt = p.name;
  document.getElementById('modal-label').textContent = p.category === 'saree' ? 'Sarees' : p.category === 'kurti' ? 'Kurtis' : "Men's Shirts";
  document.getElementById('modal-name').textContent = p.name;
  document.getElementById('modal-price').textContent = '₹' + p.price.toLocaleString('en-IN');
  document.getElementById('modal-desc').textContent = p.description || '';
  document.getElementById('modal-tags').innerHTML = (p.tags || []).map(t => `<span class="tag">${t}</span>`).join('');
  document.getElementById('modal-add-btn').onclick = () => { addToCart(p.id, p.name, p.price, p.image_url); closeModal(); };

  document.getElementById('product-modal').classList.add('open');
  document.getElementById('modal-overlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('product-modal').classList.remove('open');
  document.getElementById('modal-overlay').classList.remove('open');
  document.body.style.overflow = '';
}

// ══════════════════════════════════════════════════════
// FORMS
// ══════════════════════════════════════════════════════

async function submitOrder(e) {
  e.preventDefault();
  const btn = document.getElementById('form-submit-btn');
  btn.disabled = true; btn.textContent = 'Sending…';

  const payload = {
    name: document.getElementById('f-name').value,
    phone: document.getElementById('f-phone').value,
    email: document.getElementById('f-email').value,
    product_type: document.getElementById('f-type').value,
    budget: document.getElementById('f-budget').value,
    description: document.getElementById('f-desc').value,
  };

  try {
    const res = await fetch(`${API}/orders`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    const json = await res.json();
    showSuccess(json.message || 'Request sent!');
  } catch {
    // Offline fallback — show success anyway (WhatsApp link available)
    showSuccess('Request saved! Since backend is offline, please also WhatsApp us directly.');
  }

  e.target.reset();
  btn.disabled = false; btn.textContent = 'Send My Request ✦';
}

function showSuccess(msg) {
  const el = document.getElementById('form-success');
  el.textContent = '✅ ' + msg;
  el.style.display = 'block';
  setTimeout(() => { el.style.display = 'none'; }, 6000);
}

async function subscribeNewsletter(e) {
  e.preventDefault();
  const email = document.getElementById('nl-email').value;
  try {
    const res = await fetch(`${API}/subscribe`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ email }) });
    const json = await res.json();
    showToast(json.message || 'Subscribed!');
  } catch {
    showToast('Subscribed ' + email + ' ✓');
  }
  e.target.reset();
}

// ══════════════════════════════════════════════════════
// NAV
// ══════════════════════════════════════════════════════

function toggleNav() {
  document.getElementById('nav-links').classList.toggle('open');
  document.getElementById('nav-overlay').classList.toggle('open');
}
function closeNav() {
  document.getElementById('nav-links').classList.remove('open');
  document.getElementById('nav-overlay').classList.remove('open');
}

// Shrink nav on scroll
window.addEventListener('scroll', () => {
  document.getElementById('main-nav').classList.toggle('scrolled', window.scrollY > 60);
});

// ══════════════════════════════════════════════════════
// UTILS
// ══════════════════════════════════════════════════════

function toggleWish(e, btn) {
  e.stopPropagation();
  btn.classList.toggle('active');
  btn.textContent = btn.classList.contains('active') ? '♥' : '♡';
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

// Size buttons
document.addEventListener('click', e => {
  if (e.target.classList.contains('size-btn')) {
    e.target.closest('.size-btns')?.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');
  }
});

// Escape key
window.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeModal(); }
});

// ══════════════════════════════════════════════════════
// INIT
// ══════════════════════════════════════════════════════

window.addEventListener('DOMContentLoaded', () => {
  renderCart();
  updateBadge();
  loadWomensProducts();
  loadMensProducts();
});
