function copy () {
    const value_to_copy = this.innerText;
    const textarea = document.createElement('textarea');
    const message_box = document.querySelector("p#message-box");
    let copied;
    let timeout;

    textarea.value = value_to_copy;
    textarea.style.opacity = "0";
    textarea.style.position = "fixed";
    document.body.appendChild(textarea);
    textarea.select();

    try {
        document.execCommand("copy");
        copied = true;
    } catch {
        copied = false;
    }
    document.body.removeChild(textarea);

    if (copied) {
        clearTimeout(timeout);

        message_box.innerText = "Copied ✔️";
        message_box.style.backgroundColor = "#2ecc71";
        message_box.classList.add("animate");
        timeout = setTimeout(function () {
            message_box.classList.remove("animate")
        }, 2010)
    } else {
        clearTimeout(timeout);

        message_box.innerText = "Error ❌";
        message_box.style.backgroundColor = "#c0392b";
        message_box.classList.add("animate");
        timeout = setTimeout(function () {
            message_box.classList.remove("animate")
        }, 2010)
    }
}

const special_characters_buttons = document.getElementsByClassName("special-characters-button");

for (const button of special_characters_buttons) {
    button.addEventListener("click", copy)
}