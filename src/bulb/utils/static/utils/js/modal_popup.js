import {showSpecialCharactersList} from "./show_special_characters_popup.js"


export class ModalPopup {
    constructor(html_content) {
        this.html_content = html_content;

        this.modal_popup_container = null;
        this.modal_popup_background = null;
        this.modal_popup = null;

        this.init();
    }

    create() {
        this.modal_popup_container.style.display = "flex";
        // this.modal_popup_container.style.zIndex = 3000;
        this.modal_popup_container.onclick = function () {
            this.delete()
        }.bind(this);

        this.modal_popup = document.createElement("div");
        this.modal_popup.setAttribute("id", "modal-popup");
        this.modal_popup.innerHTML = this.html_content + "<br/><p id='modal-popup-info'>(Cliquez n'importe où pour fermer la fenêtre d'aide.)</p>";
        this.modal_popup_container.appendChild(this.modal_popup);

        // Initialize special-characters-list buttons.
        const special_characters_list_buttons = document.getElementsByClassName("special-characters-list-button");
        for (const button of special_characters_list_buttons) {
            button.addEventListener("click", showSpecialCharactersList)
        }
    }

    delete() {
        this.modal_popup_container.style.display = "none";
        this.modal_popup_container.onclick = null;
        this.modal_popup_container.removeChild(this.modal_popup);
        this.modal_popup = null;
    }

    toggle() {
        if (this.modal_popup !== null) {
            this.delete.call(this)
        } else {
            this.create.call(this)
        }
    }


    init() {
        if (!document.querySelector("div#modal-popup-container")) {
            this.modal_popup_container = document.createElement("div");
            this.modal_popup_container.setAttribute("id", "modal-popup-container");
            document.body.appendChild(this.modal_popup_container);

            this.modal_popup_background = document.createElement("div");
            this.modal_popup_background.setAttribute("id", "modal-popup-background");
            this.modal_popup_container.appendChild(this.modal_popup_background)
        } else {
            this.modal_popup_container = document.querySelector("div#modal-popup-container")
        }
    }
}
