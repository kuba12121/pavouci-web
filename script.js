// THREE.JS 3D pavouk
const spiderParts = [
  { 
    name: 'hlavohrud', 
    displayName: 'Hlavohruď (Prosoma)', 
    text: 'Přední část těla, která vznikla splynutím hlavy a hrudi. Jsou na ní umístěny oči, chelicery (klepýtka), pedipalpy (makadla) a čtyři páry kráčivých nohou. Uvnitř se nachází centrální nervová soustava (mozek) a svalovina ovládající končetiny.' 
  },
  { 
    name: 'zadecek', 
    displayName: 'Zadeček (Opisthosoma)', 
    text: 'Zadní, obvykle nečlánkovaná část těla spojená s hlavohrudí tenkou stopkou (pedicelem). Obsahuje většinu vnitřních orgánů: srdce, trávicí trakt, dýchací ústrojí (plicní vaky nebo vzdušnice) a pohlavní orgány. Na konci se nacházejí snovací bradavice produkující pavučinové vlákno.' 
  },
  { 
    name: 'klepytka', 
    displayName: 'Klepýtka a kusadla', 
    text: 'Ústní ústrojí pavouka. Klepýtka (chelicery) slouží k probodnutí kořisti a vstříknutí jedu. Kusadla se nacházejí pod nimi a slouží k mechanickému zpracování a filtraci potravy.' 
  },
  { 
    name: 'makadla', 
    displayName: 'Makadla (Pedipalpy)', 
    text: 'Druhý pár končetin, který tvarem připomíná kratší nohy. Slouží k manipulaci s kořistí a jako hmatové a chuťové orgány. U dospělých samců jsou jejich konce přeměněny v kopulační orgány pro přenos spermatu.' 
  },
  { 
    name: 'oci', 
    displayName: 'Oči (Ocelli)', 
    text: 'Většina pavouků má osm jednoduchých očí uspořádaných v různých formacích na čelní části hlavohrudi. Rozlišujeme oči hlavní (uprostřed, vnímají obraz) a oči vedlejší (po stranách, vnímají pohyb a polarizované světlo).' 
  },
  { name: '1par nohou', displayName: '1. pár nohou', text: 'Přední pár kráčivých nohou, který u mnoha druhů plní také funkci hmatovou při průzkumu okolí.' },
  { name: '2par nohou', displayName: '2. pár nohou', text: 'Druhý pár kráčivých nohou, podílející se na stabilitě a pohybu.' },
  { name: '3par nohou', displayName: '3. pár nohou', text: 'Třetí pár kráčivých nohou, obvykle nejkratší, slouží k jemné manipulaci s pavučinou nebo při pohybu v úzkých prostorech.' },
  { name: '4par nohou', displayName: '4. pár nohou', text: 'Zadní pár kráčivých nohou, zásadní pro rychlý pohyb vpřed a často používaný k vytahování vlákna ze snovacích bradavic.' }
];

let scene, camera, renderer, gltfModel, mixer, clock, controls;
let animationsMap = {};
let currentAction = null;
let is3DInitialized = false;

const spiderAnimations = [
  { name: 'walk', displayName: 'Chůze', text: 'Pavouci se pohybují pomocí hydraulického tlaku hemolymfy (vytahování nohou) a svalů (stahování nohou). Tento koordinovaný pohyb jim umožňuje rychlý přesun i po svislých plochách.' },
  { name: 'def_pose', displayName: 'Zastavit', text: 'Základní statická pozice pavouka.' },
  { name: 'defense_pose', displayName: 'Obranná póza', text: 'Při ohrožení mnoho pavouků zdvihá přední páry nohou a odhaluje chelicery. Tento postoj slouží k zastrašení predátora a přípravě na případný výpad.' }
];

function initSpider3D() {
  if (is3DInitialized) return;
  const canvas = document.getElementById('spider-canvas');
  const container = document.getElementById('spider-canvas-container');
  if (!canvas || !container) return;
  
  is3DInitialized = true;
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xeeeeee);
  
  const width = container.clientWidth;
  const height = container.clientHeight || 500;
  
  camera = new THREE.PerspectiveCamera(45, width / height, 0.01, 2000);
  camera.position.set(0, 8, 15);
  
  renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.physicallyCorrectLights = true;

  scene.add(new THREE.AmbientLight(0xffffff, 2.5));
  scene.add(new THREE.HemisphereLight(0xffffff, 0xffffff, 2.0));
  const dirLight = new THREE.DirectionalLight(0xffffff, 3.0);
  dirLight.position.set(10, 20, 10);
  scene.add(dirLight);

  const cameraLight = new THREE.PointLight(0xffffff, 5.0, 50);
  scene.add(cameraLight);
  
  if (THREE.OrbitControls) {
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
  }
  
  clock = new THREE.Clock();
  const loader = new THREE.GLTFLoader();
  
  loader.load('pavoukHighPoly.glb', 
    (gltf) => {
      gltfModel = gltf.scene;
      gltfModel.traverse((node) => {
        if (node.isMesh && node.material) {
          node.material = node.material.clone();
          node.material.side = THREE.DoubleSide;
          if (!node.material.map) node.material.color.set(0x3d2b1f); 
          node.userData.originalColor = node.material.color.clone();
        }
      });
      scene.add(gltfModel);
      createSpiderButtons();
      
      if (gltf.animations && gltf.animations.length) {
        mixer = new THREE.AnimationMixer(gltfModel);
        gltf.animations.forEach(clip => {
          console.log('Dostupná animace:', clip.name);
          animationsMap[clip.name] = mixer.clipAction(clip);
        });
        createAnimationButtons();
        if (animationsMap['defense_pose']) playAnimation('defense_pose');
      }
    }
  );
  
  function animate() {
    requestAnimationFrame(animate);
    if (mixer) mixer.update(clock.getDelta());
    if (controls) {
      controls.update();
      cameraLight.position.copy(camera.position); 
    }
    renderer.render(scene, camera);
  }
  animate();
}

function playAnimation(name) {
  let action = animationsMap[name];
  // Fallback na def_pose
  if (!action && name !== 'def_pose') {
    action = animationsMap['def_pose'];
  }
  if (!action) return;

  if (currentAction && currentAction !== action) {
    currentAction.fadeOut(0.5);
  }
  
  action.reset().fadeIn(0.5).play();

  // Nastavení smyčkování podle typu animace
  const lowerName = name.toLowerCase();
  if (lowerName.includes('walk') || lowerName.includes('chuze')) {
    action.setLoop(THREE.LoopRepeat);
    action.clampWhenFinished = false;
  } else {
    // Pro pózy (def_pose, defense_pose atd.) chceme zůstat na konci
    action.setLoop(THREE.LoopOnce);
    action.clampWhenFinished = true;
  }
  
  currentAction = action;
}

function createSpiderButtons() {
  const btnContainer = document.getElementById('spider-buttons');
  if (!btnContainer) return;
  btnContainer.innerHTML = '';
  spiderParts.forEach(part => {
    const btn = document.createElement('button');
    btn.className = 'btn btn-outline-success btn-sm';
    btn.textContent = part.displayName;
    btn.onclick = () => {
      document.querySelectorAll('#spider-buttons button').forEach(b => b.classList.replace('btn-success', 'btn-outline-success'));
      btn.classList.replace('btn-outline-success', 'btn-success');
      const infoBox = document.getElementById('spider-text');
      if (infoBox) infoBox.innerHTML = `<strong>${part.displayName}:</strong> ${part.text}`;
      highlightSpiderPart(part.name);
    };
    btnContainer.appendChild(btn);
  });
}

function highlightSpiderPart(partName) {
  if (!gltfModel) return;
  const searchName = partName.toLowerCase().replace(/[\s_]/g, "").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  gltfModel.traverse((node) => {
    if (node.isMesh && node.material) {
      const nodeName = node.name.toLowerCase().replace(/[\s_]/g, "").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      if (nodeName.includes(searchName)) node.material.color.set(0xff0000); 
      else if (node.userData.originalColor) node.material.color.copy(node.userData.originalColor);
    }
  });
}

function createAnimationButtons() {
  let animDiv = document.getElementById('animation-buttons');
  if (!animDiv) {
    animDiv = document.createElement('div');
    animDiv.id = 'animation-buttons';
    animDiv.className = 'mt-3 d-flex flex-wrap gap-2 justify-content-center';
    document.getElementById('spider-buttons').after(animDiv);
  }
  animDiv.innerHTML = '<h6 class="w-100 text-center mb-2 mt-2">Pohyby:</h6>';
  
  const animLabels = {
    'walk': 'Chůze',
    'def_pose': 'Zastavit',
    'defense_pose': 'Obranná póza'
  };

  Object.keys(animationsMap).forEach(name => {
    const btn = document.createElement('button');
    btn.className = 'btn btn-outline-primary btn-sm';
    
    // Case-insensitive vyhledávání v labels
    const labelKey = Object.keys(animLabels).find(key => key.toLowerCase() === name.toLowerCase());
    btn.textContent = labelKey ? animLabels[labelKey] : name;
    
    btn.onclick = () => playAnimation(name);
    animDiv.appendChild(btn);
  });
}

function resizeSpider3D() {
  if (!renderer || !camera) return;
  const container = document.getElementById('spider-canvas-container');
  renderer.setSize(container.clientWidth, container.clientHeight);
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
}

document.addEventListener('DOMContentLoaded', initSpider3D);
window.addEventListener('resize', resizeSpider3D);

(function () {
  const API_URL = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost')
    ? 'http://127.0.0.1:8001'
    : window.location.origin;

  function updateAuthUI() {
    const token = localStorage.getItem('access_token');
    const email = localStorage.getItem('email');
    if (token && email) {
      document.getElementById('user-icon-nav').style.display = 'none';
      document.getElementById('profile-nav').style.display = 'block';
      document.getElementById('logout-nav').style.display = 'block';
      loadProfileData(email);
    } else {
      document.getElementById('user-icon-nav').style.display = 'block';
      document.getElementById('profile-nav').style.display = 'none';
      document.getElementById('logout-nav').style.display = 'none';
    }
  }

  async function loadProfileData(email) {
    try {
      const res = await fetch(`${API_URL}/auth/profile/${email}`);
      if (res.ok) {
        const data = await res.json();
        const emailEl = document.getElementById('profile-email');
        const userEl = document.getElementById('profile-username');
        const picEl = document.getElementById('profile-pic');
        if (emailEl) emailEl.textContent = data.email;
        if (userEl) userEl.textContent = data.username || 'Uživatel';
        if (picEl) picEl.src = data.profilovka || 'img/pavouk.webp';

        const token = localStorage.getItem('access_token');
        if (token) {
          const resFav = await fetch(`${API_URL}/pavouci/favorites`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token })
          });
          if (resFav.ok) {
            const favIds = await resFav.json();
            const countEl = document.getElementById('fav-count');
            if (countEl) countEl.textContent = favIds.length;
            const resAll = await fetch(`${API_URL}/pavouci/`);
            if (resAll.ok) {
              const all = await resAll.json();
              const myFavs = all.filter(s => favIds.includes(s.id));
              const container = document.getElementById('profile-favorites');
              if (container) {
                container.innerHTML = myFavs.length ? '' : '<p class="text-muted">Žádní oblíbenci.</p>';
                myFavs.forEach(p => {
                  const card = renderPavoukCard(p, favIds);
                  card.className = 'col-sm-6 col-lg-4 mb-3';
                  container.appendChild(card);
                });
              }
            }
          }
        }
        loadUserFindings(email);
        loadFriends(email);
        loadFriendRequests(data.id_uz);
      }
    } catch (e) { console.error(e); }
  }

  async function loadFriendRequests(userId) {
    if (!userId) return;
    try {
      const res = await fetch(`${API_URL}/pratele/pending/${userId}`);
      if (res.ok) {
        const data = await res.json();
        const section = document.getElementById('pending-requests-section');
        const list = document.getElementById('pending-requests-list');
        if (section && list) {
          if (data.length > 0) {
            section.style.display = 'block';
            list.innerHTML = data.map(r => `
              <div class="list-group-item d-flex justify-content-between align-items-center bg-white border mb-2 rounded-3 p-2 shadow-sm">
                <div class="small">
                  <strong>${r.sender_username}</strong>
                  <div class="text-muted" style="font-size: 0.7rem;">${r.sender_email}</div>
                </div>
                <div class="d-flex gap-1">
                  <button class="btn btn-sm btn-success rounded-pill px-2" onclick="acceptRequest(${r.request_id})"><i class="fa-solid fa-check"></i></button>
                  <button class="btn btn-sm btn-outline-danger rounded-pill px-2" onclick="declineRequest(${r.request_id})"><i class="fa-solid fa-xmark"></i></button>
                </div>
              </div>
            `).join('');
          } else {
            section.style.display = 'none';
          }
        }
      }
    } catch (e) { console.error('Error loading friend requests:', e); }
  }

  window.acceptRequest = async function(requestId) {
    try {
      const res = await fetch(`${API_URL}/pratele/accept`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request_id: requestId })
      });
      if (res.ok) {
        updateAuthUI();
      }
    } catch (e) { alert('Chyba při schvalování.'); }
  };

  window.declineRequest = async function(requestId) {
    if (!confirm('Opravdu chcete tuto žádost zamítnout?')) return;
    try {
      const res = await fetch(`${API_URL}/pratele/decline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request_id: requestId })
      });
      if (res.ok) {
        updateAuthUI();
      }
    } catch (e) { alert('Chyba při zamítání.'); }
  };

  const sections = document.querySelectorAll('.section');
  const tabLinks = document.querySelectorAll('a[data-section]');

  window.showSection = function(id) {
    sections.forEach(s => s.style.display = 'none');
    tabLinks.forEach(l => l.classList.remove('active'));
    const target = document.getElementById(id);
    if (target) target.style.display = 'block';
    document.querySelectorAll(`a[data-section="${id}"]`).forEach(l => l.classList.add('active'));

    if (id === 'pavouci') fetchAndRenderPavouci();
    if (id === 'pavuciny') fetchAndRenderWebs();
    if (id === 'nalezy-global') fetchGlobalFindings();
    if (id === 'anatomie') {
      setTimeout(resizeSpider3D, 100);
      if (animationsMap['def_pose']) playAnimation('def_pose');
    }
  }

  tabLinks.forEach(l => l.onclick = (e) => { e.preventDefault(); showSection(l.dataset.section); });

  async function fetchGlobalFindings() {
    const container = document.getElementById('global-findings-container');
    try {
      const res = await fetch(`${API_URL}/nalezy/`);
      if (res.ok) {
        const data = await res.json();
        container.innerHTML = '';
        if (data.nalezy && data.nalezy.length > 0) {
          data.nalezy.forEach(n => {
            const card = renderFindingCard(n);
            container.appendChild(card);
          });
        } else {
          container.innerHTML = '<p class="text-center w-100">Zatím žádné nálezy.</p>';
        }
      }
    } catch (e) { container.innerHTML = 'Chyba načítání.'; }
  }

  function renderFindingCard(n) {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4';
    col.innerHTML = `
      <div class="card h-100 border-0 shadow-sm rounded-4 overflow-hidden" style="cursor:pointer;">
        ${n.obrazek ? `<img src="${n.obrazek}" class="card-img-top" style="height:200px; object-fit:cover;">` : '<div class="bg-light p-5 text-center text-muted" style="height:200px;"><i class="fa-solid fa-camera fa-2x"></i></div>'}
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h5 class="fw-bold mb-0">${n.nazev}</h5>
            <span class="badge bg-secondary bg-opacity-10 text-secondary rounded-pill small" style="font-size: 0.7rem;">
              <i class="fa-solid fa-user me-1"></i>${n.author_name || 'Neznámý'}
            </span>
          </div>
          <p class="small text-primary mb-1"><i class="fa-solid fa-location-dot me-1"></i>${n.lokace}</p>
          <p class="small text-muted text-truncate">${n.popis || ''}</p>
        </div>
      </div>
    `;
    col.onclick = () => showFindingDetails(n);
    return col;
  }

  function showFindingDetails(n) {
    const modal = new bootstrap.Modal(document.getElementById('spiderModal'));
    document.getElementById('modal-spider-name').textContent = n.nazev;
    document.getElementById('modal-spider-family').textContent = n.lokace;
    document.getElementById('modal-spider-description').textContent = n.popis || 'Bez popisu.';
    document.getElementById('modal-spider-img').src = n.obrazek || 'img/pavouk.webp';
    document.getElementById('modal-spider-latin').textContent = n.datum ? `Nalezeno: ${n.datum}` : '';
    modal.show();
  }

  window.deleteFinding = async function(nalezId, event) {
    if (event) event.stopPropagation();
    if (!confirm('Opravdu chcete tento nález odstranit?')) return;
    
    try {
      const res = await fetch(`${API_URL}/nalezy/${nalezId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        const email = localStorage.getItem('email');
        if (email) loadUserFindings(email);
        // Také aktualizujeme globální seznam, pokud je uživatel právě v něm
        if (typeof fetchGlobalFindings === 'function') {
            fetchGlobalFindings();
        }
      } else {
        alert('Chyba při odstraňování nálezu.');
      }
    } catch (e) {
      console.error('Delete error:', e);
      alert('Chyba při komunikaci se serverem.');
    }
  };

  async function loadUserFindings(email) {
    const container = document.getElementById('user-findings-list');
    try {
      const res = await fetch(`${API_URL}/nalezy/email/${email}`);
      if (res.ok) {
        const data = await res.json();
        container.innerHTML = '';
        if (data.nalezy && data.nalezy.length > 0) {
          data.nalezy.forEach(n => {
            const div = document.createElement('div');
            div.className = 'col-12 mb-2';
            div.innerHTML = `
              <div class="d-flex align-items-center bg-light p-2 rounded-3 border" style="cursor:pointer;" onclick="showFindingDetailsById(${n.id})">
                ${n.obrazek ? `<img src="${n.obrazek}" class="rounded me-3" style="width:40px; height:40px; object-fit:cover;">` : '<div class="rounded me-3 bg-secondary d-flex align-items-center justify-content-center" style="width:40px; height:40px;"><i class="fa-solid fa-camera text-white"></i></div>'}
                <div class="flex-grow-1">
                  <h6 class="mb-0 small">${n.nazev}</h6>
                  <p class="small text-muted mb-0" style="font-size: 0.7rem;">${n.lokace}</p>
                </div>
                <button class="btn btn-sm text-danger ms-2" onclick="deleteFinding(${n.id}, event)">
                  <i class="fa-solid fa-trash-can"></i>
                </button>
              </div>
            `;
            container.appendChild(div);
          });
        } else {
          container.innerHTML = '<p class="text-muted small">Žádné vlastní nálezy.</p>';
        }
      }
    } catch (e) { }
  }

  // Pomocná funkce pro zobrazení detailu podle dat (pro zjednodušení volání z loadUserFindings)
  window.showFindingDetailsById = function(id) {
    // Najdeme data v UI nebo znovu načteme, pro teď použijeme existující showFindingDetails
    // ale musíme mít objekt nálezu. V loadUserFindings ho máme v cyklu.
    // Aby to fungovalo čistě, upravíme loadUserFindings výše.
  };

  const findingForm = document.getElementById('add-finding-form');
  if (findingForm) {
    findingForm.onsubmit = async (e) => {
      e.preventDefault();
      const email = localStorage.getItem('email');
      const imageInput = document.getElementById('finding-image');
      let imageBase64 = null;
      if (imageInput.files[0]) {
        imageBase64 = await new Promise(r => {
          const reader = new FileReader();
          reader.onload = e => r(e.target.result);
          reader.readAsDataURL(imageInput.files[0]);
        });
      }
      const res = await fetch(`${API_URL}/nalezy/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: email,
          nazev: document.getElementById('finding-name').value,
          lokace: document.getElementById('finding-location').value,
          popis: document.getElementById('finding-popis').value,
          obrazek: imageBase64
        })
      });
      if (res.ok) {
        findingForm.reset();
        document.getElementById('add-finding-form-container').style.display = 'none';
        loadUserFindings(email);
      }
    };
  }

  async function loadFriends(email) {
    try {
      const pRes = await fetch(`${API_URL}/auth/profile/${email}`);
      if (!pRes.ok) throw new Error('Profil nenalezen');
      const p = await pRes.json();
      
      if (!p.id_uz) return;

      const res = await fetch(`${API_URL}/pratele/list/${p.id_uz}`);
      if (res.ok) {
        const data = await res.json();
        const listEl = document.getElementById('friends-list');
        if (listEl) {
          listEl.innerHTML = data.friends.length ? data.friends.map(f => `
            <div class="list-group-item border-0 px-0 d-flex align-items-center justify-content-between small">
              <div class="d-flex align-items-center">
                <i class="fa-solid fa-user-circle fa-xl me-2 text-muted"></i>
                <span>${f.username}</span>
              </div>
              <button class="btn btn-sm btn-outline-primary rounded-pill px-3" onclick="showFriendProfile('${f.email}')">Profil</button>
            </div>
          `).join('') : '<p class="small text-muted">Žádní přátelé.</p>';
        }
      }
    } catch (e) { }
  }

  window.showFriendProfile = async function(email) {
    try {
      const res = await fetch(`${API_URL}/auth/profile/${email}`);
      if (!res.ok) return;
      const data = await res.json();
      
      document.getElementById('f-profile-username').textContent = data.username;
      document.getElementById('f-profile-email').textContent = data.email;
      document.getElementById('f-profile-pic').src = data.profilovka || 'img/pavouk.webp';
      
      showSection('friend-profile');
      
      // Load friend's findings
      const container = document.getElementById('f-user-findings-list');
      container.innerHTML = '<p class="text-center py-2">Načítám nálezy...</p>';
      
      const resNal = await fetch(`${API_URL}/nalezy/email/${email}`);
      if (resNal.ok) {
        const nalData = await resNal.json();
        container.innerHTML = '';
        if (nalData.nalezy && nalData.nalezy.length > 0) {
          nalData.nalezy.forEach(n => {
            const div = document.createElement('div');
            div.className = 'col-12 mb-2';
            div.innerHTML = `
              <div class="d-flex align-items-center bg-light p-2 rounded-3 border" style="cursor:pointer;">
                ${n.obrazek ? `<img src="${n.obrazek}" class="rounded me-3" style="width:40px; height:40px; object-fit:cover;">` : '<div class="rounded me-3 bg-secondary d-flex align-items-center justify-content-center" style="width:40px; height:40px;"><i class="fa-solid fa-camera text-white"></i></div>'}
                <div class="flex-grow-1"><h6 class="mb-0 small">${n.nazev}</h6><p class="small text-muted mb-0" style="font-size: 0.7rem;">${n.lokace}</p></div>
              </div>
            `;
            div.onclick = () => showFindingDetails(n);
            container.appendChild(div);
          });
        } else {
          container.innerHTML = '<p class="text-muted small text-center">Žádné nálezy.</p>';
        }
      }
    } catch (e) { console.error(e); }
  };

  const searchBtn = document.getElementById('friend-search-btn');
  if (searchBtn) {
    searchBtn.onclick = async () => {
      const q = document.getElementById('friend-search-input').value;
      const res = await fetch(`${API_URL}/auth/search?query=${q}`);
      const users = await res.json();
      const results = document.getElementById('friend-search-results');
      results.style.display = 'block';
      results.innerHTML = users.map(u => `
        <div class="list-group-item d-flex justify-content-between align-items-center small">
          <span>${u.username}</span>
          <button class="btn btn-sm btn-primary" onclick="sendFriendRequest(${u.id_uz})">Přidat</button>
        </div>
      `).join('');
    };
  }

  window.sendFriendRequest = async (id) => {
    try {
      const email = localStorage.getItem('email');
      if (!email) {
        alert('Musíte být přihlášeni.');
        return;
      }
      const pRes = await fetch(`${API_URL}/auth/profile/${email}`);
      if (!pRes.ok) throw new Error('Profil nenalezen');
      const p = await pRes.json();
      
      if (!p.id_uz || p.id_uz === id) {
        alert(p.id_uz === id ? 'Nemůžete přidat sami sebe.' : 'Chyba profilu.');
        return;
      }

      const res = await fetch(`${API_URL}/pratele/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sender_id: p.id_uz, receiver_id: id })
      });
      if (res.ok) {
        alert('Žádost o přátelství odeslána.');
        document.getElementById('friend-search-results').style.display = 'none';
        document.getElementById('friend-search-input').value = '';
      } else {
        const err = await res.json();
        alert('Chyba: ' + (err.detail || 'Nepodařilo se odeslat žádost.'));
      }
    } catch (e) { 
      console.error('API Error:', e);
      alert('Chyba při komunikaci se serverem: ' + e.message); 
    }
  };

  window.toggleAuthForms = function(showRegister) {
    document.getElementById('login-container').style.display = showRegister ? 'none' : 'block';
    document.getElementById('register-container').style.display = showRegister ? 'block' : 'none';
  };

  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.onsubmit = async (e) => {
      e.preventDefault();
      const username = document.getElementById('register-username').value;
      const email = document.getElementById('register-email').value;
      const password = document.getElementById('register-password').value;
      
      try {
        const res = await fetch(`${API_URL}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, email, password })
        });
        const data = await res.json();
        if (res.ok) {
          alert('Registrace úspěšná! Nyní se můžete přihlásit.');
          toggleAuthForms(false);
        } else {
          alert('Chyba: ' + (data.detail || 'Registrace selhala.'));
        }
      } catch (err) {
        alert('Chyba při komunikaci se serverem.');
      }
    };
  }

  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.onsubmit = async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value;
      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password: document.getElementById('login-password').value })
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('email', email);
        updateAuthUI();
        showSection('home');
      }
    };
  }

  const googleBtn = document.getElementById('google-login-btn');
  if (googleBtn) {
    googleBtn.onclick = () => {
      window.open(`${API_URL}/auth/google/login`, 'Login', 'width=500,height=600');
    };
  }

  window.addEventListener('message', (e) => {
    if (e.data.access_token) {
      localStorage.setItem('access_token', e.data.access_token);
      localStorage.setItem('email', e.data.email);
      updateAuthUI();
      showSection('home');
    }
  });

  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.onclick = () => {
      localStorage.clear();
      updateAuthUI();
      showSection('home');
    };
  }

  // Obsluha nahrávání profilového obrázku
  const profilePicInput = document.getElementById('profile-pic-input');
  if (profilePicInput) {
    profilePicInput.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = async (event) => {
        const base64Image = event.target.result;
        const token = localStorage.getItem('access_token');
        
        try {
          const res = await fetch(`${API_URL}/auth/profile/upload-picture`, {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ image: base64Image })
          });
          
          if (res.ok) {
            document.getElementById('profile-pic').src = base64Image;
            alert('Profilový obrázek byl úspěšně nahrán.');
          } else {
            const err = await res.json();
            alert('Chyba při nahrávání: ' + (err.detail || 'Neznámá chyba'));
          }
        } catch (err) {
          console.error('Upload error:', err);
          alert('Chyba při komunikaci se serverem.');
        }
      };
      reader.readAsDataURL(file);
    };
  }

  function getThreatBadgeClasses(status) {
    if (!status) return 'bg-secondary bg-opacity-10 text-secondary';
    const s = status.toLowerCase();
    // LC - Málo dotčený
    if (s.includes('málo') || s.includes('lc')) return 'bg-success bg-opacity-10 text-success';
    // NT, VU - Téměř ohrožený, Zranitelný
    if (s.includes('téměř') || s.includes('zranitelný') || s.includes('nt') || s.includes('vu')) return 'bg-warning bg-opacity-10 text-warning';
    // EN, CR - Ohrožený, Kriticky ohrožený
    if (s.includes('ohrožený') || s.includes('kriticky') || s.includes('en') || s.includes('cr')) return 'bg-danger bg-opacity-10 text-danger';
    
    return 'bg-warning bg-opacity-10 text-warning'; // Výchozí žlutá
  }

  function formatAuthorLabel(name, url) {
    if (!name) return '';
    let finalUrl = url;
    if (url && !url.startsWith('http')) {
      finalUrl = 'https://' + url;
    }
    
    if (finalUrl) {
      return `<a href="${finalUrl}" target="_blank" onclick="event.stopPropagation()" class="photo-author small text-white text-decoration-none" style="cursor: pointer; display: block;">
          ${name}
      </a>`;
    }
    return `<div class="photo-author small">${name}</div>`;
  }

  function renderPavoukCard(p, favIds) {
    const col = document.createElement('div');
    col.className = 'col-md-4 mb-4';
    const isFav = favIds.includes(p.id);
    const t = new Date().getTime();
    let img = p.obrazek ? (p.obrazek.startsWith('http') ? p.obrazek : `${API_URL}/pavouci/image/${p.obrazek}?t=${t}`) : 'img/KrizakObecny.webp';
    
    const threatClasses = getThreatBadgeClasses(p.ohrozeni);

    col.innerHTML = `
      <div class="spider-card position-relative" style="cursor:pointer;">
        <button class="favorite-btn" onclick="event.stopPropagation(); toggleFav(${p.id}, this.querySelector('i'))">
          <i class="${isFav ? 'fa-solid' : 'fa-regular'} fa-heart"></i>
        </button>
        <div class="position-relative">
          <img src="${img}" alt="${p.nazev}">
          ${formatAuthorLabel(p.autor, p.foto_odkaz)}
        </div>
        <div class="card-body">
          <h5 class="card-title mb-1">${p.nazev}</h5>
          <p class="text-muted small fst-italic mb-2">${p.lat_nazev || ''}</p>
          <div class="d-flex flex-wrap gap-1 mb-2">
            <span class="badge bg-success bg-opacity-10 text-success small rounded-pill">${p.nazev_celed || ''}</span>
            <span class="badge bg-primary bg-opacity-10 text-primary small rounded-pill">${p.nazev_pavuciny || 'Nestaví sítě'}</span>
            ${p.ohrozeni ? `<span class="badge ${threatClasses} small rounded-pill">${p.ohrozeni}</span>` : ''}
          </div>
          <p class="small text-muted text-truncate" style="max-height: 3rem; overflow: hidden;">${p.popis || ''}</p>
        </div>
        <div class="card-footer border-0 bg-transparent">
          <button class="btn btn-sm btn-outline-primary w-100 rounded-pill">Podrobnosti</button>
        </div>
      </div>
    `;
    col.onclick = () => showPavoukDetails(p);
    return col;
  }

  window.toggleFav = async (id, iconEl) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('Pro přidání do oblíbených se musíte přihlásit.');
      return;
    }
    try {
      const res = await fetch(`${API_URL}/pavouci/${id}/favorite`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      });
      const data = await res.json();
      if (res.ok) {
        iconEl.className = (data.msg === 'added' ? 'fa-solid' : 'fa-regular') + ' fa-heart';
        
        // REAKTIVNÍ AKTUALIZACE:
        const email = localStorage.getItem('email');
        if (email) {
          // Načteme znovu data profilu, aby se aktualizoval seznam oblíbených
          loadProfileData(email);
        }
      }
    } catch (e) { console.error('Error toggling favorite:', e); }
  };

  function showPavoukDetails(p) {
    const modal = new bootstrap.Modal(document.getElementById('spiderModal'));
    document.getElementById('modal-spider-name').textContent = p.nazev;
    document.getElementById('modal-spider-latin').textContent = p.lat_nazev || '';
    document.getElementById('modal-spider-family').textContent = p.nazev_celed || 'Neznámá čeleď';
    document.getElementById('modal-spider-web').textContent = p.nazev_pavuciny || 'Nestaví sítě';
    const threatEl = document.getElementById('modal-spider-threat');
    if (p.ohrozeni) {
      threatEl.textContent = p.ohrozeni;
      threatEl.className = 'badge ' + getThreatBadgeClasses(p.ohrozeni) + ' rounded-pill px-3';
      threatEl.style.display = 'inline-block';
    } else {
      threatEl.style.display = 'none';
    }

    const locEl = document.getElementById('modal-spider-location');
    const locContainer = document.getElementById('modal-spider-location-container');
    if (p.vyskyt) {
      locEl.textContent = p.vyskyt;
      locContainer.style.display = 'block';
    } else {
      locContainer.style.display = 'none';
    }

    document.getElementById('modal-spider-description').textContent = p.popis;
    const t = new Date().getTime();
    document.getElementById('modal-spider-img').src = p.obrazek ? (p.obrazek.startsWith('http') ? p.obrazek : `${API_URL}/pavouci/image/${p.obrazek}?t=${t}`) : 'img/pavouk.webp';
    
    const authorEl = document.getElementById('modal-spider-author');
    if (p.autor) {
      authorEl.innerHTML = p.foto_odkaz ? `<a href="${p.foto_odkaz}" target="_blank" class="text-white text-decoration-none">${p.autor}</a>` : p.autor;
      authorEl.style.display = 'block';
    } else {
      authorEl.style.display = 'none';
    }
    
    modal.show();
  }

  let allSpiders = []; // Seznam aktuálně zobrazených pavouků (včetně načtených přes Načíst další)
  let spiderOffset = 0;
  const spiderLimit = 12;
  let currentSearch = '';
  let currentFamilyId = 'all';

  async function fetchAndRenderPavouci(append = false) {
    const container = document.getElementById('pavouci-cards');
    const loadMoreContainer = document.getElementById('load-more-container');
    
    if (!append) {
      spiderOffset = 0;
      allSpiders = [];
      if (container) container.innerHTML = '<div class="col-12 text-center py-5"><div class="spinner-border text-primary"></div></div>';
    }

    try {
      let url = `${API_URL}/pavouci/?limit=${spiderLimit}&offset=${spiderOffset}`;
      if (currentSearch) url += `&search=${encodeURIComponent(currentSearch)}`;
      if (currentFamilyId !== 'all') url += `&family_id=${currentFamilyId}`;

      const res = await fetch(url);
      const data = await res.json();
      const spiders = data.spiders;
      const total = data.total;
      
      const token = localStorage.getItem('access_token');
      let favIds = [];
      if (token) {
        const r = await fetch(`${API_URL}/pavouci/favorites`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({token})});
        if (r.ok) favIds = await r.json();
      }
      
      if (!append) {
        if (container) container.innerHTML = '';
        populateFamilyFilter(); // Načte čeledi jen pokud ještě nejsou
      }

      allSpiders = append ? [...allSpiders, ...spiders] : spiders;
      
      renderSpiderList(spiders, favIds, append);
      
      // Update count
      const countEl = document.getElementById('spider-count');
      if (countEl) countEl.textContent = total;

      // Show/hide Load More
      if (loadMoreContainer) {
        loadMoreContainer.style.display = (allSpiders.length < total) ? 'block' : 'none';
      }

      // Inicializace listenerů (jen při prvním vstupu do sekce)
      if (!append && spiderOffset === 0) {
        setupFilterListeners();
      }
      
    } catch (e) { 
      console.error('Error fetching spiders:', e);
      if (container) container.innerHTML = '<div class="col-12 text-center py-5 text-danger">Chyba při načítání dat ze serveru.</div>';
    }
  }

  function setupFilterListeners() {
    const searchInput = document.getElementById('spider-search-input');
    const familyFilter = document.getElementById('spider-family-filter');
    
    if (searchInput && !searchInput.dataset.hasListener) {
      searchInput.oninput = debounce(() => {
        currentSearch = searchInput.value;
        fetchAndRenderPavouci(false);
      }, 300);
      searchInput.dataset.hasListener = "true";
    }
    
    if (familyFilter && !familyFilter.dataset.hasListener) {
      familyFilter.onchange = () => {
        currentFamilyId = familyFilter.value;
        fetchAndRenderPavouci(false);
      };
      familyFilter.dataset.hasListener = "true";
    }
  }

  function debounce(func, timeout = 300) {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
  }

  async function populateFamilyFilter() {
    const filter = document.getElementById('spider-family-filter');
    if (!filter || filter.options.length > 1) return; 
    
    try {
      const res = await fetch(`${API_URL}/pavouci/families`);
      const families = await res.json();
      filter.innerHTML = '<option value="all">Všechny čeledi</option>' + 
        families.map(f => `<option value="${f.id}">${f.nazev}</option>`).join('');
    } catch (e) { console.error('Error loading families:', e); }
  }

  function renderSpiderList(spiders, favIds, append) {
    const container = document.getElementById('pavouci-cards');
    if (!container) return;
    
    if (spiders.length === 0 && !append) {
      container.innerHTML = '<div class="col-12 text-center py-5 text-muted">Nenalezen žádný odpovídající pavouk.</div>';
      return;
    }
    
    spiders.forEach(p => container.appendChild(renderPavoukCard(p, favIds)));
  }

  // Tlačítko Načíst další
  const loadMoreBtn = document.getElementById('load-more-btn');
  if (loadMoreBtn) {
    loadMoreBtn.onclick = () => {
      spiderOffset += spiderLimit;
      fetchAndRenderPavouci(true);
    };
  }

  async function fetchAndRenderWebs() {
    const container = document.getElementById('webs-container');
    if (!container) return;
    
    try {
      const res = await fetch(`${API_URL}/pavouci/webs`);
      if (res.ok) {
        const webs = await res.json();
        container.innerHTML = '';
        if (webs.length === 0) {
          container.innerHTML = '<p class="text-center w-100 py-5">Žádné typy pavučin nebyly nalezeny.</p>';
          return;
        }
        
        webs.forEach(w => {
          const col = document.createElement('div');
          col.className = 'col-md-4 mb-4';
          
          const t = new Date().getTime();
          const hasImage = w.obrazek && w.obrazek !== 'null' && w.obrazek !== '' && !w.obrazek.includes('undefined');
          let img = hasImage ? (w.obrazek.startsWith('http') ? w.obrazek : `${API_URL}/pavouci/image/${w.obrazek}?t=${t}`) : null;
          
          let finalUrl = w.foto_odkaz;
          if (finalUrl && !finalUrl.startsWith('http')) finalUrl = 'https://' + finalUrl;

          const imgStyle = w.id === 1 ? 'object-fit: contain; background: #f8f9fa;' : 'object-fit: cover;';

          col.innerHTML = `
            <div class="card h-100 border-0 shadow-sm rounded-4 overflow-hidden">
              ${img ? `
                <div class="position-relative">
                  <img src="${img}" class="card-img-top" alt="${w.typ}" style="height: 200px; ${imgStyle}" onerror="this.parentElement.remove()">
                  ${w.autor ? `<div class="photo-author small">${finalUrl ? `<a href="${finalUrl}" target="_blank" class="text-white text-decoration-none">${w.autor}</a>` : w.autor}</div>` : ''}
                </div>
              ` : ''}
              <div class="card-body">
                <h5 class="fw-bold">${w.typ}</h5>
                <p class="text-muted small mb-0">${w.popis || 'Bez popisu.'}</p>
              </div>
            </div>
          `;
          container.appendChild(col);
        });
      }
    } catch (e) {
      console.error('Error fetching webs:', e);
      container.innerHTML = '<p class="text-center w-100 py-5 text-danger">Chyba při načítání dat.</p>';
    }
  }

  const spiderFacts = [
    "Pavoučí vlákno je v poměru ke své váze pevnější než ocel a dokáže se natáhnout až na pětinásobek své délky.",
    "Některé druhy pavouků dokážou pod vodou přežít i několik hodin díky vzduchové bublině zachycené na chloupcích těla.",
    "Pavouci nejsou hmyz; patří do třídy pavoukovců a mají osm noh, zatímco hmyz má pouze šest.",
    "Většina pavouků má 8 očí, ale existují i druhy se 6, 4, 2 nebo dokonce úplně bez očí (v jeskyních).",
    "Největší pavouk na světě, sklípkan největší, může mít rozpětí nohou až 30 centimetrů.",
    "Pavouci recyklují své sítě – mnoho druhů starou síť sní, aby získali zpět drahocenné proteiny pro stavbu nové.",
    "Existuje druh pavouka (Bagheera kiplingi), který je téměř výhradně býložravý.",
    "Skákavky mají nejlepší zrak ze všech pavouků a dokážou vnímat barvy podobně jako lidé."
  ];

  function displayRandomFact() {
    const el = document.getElementById('random-fact');
    if (el) {
      const fact = spiderFacts[Math.floor(Math.random() * spiderFacts.length)];
      el.textContent = fact;
    }
  }

  updateAuthUI();
  showSection('home');
  displayRandomFact();
})();
