const toggleCommonFiles = document.getElementById("toggle-common-files");
const toggleAllFields = document.getElementById("toggle-all-fields");

function updateTableRows() {
    const rows = document.querySelectorAll("tr");

    const showUnmatched = !toggleCommonFiles.checked;
    const showAllFields = toggleAllFields.checked;

    rows.forEach(row => {
        const is_matched = row.classList.contains("matched");
        const is_unmatched = row.classList.contains("unmatched");
        const is_main = row.classList.contains("main_field");
        const is_other = row.classList.contains("other_field");

        if ((is_matched || is_unmatched) && !(is_main || is_other)) {
            if (showUnmatched) {
                show = true
            } else {
                show = is_matched
            }
            row.style.display = show ? "" : "none";
        }
        else if (!(is_matched || is_unmatched) || !(is_main || is_other)) {
            return;
        }
        else {
            let show = false;

            // Case 1: unmatched files checkbox - off, all file fields checkbox - off
            if (!showUnmatched && !showAllFields) {
                show = is_matched && is_main;
            }
            // Case 2: off, on
            else if (!showUnmatched && showAllFields) {
                show = is_matched && (is_main || is_other);
            }
            // Case 3: on, off
            else if (showUnmatched && !showAllFields) {
                show = is_main && (is_matched || is_unmatched);
            }
            // Case 4: off, off
            else if (showUnmatched && showAllFields) {
                show = true;
            }

            row.style.display = show ? "" : "none";
        }
    });
}

toggleCommonFiles.addEventListener("change", updateTableRows);
toggleAllFields.addEventListener("change", updateTableRows);
