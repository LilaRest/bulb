// This script handle 'file' fields.

window.addEventListener("load", function () {
    const reset_buttons = document.getElementsByClassName("file-reset-button");
    const file_removing_helpers = document.getElementsByClassName("file-removing-helper");

    // Initialize reset buttons behavior.
    for (const reset_button of reset_buttons) {

        const file_field_name = reset_button.getAttribute("id").replace("-reset-button", "");
        const file_input = document.querySelector(`input[type=file]#${file_field_name}`);
        const file_removing_helper = document.getElementById(`${file_field_name}-removing-helper`);

        reset_button.onclick = function (event) {
            event.preventDefault();

            file_input.value = "";
            file_input.hidden = false;

            if (file_removing_helper) {
                file_removing_helper.checked = false;
            }
        };
    }

    // Initialize file removing helpers checkboxes behavior.
    for (const file_removing_helper of file_removing_helpers) {
        file_removing_helper.onclick = function () {
            const form = this.parentElement.parentElement;

            const file_field_name = file_removing_helper.getAttribute("id").replace("-removing-helper", "");
            const file_input = document.querySelector(`input[type=file]#${file_field_name}`);
            const file_preview = file_removing_helper.parentElement.nextElementSibling.nextElementSibling;
            const reset_button = file_removing_helper.parentElement.previousElementSibling.previousElementSibling.previousElementSibling;
            const remove_file_label = file_removing_helper.parentElement.previousElementSibling;

            console.log(reset_button);

            if (this.checked) {
                const new_hidden_input = document.createElement('input');

                new_hidden_input.setAttribute('id', file_field_name);
                new_hidden_input.setAttribute('type', 'hidden');
                new_hidden_input.setAttribute('name', file_field_name);
                new_hidden_input.value = 'None';

                form.insertBefore(new_hidden_input, file_input);
                file_input.hidden = true;

                file_preview.style.display = "none";
                reset_button.style.display = "none";

                remove_file_label.style.borderTopLeftRadius = "0";
                remove_file_label.style.borderBottomLeftRadius = "0";
            }
            else {
                const hidden_input = form.querySelector(`#${file_field_name}[type=hidden]`);
                form.removeChild(hidden_input);
                file_input.hidden = false;

                file_preview.style.display = "inline-flex";
                reset_button.style.display = "inline-flex";

                remove_file_label.style.borderTopLeftRadius = "4px";
                remove_file_label.style.borderBottomLeftRadius = "4px";
            }
        }
    }
});
