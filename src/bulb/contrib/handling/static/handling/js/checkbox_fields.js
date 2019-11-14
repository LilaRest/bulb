// This script handle 'checkbox' fields.

window.addEventListener("load", function () {
    const form = document.querySelector("form#handling-form") ? document.querySelector("form#handling-form") : document.querySelector("form#creation-form");
    const checkboxes = form.querySelectorAll("div.checkbox-div input[type=checkbox]");

    form.onsubmit = function () {
        for (const checkbox of checkboxes) {
            const related_hidden_input = form.querySelector(`input[type=hidden]#${checkbox.id}-hidden`);

            if (checkbox.checked) {
                related_hidden_input.disabled = true;
            }
        }
    }
});
