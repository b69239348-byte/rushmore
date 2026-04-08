// Rushmore MVP — Frontend

const API = '';
const state = {
    slots: [null, null, null, null, null],
    searchResults: [],
    drawerOpen: false,
    activeSlot: -1, // which slot triggered the drawer
};

// --- DOM ---
const searchInput = document.getElementById('search-input');
const searchResultsEl = document.getElementById('search-results');
const slotsEl = document.getElementById('slots');
const exportBtn = document.getElementById('export-btn');
const previewOverlay = document.getElementById('preview-overlay');
const previewImg = document.getElementById('preview-img');
const previewDownload = document.getElementById('preview-download');
const previewClose = document.getElementById('preview-close');
const searchDrawer = document.getElementById('search-drawer');
const searchBackdrop = document.getElementById('search-backdrop');
const searchCloseBtn = document.getElementById('search-close');

// --- Search Drawer ---

function openDrawer(slotIndex) {
    state.activeSlot = slotIndex !== undefined ? slotIndex : -1;
    state.drawerOpen = true;
    searchDrawer.classList.add('open');
    searchBackdrop.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Focus search input after animation
    setTimeout(() => searchInput.focus(), 350);

    // Load results if empty
    if (state.searchResults.length === 0) {
        fetchPlayers('');
    } else {
        renderSearchResults();
    }
}

function closeDrawer() {
    state.drawerOpen = false;
    state.activeSlot = -1;
    searchDrawer.classList.remove('open');
    searchBackdrop.classList.add('hidden');
    document.body.style.overflow = '';
    searchInput.blur();
}

searchBackdrop.addEventListener('click', closeDrawer);
searchCloseBtn.addEventListener('click', closeDrawer);

// Close on escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        if (!previewOverlay.classList.contains('hidden')) {
            previewOverlay.classList.add('hidden');
        } else if (state.drawerOpen) {
            closeDrawer();
        }
    }
});

// --- Slot clicks ---

slotsEl.addEventListener('click', (e) => {
    const slot = e.target.closest('.slot');
    if (!slot) return;

    const rank = parseInt(slot.dataset.rank);
    const index = rank - 1;

    // If clicking remove button
    if (e.target.closest('.slot-remove')) {
        e.stopPropagation();
        removePlayer(index);
        return;
    }

    // Empty slot → open drawer to add
    if (slot.classList.contains('empty')) {
        openDrawer(index);
    }
});

// --- Search ---

let searchTimeout = null;

searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        fetchPlayers(searchInput.value.trim());
    }, 200);
});

async function fetchPlayers(query) {
    try {
        const res = await fetch(`${API}/api/players?q=${encodeURIComponent(query)}&limit=40`);
        state.searchResults = await res.json();
        renderSearchResults();
    } catch (err) {
        console.error('Search failed:', err);
    }
}

function getInitials(name) {
    return name.split(' ').map(w => w[0]).join('').slice(0, 3).toUpperCase();
}

function renderSearchResults() {
    const selectedIds = new Set(state.slots.filter(Boolean).map(p => p.id));

    searchResultsEl.innerHTML = state.searchResults
        .map(p => {
            const isSelected = selectedIds.has(p.id);
            const teams = (p.teams || []).slice(0, 3).join(' / ');
            const years = p.from_year && p.to_year ? `${p.from_year}–${p.to_year}` : '';
            const awards = p.awards || {};
            const badges = [];
            if (awards.championships) badges.push(`${awards.championships}x Champ`);
            if (awards.mvps) badges.push(`${awards.mvps}x MVP`);

            return `
                <div class="result-item ${isSelected ? 'selected' : ''}" onclick="addPlayer(${p.id})">
                    <div class="result-avatar">${getInitials(p.name)}</div>
                    <div class="result-info">
                        <div class="result-name">${p.name}</div>
                        <div class="result-meta">${p.position}  ·  ${teams}${years ? '  ·  ' + years : ''}</div>
                        ${badges.length ? `<div class="result-awards">${badges.join('  ·  ')}</div>` : ''}
                    </div>
                    <div class="result-stats">
                        <div><span class="result-stat-val">${p.ppg}</span> <span class="result-stat-label">PPG</span></div>
                        <div><span class="result-stat-val">${p.rpg}</span> <span class="result-stat-label">RPG</span></div>
                        <div><span class="result-stat-val">${p.apg}</span> <span class="result-stat-label">APG</span></div>
                    </div>
                    <div class="result-add-icon">+</div>
                </div>
            `;
        })
        .join('');
}

// --- Slot Management ---

function addPlayer(playerId) {
    const player = state.searchResults.find(p => p.id === playerId);
    if (!player) return;
    if (state.slots.some(s => s && s.id === playerId)) return;

    // Use active slot if set, otherwise first empty
    let targetIndex = state.activeSlot;
    if (targetIndex < 0 || state.slots[targetIndex] !== null) {
        targetIndex = state.slots.findIndex(s => s === null);
    }
    if (targetIndex === -1) return;

    state.slots[targetIndex] = player;
    renderSlots();
    renderSearchResults();

    // Auto-close if all slots filled
    const filledCount = state.slots.filter(Boolean).length;
    if (filledCount === 5) {
        closeDrawer();
    }
}

function removePlayer(index) {
    state.slots[index] = null;
    renderSlots();
    if (state.drawerOpen) renderSearchResults();
}

function renderSlots() {
    const slotEls = slotsEl.querySelectorAll('.slot');

    slotEls.forEach((el, i) => {
        const player = state.slots[i];

        if (player) {
            const teams = (player.teams || []).slice(0, 3).join(' / ');
            el.className = 'slot filled';
            el.draggable = true;
            el.innerHTML = `
                <span class="slot-rank">${i + 1}</span>
                <div class="slot-info">
                    <div class="slot-name">${player.name}</div>
                    <div class="slot-meta">${player.position}  ·  ${teams}</div>
                </div>
                <span class="slot-stats">${player.ppg} PPG</span>
                <button class="slot-remove" title="Remove">&times;</button>
            `;
        } else {
            el.className = 'slot empty';
            el.draggable = false;
            el.innerHTML = `
                <span class="slot-rank">${i + 1}</span>
                <span class="slot-empty-label">Tap to add</span>
            `;
        }
    });

    exportBtn.disabled = state.slots.filter(Boolean).length === 0;
}

// --- Drag & Drop Reorder ---

let dragIndex = null;

slotsEl.addEventListener('dragstart', (e) => {
    const slot = e.target.closest('.slot');
    if (!slot || !slot.classList.contains('filled')) return;
    dragIndex = parseInt(slot.dataset.rank) - 1;
    slot.style.opacity = '0.4';
    e.dataTransfer.effectAllowed = 'move';
});

slotsEl.addEventListener('dragend', (e) => {
    const slot = e.target.closest('.slot');
    if (slot) slot.style.opacity = '1';
    dragIndex = null;
    slotsEl.querySelectorAll('.slot').forEach(s => s.classList.remove('drag-over'));
});

slotsEl.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    const slot = e.target.closest('.slot');
    if (!slot) return;
    slotsEl.querySelectorAll('.slot').forEach(s => s.classList.remove('drag-over'));
    slot.classList.add('drag-over');
});

slotsEl.addEventListener('dragleave', (e) => {
    const slot = e.target.closest('.slot');
    if (slot && !slot.contains(e.relatedTarget)) {
        slot.classList.remove('drag-over');
    }
});

slotsEl.addEventListener('drop', (e) => {
    e.preventDefault();
    const slot = e.target.closest('.slot');
    if (!slot || dragIndex === null) return;

    const dropIndex = parseInt(slot.dataset.rank) - 1;
    if (dragIndex === dropIndex) return;

    const temp = state.slots[dragIndex];
    state.slots[dragIndex] = state.slots[dropIndex];
    state.slots[dropIndex] = temp;

    renderSlots();
    slotsEl.querySelectorAll('.slot').forEach(s => s.classList.remove('drag-over'));
});

// --- Touch Reorder (mobile) ---

let touchStartY = 0;
let touchSlotIndex = null;
let touchClone = null;

slotsEl.addEventListener('touchstart', (e) => {
    const slot = e.target.closest('.slot.filled');
    if (!slot || e.target.closest('.slot-remove')) return;

    // Long press detection
    const startTime = Date.now();
    const startTouch = e.touches[0];
    touchStartY = startTouch.clientY;

    slot._longPressTimer = setTimeout(() => {
        touchSlotIndex = parseInt(slot.dataset.rank) - 1;
        slot.style.opacity = '0.4';
        navigator.vibrate && navigator.vibrate(30);
    }, 400);
}, { passive: true });

slotsEl.addEventListener('touchmove', (e) => {
    if (touchSlotIndex === null) {
        // Cancel long press if moved too much
        const slot = e.target.closest('.slot');
        if (slot && slot._longPressTimer) {
            const dy = Math.abs(e.touches[0].clientY - touchStartY);
            if (dy > 10) clearTimeout(slot._longPressTimer);
        }
        return;
    }

    const touch = e.touches[0];
    const target = document.elementFromPoint(touch.clientX, touch.clientY);
    const targetSlot = target && target.closest('.slot');

    slotsEl.querySelectorAll('.slot').forEach(s => s.classList.remove('drag-over'));
    if (targetSlot && parseInt(targetSlot.dataset.rank) - 1 !== touchSlotIndex) {
        targetSlot.classList.add('drag-over');
    }
}, { passive: true });

slotsEl.addEventListener('touchend', (e) => {
    const slot = e.target.closest('.slot');
    if (slot && slot._longPressTimer) clearTimeout(slot._longPressTimer);

    if (touchSlotIndex === null) return;

    const touch = e.changedTouches[0];
    const target = document.elementFromPoint(touch.clientX, touch.clientY);
    const targetSlot = target && target.closest('.slot');

    if (targetSlot) {
        const dropIndex = parseInt(targetSlot.dataset.rank) - 1;
        if (dropIndex !== touchSlotIndex) {
            const temp = state.slots[touchSlotIndex];
            state.slots[touchSlotIndex] = state.slots[dropIndex];
            state.slots[dropIndex] = temp;
        }
    }

    touchSlotIndex = null;
    renderSlots();
    slotsEl.querySelectorAll('.slot').forEach(s => s.classList.remove('drag-over'));
});

// --- Export ---

exportBtn.addEventListener('click', async () => {
    const playerIds = state.slots.filter(Boolean).map(p => p.id);
    if (playerIds.length === 0) return;

    exportBtn.textContent = 'Generating...';
    exportBtn.classList.add('loading');

    try {
        const res = await fetch(`${API}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_ids: playerIds }),
        });

        if (!res.ok) throw new Error('Generation failed');

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);

        previewImg.src = url;
        previewDownload.href = url;
        previewOverlay.classList.remove('hidden');
    } catch (err) {
        console.error('Export failed:', err);
    } finally {
        exportBtn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Export Image
        `;
        exportBtn.classList.remove('loading');
    }
});

// --- Preview ---

previewClose.addEventListener('click', () => {
    previewOverlay.classList.add('hidden');
});

previewOverlay.addEventListener('click', (e) => {
    if (e.target === previewOverlay) {
        previewOverlay.classList.add('hidden');
    }
});

// --- Init ---
fetchPlayers('');
