const API='http://localhost:5000/api';
let allProducts=[],allOrders=[],currentPage='dashboard';

// ── Toast ─────────────────────────────────────────────
function toast(msg,type='ok'){
  const t=document.getElementById('toast');
  t.textContent=msg;t.className='toast show';
  t.style.background=type==='err'?'#c0392b':type==='warn'?'#e67e22':'#1A0E05';
  setTimeout(()=>t.classList.remove('show'),3500);
}

// ── Page nav ──────────────────────────────────────────
function goPage(name){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-i').forEach(n=>n.classList.remove('active'));
  document.getElementById('page-'+name).classList.add('active');
  document.getElementById('nav-'+name).classList.add('active');
  document.getElementById('topbar-title').textContent=
    {dashboard:'Dashboard',products:'Products',inventory:'Inventory',
     orders:'Orders',coupons:'Coupons',subscribers:'Subscribers',analytics:'Analytics'}[name]||name;
  currentPage=name;
  const loaders={dashboard:loadDashboard,products:loadProducts,inventory:loadInventory,
                 orders:loadOrders,coupons:loadCoupons,subscribers:loadSubscribers,analytics:loadAnalytics};
  loaders[name]&&loaders[name]();
}

// ── API helpers ───────────────────────────────────────
async function api(path,method='GET',body=null){
  try{
    const r=await fetch(API+path,{method,headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):null});
    return await r.json();
  }catch{return{success:false,message:'Backend offline'};}
}

function loadingHTML(id){document.getElementById(id).innerHTML='<div class="loading"><div class="spinner"></div><p>Loading…</p></div>';}

// ═════════════════════════════════════════════════════
// DASHBOARD
// ═════════════════════════════════════════════════════
async function loadDashboard(){
  const j=await api('/analytics');
  if(!j.success){document.getElementById('stat-grid').innerHTML='<div class="empty">Backend offline. Run: python gateway.py</div>';return;}
  const d=j.data;
  document.getElementById('stat-grid').innerHTML=`
    <div class="sc good"><div class="s-top"><span class="s-icon">💰</span></div><div class="s-val">₹${(d.revenue||0).toLocaleString('en-IN')}</div><div class="s-lbl">Total Revenue</div></div>
    <div class="sc"><div class="s-top"><span class="s-icon">🛍️</span></div><div class="s-val">${d.total_orders}</div><div class="s-lbl">Total Orders</div></div>
    <div class="sc warn"><div class="s-top"><span class="s-icon">⏳</span></div><div class="s-val">${d.pending}</div><div class="s-lbl">Pending</div></div>
    <div class="sc good"><div class="s-top"><span class="s-icon">✅</span></div><div class="s-val">${d.delivered}</div><div class="s-lbl">Delivered</div></div>
    <div class="sc"><div class="s-top"><span class="s-icon">👗</span></div><div class="s-val">${d.total_products}</div><div class="s-lbl">Products</div></div>
    <div class="sc ${d.low_stock>0?'danger':''}"><div class="s-top"><span class="s-icon">⚠️</span></div><div class="s-val">${d.low_stock}</div><div class="s-lbl">Low Stock</div></div>
    <div class="sc"><div class="s-top"><span class="s-icon">📧</span></div><div class="s-val">${d.subscribers}</div><div class="s-lbl">Subscribers</div></div>
    <div class="sc"><div class="s-top"><span class="s-icon">⭐</span></div><div class="s-val">${d.avg_rating}</div><div class="s-lbl">Avg Rating</div></div>
  `;
  // Recent orders
  const rEl=document.getElementById('recent-orders');
  if(!d.recent_orders?.length){rEl.innerHTML='<div class="empty">No orders yet</div>';return;}
  rEl.innerHTML=d.recent_orders.map(o=>`
    <div class="order-row">
      <div><strong>#${o.id}</strong> ${o.name}<br><small style="color:var(--muted)">${o.phone} · ${o.product_type||'Custom'}</small></div>
      <div style="text-align:right"><span class="badge b-${o.status}">${o.status}</span><br><small style="color:var(--muted)">${new Date(o.created_at).toLocaleDateString('en-IN')}</small></div>
    </div>`).join('');
  // Low stock alert
  if(d.low_stock_products?.length){
    document.getElementById('low-stock-alert').innerHTML=`<div class="alert-banner">⚠️ ${d.low_stock} product(s) have low stock: ${d.low_stock_products.map(p=>`<strong>${p.name} (${p.stock})</strong>`).join(', ')}</div>`;
  }
}

// ═════════════════════════════════════════════════════
// PRODUCTS
// ═════════════════════════════════════════════════════
async function loadProducts(search=''){
  loadingHTML('products-body');
  const j=await api('/products'+(search?`?search=${search}`:''));
  allProducts=j.data||[];
  renderProductsTable(allProducts);
}

function renderProductsTable(prods){
  const el=document.getElementById('products-body');
  if(!prods.length){el.innerHTML='<div class="empty">No products found.</div>';return;}
  el.innerHTML=`<div class="tbl-wrap"><table>
    <thead><tr><th>IMG</th><th>Name</th><th>Category</th><th>Price</th><th>Stock</th><th>Badge</th><th>Actions</th></tr></thead>
    <tbody>${prods.map(p=>`
      <tr>
        <td><img class="p-img" src="${p.image_url}" alt="${p.name}"/></td>
        <td><strong>${p.name}</strong></td>
        <td><span class="badge b-${p.category}">${p.category.replace('_',' ')}</span></td>
        <td>₹${(p.price||0).toLocaleString('en-IN')}</td>
        <td class="${p.stock<=0?'stock-out':p.stock<=10?'stock-low':'stock-ok'}">${p.stock??'—'}</td>
        <td>${p.badge?`<span class="badge b-confirmed">${p.badge}</span>`:'—'}</td>
        <td style="display:flex;gap:6px;flex-wrap:wrap">
          <button class="btn btn-outline btn-sm" onclick="openEditModal(${p.id})">✏️ Edit</button>
          <button class="btn btn-red btn-sm" onclick="deleteProduct(${p.id},'${p.name}')">🗑️</button>
        </td>
      </tr>`).join('')}
    </tbody></table></div>`;
}

function openAddModal(){
  document.getElementById('prod-modal-title').textContent='Add New Product';
  document.getElementById('prod-form').reset();
  document.getElementById('prod-id').value='';
  document.getElementById('prod-modal').classList.add('open');
}

async function openEditModal(id){
  const p=allProducts.find(x=>x.id===id);if(!p)return;
  document.getElementById('prod-modal-title').textContent='Edit Product';
  document.getElementById('prod-id').value=p.id;
  document.getElementById('prod-name').value=p.name;
  document.getElementById('prod-cat').value=p.category;
  document.getElementById('prod-price').value=p.price;
  document.getElementById('prod-stock').value=p.stock??50;
  document.getElementById('prod-img').value=p.image_url;
  document.getElementById('prod-badge').value=p.badge||'';
  document.getElementById('prod-desc').value=p.description||'';
  document.getElementById('prod-modal').classList.add('open');
}

async function saveProduct(){
  const id=document.getElementById('prod-id').value;
  const body={
    name:document.getElementById('prod-name').value,
    category:document.getElementById('prod-cat').value,
    price:parseInt(document.getElementById('prod-price').value),
    stock:parseInt(document.getElementById('prod-stock').value),
    image_url:document.getElementById('prod-img').value,
    badge:document.getElementById('prod-badge').value||null,
    description:document.getElementById('prod-desc').value,
  };
  const j=id?await api(`/products/${id}`,'PUT',body):await api('/products','POST',body);
  toast(j.message||'Saved',j.success?'ok':'err');
  if(j.success){closeModal('prod-modal');loadProducts();}
}

async function deleteProduct(id,name){
  if(!confirm(`Remove "${name}"?`))return;
  const j=await api(`/products/${id}`,'DELETE');
  toast(j.message,j.success?'ok':'err');
  if(j.success)loadProducts();
}

// ═════════════════════════════════════════════════════
// INVENTORY
// ═════════════════════════════════════════════════════
async function loadInventory(){
  loadingHTML('inventory-body');
  const j=await api('/products');
  allProducts=j.data||[];
  const el=document.getElementById('inventory-body');
  if(!allProducts.length){el.innerHTML='<div class="empty">No products.</div>';return;}
  el.innerHTML=`<div class="tbl-wrap"><table>
    <thead><tr><th>Name</th><th>Category</th><th>Current Stock</th><th>Status</th><th>Add Stock</th><th>Set Stock</th></tr></thead>
    <tbody>${allProducts.map(p=>`
      <tr>
        <td><strong>${p.name}</strong></td>
        <td><span class="badge b-${p.category}">${p.category.replace('_',' ')}</span></td>
        <td class="${p.stock<=0?'stock-out':p.stock<=10?'stock-low':'stock-ok'} ">${p.stock??0}</td>
        <td><span class="badge ${p.stock<=0?'b-cancelled':p.stock<=10?'b-pending':'b-delivered'}">${p.stock<=0?'Out of Stock':p.stock<=10?'Low Stock':'In Stock'}</span></td>
        <td><div style="display:flex;gap:6px;align-items:center">
          <input class="inline-stock" id="add-${p.id}" type="number" min="1" value="10" placeholder="Qty"/>
          <button class="btn btn-green btn-sm" onclick="updateStock(${p.id},'add','add-${p.id}')">+ Add</button>
        </div></td>
        <td><div style="display:flex;gap:6px;align-items:center">
          <input class="inline-stock" id="set-${p.id}" type="number" min="0" value="${p.stock??0}"/>
          <button class="btn btn-gold btn-sm" onclick="updateStock(${p.id},'set','set-${p.id}')">Set</button>
        </div></td>
      </tr>`).join('')}
    </tbody></table></div>`;
}

async function updateStock(id,action,inputId){
  const qty=parseInt(document.getElementById(inputId).value)||0;
  const j=await api(`/products/${id}/stock`,'PATCH',{action,quantity:qty});
  toast(j.message+` → Stock: ${j.stock}`,j.success?'ok':'err');
  if(j.success)loadInventory();
}

// ═════════════════════════════════════════════════════
// ORDERS
// ═════════════════════════════════════════════════════
async function loadOrders(status=''){
  loadingHTML('orders-body');
  const j=await api('/orders'+(status?`?status=${status}`:''));
  allOrders=j.data||[];
  renderOrdersTable(allOrders);
}

function renderOrdersTable(orders){
  const el=document.getElementById('orders-body');
  if(!orders.length){el.innerHTML='<div class="empty">No orders found.</div>';return;}
  el.innerHTML=`<div class="tbl-wrap"><table>
    <thead><tr><th>#</th><th>Customer</th><th>Phone</th><th>Product</th><th>Budget</th><th>Description</th><th>Status</th><th>Date</th><th>Update</th></tr></thead>
    <tbody>${orders.map(o=>`
      <tr>
        <td><strong>#${o.id}</strong></td>
        <td>${o.name}</td>
        <td><a href="https://wa.me/91${o.phone.replace(/\D/g,'')}" target="_blank" style="color:var(--gold)">${o.phone}</a></td>
        <td>${o.product_type||'—'}</td>
        <td>${o.budget||'—'}</td>
        <td style="max-width:160px;font-size:.78rem;color:var(--muted)">${(o.description||'—').slice(0,60)}</td>
        <td><span class="badge b-${o.status}">${o.status}</span></td>
        <td style="white-space:nowrap">${new Date(o.created_at).toLocaleDateString('en-IN')}</td>
        <td>
          <select class="status-sel" onchange="updateOrder(${o.id},this.value)">
            ${['pending','confirmed','in_progress','dispatched','delivered','cancelled']
              .map(s=>`<option value="${s}"${s===o.status?' selected':''}>${s}</option>`).join('')}
          </select>
        </td>
      </tr>`).join('')}
    </tbody></table></div>`;
}

async function updateOrder(id,status){
  const j=await api(`/orders/${id}/status`,'PATCH',{status});
  toast(j.message,j.success?'ok':'err');
}

function filterOrders(){
  const s=document.getElementById('order-status-filter').value;
  const q=document.getElementById('order-search').value.toLowerCase();
  let filtered=allOrders;
  if(s)filtered=filtered.filter(o=>o.status===s);
  if(q)filtered=filtered.filter(o=>o.name.toLowerCase().includes(q)||o.phone.includes(q));
  renderOrdersTable(filtered);
}

// ═════════════════════════════════════════════════════
// COUPONS
// ═════════════════════════════════════════════════════
async function loadCoupons(){
  loadingHTML('coupons-body');
  const j=await api('/coupons');
  const data=j.data||[];
  const el=document.getElementById('coupons-body');
  if(!data.length){el.innerHTML='<div class="empty">No coupons yet. Create one above!</div>';return;}
  el.innerHTML=`<div class="tbl-wrap"><table>
    <thead><tr><th>Code</th><th>Discount</th><th>Min Order</th><th>Uses</th><th>Max Uses</th><th>Status</th><th>Actions</th></tr></thead>
    <tbody>${data.map(c=>`
      <tr>
        <td><strong style="letter-spacing:.1em;font-size:1rem">${c.code}</strong></td>
        <td><span class="badge b-confirmed">${c.discount_pct}% OFF</span></td>
        <td>₹${(c.min_order||0).toLocaleString('en-IN')}</td>
        <td>${c.uses}</td>
        <td>${c.max_uses}</td>
        <td><span class="badge ${c.is_active?'b-active':'b-inactive'}">${c.is_active?'Active':'Inactive'}</span></td>
        <td style="display:flex;gap:6px">
          <button class="btn btn-outline btn-sm" onclick="toggleCoupon(${c.id},${c.is_active?0:1})">${c.is_active?'Disable':'Enable'}</button>
          <button class="btn btn-red btn-sm" onclick="deleteCoupon(${c.id},'${c.code}')">🗑️</button>
        </td>
      </tr>`).join('')}
    </tbody></table></div>`;
}

async function addCoupon(){
  const body={
    code:document.getElementById('cp-code').value.trim(),
    discount_pct:parseInt(document.getElementById('cp-disc').value),
    min_order:parseInt(document.getElementById('cp-min').value)||0,
    max_uses:parseInt(document.getElementById('cp-max').value)||100,
  };
  if(!body.code||!body.discount_pct){toast('Code and discount required','err');return;}
  const j=await api('/coupons','POST',body);
  toast(j.message,j.success?'ok':'err');
  if(j.success){document.getElementById('coupon-form').reset();loadCoupons();}
}

async function toggleCoupon(id,active){
  const j=await api(`/coupons/${id}/toggle`,'PATCH',{active});
  toast(j.message,j.success?'ok':'err');
  if(j.success)loadCoupons();
}

async function deleteCoupon(id,code){
  if(!confirm(`Delete coupon "${code}"?`))return;
  const j=await api(`/coupons/${id}`,'DELETE');
  toast(j.message,j.success?'ok':'err');
  if(j.success)loadCoupons();
}

// ═════════════════════════════════════════════════════
// SUBSCRIBERS
// ═════════════════════════════════════════════════════
async function loadSubscribers(){
  loadingHTML('subs-body');
  const j=await api('/subscribers');
  const data=j.data||[];
  const el=document.getElementById('subs-body');
  if(!data.length){el.innerHTML='<div class="empty">No subscribers yet.</div>';return;}
  el.innerHTML=`<div class="tbl-wrap"><table>
    <thead><tr><th>#</th><th>Email</th><th>Subscribed On</th></tr></thead>
    <tbody>${data.map(s=>`
      <tr><td>${s.id}</td><td>${s.email}</td>
      <td>${new Date(s.created_at).toLocaleDateString('en-IN')}</td></tr>`)
    .join('')}</tbody></table></div>`;
}

// ═════════════════════════════════════════════════════
// ANALYTICS
// ═════════════════════════════════════════════════════
async function loadAnalytics(){
  const j=await api('/analytics');
  if(!j.success){document.getElementById('analytics-body').innerHTML='<div class="empty">Backend offline.</div>';return;}
  const d=j.data;
  // Orders by status bar chart
  const maxOrd=Math.max(...(d.orders_by_status||[]).map(x=>x.count),1);
  const statusBars=(d.orders_by_status||[]).map(s=>`
    <div class="bar-row">
      <span>${s.status}</span>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.round(s.count/maxOrd*100)}%;background:${
        s.status==='delivered'?'#27ae60':s.status==='pending'?'#e67e22':s.status==='cancelled'?'#e74c3c':'var(--gold)'
      }"></div></div>
      <span class="bar-num">${s.count}</span>
    </div>`).join('');
  // Categories bar chart
  const maxCat=Math.max(...(d.top_categories||[]).map(x=>x.count),1);
  const catBars=(d.top_categories||[]).map(c=>`
    <div class="bar-row">
      <span>${c.category.replace('_',' ')}</span>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.round(c.count/maxCat*100)}%"></div></div>
      <span class="bar-num">${c.count}</span>
    </div>`).join('');
  document.getElementById('analytics-body').innerHTML=`
    <div class="stat-grid" style="margin-bottom:20px">
      <div class="sc good"><div class="s-val">₹${(d.revenue||0).toLocaleString('en-IN')}</div><div class="s-lbl">Total Revenue</div></div>
      <div class="sc"><div class="s-val">${d.total_orders}</div><div class="s-lbl">All Orders</div></div>
      <div class="sc"><div class="s-val">${d.avg_rating}★</div><div class="s-lbl">Avg Rating</div></div>
      <div class="sc"><div class="s-val">${d.subscribers}</div><div class="s-lbl">Subscribers</div></div>
    </div>
    <div class="chart-row">
      <div class="chart-box"><h3>Orders by Status</h3><div class="bar-chart">${statusBars||'<p class="empty">No data</p>'}</div></div>
      <div class="chart-box"><h3>Products by Category</h3><div class="bar-chart">${catBars||'<p class="empty">No data</p>'}</div></div>
    </div>
    ${d.low_stock_products?.length?`
    <div class="panel">
      <div class="panel-head"><h2>Low Stock Alert</h2></div>
      <div class="panel-body">
        <div class="tbl-wrap"><table>
          <thead><tr><th>Product</th><th>Category</th><th>Stock</th></tr></thead>
          <tbody>${d.low_stock_products.map(p=>`
            <tr><td>${p.name}</td><td>${p.category}</td>
            <td class="${p.stock<=0?'stock-out':'stock-low'}">${p.stock}</td></tr>`).join('')}
          </tbody></table></div>
      </div></div>`:''}`;
}

// ═════════════════════════════════════════════════════
// MODAL UTILS
// ═════════════════════════════════════════════════════
function closeModal(id){document.getElementById(id).classList.remove('open');}
window.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelectorAll('.modal-bg.open').forEach(m=>m.classList.remove('open'));});

// ═════════════════════════════════════════════════════
// INIT
// ═════════════════════════════════════════════════════
window.addEventListener('DOMContentLoaded',()=>{
  document.getElementById('topbar-time').textContent=new Date().toLocaleString('en-IN');
  loadDashboard();
});
