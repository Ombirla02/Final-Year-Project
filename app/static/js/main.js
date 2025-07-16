document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
        let alerts = document.querySelectorAll(".alert");
        alerts.forEach(alert => {
            alert.classList.add("hide");
            setTimeout(() => alert.remove(), 500);
        });
    }, 3000);
}); 