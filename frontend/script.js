/*
    ==========================================
    SCRUBIT FRONTEND LOGIC
    ==========================================

    IMPORTANT:

    We currently use fake scan results.

    This lets the frontend work independently
    while the backend + AI teammates finish
    their components.

    Later, fakeResults will be replaced with
    data returned by the backend.
*/


// ==========================================
// TEMPORARY DEMO DATA
// ==========================================

const fakeResults = [

    {
        id: "post_001",

        text:
            "Called out sick today but actually went to Vegas lol",

        risk: "HIGH",

        category: "Professional Conduct",

        explanation:
            "This post publicly suggests dishonesty about missing work and could be interpreted negatively by someone viewing it without context."
    },

    {
        id: "post_002",

        text:
            "My manager is literally the worst person to work for.",

        risk: "MEDIUM",

        category: "Professional Conduct",

        explanation:
            "Public criticism of a workplace or manager could be interpreted as unprofessional depending on the context."
    },

    {
        id: "post_003",

        text:
            "This presentation is going to be killer tomorrow!",

        risk: "LOW",

        category: "General",

        explanation:
            "The phrase is figurative and does not appear to represent a meaningful professional reputation risk."
    }

];


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

// Clicking our pretty button opens the
// browser's real file picker.

chooseFileButton.addEventListener("click", () => {

    fileInput.click();

});


// When the user selects a file...

fileInput.addEventListener("change", () => {

    const file = fileInput.files[0];

    if (file) {

        // Show filename to user.
        fileName.textContent = file.name;

        // Enable scan button.
        scanButton.disabled = false;

    }

});


// ==========================================
// START SCAN
// ==========================================

scanButton.addEventListener("click", () => {

    // Hide upload screen.
    uploadScreen.classList.add("hidden");

    // Show scanning screen.
    scanningScreen.classList.remove("hidden");

    runFakeScan();

});


// ==========================================
// TEMPORARY FAKE SCAN

// This creates the illusion of scanning
// while our teammates build the real backend.
//
// Later this function will call FastAPI.
// ==========================================

function runFakeScan() {

    let progress = 0;

    const messages = [
        "Reading archive...",
        "Extracting posts...",
        "Running local AI analysis...",
        "Checking professional reputation risks...",
        "Preparing your results..."
    ];


    const interval = setInterval(() => {

        progress += 20;

        progressBar.style.width =
            progress + "%";


        const messageIndex =
            Math.min(
                Math.floor(progress / 20) - 1,
                messages.length - 1
            );


        progressText.textContent =
            messages[messageIndex];


        if (progress >= 100) {

            clearInterval(interval);

            setTimeout(() => {

                showResults(fakeResults);

            }, 500);

        }

    }, 550);

}


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


    // High risk should appear first.

    const riskOrder = {
        HIGH: 1,
        MEDIUM: 2,
        LOW: 3
    };


    const sortedResults =
        [...results].sort(
            (a, b) =>
                riskOrder[a.risk] -
                riskOrder[b.risk]
        );


    sortedResults.forEach(post => {

        const card =
            document.createElement("article");

        card.className = "post-card";


        const riskClass =
            post.risk.toLowerCase();


        card.innerHTML = `

            <div class="post-top">

                <span class="risk-label ${riskClass}">
                    ${post.risk} RISK
                </span>

                <span class="category">
                    ${post.category}
                </span>

            </div>


            <p class="post-text">
                "${post.text}"
            </p>


            <p class="explanation">
                <strong>Why was this flagged?</strong>
                <br><br>
                ${post.explanation}
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

});