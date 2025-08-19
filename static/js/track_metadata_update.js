
const notice = document.getElementById("updateNotice");
const trackedInputs = document.querySelectorAll(".track-update");

trackedInputs.forEach(input => {
input.addEventListener("input", () => {
    notice.style.display = "block";
});
});
