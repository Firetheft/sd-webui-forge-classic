onUiLoaded(function() {
    setupAspectRatioLock('txt2img');
    setupAspectRatioLock('img2img');
});

function setupAspectRatioLock(tabName) {
    const lockBtnId = `#${tabName}_lock_ratio`;
    const widthRowId = `#${tabName}_width`;
    const heightRowId = `#${tabName}_height`;

    function getInputs(rowId) {
        const row = document.querySelector(rowId);
        if (!row) return null;
        return {
            slider: row.querySelector('input[type="range"]'),
            number: row.querySelector('input[type="number"]')
        };
    }

    const lockBtn = document.querySelector(lockBtnId);
    const widthInputs = getInputs(widthRowId);
    const heightInputs = getInputs(heightRowId);

    if (!lockBtn || !widthInputs || !heightInputs) return;

    let lockedRatio = 0;
    let isLocked = false;
    let isUpdating = false;

    lockBtn.addEventListener('click', () => {
        isLocked = !isLocked;
        
        if (isLocked) {
            lockBtn.classList.add('selected');
            lockBtn.style.setProperty('background-color', 'var(--primary-500, #4f46e5)', 'important');
            lockBtn.style.setProperty('color', 'white', 'important');
            
            const w = parseFloat(widthInputs.number.value);
            const h = parseFloat(heightInputs.number.value);
            lockedRatio = w / h;
        } else {
            lockBtn.classList.remove('selected');
            lockBtn.style.removeProperty('background-color');
            lockBtn.style.removeProperty('color');
        }
    });

    function updateDims(source) {
        if (!isLocked || isUpdating) return;

        isUpdating = true;

        try {
            if (source === 'width') {
                const w = parseFloat(widthInputs.number.value);
                if (!isNaN(w) && lockedRatio !== 0) {
                    let newH = Math.round((w / lockedRatio) / 8) * 8;
                    newH = Math.max(64, newH);
                    setInput(heightInputs, newH);
                }
            } else {
                const h = parseFloat(heightInputs.number.value);
                if (!isNaN(h) && lockedRatio !== 0) {
                    let newW = Math.round((h * lockedRatio) / 8) * 8;
                    newW = Math.max(64, newW);
                    setInput(widthInputs, newW);
                }
            }
        } finally {
            isUpdating = false;
        }
    }

    function setInput(inputs, value) {
        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        
        nativeSetter.call(inputs.number, value);
        inputs.number.dispatchEvent(new Event('input', { bubbles: true }));
        
        nativeSetter.call(inputs.slider, value);
        inputs.slider.dispatchEvent(new Event('input', { bubbles: true }));
    }

    widthInputs.number.addEventListener('input', () => updateDims('width'));
    widthInputs.slider.addEventListener('input', () => updateDims('width'));
    
    heightInputs.number.addEventListener('input', () => updateDims('height'));
    heightInputs.slider.addEventListener('input', () => updateDims('height'));
}