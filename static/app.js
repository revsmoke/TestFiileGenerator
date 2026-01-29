document.addEventListener('DOMContentLoaded', () => {
    const chips = document.querySelectorAll('.chip');
    const generateBtn = document.getElementById('generate-btn');
    const promptInput = document.getElementById('prompt');
    const resultsSection = document.getElementById('results');
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
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to generate file');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            // Set up download
            const ext = selectedType === 'excel' ? 'xlsx' : selectedType === 'image' ? 'png' : 'pdf';
            downloadLink.href = url;
            downloadLink.download = `test_asset_${Date.now()}.${ext}`;

            // Show results
            resultsSection.classList.remove('hidden');
            resultsSection.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            console.error(error);
            alert('Error: ' + error.message);
        } finally {
            generateBtn.disabled = false;
            loader.classList.add('hidden');
            btnText.classList.remove('hidden');
        }
    });
});
