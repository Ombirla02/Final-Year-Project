// Toggle Profile Dropdown
function toggleProfile() {
    let dropdown = document.getElementById("profileDropdown");
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}

// Update Experience
function updateExperience() {
    let experience = document.getElementById("experience").value;
    alert("Experience updated to " + experience + " years.");
}

// Updated f.js
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("logout-button").addEventListener("click", function () {
        // Clear session storage or any authentication tokens
        sessionStorage.clear();
        localStorage.removeItem("user");
        
        // Redirect to login page
        window.location.href = "index.html";
    });
});


// Show Modals
function showRegisteredStudents() {
    document.getElementById("registeredStudentsModal").style.display = "block";
}

function showCertificateIssuance() {
    document.getElementById("certificateIssuanceModal").style.display = "block";
}

function showDoubtSolving() {
    document.getElementById("doubtSolvingModal").style.display = "block";
}

// Close Modals
function closeModal(modalId) {
    document.getElementById(modalId).style.display = "none";
}

// Issue Certificate
function issueCertificate(userId) {
    alert("Certificate issued for User ID: " + userId);
}

// Submit Doubt Response
function submitResponse(responseId) {
    let response = document.getElementById("response" + responseId).value;
    alert("Response submitted: " + response);
}
