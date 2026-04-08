// Global state
let selectedFile = null;
let selectedFormat = null;
let conversionId = null;
let supportedFormats = {};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadSupportedFormats();
    loadStats();
});

function initializeEventListeners() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const targetFormatSelect = document.getElementById('targetFormat');
    const convertBtn = document.getElementById('convertBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const convertAnotherBtn = document.getElementById('convertAnotherBtn');

    // Upload area click
    uploadArea.addEventListener('click', () => fileInput.click());

    // File input change
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFileSelect(file);
        }
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelect(file);
        }
    });

    // Format select
    targetFormatSelect.addEventListener('change', (e) => {
        selectedFormat = e.target.value;
        updateConvertButtonState();
    });

    // Convert button
    convertBtn.addEventListener('click', performConversion);

    // Download button
    downloadBtn.addEventListener('click', performDownload);

    // Convert another
    convertAnotherBtn.addEventListener('click', resetConverter);
}

function handleFileSelect(file) {
    selectedFile = file;

    // Validate file
    const ext = file.name.split('.').pop().toLowerCase();
    const allowedFormats = ['pdf', 'docx', 'pptx', 'doc', 'ppt', 'txt', 'odt'];

    if (!allowedFormats.includes(ext)) {
        showMessage('File format not supported', 'error');
        selectedFile = null;
        return;
    }

    // Display file info
    const fileInfo = document.getElementById('fileInfo');
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    fileInfo.classList.remove('hidden');

    // Update target formats
    updateTargetFormats(ext);

    // Clear previous selection
    document.getElementById('targetFormat').value = '';
    selectedFormat = null;
    updateConvertButtonState();
}

function updateTargetFormats(inputFormat) {
    const select = document.getElementById('targetFormat');
    const availableFormats = supportedFormats[inputFormat] || [];

    // Clear existing options
    select.innerHTML = '<option value="">Select target format</option>';

    // Add available formats
    availableFormats.forEach((format) => {
        const option = document.createElement('option');
        option.value = format;
        option.textContent = format.toUpperCase();
        select.appendChild(option);
    });
}

function updateConvertButtonState() {
    const convertBtn = document.getElementById('convertBtn');
    convertBtn.disabled = !(selectedFile && selectedFormat);
}

async function loadSupportedFormats() {
    try {
        const response = await fetch('/api/supported-formats');
        const data = await response.json();
        supportedFormats = data;
    } catch (error) {
        console.error('Error loading supported formats:', error);
    }
}

async function performConversion() {
    if (!selectedFile || !selectedFormat) {
        showMessage('Please select a file and target format', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('target_format', selectedFormat);

    const convertBtn = document.getElementById('convertBtn');
    const progress = document.getElementById('progress');
    const message = document.getElementById('message');

    convertBtn.disabled = true;
    progress.classList.remove('hidden', 'hidden');
    progress.classList.add('show');
    message.classList.add('hidden');

    try {
        const response = await fetch('/api/upload-and-convert', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            conversionId = data.conversion_id;
            showMessage(data.message, 'success');

            setTimeout(() => {
                progress.classList.add('hidden');
                progress.classList.remove('show');
                showDownloadSection();
                loadStats();
            }, 1500);
        } else {
            showMessage(data.error || 'Conversion failed', 'error');
            progress.classList.add('hidden');
            progress.classList.remove('show');
            convertBtn.disabled = false;
        }
    } catch (error) {
        showMessage(`Error: ${error.message}`, 'error');
        progress.classList.add('hidden');
        progress.classList.remove('show');
        convertBtn.disabled = false;
    }
}

function performDownload() {
    if (!conversionId) {
        showMessage('No file to download', 'error');
        return;
    }

    window.location.href = `/api/download/${conversionId}`;
}

function showDownloadSection() {
    const downloadSection = document.getElementById('downloadSection');
    downloadSection.classList.remove('hidden');
    downloadSection.classList.add('show');
}

function resetConverter() {
    selectedFile = null;
    selectedFormat = null;
    conversionId = null;

    document.getElementById('fileInput').value = '';
    document.getElementById('fileInfo').classList.add('hidden');
    document.getElementById('targetFormat').value = '';
    document.getElementById('targetFormat').innerHTML = '<option value="">Select target format</option>';
    document.getElementById('message').classList.add('hidden');
    document.getElementById('downloadSection').classList.add('hidden');
    document.getElementById('downloadSection').classList.remove('show');
    document.getElementById('convertBtn').disabled = true;
}

function showMessage(text, type = 'info') {
    const message = document.getElementById('message');
    message.textContent = text;
    message.className = `message show ${type}`;

    if (type !== 'error') {
        setTimeout(() => {
            message.classList.add('hidden');
        }, 5000);
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

async function loadStats() {
    try {
        const response = await fetch('/api/conversion-stats');
        const data = await response.json();

        const statsGrid = document.getElementById('stats');
        statsGrid.innerHTML = `
            <div class="stat-item">
                <span class="stat-value">${data.total_conversions}</span>
                <span class="stat-label">Total Conversions</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${data.completed}</span>
                <span class="stat-label">Completed</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${data.failed}</span>
                <span class="stat-label">Failed</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${data.total_size_mb} MB</span>
                <span class="stat-label">Total Size</span>
            </div>
        `;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}
