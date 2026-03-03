document.addEventListener('DOMContentLoaded', function () {
    initParticles();

    const form = document.getElementById('salesForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.querySelector('.btn-text');
    const btnLoader = document.querySelector('.btn-loader');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        submitBtn.disabled = true;
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');
        submitBtn.style.transform = 'scale(0.98)';

        try {
            // ✅ FIXED: send ALL required fields
            const formData = {
                price: parseFloat(document.getElementById('price').value),
                discount: parseFloat(document.getElementById('discount').value),
                sold_units: parseInt(document.getElementById('units').value),
                category: document.getElementById('category').value,
                region: document.getElementById('region').value
            };

            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                showResult(data);
            } else {
                showError(data.error || 'Prediction failed');
            }

        } catch (error) {
            console.error('Error:', error);
            showError('Network error. Please try again.');
        } finally {
            setTimeout(() => {
                submitBtn.disabled = false;
                btnText.classList.remove('hidden');
                btnLoader.classList.add('hidden');
                submitBtn.style.transform = 'scale(1)';
            }, 800);
        }
    });

    function showResult(data) {
        const statusEl = document.getElementById('resultStatus');
        const msgEl = document.getElementById('resultMessage');
        const confidenceFill = document.getElementById('confidenceFill');
        const confidenceText = document.getElementById('confidenceText');
        const salesPredEl = document.getElementById('salesPrediction');
        const salesValueEl = document.querySelector('.prediction-value');

        const confidence = data.confidence;

        if (data.prediction === 1) {
            statusEl.innerHTML = '🚀 HIGHLY VIABLE';
            statusEl.className = 'result-status success';
            msgEl.innerHTML = '✅ <strong>Excellent sales potential!</strong> Strong market fit confirmed.';
            confidenceFill.style.width = `${confidence * 100}%`;
            confidenceFill.style.background = 'var(--success-gradient)';
        } else {
            statusEl.innerHTML = '⚠️ LOW VIABILITY';
            statusEl.className = 'result-status error';
            msgEl.innerHTML = '🔄 <strong>Market challenges detected.</strong> Consider price adjustment.';
            confidenceFill.style.width = `${confidence * 100}%`;
            confidenceFill.style.background = 'var(--error-gradient)';
        }

        salesPredEl.classList.remove('hidden');
        salesValueEl.textContent = `$${data.sales_prediction.toLocaleString()}`;
        confidenceText.textContent = `Model Confidence: ${Math.round(confidence * 100)}%`;

        document.querySelector('.result-card').scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }

    function showError(message) {
        const statusEl = document.getElementById('resultStatus');
        statusEl.innerHTML = '❌ ERROR';
        statusEl.className = 'result-status error';
        document.getElementById('resultMessage').textContent = message;
    }

    function initParticles() {
        const container = document.getElementById('particles');
        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 10 + 's';
            particle.style.animationDuration = (Math.random() * 20 + 15) + 's';
            container.appendChild(particle);
        }
    }
});