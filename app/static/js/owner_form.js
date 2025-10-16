(function() {
    'use strict';

    // Scroll to first error on page load
    document.addEventListener('DOMContentLoaded', function() {
        const firstErrorElement = document.querySelector('.is-invalid, .invalid-feedback.d-block, .alert.alert-danger');
        if (firstErrorElement) {
            firstErrorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });

    // Scroll to image section if 'tab=images' is in URL (for after upload redirect)
    document.addEventListener('DOMContentLoaded', function() {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('tab') === 'images') {
            const imageSection = document.getElementById('image-management-section');
            if (imageSection) {
                imageSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    });

    const mapContainer = document.getElementById('map');
    if (mapContainer) {
        const initialCoords = [13.7292, 100.7758]; // KMITL Default
        const map = L.map('map').setView(initialCoords, 15);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        let marker = null;
        const hiddenInput = document.getElementById('location_pin_json_input');
        const searchProvider = new GeoSearch.OpenStreetMapProvider();
        const searchControl = new GeoSearch.GeoSearchControl({
            provider: searchProvider, style: 'bar', showMarker: false, autoClose: true, searchLabel: 'ค้นหาสถานที่...',
        });
        map.addControl(searchControl);
        function updateMarkerAndInput(lat, lng) {
            if (marker) map.removeLayer(marker);
            marker = L.marker([lat, lng]).addTo(map);
            const geoJsonData = { "type": "Point", "coordinates": [lng, lat] };
            hiddenInput.value = JSON.stringify(geoJsonData);
        }
        map.on('geosearch/showlocation', function(result) {
            const { x, y } = result.location;
            map.setView([y, x], 16);
            updateMarkerAndInput(y, x);
        });
        try {
            const formJsonData = document.getElementById('location_pin_json_input').value;
            let existingData = null;
            if (formJsonData) { try { existingData = JSON.parse(formJsonData); } catch(e) {} }
            if (!existingData) {
                const propDataStr = mapContainer.dataset.propLocation;
                if (propDataStr) {
                    existingData = JSON.parse(propDataStr);
                }
            }
            if (existingData && existingData.type === 'Point' && Array.isArray(existingData.coordinates)) {
                const [lng, lat] = existingData.coordinates;
                updateMarkerAndInput(lat, lng);
                map.setView([lat, lng], 16);
            }
        } catch (e) { console.error("Could not parse existing location data:", e); }
        map.on('click', function(e) { updateMarkerAndInput(e.latlng.lat, e.latlng.lng); });
    }

    const additionalInfoTextarea = document.getElementById('additionalInfo');
    const charCountDisplay = document.getElementById('charCount');
    if (additionalInfoTextarea && charCountDisplay) {
        const maxLength = 5000;
        function updateCharCount() {
            const currentLength = additionalInfoTextarea.value.length;
            charCountDisplay.textContent = `${currentLength} / ${maxLength}`;
            charCountDisplay.classList.toggle('text-danger', currentLength > maxLength);
        }
        updateCharCount();
        additionalInfoTextarea.addEventListener('input', updateCharCount);
    }

    const roomTypeSelect = document.getElementById('room_type_select');
    const otherRoomTypeContainer = document.getElementById('other_room_type_container');
    const otherRoomTypeInput = document.querySelector('[name="other_room_type"]');
    function toggleOtherRoomType() {
        if (roomTypeSelect && otherRoomTypeContainer) {
            const isOther = roomTypeSelect.value === 'other';
            otherRoomTypeContainer.style.display = isOther ? 'block' : 'none';
            if (!isOther && otherRoomTypeInput) { otherRoomTypeInput.value = ''; }
        }
    }
    document.addEventListener('DOMContentLoaded', function() {
        if (roomTypeSelect) {
            toggleOtherRoomType();
            roomTypeSelect.addEventListener('change', toggleOtherRoomType);
        }
    });

    // --- Drag and Drop for EDIT page ---
    const gallery = document.getElementById('gallery');
    if (gallery) {
        let dragEl = null;

        const updatePositions = () => {
            const orderedIds = Array.from(gallery.querySelectorAll('[draggable="true"]')).map(el => parseInt(el.dataset.imageId, 10));
            
            // Update badge text immediately
            gallery.querySelectorAll('.badge').forEach((badge, index) => {
                badge.textContent = `ลำดับ ${index + 1}`;
            });
            
            // Send to server
            const propId = gallery.dataset.propId;
            const url = `/owner/property/${propId}/images/reorder`;
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ order: orderedIds })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && typeof createToast === 'function') {
                    createToast(data.message, 'success');
                } else if (!data.success && typeof createToast === 'function') {
                    createToast(data.message || 'เกิดข้อผิดพลาดในการจัดเรียง', 'danger');
                }
            })
            .catch(error => {
                console.error('Error reordering images:', error);
                if (typeof createToast === 'function') {
                    createToast('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้', 'danger');
                }
            });
        };

        gallery.addEventListener('dragstart', (e) => {
            const cardCol = e.target.closest('[draggable="true"]');
            if (cardCol) {
                dragEl = cardCol;
                e.dataTransfer.effectAllowed = 'move';
                setTimeout(() => cardCol.classList.add('dragging'), 0);
            }
        });

        gallery.addEventListener('dragover', (e) => {
            e.preventDefault();
            const targetCol = e.target.closest('[draggable="true"]');
            if (targetCol && targetCol !== dragEl) {
                const rect = targetCol.getBoundingClientRect();
                const next = (e.clientY - rect.top) / rect.height > 0.5;
                gallery.insertBefore(dragEl, next ? targetCol.nextSibling : targetCol);
            }
        });

        gallery.addEventListener('dragend', (e) => {
            if (dragEl) {
                dragEl.classList.remove('dragging');
                dragEl = null;
                updatePositions();
            }
        });
    }

    // --- Delete/Undo for EDIT page ---
    const imagesToDeleteInput = document.getElementById('images-to-delete-input');
    const imageManagementSection = document.getElementById('image-management-section');
    if (imageManagementSection && imagesToDeleteInput) {
        let imagesToDelete = new Set();
        function updateHiddenInput() {
            imagesToDeleteInput.value = Array.from(imagesToDelete).join(',');
        }
        imageManagementSection.addEventListener('click', function(e) {
            const deleteBtn = e.target.closest('.delete-image-btn');
            const undoBtn = e.target.closest('.undo-delete-btn');
            if (deleteBtn) {
                const imageId = deleteBtn.dataset.imageId;
                const card = deleteBtn.closest('.card');
                imagesToDelete.add(imageId);
                card.style.opacity = '0.4';
                deleteBtn.style.display = 'none';
                card.querySelector('.undo-delete-btn').style.display = 'inline-block';
                updateHiddenInput();
            }
            if (undoBtn) {
                const imageId = undoBtn.dataset.imageId;
                const card = undoBtn.closest('.card');
                imagesToDelete.delete(imageId);
                card.style.opacity = '1';
                undoBtn.style.display = 'none';
                card.querySelector('.delete-image-btn').style.display = 'inline-block';
                updateHiddenInput();
            }
        });
    }

    // --- Image preview and Drag & Drop for CREATE page ---
    const imageInput = document.getElementById('image-input');
    const addImageBtn = document.getElementById('add-image-btn');
    const previewContainer = document.getElementById('image-preview-container');
    const mainForm = document.getElementById('main-property-form');
    const fileCollector = document.getElementById('image-file-list');
    
    if (imageInput && addImageBtn && previewContainer && mainForm && fileCollector) {
        const maxImages = parseInt(mainForm.dataset.maxImages || '6', 10);
        let fileStore = new Map();
        const storageKey = `fileStore_${window.location.pathname}`;

        // --- Helper functions for session storage (to keep images on page refresh) ---
        const fileToBase64 = (file) => new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
        const base64ToFile = (dataUrl, filename) => {
            const arr = dataUrl.split(',');
            const mime = arr[0].match(/:(.*?);/)[1];
            const bstr = atob(arr[1]);
            let n = bstr.length;
            const u8arr = new Uint8Array(n);
            while(n--) { u8arr[n] = bstr.charCodeAt(n); }
            return new File([u8arr], filename, {type:mime});
        };
        const saveFileStore = async () => {
            const serializable = [];
            document.querySelectorAll('#image-preview-container .col').forEach(col => {
                const key = col.dataset.key;
                const file = fileStore.get(key);
                if (file) {
                    serializable.push([key, file]);
                }
            });
            const dataToStore = [];
            for (const [key, file] of serializable) {
                const base64 = await fileToBase64(file);
                dataToStore.push([key, { name: file.name, data: base64 }]);
            }
            sessionStorage.setItem(storageKey, JSON.stringify(dataToStore));
        };
        const loadFileStore = () => {
            const stored = sessionStorage.getItem(storageKey);
            if (stored) {
                try {
                    const parsed = JSON.parse(stored);
                    fileStore.clear();
                    for (const [key, fileData] of parsed) {
                        const file = base64ToFile(fileData.data, fileData.name);
                        fileStore.set(key, file);
                    }
                } catch(e) {
                    console.error("Failed to parse file store from sessionStorage", e);
                    sessionStorage.removeItem(storageKey);
                }
            }
        };
        
        const renderPreviews = () => {
            previewContainer.innerHTML = '';
            let index = 1;
            fileStore.forEach((file, key) => {
                const col = document.createElement('div');
                col.className = 'col';
                col.setAttribute('draggable', 'true');
                col.dataset.key = key;
                col.innerHTML = `
                    <div class="card h-100">
                        <img src="${URL.createObjectURL(file)}" class="card-img-top" style="height: 150px; object-fit: cover;" alt="Preview">
                        <div class="card-body p-2 d-flex justify-content-between align-items-center">
                            <span class="badge text-bg-light">ลำดับ ${index++}</span>
                            <button type="button" class="btn btn-sm btn-outline-danger remove-img-btn" data-key="${key}">ลบ</button>
                        </div>
                    </div>`;
                previewContainer.appendChild(col);
            });
            updatePreviewOrderIndices();
        };

        const updatePreviewOrderIndices = () => {
            document.querySelectorAll('#image-preview-container .badge').forEach((badge, index) => {
                badge.textContent = `ลำดับ ${index + 1}`;
            });
        };

        addImageBtn.addEventListener('click', () => {
            if (imageInput.files.length > 0) {
                for(const file of imageInput.files){
                    if (fileStore.size >= maxImages) {
                        alert(`สามารถอัปโหลดได้สูงสุด ${maxImages} รูปเท่านั้น`);
                        break;
                    }
                    const key = `${Date.now()}-${file.name}`;
                    fileStore.set(key, file);
                }
                renderPreviews();
                imageInput.value = '';
                saveFileStore();
            } else {
                alert('กรุณาเลือกไฟล์รูปภาพก่อน');
            }
        });

        previewContainer.addEventListener('click', (e) => {
            const removeBtn = e.target.closest('.remove-img-btn');
            if (removeBtn) {
                const key = removeBtn.dataset.key;
                fileStore.delete(key);
                removeBtn.closest('.col').remove();
                updatePreviewOrderIndices();
                saveFileStore();
            }
        });

        // --- Drag & Drop logic for CREATE page ---
        let dragEl = null;
        previewContainer.addEventListener('dragstart', (e) => {
            const col = e.target.closest('[draggable="true"]');
            if (col) {
                dragEl = col;
                e.dataTransfer.effectAllowed = 'move';
            }
        });
        previewContainer.addEventListener('dragover', (e) => {
            e.preventDefault();
            const targetCol = e.target.closest('[draggable="true"]');
            if (targetCol && targetCol !== dragEl) {
                const rect = targetCol.getBoundingClientRect();
                const next = (e.clientY - rect.top) / rect.height > 0.5;
                previewContainer.insertBefore(dragEl, next ? targetCol.nextSibling : targetCol);
            }
        });
        previewContainer.addEventListener('dragend', () => {
            dragEl = null;
            updatePreviewOrderIndices();
            saveFileStore(); // Save the new order
        });

        mainForm.addEventListener('submit', (e) => {
            const dataTransfer = new DataTransfer();
            const orderedKeys = Array.from(previewContainer.querySelectorAll('[data-key]')).map(el => el.dataset.key);
            
            orderedKeys.forEach(key => {
                const file = fileStore.get(key);
                if (file) {
                    dataTransfer.items.add(file);
                }
            });

            fileCollector.files = dataTransfer.files;
            sessionStorage.removeItem(storageKey); // Clear storage on successful submit
        });

        const cancelButton = document.getElementById('cancel-form-btn');
        if (cancelButton) {
            cancelButton.addEventListener('click', function() {
                sessionStorage.removeItem(storageKey);
            });
        }
        
        document.addEventListener('DOMContentLoaded', () => {
            const flashMessages = document.querySelectorAll('.flash-messages .alert');
            flashMessages.forEach(flash => {
                if (flash.textContent.includes('clear_form_storage')) {
                    sessionStorage.removeItem(storageKey);
                    flash.style.display = 'none';
                }
            });
            loadFileStore();
            renderPreviews();
        });
    }
})();