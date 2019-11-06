window.addEventListener("load", function () {
    const description_boxes = document.querySelectorAll("div.description-box");

    for (const description_box of description_boxes) {
        let description_is_opened = false;
        const i_element = description_box.firstElementChild;
        const small_element = description_box.lastElementChild;
        const small_initial_size = small_element.scrollWidth;

        // If it is a textarea field.
        if (description_box.previousElementSibling.nodeName === "TEXTAREA") {
             small_element.style.top = "201px";
        }

        // If it is a ckeditor field.
        const double_previous_element = description_box.previousElementSibling.previousElementSibling;

        if (double_previous_element) {
            if (double_previous_element.className === "ckeditor-textarea") {
                small_element.style.top = "339px";
            }
        }

        description_box.addEventListener("click", function () {
            if (!description_is_opened) {
                description_box.parentElement.style.marginBottom = "80px";
                i_element.style.transform = "rotate(360deg)";
                i_element.innerText = "help_outline";
                small_element.style.width = small_initial_size + "px";
                small_element.style.padding = "10px";
                small_element.style.backgroundColor = "#2D3436";
                description_is_opened = true;
            }
            else {
                description_box.parentElement.style.marginBottom = "40px";
                i_element.style.transform = "rotate(-360deg)";
                i_element.innerText = "help";
                small_element.style.width = "0";
                small_element.style.padding = "0";
                small_element.style.backgroundColor = "#f2f3fa";
                description_is_opened = false;
            }
        })
    }
});