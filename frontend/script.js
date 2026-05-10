// =====================================================================
//  API base URL — user pastes their API Gateway endpoint here
// =====================================================================
const apiUrlInput = document.getElementById("apiUrlInput");

// Try loading a saved URL from localStorage
apiUrlInput.value = localStorage.getItem("apiUrl") || "https://mliw6mw8fe.execute-api.us-east-1.amazonaws.com/Prod";
apiUrlInput.addEventListener("change", () => {
    localStorage.setItem("apiUrl", apiUrlInput.value.replace(/\/+$/, ""));
});

function getApiUrl() {
    const url = apiUrlInput.value.replace(/\/+$/, "");
    if (!url) {
        alert("Please enter your API Gateway endpoint URL at the top of the page.");
        return null;
    }
    return url;
}

// =====================================================================
//  DOM references
// =====================================================================
const canvas            = document.getElementById("canvas");
const ctx               = canvas.getContext("2d");

const modeDrawBtn       = document.getElementById("modeDrawBtn");
const modeUploadBtn     = document.getElementById("modeUploadBtn");
const drawMode          = document.getElementById("drawMode");
const uploadMode        = document.getElementById("uploadMode");

const clearBtn          = document.getElementById("clearBtn");
const predictDrawBtn    = document.getElementById("predictDrawBtn");

const fileInput         = document.getElementById("fileInput");
const uploadArea        = document.getElementById("uploadArea");
const uploadPlaceholder = document.getElementById("uploadPlaceholder");
const imagePreview      = document.getElementById("imagePreview");
const clearUploadBtn    = document.getElementById("clearUploadBtn");
const predictUploadBtn  = document.getElementById("predictUploadBtn");

const predictionResult  = document.getElementById("predictionResult");

let drawing      = false;
let uploadedFile = null;

// =====================================================================
//  Mode Toggle
// =====================================================================
function setMode(mode) {
    if (mode === "draw") {
        modeDrawBtn.classList.add("active");
        modeUploadBtn.classList.remove("active");
        drawMode.classList.add("active");
        uploadMode.classList.remove("active");
    } else {
        modeUploadBtn.classList.add("active");
        modeDrawBtn.classList.remove("active");
        uploadMode.classList.add("active");
        drawMode.classList.remove("active");
    }
    resetResult();
}

modeDrawBtn.addEventListener("click",   () => setMode("draw"));
modeUploadBtn.addEventListener("click", () => setMode("upload"));

// =====================================================================
//  Shared helpers
// =====================================================================
function resetResult() {
    predictionResult.textContent = "?";
    renderBars({});
}

function displayResult(data) {
    if (data.error) { alert("Error: " + data.error); return; }
    predictionResult.textContent = data.prediction;
    renderBars(data.confidence || {});
}

function renderBars(confidence) {
    const container = document.getElementById("confidenceBars");
    container.innerHTML = "";
    const topDigit = Object.entries(confidence).sort((a, b) => b[1] - a[1])[0]?.[0];

    for (let i = 0; i <= 9; i++) {
        const pct   = confidence[String(i)] ?? 0;
        const isTop = String(i) === topDigit;
        container.innerHTML += `
            <div class="bar-row">
                <span class="bar-label">${i}</span>
                <div class="bar-track">
                    <div class="bar-fill ${isTop ? "highlight" : ""}"
                         style="width: ${pct}%"></div>
                </div>
                <span class="bar-value">${pct.toFixed(1)}%</span>
            </div>`;
    }
}

renderBars({});

// =====================================================================
//  DRAW MODE — Canvas
// =====================================================================
ctx.fillStyle = "#000";
ctx.fillRect(0, 0, canvas.width, canvas.height);
ctx.strokeStyle = "#fff";
ctx.lineWidth   = 16;
ctx.lineCap     = "round";
ctx.lineJoin    = "round";

function getPos(e) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: (e.clientX - rect.left) * (canvas.width  / rect.width),
        y: (e.clientY - rect.top)  * (canvas.height / rect.height),
    };
}

canvas.addEventListener("mousedown", (e) => {
    drawing = true;
    const p = getPos(e);
    ctx.beginPath();
    ctx.moveTo(p.x, p.y);
});
canvas.addEventListener("mousemove", (e) => {
    if (!drawing) return;
    const p = getPos(e);
    ctx.lineTo(p.x, p.y);
    ctx.stroke();
});
canvas.addEventListener("mouseup",   () => { drawing = false; });
canvas.addEventListener("mouseleave", () => { drawing = false; });

function getTouchPos(e) {
    const rect  = canvas.getBoundingClientRect();
    const touch = e.touches[0];
    return {
        x: (touch.clientX - rect.left) * (canvas.width  / rect.width),
        y: (touch.clientY - rect.top)  * (canvas.height / rect.height),
    };
}
canvas.addEventListener("touchstart", (e) => {
    e.preventDefault(); drawing = true;
    const p = getTouchPos(e);
    ctx.beginPath(); ctx.moveTo(p.x, p.y);
});
canvas.addEventListener("touchmove", (e) => {
    e.preventDefault();
    if (!drawing) return;
    const p = getTouchPos(e);
    ctx.lineTo(p.x, p.y); ctx.stroke();
});
canvas.addEventListener("touchend", () => { drawing = false; });

clearBtn.addEventListener("click", () => {
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    resetResult();
});

predictDrawBtn.addEventListener("click", async () => {
    const apiUrl = getApiUrl();
    if (!apiUrl) return;

    const dataURL = canvas.toDataURL("image/png");
    try {
        const res = await fetch(`${apiUrl}/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: dataURL }),
        });
        displayResult(await res.json());
    } catch (err) {
        alert("Network error: " + err.message);
    }
});

// =====================================================================
//  UPLOAD MODE — File input / drag-and-drop
// =====================================================================
function showPreview(file) {
    uploadedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        imagePreview.classList.remove("hidden");
        uploadPlaceholder.classList.add("hidden");
    };
    reader.readAsDataURL(file);
}

function clearUpload() {
    uploadedFile = null;
    fileInput.value = "";
    imagePreview.src = "";
    imagePreview.classList.add("hidden");
    uploadPlaceholder.classList.remove("hidden");
    resetResult();
}

fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) showPreview(e.target.files[0]);
});

uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadArea.classList.add("drag-over");
});
uploadArea.addEventListener("dragleave", () => {
    uploadArea.classList.remove("drag-over");
});
uploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadArea.classList.remove("drag-over");
    if (e.dataTransfer.files.length > 0) showPreview(e.dataTransfer.files[0]);
});

clearUploadBtn.addEventListener("click", clearUpload);

predictUploadBtn.addEventListener("click", async () => {
    if (!uploadedFile) { alert("Please select or drop an image first."); return; }

    const apiUrl = getApiUrl();
    if (!apiUrl) return;

    // Convert file to base64 and send as JSON (avoids multipart/binary issues with API Gateway)
    const reader = new FileReader();
    reader.onload = async (e) => {
        try {
            const res = await fetch(`${apiUrl}/predict`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image: e.target.result }),
            });
            displayResult(await res.json());
        } catch (err) {
            alert("Network error: " + err.message);
        }
    };
    reader.readAsDataURL(uploadedFile);
});
