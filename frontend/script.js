/*
    ==========================================
    SCRUBIT UNIFIED FRONTEND LOGIC 🛡️
    ==========================================
<<<<<<< HEAD
=======

    Connects the SCRUBIT frontend to the
    FastAPI backend running locally.

    The selected social media archive is sent
    to the backend, where posts are extracted
    and analyzed by the local AI model.
>>>>>>> e28e4125931d696ff813efbfa752ce624b7432c9
*/

async function handleRealScan(fileFileObject) {
    // Clear old dashboard cards before initiating a fresh scan run
    postsContainer.innerHTML = "";
    
    // Bundle the selected physical file into multi-part form data mapping
    const formData = new FormData();
    // Your teammate's backend route name signature expects the exact key name "file"
    formData.append("file", fileFileObject); 

<<<<<<< HEAD
    // Update UI progress indicators before making the live fetch network call
    progressText.textContent = "Running live local AI analysis via Ollama (this will take a moment)...";
    progressBar.style.width = "75%";

    try {
        // 🚀 FIX: Connect explicitly to the fully qualified FastAPI port endpoint
        const response = await fetch("http://127.0.0", {
            method: "POST",
            body: formData,
            headers: {
                "Accept": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error(`Server returned error code: ${response.status}`);
        }

        // Catch the real data package successfully returned by your local AI engine
        const serverPayload = await response.json();
        
        progressBar.style.width = "100%";
        progressText.textContent = "Pipeline complete!";

        // Wait half a second so the user sees 100% completion before switching screens
        setTimeout(() => {
            // Pass the .results array block directly to the data renderer
            showResults(serverPayload.results);
        }, 500);

    } catch (error) {
        console.error("Failed to connect to local SCRUBIT backend:", error);
        alert("Could not communicate with the local AI model. Ensure your FastAPI terminal is running on port 8000.");
        
        // Fail-safe: Reset the view back to the upload screen if network drops
        resultsScreen.classList.add("hidden");
        scanningScreen.classList.add("hidden");
        uploadScreen.classList.remove("hidden");
    }
}


=======
>>>>>>> e28e4125931d696ff813efbfa752ce624b7432c9
// ==========================================
// GET ELEMENTS FROM HTML
// ==========================================

const uploadScreen =
    document.getElementById("upload-screen");

const scanningScreen =
    document.getElementById("scanning-screen");

const resultsScreen =
    document.getElementById("results-screen");

const fileInput =
    document.getElementById("file-input");

const chooseFileButton =
    document.getElementById("choose-file-button");

const fileName =
    document.getElementById("file-name");

const scanButton =
    document.getElementById("scan-button");

const scanAgainButton =
    document.getElementById("scan-again-button");

const progressBar =
    document.getElementById("progress-bar");

const progressText =
    document.getElementById("progress-text");

const postsContainer =
    document.getElementById("posts-container");


// ==========================================
// FILE SELECTION
// ==========================================

chooseFileButton.addEventListener("click", () => {
    fileInput.click();
});

<<<<<<< HEAD
=======

>>>>>>> e28e4125931d696ff813efbfa752ce624b7432c9
fileInput.addEventListener("change", () => {
    const file = fileInput.files[0]; // Fetch the singular active file object
    if (file) {
<<<<<<< HEAD
        fileName.textContent = file.name;
=======

        fileName.textContent = file.name;

>>>>>>> e28e4125931d696ff813efbfa752ce624b7432c9
        scanButton.disabled = false;
    }
});


// ==========================================
// START REAL SCAN
// ==========================================

<<<<<<< HEAD
scanButton.addEventListener("click", () => {
    const file = fileInput.files[0]; // Fetch the targeted file item target
    if (!file) return;
=======
scanButton.addEventListener("click", async () => {

    const file = fileInput.files[0];

    if (!file) {
        alert("Please select an archive first.");
        return;
    }

>>>>>>> e28e4125931d696ff813efbfa752ce624b7432c9

    // Hide upload screen and swap out the screening viewports
    uploadScreen.classList.add("hidden");
    scanningScreen.classList.remove("hidden");

<<<<<<< HEAD
    // Initialize progress indicators
    progressBar.style.width = "10%";
    progressText.textContent = "Reading archive and extracting posts...";

    // Trigger the real live execution pipeline
    setTimeout(() => {
        handleRealScan(file);
    }, 600);
});


=======
    // Reset progress.
    progressBar.style.width = "10%";
    progressText.textContent = "Reading archive...";


    // Prepare file for FastAPI.
    const formData = new FormData();

    formData.append("file", file);


    try {

        progressBar.style.width = "25%";
        progressText.textContent = "Uploading archive...";


        // Send the ZIP file to the SCRUBIT backend.
        const response = await fetch(
            "http://127.0.0.1:8000/scan",
            {
                method: "POST",
                body: formData
            }
        );


        progressBar.style.width = "60%";
        progressText.textContent =
            "Running local AI analysis...";


        // Check for backend errors.
        if (!response.ok) {

            const errorText =
                await response.text();

            throw new Error(
                `Backend error ${response.status}: ${errorText}`
            );

        }


        // Get results from FastAPI.
        const data =
            await response.json();


        console.log(
            "SCRUBIT backend response:",
            data
        );


        // Make sure results were returned.
        if (!data.results ||
            !Array.isArray(data.results)) {

            throw new Error(
                "Backend did not return a valid results array."
            );

        }


        progressBar.style.width = "90%";
        progressText.textContent =
            "Preparing your results...";


        setTimeout(() => {

            progressBar.style.width = "100%";

            progressText.textContent =
                "Analysis complete!";


            setTimeout(() => {

                showResults(data.results);

            }, 300);

        }, 300);


    } catch (error) {

        console.error(
            "SCRUBIT scan failed:",
            error
        );


        scanningScreen.classList.add("hidden");

        uploadScreen.classList.remove("hidden");


        alert(
            "SCRUBIT scan failed.\n\n" +
            "Make sure the backend and Ollama are running.\n\n" +
            error.message
        );

    }

});


>>>>>>> e28e4125931d696ff813efbfa752ce624b7432c9
// ==========================================
// SHOW RESULTS
// ==========================================

function showResults(results) {
    scanningScreen.classList.add("hidden");
    resultsScreen.classList.remove("hidden");

    // Dynamically calculate metrics based on the incoming array stream
    const high = results.filter(post => post.risk === "HIGH").length;
    const medium = results.filter(post => post.risk === "MEDIUM").length;
    const low = results.filter(post => post.risk === "LOW").length;

    document.getElementById("high-count").textContent = high;
    document.getElementById("medium-count").textContent = medium;
    document.getElementById("low-count").textContent = low;
    document.getElementById("total-posts").textContent = results.length;

    renderPosts(results);
}


// ==========================================
// CREATE POST CARDS
// ==========================================

function renderPosts(results) {
    postsContainer.innerHTML = "";

<<<<<<< HEAD
=======

    // High-risk posts appear first.

>>>>>>> e28e4125931d696ff813efbfa752ce624b7432c9
    const riskOrder = {
        HIGH: 1,
        MEDIUM: 2,
        LOW: 3
    };

<<<<<<< HEAD
    const sortedResults = [...results].sort(
        (a, b) => riskOrder[a.risk] - riskOrder[b.risk]
    );
=======

    const sortedResults =
        [...results].sort(
            (a, b) =>
                (riskOrder[a.risk] || 99) -
                (riskOrder[b.risk] || 99)
        );

>>>>>>> e28e4125931d696ff813efbfa752ce624b7432c9

    sortedResults.forEach(post => {
        const card = document.createElement("article");
        card.className = "post-card";
<<<<<<< HEAD
        const riskClass = post.risk ? post.risk.toLowerCase() : "low";
=======


        const riskClass =
            (post.risk || "LOW").toLowerCase();

>>>>>>> e28e4125931d696ff813efbfa752ce624b7432c9

        card.innerHTML = `
            <div class="post-top">
                <span class="risk-label ${riskClass}">
                    ${post.risk || "LOW"} RISK
                </span>
                <span class="category">
                    ${post.category || "General"}
                </span>
            </div>

            <p class="post-text">
                "${post.text}"
            </p>

            <p class="explanation">
                <strong>Why was this flagged?</strong>
                <br><br>
<<<<<<< HEAD
                ${post.explanation || "No risk elements detected in text footprint."}
=======
                ${post.explanation || "No explanation provided."}
>>>>>>> e28e4125931d696ff813efbfa752ce624b7432c9
            </p>
        `;

        postsContainer.appendChild(card);
    });
}


// ==========================================
// SCAN AGAIN
// ==========================================

scanAgainButton.addEventListener("click", () => {
    resultsScreen.classList.add("hidden");
    uploadScreen.classList.remove("hidden");
    fileInput.value = "";
    fileName.textContent = "No file selected";
    scanButton.disabled = true;
    progressBar.style.width = "0%";
<<<<<<< HEAD
});
=======

    progressText.textContent =
        "Reading archive...";

    postsContainer.innerHTML = "";

});
>>>>>>> e28e4125931d696ff813efbfa752ce624b7432c9
