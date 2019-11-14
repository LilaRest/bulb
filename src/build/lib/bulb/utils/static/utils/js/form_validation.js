function set_error_style(field, errorlist, error_message) {
    field.classList.remove("valid");
    field.classList.remove("error");
    field.classList.add("error");
    const error = document.createElement("li");
    error.innerHTML = `${error_message}`;
    errorlist.innerHTML = "";
    errorlist.appendChild(error);
}

function set_valid_style(field, errorlist) {
    field.classList.remove("valid");
    field.classList.remove("error");
    field.classList.add("valid");
    errorlist.innerHTML = "";
}

function getCsrfTokenCookie() {
    for (const cookie of document.cookie.split(";")) {
        if (cookie.includes("csrftoken")) {
            return cookie.substring(10)
        }
    }
    return null
}

class Validator {
    constructor(form_id,
                field_id,
                field_name) {

        // DOM elements.
        this.form = document.querySelector(`form#${form_id}`);
        this.field = this.form.querySelector(`#${field_id}`);
        this.errorlist = this.getErrorList();

        // Field informations.
        this.field_name = field_name;
        this.is_valid = false;
    }

    // Retrieve the errolist related to the field.
    getErrorList() {
        // If there is already an error list.
        if (this.field.parentElement.previousElementSibling.className === "errorlist") {
            return this.field.parentElement.previousElementSibling;
        }
        // If there isn't.
        else {
            const errorlist = document.createElement("ul");
            errorlist.classList.add("errorlist");
            this.form.insertBefore(errorlist, this.field.parentElement);
            return errorlist
        }
    }
}

export class FieldValidator extends Validator {

    constructor(form_id,
                field_id,
                field_name,
                pronoun_un_une,
                pronoun_ce_cette,
                required,
                min_length,
                max_length,
                first_regex,
                second_regex,
                case_sensitive,
                ajax_validation,
                ajax_validation_test_type,
                ajax_exists_message,
                ajax_not_exists_message,
                modal_popup,
                confirmation_field_instance) {

        super(form_id, field_id, field_name);

        // DOM elements.
        this.modal_popup = modal_popup;

        // Field informations.
        this.field_id = field_id;
        this.case_sensitive = case_sensitive;

        // This variable determines the pronoun to use before the field_name in errors : 'un' or 'une'.
        this.pronoun_un_une = pronoun_un_une;

        // This variable determines the pronoun to use before the field_name in errors : 'ce' or 'cette'.
        this.pronoun_ce_cette = pronoun_ce_cette;

        // Field restrictions.
        this.required = required;
        this.max_length = max_length;
        this.min_length = min_length;
        this.first_regex = RegExp(first_regex);
        this.second_regex = RegExp(second_regex);
        this.ajax_validation = ajax_validation;
        this.ajax_validation_test_type = ajax_validation_test_type;
        this.ajax_exists_message = ajax_exists_message;
        this.ajax_not_exists_message = ajax_not_exists_message;

        // Timout for the ajax validation
        this.timeout = null;

        // The instance of the related confirmation field.
        this.confirmation_field_instance = confirmation_field_instance;

        this.init();
    }

    // Set the input event listener on the field.
    init() {
        if (this.field.value) {
            this.validate()
        }

        this.field.addEventListener("input", function () {
            this.validate();
            if (this.confirmation_field_instance) {
                this.confirmation_field_instance.validate()
            }
        }.bind(this));

        this.field.addEventListener("change", function () {
            this.validate();
            if (this.confirmation_field_instance) {
                this.confirmation_field_instance.validate()
            }
        }.bind(this))
    }

    ajax_check(request) {
        if (request.readyState === XMLHttpRequest.DONE) {
            if (request.status === 200) {
                const value_is_unused = JSON.parse(request.responseText).value_is_unused;
                if (this.ajax_validation_test_type === "exists") {
                    if (value_is_unused) {
                        set_error_style(this.field, this.errorlist, this.ajax_exists_message);
                        this.is_valid = false;
                        return false
                    }
                } else if (this.ajax_validation_test_type === "not-exists") {
                    if (!value_is_unused) {
                        set_error_style(this.field, this.errorlist, this.ajax_not_exists_message);
                        this.is_valid = false;
                        return false
                    }
                }
                set_valid_style(this.field, this.errorlist);
                this.is_valid = true;
            }
        }
    };

    // Check if the field respect his restrictions.
    validate() {
        const field_value = this.field.value;

        // Check the 'required' restriction.
        if (this.required) {
            if (!field_value) {
                set_error_style(this.field, this.errorlist, `Veuillez saisir votre ${this.field_name}.`);
                this.is_valid = false;
                return false
            }
        }

        // Check the 'max_length' restriction.
        if (this.max_length !== null) {
            if (this.max_length < field_value.length) {
                set_error_style(this.field, this.errorlist, `Veuillez renseigner ${this.pronoun_un_une} ${this.field_name} valide. <a href="#" id="${this.field_name}-modal-input-button">En savoir plus</a>.`);
                const modal_popup_link = document.getElementById(`${this.field_name}-modal-input-button`);
                modal_popup_link.onclick = this.modal_popup.toggle.bind(this.modal_popup);
                this.is_valid = false;
                return false
            }
        }

        // Check the 'min_length' restriction.
        if (this.min_length !== null) {
            if (this.min_length > field_value.length) {
                set_error_style(this.field, this.errorlist, `Veuillez renseigner ${this.pronoun_un_une} ${this.field_name} valide. <a href="#" id="${this.field_name}-modal-input-button">En savoir plus</a>.`);
                const modal_popup_link = document.getElementById(`${this.field_name}-modal-input-button`);
                modal_popup_link.onclick = this.modal_popup.toggle.bind(this.modal_popup);
                this.is_valid = false;
                return false
            }
        }

        // Check the 'first_regex' and 'second_regex' restrictions.
        if (this.first_regex.toString() !== "/null/") {
            if (!this.first_regex.test(field_value)) {
                set_error_style(this.field, this.errorlist, `Veuillez renseigner ${this.pronoun_un_une} ${this.field_name} valide. <a href="#" id="${this.field_name}-modal-input-button">En savoir plus</a>.`);
                const modal_popup_link = document.getElementById(`${this.field_name}-modal-input-button`);
                modal_popup_link.onclick = this.modal_popup.toggle.bind(this.modal_popup);
                this.is_valid = false;
                return false
            }
            if (this.second_regex.toString() !== "/null/") {
                if (!this.second_regex.test(field_value)) {
                    set_error_style(this.field, this.errorlist, `Veuillez renseigner ${this.pronoun_un_une} ${this.field_name} valide. <a href="#" id="${this.field_name}-modal-input-button">En savoir plus</a>.`);
                    const modal_popup_link = document.getElementById(`${this.field_name}-modal-input-button`);
                    modal_popup_link.onclick = this.modal_popup.toggle.bind(this.modal_popup);
                    this.is_valid = false;
                    return false
                }
            }
        }

        // Check the 'ajax_validation' restriction.
        if (this.ajax_validation) {
            clearTimeout(this.timeout);
            this.timeout = setTimeout(function () {
                const request = new XMLHttpRequest();

                const url = window.location;
                const method = "POST";
                const data = new FormData();

                data.append('field_id', this.field_id);
                data.append('field_value', field_value);

                request.open(method, url);
                request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
                request.setRequestHeader("X-CSRFToken", getCsrfTokenCookie());

                request.onreadystatechange = this.ajax_check.bind(this, request);

                request.send(data);

                // Cause we wait the onreadystatechange event, the field style validation is handled in the ajax_check() function.
                return false
            }.bind(this), 750);
        }

        set_valid_style(this.field, this.errorlist);
        this.is_valid = true;
    }
}

export class ConfirmationFieldValidator extends Validator {

    constructor(form_id,
                field_id,
                field_name,
                field_to_confirm_id,
                field_to_confirm_name) {

        super(form_id, field_id, field_name);

        // DOM elements.
        this.field_to_confirm = this.form.querySelector(`#${field_to_confirm_id}`);

        // Fields informations.
        this.field_to_confirm_is_case_sensitive = this.field_to_confirm.case_sensitive;
        this.field_to_confirm_name = field_to_confirm_name;

        this.init()
    }

    // Set the input event listener on the field.
    init() {
        if (this.field.value) {
            this.validate()
        }

        this.field.addEventListener("input", this.validate.bind(this));
    }

    // Check if the confirmation field is valid.
    validate() {
        let field_value;
        let field_to_confirm_value;

        if (this.field_to_confirm_is_case_sensitive) {
            field_value = this.field.value;
            field_to_confirm_value = this.field_to_confirm.value;
        } else {
            field_value = this.field.value.toLowerCase();
            field_to_confirm_value = this.field_to_confirm.value.toLowerCase();
        }

        // First, check if the confirmation field is not empty.
        if (!field_value) {
            set_error_style(this.field, this.errorlist, `Veuillez confirmer votre ${this.field_to_confirm_name}.`);
            this.is_valid = false;
            return false
        }

        // Then, test if it is identical to his related field.
        if (field_value !== field_to_confirm_value) {
            set_error_style(this.field, this.errorlist, `${this.field_name === "adresse email de confirmation" ? "L'" : "Le "}${this.field_name} ne correspond pas ${this.field_name === "adresse email de confirmation" ? "à l'" : "au "}${this.field_to_confirm_name}.`);
            this.is_valid = false;
            return false
        }

        // If all the test are successful.
        set_valid_style(this.field, this.errorlist);
        this.is_valid = true;
    }
}

export function EnableValidation(form, submit_input, fields_validation_instances_list) {

    function check_form_validity () {
        let no_error = true;

        submit_input.setAttribute("disabled", "disabled");

        for (const field of fields_validation_instances_list) {
            if (!field.is_valid) {
                no_error = false
            }
        }

        if (no_error) {
            submit_input.removeAttribute("disabled")
        }
    }

    check_form_validity();

    form.addEventListener("input", check_form_validity)
}