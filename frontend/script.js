const API_BASE = 'http://localhost:5000/api';

let selectedFile = null;
let uploadedFilename = null;

// Upload area handling
const uploadArea = document.getElementById('uploadArea');
const videoFile = document.getElementById('videoFile');
const uploadStatus = document.getElementById('uploadStatus');

uploadArea.addEventListener('click', () => videoFile.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('active');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('active');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('active');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

videoFile.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    if (!file.type.startsWith('video/')) {
        showStatus('Vui lòng chọn file video', 'error');
        return;
    }

    if (file.size > 500 * 1024 * 1024) {
        showStatus('File quá lớn (tối đa 500MB)', 'error');
        return;
    }

    selectedFile = file;
    uploadArea.innerHTML = `<p>✅ ${file.name}</p>`;
    showStatus(`Đã chọn: ${file.name}`, 'success');
    
    uploadVideo(file);
}

async function uploadVideo(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const data = await response.json();
        uploadedFilename = data.filename;
        document.getElementById('processBtn').disabled = false;
        showStatus(`Video đã sẵn sàng (${data.duration.toFixed(2)}s)`, 'success');
    } catch (error) {
        showStatus('Lỗi upload: ' + error.message, 'error');
        document.getElementById('processBtn').disabled = true;
    }
}

function showStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = `status ${type}`;
}

// Process button
document.getElementById('processBtn').addEventListener('click', processVideo);

async function processVideo() {
    if (!uploadedFilename) {
        showStatus('Vui lòng chọn video trước', 'error');
        return;
    }

    const targetLanguage = document.getElementById('targetLanguage').value;
    
    // Show progress section
    document.getElementById('progressSection').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('processBtn').disabled = true;

    try {
        updateProgress(25, 'Bước 1/4: Nhận dạng văn bản (OCR)...');
        
        const response = await fetch(`${API_BASE}/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: uploadedFilename,
                target_language: targetLanguage
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Processing failed');
        }

        updateProgress(50, 'Bước 2/4: Dịch văn bản...');
        setTimeout(() => updateProgress(75, 'Bước 3/4: Tạo giọng đọc...'), 1000);
        setTimeout(() => updateProgress(100, 'Bước 4/4: Ghép video...'), 2000);

        const data = await response.json();
        
        setTimeout(() => {
            showResults(data.output_file);
        }, 3000);
    } catch (error) {
        showStatus('Lỗi xử lý: ' + error.message, 'error');
        document.getElementById('progressSection').style.display = 'none';
        document.getElementById('processBtn').disabled = false;
    }
}

function updateProgress(percent, text) {
    document.getElementById('progressFill').style.width = percent + '%';
    document.getElementById('progressText').textContent = text;
}

function showResults(outputFile) {
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('resultMessage').textContent = '✅ Video đã được xử lý thành công!';
    
    const downloadBtn = document.getElementById('downloadBtn');
    downloadBtn.href = `${API_BASE}/download/${outputFile}`;
    downloadBtn.download = outputFile;
}
