/*
   ==========================================
   SCRUBIT FRONTEND LOGIC
   ==========================================

   Connects the SCRUBIT frontend to the
   FastAPI backend running locally.

   Classification system:

   HIGH  = High Priority
           Serious concern that should be
           reviewed first.

   LOW   = Low Priority
           Potential concern worth reviewing.

   CLEAR = No meaningful concern detected.
           These posts are counted but are
           not displayed as flagged posts.
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

    progressText.textContent =
        "Reading archive...";


    // Prepare the selected archive for FastAPI.
    const formData = new FormData();

    formData.append("file", file);


    try {

        progressBar.style.width = "25%";

        progressText.textContent =
            "Uploading archive...";


        // Send archive to local SCRUBIT backend.
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


        // Validate backend response.
        if (
            !data.results ||
            !Array.isArray(data.results)
        ) {

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


    // ======================================
    // COUNT CLASSIFICATIONS
    // ======================================

    const high =
        results.filter(
            post => post.risk === "HIGH"
        ).length;


    const low =
        results.filter(
            post => post.risk === "LOW"
        ).length;


    const clear =
        results.filter(
            post => post.risk === "CLEAR"
        ).length;


    // ======================================
    // UPDATE DASHBOARD
    // ======================================

    document.getElementById("high-count")
        .textContent = high;


    document.getElementById("low-count")
        .textContent = low;


    document.getElementById("clear-count")
        .textContent = clear;


    document.getElementById("total-posts")
        .textContent = results.length;


    // Only flagged posts are displayed below.
    renderPosts(results);

}


// ==========================================
// CREATE FLAGGED POST CARDS
// ==========================================

function renderPosts(results) {

    // Clear previous results.
    postsContainer.innerHTML = "";


    // ======================================
    // REMOVE CLEAR POSTS
    // ======================================

    // HIGH and LOW posts require some level
    // of review.
    //
    // CLEAR posts do not need to appear under
    // "Flagged Posts."

    const flaggedResults =
        results.filter(
            post =>
                post.risk === "HIGH" ||
                post.risk === "LOW" ||
                post.risk === "UNKNOWN"
        );


    // ======================================
    // NO FLAGGED POSTS
    // ======================================

    if (flaggedResults.length === 0) {

        postsContainer.innerHTML = `
            <article class="post-card">

                <div class="post-top">

                    <span class="risk-label clear">
                        CLEAR
                    </span>

                    <span class="category">
                        No Significant Risk
                    </span>

                </div>

                <p class="post-text">
                    No posts were flagged for review.
                </p>

                <p class="explanation">
                    SCRUBIT did not detect any meaningful
                    professional or reputational concerns
                    in this archive.
                </p>

            </article>
        `;

        return;

    }


    // ======================================
    // SORT FLAGGED POSTS
    // ======================================

    const riskOrder = {
        HIGH: 1,
        LOW: 2,
        UNKNOWN: 3
    };


    const sortedResults =
        [...flaggedResults].sort(
            (a, b) =>
                (riskOrder[a.risk] || 99) -
                (riskOrder[b.risk] || 99)
        );


    // ======================================
    // BUILD POST CARDS
    // ======================================

    sortedResults.forEach(post => {

        const card =
            document.createElement("article");


        card.className = "post-card";


        const riskClass =
            (post.risk || "UNKNOWN")
                .toLowerCase();


        // Convert backend classification into
        // user-friendly UI wording.

        let riskLabel = "REVIEW";


        if (post.risk === "HIGH") {

            riskLabel =
                "HIGH PRIORITY";

        } else if (post.risk === "LOW") {

            riskLabel =
                "LOW PRIORITY";

        } else if (post.risk === "UNKNOWN") {

            riskLabel =
                "MANUAL REVIEW";

        }


        card.innerHTML = `

            <div class="post-top">

                <span class="risk-label ${riskClass}">
                    ${riskLabel}
                </span>

                <span class="category">
                    ${post.category || "Other"}
                </span>

            </div>


            <p class="post-text">
                "${post.text || ""}"
            </p>


            <p class="explanation">

                <strong>
                    Why should I review this?
                </strong>

                <br><br>

                ${
                    post.explanation ||
                    "No explanation provided."
                }

            </p>


            ${
                post.recommendation
                    ? `
                        <p class="recommendation">

                            <strong>
                                Recommendation:
                            </strong>

                            <br><br>

                            ${post.recommendation}

                        </p>
                    `
                    : ""
            }

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