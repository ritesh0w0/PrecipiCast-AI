document.addEventListener('DOMContentLoaded', () => {
    // Form and Buttons
    const form = document.getElementById('predictionForm');
    const submitBtn = document.getElementById('submitBtn');
    const resetBtn = document.getElementById('resetBtn');
    const copyCurlBtn = document.getElementById('copyCurlBtn');
    const presetBtns = document.querySelectorAll('.preset-btn');

    // UI Result Components
    const resultPlaceholder = document.getElementById('resultPlaceholder');
    const resultContent = document.getElementById('resultContent');
    const predictionValue = document.getElementById('predictionValue');
    const categoryBadge = document.getElementById('categoryBadge');
    const predictionBar = document.getElementById('predictionBar');
    const insightHeading = document.getElementById('insightHeading');
    const insightText = document.getElementById('insightText');
    const statusLabel = document.querySelector('.status-label');
    const modelBadgeSpan = document.querySelector('.model-badge span');

    // RWH Calculator Elements
    const rwhArea = document.getElementById('rwh_area');
    const rwhRoofType = document.getElementById('rwh_roof_type');
    const rwhLiters = document.getElementById('rwhLiters');
    const rwhM3 = document.getElementById('rwhM3');
    const rwhDays = document.getElementById('rwhDays');
    const rwhTank = document.getElementById('rwhTank');
    const rwhTankDesc = document.getElementById('rwhTankDesc');

    let currentPredictionMm = 0.0;
    const isStaticDeploy = window.location.hostname.includes('github.io') || window.location.protocol === 'file:';

    // Update initial status indicators based on hosting environment
    if (isStaticDeploy) {
        if (statusLabel) statusLabel.textContent = "Web Engine Online";
        if (modelBadgeSpan) modelBadgeSpan.textContent = "Client-Side XGBoost • 11 Features";
    }

    // Presets Definition
    const presets = {
        dry: {
            sw_down: 24.0, sw_direct: 18.0, temp_avg: 32.0, temp_max: 35.0,
            temp_min: 27.0, temp_dew: 18.0, temp_wet: 21.0, humidity_rel: 45.0,
            humidity_spec: 12.0, wind_speed: 3.5, soil_wetness: 0.25
        },
        default: {
            sw_down: 18.5, sw_direct: 10.2, temp_avg: 27.5, temp_max: 30.1,
            temp_min: 25.0, temp_dew: 24.1, temp_wet: 25.8, humidity_rel: 85.5,
            humidity_spec: 19.1, wind_speed: 2.5, soil_wetness: 0.85
        },
        monsoon: {
            sw_down: 5.0, sw_direct: 1.0, temp_avg: 25.0, temp_max: 26.0,
            temp_min: 24.0, temp_dew: 24.5, temp_wet: 24.8, humidity_rel: 98.0,
            humidity_spec: 22.0, wind_speed: 5.0, soil_wetness: 0.98
        },
        storm: {
            sw_down: 1.5, sw_direct: 0.2, temp_avg: 23.0, temp_max: 24.0,
            temp_min: 22.0, temp_dew: 22.8, temp_wet: 23.0, humidity_rel: 99.0,
            humidity_spec: 24.0, wind_speed: 12.0, soil_wetness: 1.00
        }
    };

    function populateForm(values) {
        Object.keys(values).forEach(key => {
            const input = document.getElementById(key);
            if (input) input.value = values[key];
        });
    }

    // Handle Preset Clicks
    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            presetBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const presetKey = btn.dataset.preset;
            if (presets[presetKey]) {
                populateForm(presets[presetKey]);
            }
        });
    });

    // Reset Form to Default
    resetBtn.addEventListener('click', () => {
        resetBtn.style.transform = 'rotate(-180deg)';
        setTimeout(() => resetBtn.style.transform = '', 300);
        
        presetBtns.forEach(b => b.classList.remove('active'));
        document.querySelector('[data-preset="default"]').classList.add('active');
        populateForm(presets.default);

        resultContent.classList.add('hidden');
        resultPlaceholder.classList.remove('hidden');
        currentPredictionMm = 0.0;
    });

    // Collect Input Payload
    function getFormData() {
        return {
            sw_down: parseFloat(document.getElementById('sw_down').value),
            sw_direct: parseFloat(document.getElementById('sw_direct').value),
            temp_avg: parseFloat(document.getElementById('temp_avg').value),
            temp_max: parseFloat(document.getElementById('temp_max').value),
            temp_min: parseFloat(document.getElementById('temp_min').value),
            temp_dew: parseFloat(document.getElementById('temp_dew').value),
            temp_wet: parseFloat(document.getElementById('temp_wet').value),
            humidity_rel: parseFloat(document.getElementById('humidity_rel').value),
            humidity_spec: parseFloat(document.getElementById('humidity_spec').value),
            wind_speed: parseFloat(document.getElementById('wind_speed').value),
            soil_wetness: parseFloat(document.getElementById('soil_wetness').value)
        };
    }

    // Client-Side XGBoost Inference Engine (Used on GitHub Pages and Offline)
    function predictClientSide(formData) {
        if (!window.PRECIPICAST_MODEL) {
            throw new Error("Embedded model weights not available.");
        }
        const { base_score, scaler, trees } = window.PRECIPICAST_MODEL;
        const raw = [
            formData.sw_down,
            formData.sw_direct,
            formData.temp_avg,
            formData.temp_dew,
            formData.temp_wet,
            formData.temp_max,
            formData.temp_min,
            formData.humidity_rel,
            formData.humidity_spec,
            formData.wind_speed,
            formData.soil_wetness
        ];

        // 1. StandardScaler Transformation
        const scaled = raw.map((val, idx) => (val - scaler.mean[idx]) / scaler.scale[idx]);

        // 2. Ensemble Tree Traversal across 300 Boosting Estimators
        let total = base_score;
        for (let i = 0; i < trees.length; i++) {
            const { l, r, f, c } = trees[i];
            let node = 0;
            while (l[node] !== -1) {
                if (scaled[f[node]] < c[node]) {
                    node = l[node];
                } else {
                    node = r[node];
                }
            }
            total += c[node];
        }

        // 3. Non-Negative Rectification
        const predictionMm = Math.max(0.0, total);

        // 4. Intensity Classification
        let category = "No Rain";
        let intensityDesc = "Clear skies and dry atmospheric conditions.";
        if (predictionMm >= 75.0) {
            category = "Torrential / Storm Rain";
            intensityDesc = "Severe storm event; monitor catchment overflow buffers.";
        } else if (predictionMm >= 35.0) {
            category = "Heavy Rain";
            intensityDesc = "Intense precipitation; strong rainwater harvesting yields.";
        } else if (predictionMm >= 10.0) {
            category = "Moderate Rain";
            intensityDesc = "Steady, significant rainfall across catchment areas.";
        } else if (predictionMm >= 0.1) {
            category = "Light Rain";
            intensityDesc = "Scattered drizzle or light showers expected.";
        }

        return {
            success: true,
            prediction_mm: parseFloat(predictionMm.toFixed(2)),
            category: category,
            intensity_description: intensityDesc,
            engine: "client-side-xgboost"
        };
    }

    // Update Rainwater Harvesting (RWH) Calculations
    function updateRwhCalculations() {
        const area = parseFloat(rwhArea.value) || 0;
        const runoffCoeff = parseFloat(rwhRoofType.value) || 0.85;
        const filterEfficiency = 0.90; // Standard filtration / first-flush retention

        // Formula: Liters = Rainfall (mm) * Catchment Area (m2) * Runoff Coefficient * Filter Efficiency
        const liters = Math.max(0, currentPredictionMm * area * runoffCoeff * filterEfficiency);
        const m3 = liters / 1000;
        
        // Household offset days based on 3-person home at 150L/day baseline
        const dailyNeed = 3 * 150;
        const days = liters > 0 ? (liters / dailyNeed).toFixed(1) : 0;

        rwhLiters.textContent = `${Math.round(liters).toLocaleString()} L`;
        rwhM3.textContent = `${m3.toFixed(2)} m³`;
        rwhDays.textContent = `${days} Days`;

        // Tank recommendation
        if (liters <= 0) {
            rwhTank.textContent = "Standby";
            rwhTankDesc.textContent = "No harvesting yield";
        } else if (liters < 1000) {
            rwhTank.textContent = "1,000 L";
            rwhTankDesc.textContent = "Compact Rain Barrel";
        } else if (liters < 3000) {
            rwhTank.textContent = "3,000 L";
            rwhTankDesc.textContent = "Slimline Wall Tank";
        } else if (liters < 6000) {
            rwhTank.textContent = "5,000 L";
            rwhTankDesc.textContent = "Cylindrical Poly Tank";
        } else if (liters < 12000) {
            rwhTank.textContent = "10,000 L";
            rwhTankDesc.textContent = "Dual Tank Array";
        } else {
            rwhTank.textContent = "15,000+ L";
            rwhTankDesc.textContent = "Underground Cistern";
        }
    }

    rwhArea.addEventListener('input', updateRwhCalculations);
    rwhRoofType.addEventListener('change', updateRwhCalculations);

    // Form Submission for Prediction
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Loading state
        submitBtn.disabled = true;
        submitBtn.querySelector('.btn-text').textContent = "Analyzing Atmosphere...";
        submitBtn.querySelector('.spinner').classList.remove('hidden');
        submitBtn.querySelector('.btn-icon').classList.add('hidden');

        const payload = getFormData();

        try {
            let data = null;

            // If on GitHub Pages or static local file, use the in-browser XGBoost engine directly
            if (isStaticDeploy) {
                data = predictClientSide(payload);
            } else {
                // Otherwise try Flask server first
                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });

                    if (response.ok) {
                        data = await response.json();
                    } else {
                        // Fallback to client-side engine if server returned an error
                        data = predictClientSide(payload);
                    }
                } catch (netErr) {
                    // Fallback to client-side engine if backend is offline or static
                    data = predictClientSide(payload);
                }
            }

            // Smooth transition
            setTimeout(() => {
                displayResult(data);
                submitBtn.disabled = false;
                submitBtn.querySelector('.btn-text').textContent = "Execute AI Rainfall Forecast";
                submitBtn.querySelector('.spinner').classList.add('hidden');
                submitBtn.querySelector('.btn-icon').classList.remove('hidden');
            }, 300);

        } catch (err) {
            alert(`Prediction Error: ${err.message}`);
            submitBtn.disabled = false;
            submitBtn.querySelector('.btn-text').textContent = "Execute AI Rainfall Forecast";
            submitBtn.querySelector('.spinner').classList.add('hidden');
            submitBtn.querySelector('.btn-icon').classList.remove('hidden');
        }
    });

    // Display Result
    function displayResult(data) {
        currentPredictionMm = data.prediction_mm;
        predictionValue.textContent = currentPredictionMm.toFixed(2);

        // Category Badge
        categoryBadge.textContent = data.category;
        if (currentPredictionMm < 0.1) {
            categoryBadge.style.color = '#94a3b8';
            categoryBadge.style.borderColor = 'rgba(148, 163, 184, 0.3)';
            categoryBadge.style.background = 'rgba(148, 163, 184, 0.1)';
        } else if (currentPredictionMm < 10) {
            categoryBadge.style.color = '#38bdf8';
            categoryBadge.style.borderColor = 'rgba(56, 189, 248, 0.3)';
            categoryBadge.style.background = 'rgba(56, 189, 248, 0.1)';
        } else if (currentPredictionMm < 35) {
            categoryBadge.style.color = '#60a5fa';
            categoryBadge.style.borderColor = 'rgba(96, 165, 250, 0.3)';
            categoryBadge.style.background = 'rgba(96, 165, 250, 0.1)';
        } else if (currentPredictionMm < 75) {
            categoryBadge.style.color = '#818cf8';
            categoryBadge.style.borderColor = 'rgba(129, 140, 248, 0.3)';
            categoryBadge.style.background = 'rgba(129, 140, 248, 0.1)';
        } else {
            categoryBadge.style.color = '#f43f5e';
            categoryBadge.style.borderColor = 'rgba(244, 63, 94, 0.3)';
            categoryBadge.style.background = 'rgba(244, 63, 94, 0.15)';
        }

        // Progress Bar (scaled to 100mm max visually)
        const progressPercent = Math.min(100, (currentPredictionMm / 100) * 100);
        predictionBar.style.width = `${progressPercent}%`;

        // Insight Texts
        insightHeading.textContent = `${data.category} Event`;
        insightText.textContent = data.intensity_description;

        // Calculate RWH
        updateRwhCalculations();

        // Toggle Views
        resultPlaceholder.classList.add('hidden');
        resultContent.classList.remove('hidden');
    }

    // Copy cURL Button
    copyCurlBtn.addEventListener('click', () => {
        const payload = getFormData();
        const curlCmd = `curl -X POST "http://localhost:5000/predict" \\\n  -H "Content-Type: application/json" \\\n  -d '${JSON.stringify(payload)}'`;
        
        navigator.clipboard.writeText(curlCmd).then(() => {
            const originalHtml = copyCurlBtn.innerHTML;
            copyCurlBtn.innerHTML = '<i class="ph-bold ph-check"></i> <span>Copied!</span>';
            setTimeout(() => {
                copyCurlBtn.innerHTML = originalHtml;
            }, 2000);
        }).catch(() => {
            alert("Could not copy cURL to clipboard.");
        });
    });

    // Auto-trigger if ?preview=true is in URL (used for automated screenshot generation)
    if (window.location.search.includes('preview=true')) {
        setTimeout(() => {
            const monsoonBtn = document.querySelector('[data-preset="monsoon"]');
            if (monsoonBtn) monsoonBtn.click();
            form.dispatchEvent(new Event('submit', { cancelable: true }));
        }, 500);
    }
});
