document.addEventListener('DOMContentLoaded', () => {
    const chips = document.querySelectorAll('.chip');
    const generateBtn = document.getElementById('generate-btn');
    const promptInput = document.getElementById('prompt');
    const resultsSection = document.getElementById('results');
    const errorSection = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const downloadLink = document.getElementById('download-link');
    const loader = document.querySelector('.loader');
    const btnText = document.querySelector('.btn-text');

    let selectedType = 'pdf';

    // Type Selection
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            chips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            selectedType = chip.dataset.type;
        });
    });

    // Generate Logic
    generateBtn.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();
        if (!prompt) {
            alert('Please enter a description for the test file.');
            return;
        }

        // UI State: Loading
        generateBtn.disabled = true;
        loader.classList.remove('hidden');
        btnText.classList.add('hidden');
        resultsSection.classList.add('hidden');
        errorSection.classList.add('hidden');

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    file_type: selectedType,
                    prompt: prompt
                })
            });

            if (!response.ok) {
                let errorMsg = 'Failed to generate file';
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.detail || errorMsg;
                } catch (e) {
                    errorMsg = await response.text() || errorMsg;
                }
                throw new Error(errorMsg);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            // Set up download
            const ext = selectedType === 'excel' ? 'xlsx' : (selectedType === 'image' || selectedType === 'photo') ? 'png' : 'pdf';
            downloadLink.href = url;
            downloadLink.download = `test_asset_${Date.now()}.${ext}`;

            // Show results
            resultsSection.classList.remove('hidden');
            resultsSection.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            console.error(error);
            errorText.textContent = error.message;
            errorSection.classList.remove('hidden');
            errorSection.scrollIntoView({ behavior: 'smooth' });
        } finally {
            generateBtn.disabled = false;
            loader.classList.add('hidden');
            btnText.classList.remove('hidden');
        }
    });
});
