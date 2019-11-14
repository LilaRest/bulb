export function showSpecialCharactersList() {
    const width = window.outerWidth / 2;
    const left = window.outerWidth - width;
    window.open('/special-characters',
        "_blank",
        `height=${window.outerHeight},
         width=${width},
         top=0,
         left=${left},
         menubar=no,
         toolbar=no,
         location=no,
         status=no,`);
}
