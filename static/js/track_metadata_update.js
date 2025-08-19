
const notice = document.getElementById("updateNotice");
const trackedInputs = document.querySelectorAll(".track-update");

trackedInputs.forEach(input => {
input.addEventListener("input", () => {
    notice.style.display = "block";
});
});

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("input[type='text']").forEach(function (input) {
        input.addEventListener("input", function () {
            if (input.value !== input.defaultValue) {
                input.style.backgroundColor = "lightyellow";
            } else {
                input.style.backgroundColor = "";
            }
        });
    });

    const form = document.querySelector("#file_action_form");
    if (form) {
        form.addEventListener("submit", () => {
            form.querySelectorAll("input[type='text']").forEach(input => {
                if (input.value === input.defaultValue) {
                    input.disabled = true;
                }
            });
        });
    }
});
