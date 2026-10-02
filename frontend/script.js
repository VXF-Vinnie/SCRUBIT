/*
    ==========================================
    SCRUBIT FRONTEND LOGIC
    ==========================================

    Connects the SCRUBIT frontend to the
    FastAPI backend running locally.

    The selected social media archive is sent
    to the backend, where posts are extracted
    and analyzed by the local AI model.
*/


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


fileInput.addEventListener("change", () => {

    const file = fileInput.files[0];

    if (file) {

        fileName.textContent = file.name;

        scanButton.disabled = false;

    }

});


// ==========================================
// START REAL SCAN
// ==========================================

scanButton.addEventListener("click", async () => {

    const file = fileInput.files[0];

    if (!file) {
        alert("Please select an archive first.");
        return;
    }


    // Hide upload screen.
    uploadScreen.classList.add("hidden");

    // Show scanning screen.
    scanningScreen.classList.remove("hidden");

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


// ==========================================
// SHOW RESULTS
// ==========================================

function showResults(results) {

    scanningScreen.classList.add("hidden");

    resultsScreen.classList.remove("hidden");


    // Count risk levels.

    const high =
        results.filter(
            post => post.risk === "HIGH"
        ).length;

    const medium =
        results.filter(
            post => post.risk === "MEDIUM"
        ).length;

    const low =
        results.filter(
            post => post.risk === "LOW"
        ).length;


    document.getElementById("high-count")
        .textContent = high;

    document.getElementById("medium-count")
        .textContent = medium;

    document.getElementById("low-count")
        .textContent = low;

    document.getElementById("total-posts")
        .textContent = results.length;


    renderPosts(results);

}


// ==========================================
// CREATE POST CARDS
// ==========================================

function renderPosts(results) {

    // Clear old cards.
    postsContainer.innerHTML = "";


    // High-risk posts appear first.

    const riskOrder = {
        HIGH: 1,
        MEDIUM: 2,
        LOW: 3
    };


    const sortedResults =
        [...results].sort(
            (a, b) =>
                (riskOrder[a.risk] || 99) -
                (riskOrder[b.risk] || 99)
        );


    sortedResults.forEach(post => {

        const card =
            document.createElement("article");

        card.className = "post-card";


        const riskClass =
            (post.risk || "LOW").toLowerCase();


        card.innerHTML = `

            <div class="post-top">

                <span class="risk-label ${riskClass}">
                    ${post.risk} RISK
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
                ${post.explanation || "No explanation provided."}
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

    fileName.textContent =
        "No file selected";

    scanButton.disabled = true;

    progressBar.style.width = "0%";

    progressText.textContent =
        "Reading archive...";

    postsContainer.innerHTML = "";

});