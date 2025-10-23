// Custom Personality Modal Handler
document.addEventListener('DOMContentLoaded', function() {
    const personalityInput = document.getElementById('personalityInput');
    const charCount = document.getElementById('charCount');
    const saveBtn = document.getElementById('savePersonalityBtn');
    const clearBtn = document.getElementById('clearPersonalityBtn');
    const statusDiv = document.getElementById('personalityStatus');
    const modal = document.getElementById('personalityModal');

    // Character counter
    personalityInput.addEventListener('input', function() {
        const count = this.value.length;
        charCount.textContent = `${count} / 3,000`;
        
        if (count > 2800) {
            charCount.classList.remove('text-info');
            charCount.classList.add('text-warning');
        } else {
            charCount.classList.remove('text-warning');
            charCount.classList.add('text-info');
        }
    });

    // Load personality when modal opens
    modal.addEventListener('show.bs.modal', function() {
        loadPersonality();
    });

    // Save personality
    saveBtn.addEventListener('click', function() {
        const personality = personalityInput.value.trim();
        
        if (personality.length > 3000) {
            showStatus('error', 'Personality text exceeds 3,000 character limit!');
            return;
        }

        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Saving...';

        fetch('/api/personality/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ personality: personality })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showStatus('success', data.message || 'Custom personality saved successfully!');
                setTimeout(() => {
                    bootstrap.Modal.getInstance(modal).hide();
                }, 1500);
            } else {
                showStatus('error', data.error || 'Failed to save personality');
            }
        })
        .catch(error => {
            showStatus('error', 'Network error: ' + error.message);
        })
        .finally(() => {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-save me-1"></i>Save Personality';
        });
    });

    // Clear personality
    clearBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to clear your custom personality? This will reset Roboto to default behavior.')) {
            personalityInput.value = '';
            charCount.textContent = '0 / 3,000';
            
            fetch('/api/personality/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ personality: '' })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus('success', 'Custom personality cleared!');
                } else {
                    showStatus('error', data.error || 'Failed to clear personality');
                }
            })
            .catch(error => {
                showStatus('error', 'Network error: ' + error.message);
            });
        }
    });

    // Load personality from server
    function loadPersonality() {
        fetch('/api/personality/load')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                personalityInput.value = data.personality || '';
                charCount.textContent = `${data.character_count || 0} / 3,000`;
                
                if (data.character_count > 2800) {
                    charCount.classList.remove('text-info');
                    charCount.classList.add('text-warning');
                }
            } else {
                console.error('Failed to load personality:', data.error);
            }
        })
        .catch(error => {
            console.error('Error loading personality:', error);
        });
    }

    // Show status message
    function showStatus(type, message) {
        statusDiv.style.display = 'block';
        statusDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
        statusDiv.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>${message}`;
        
        if (type === 'success') {
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 3000);
        }
    }
});
