document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const textInput = document.getElementById('text-input');
    const charCount = document.getElementById('char-count');
    const convertBtn = document.getElementById('convert-btn');
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-input');
    const languageSelect = document.getElementById('language-select');
    const resultSection = document.getElementById('result-section');
    const audioElement = document.getElementById('audio-element');
    const downloadBtn = document.getElementById('download-btn');
    const newConversionBtn = document.getElementById('new-conversion-btn');
    const loadingIndicator = document.getElementById('loading-indicator');
    const alertContainer = document.getElementById('alert-container');
    const useAzureToggle = document.getElementById('use-azure-toggle');
    const azureVoiceOptions = document.getElementById('azure-voice-options');
    const voiceSelect = document.getElementById('voice-select');

    // Update character count
    textInput.addEventListener('input', function() {
        charCount.textContent = this.value.length;
    });
    
    // Azure toggle handling
    useAzureToggle.addEventListener('change', function() {
        if (this.checked) {
            azureVoiceOptions.style.display = 'block';
        } else {
            azureVoiceOptions.style.display = 'none';
        }
    });

    // File upload handling
    uploadBtn.addEventListener('click', function() {
        fileInput.click();
    });

    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            
            // Check if it's a text file
            if (!file.type.match('text.*') && !file.name.endsWith('.txt')) {
                showAlert('Please upload a text file (.txt)', 'danger');
                return;
            }
            
            // Check file size (10MB max)
            if (file.size > 10 * 1024 * 1024) {
                showAlert('File is too large. Maximum size is 10MB.', 'danger');
                return;
            }
            
            const reader = new FileReader();
            
            reader.onload = function(e) {
                textInput.value = e.target.result;
                charCount.textContent = textInput.value.length;
                
                if (textInput.value.length > 100000) {
                    showAlert('Text has been truncated to 100,000 characters.', 'warning');
                    textInput.value = textInput.value.substring(0, 100000);
                    charCount.textContent = textInput.value.length;
                }
            };
            
            reader.onerror = function() {
                showAlert('Error reading file', 'danger');
            };
            
            reader.readAsText(file);
        }
    });

    // Convert text to speech
    convertBtn.addEventListener('click', function() {
        const text = textInput.value.trim();
        
        if (!text) {
            showAlert('Please enter some text to convert', 'warning');
            return;
        }
        
        if (text.length > 100000) {
            showAlert('Text is too long. Maximum is 100,000 characters.', 'danger');
            return;
        }
        
        // Get selected language and speed
        const language = languageSelect.value;
        const voiceSpeed = document.querySelector('input[name="voice-speed"]:checked').value;
        
        // Show loading indicator
        loadingIndicator.classList.remove('d-none');
        resultSection.classList.add('d-none');
        convertBtn.disabled = true;
        
        // Prepare form data
        const formData = new FormData();
        formData.append('text', text);
        formData.append('language', language);
        formData.append('voice_speed', voiceSpeed);
        
        // Add Azure options if enabled
        if (useAzureToggle.checked) {
            formData.append('use_azure', 'true');
            formData.append('voice_name', voiceSelect.value);
            // Update loading message to indicate premium voice processing
            document.querySelector('#loading-indicator p').textContent = 'Converting your text to premium speech...';
        } else {
            formData.append('use_azure', 'false');
            // Reset loading message
            document.querySelector('#loading-indicator p').textContent = 'Converting your text to speech...';
        }
        
        // Send request to server
        fetch('/convert', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator
            loadingIndicator.classList.add('d-none');
            convertBtn.disabled = false;
            
            if (data.error) {
                showAlert(data.error, 'danger');
                return;
            }
            
            // Show results and set up audio player
            resultSection.classList.remove('d-none');
            audioElement.src = data.file_path;
            downloadBtn.href = data.file_path;
            
            // Scroll to the result section
            resultSection.scrollIntoView({ behavior: 'smooth' });
            
            // Show appropriate success message
            showAlert(data.message || 'Text converted successfully!', 'success');
        })
        .catch(error => {
            loadingIndicator.classList.add('d-none');
            convertBtn.disabled = false;
            showAlert('Error: ' + (error.message || 'Unknown error occurred'), 'danger');
            console.error('Conversion error:', error);
        });
    });

    // Handle file upload via AJAX
    uploadBtn.addEventListener('click', function() {
        fileInput.click();
    });

    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            
            // Check if it's a valid file type (just a basic check)
            if (!file.type.match('text.*') && !file.name.endsWith('.txt')) {
                showAlert('Please upload a text file', 'danger');
                return;
            }
            
            // Show loading
            loadingIndicator.classList.remove('d-none');
            
            const formData = new FormData();
            formData.append('file', file);
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server responded with status ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                loadingIndicator.classList.add('d-none');
                
                if (data.error) {
                    showAlert(data.error, 'danger');
                    return;
                }
                
                textInput.value = data.text;
                charCount.textContent = textInput.value.length;
                showAlert('File uploaded successfully!', 'success');
            })
            .catch(error => {
                loadingIndicator.classList.add('d-none');
                showAlert('Error uploading file: ' + (error.message || 'Unknown error occurred'), 'danger');
                console.error('Upload error:', error);
            });
        }
    });

    // New conversion button
    newConversionBtn.addEventListener('click', function() {
        resultSection.classList.add('d-none');
        audioElement.pause();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Function to show alerts
    function showAlert(message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertContainer.innerHTML = '';
        alertContainer.appendChild(alert);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    }
});