const TOTAL_STEPS = 9;
let currentStep = 1;

function updateUI() {
    // Show/hide steps
    document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
    const active = document.querySelector(`.step[data-step="${currentStep}"]`);
    if (active) active.classList.add('active');

    // Progress bar
    const pct = (currentStep / TOTAL_STEPS) * 100;
    document.getElementById('progressBar').style.width = pct + '%';

    // Step label
    document.getElementById('stepLabel').textContent = `Step ${currentStep} of ${TOTAL_STEPS}`;

    // Buttons
    document.getElementById('backBtn').style.display  = currentStep > 1 ? 'block' : 'none';
    document.getElementById('nextBtn').style.display  = currentStep < TOTAL_STEPS ? 'block' : 'none';
    document.getElementById('predictBtn').style.display = currentStep === TOTAL_STEPS ? 'block' : 'none';
}

function nextStep() {
    if (currentStep < TOTAL_STEPS) {
        currentStep++;
        updateUI();
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateUI();
    }
}

function predict() {
    const formData = {
        sem_present_count:                  parseFloat(document.getElementById('sem_present_count').value),
        sem_absent_count:                   parseFloat(document.getElementById('sem_absent_count').value),
        sem_eval_lec_test_1_mark:           parseFloat(document.getElementById('sem_eval_lec_test_1_mark').value),
        sem_eval_lab_test_1_mark:           parseFloat(document.getElementById('sem_eval_lab_test_1_mark').value),
        semester_evaluation_mid_mark:       parseFloat(document.getElementById('semester_evaluation_mid_mark').value),
        sem_eval_lec_test_2_mark:           parseFloat(document.getElementById('sem_eval_lec_test_2_mark').value),
        sem_eval_lab_test_2_mark:           parseFloat(document.getElementById('sem_eval_lab_test_2_mark').value),
        semester_evaluation_pre_gtu_mark:   parseFloat(document.getElementById('semester_evaluation_pre_gtu_mark').value),
        semester_evaluation_internal_mark:  parseFloat(document.getElementById('semester_evaluation_internal_mark').value),
    };

    const predictBtn = document.getElementById('predictBtn');
    predictBtn.textContent = 'Predicting...';
    predictBtn.disabled = true;

    fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            predictBtn.textContent = 'Predict Marks';
            predictBtn.disabled = false;
            return;
        }
        // Show result
        document.getElementById('stepContainer').style.display = 'none';
        document.querySelector('.progress-wrap').style.display = 'none';
        document.getElementById('stepLabel').style.display = 'none';
        document.querySelector('.btn-row').style.display = 'none';

        const mark = Math.round(data.predicted_gtu_mark * 10) / 10;
        document.getElementById('predictedFinalExamMarks').textContent = mark;
        document.getElementById('result').style.display = 'block';
    })
    .catch(() => {
        alert('Failed to connect to server. Please try again.');
        predictBtn.textContent = 'Predict Marks';
        predictBtn.disabled = false;
    });
}

function resetForm() {
    currentStep = 1;
    // Clear all inputs
    document.querySelectorAll('.step input').forEach(i => i.value = '');
    // Show form, hide result
    document.getElementById('stepContainer').style.display = 'block';
    document.querySelector('.progress-wrap').style.display = 'block';
    document.getElementById('stepLabel').style.display = 'block';
    document.querySelector('.btn-row').style.display = 'flex';
    document.getElementById('result').style.display = 'none';
    updateUI();
}

// Init
document.addEventListener('DOMContentLoaded', updateUI);
