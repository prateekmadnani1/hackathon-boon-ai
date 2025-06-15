document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file');
    const submitBtn = document.getElementById('submit-btn');
    const spinner = document.getElementById('spinner');
    const statusContainer = document.getElementById('status-container');
    const resultsContainer = document.getElementById('results-container');
    const totalEntitiesEl = document.getElementById('total-entities');
    const mappedEntitiesEl = document.getElementById('mapped-entities');
    const nameChangesEl = document.getElementById('name-changes');
    const entitiesJsonEl = document.getElementById('entities-json');
    const mappingJsonEl = document.getElementById('mapping-json');

    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Validate file input
        if (!fileInput.files[0]) {
            alert('Please select a file to upload.');
            return;
        }

        // Show processing indicator
        submitBtn.disabled = true;
        spinner.classList.remove('d-none');
        statusContainer.classList.remove('d-none');
        resultsContainer.classList.add('d-none');

        // Create form data
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        // Send request
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide processing indicator
            statusContainer.classList.add('d-none');
            
            // Show results
            resultsContainer.classList.remove('d-none');
            
            // Update summary counts
            totalEntitiesEl.textContent = data.total_entities;
            mappedEntitiesEl.textContent = data.mapped_entities;
            nameChangesEl.textContent = data.name_changes_detected;
            
            // Format and display JSON
            entitiesJsonEl.textContent = formatEntitiesJson(data.entities);
            mappingJsonEl.textContent = formatMappingJson(data.mapping_results);
        })
        .catch(error => {
            console.error('Error:', error);
            statusContainer.classList.add('d-none');
            alert('Error processing document: ' + error.message);
        })
        .finally(() => {
            // Re-enable submit button
            submitBtn.disabled = false;
            spinner.classList.add('d-none');
        });
    });

    // Format entities JSON with syntax highlighting
    function formatEntitiesJson(entities) {
        if (!entities || entities.length === 0) {
            return 'No entities found.';
        }
        
        return JSON.stringify(entities, null, 2);
    }
    
    // Format mapping results JSON with syntax highlighting
    function formatMappingJson(mappingResults) {
        if (!mappingResults || mappingResults.length === 0) {
            return 'No mapping results available.';
        }
        
        // Format mapping results for better readability
        const formatted = mappingResults.map(result => {
            return {
                original_entity: result.original_entity.name,
                entity_type: result.original_entity.type,
                mapped_to: result.mapped_entity_name || 'Not Mapped',
                confidence: result.confidence.toFixed(2),
                name_change_detected: result.name_change_detected,
                name_change: result.name_change_detected ? 
                    `${result.name_change.previous_name} → ${result.name_change.current_name}` : null
            };
        });
        
        return JSON.stringify(formatted, null, 2);
    }
    
    // Handle file input change (optional preview)
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
            const fileName = fileInput.files[0].name;
            const fileLabel = document.querySelector('.form-label');
            fileLabel.textContent = `Selected file: ${fileName}`;
        }
    });
}); 