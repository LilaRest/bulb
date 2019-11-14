function getCsrfTokenCookie() {
    for (const cookie of document.cookie.split(";")) {
        if (cookie.includes("csrftoken")) {
            const substring = null;

            if (cookie.indexOf(" ") !== -1) {
                return cookie.substring(11)
            }

            else {
                return cookie.substring(10)
            }
        }
    }
    return null
}

export function AJAXRequest(method, target, callback, async = true, data = null) {
    const xhr = new XMLHttpRequest();
    let response = null;

    xhr.addEventListener("readystatechange", function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                if (xhr.responseText) {

                    if (callback) {
                        response = JSON.parse(xhr.responseText);
                        callback(response)
                    }
                }
            }
        }
    });

    xhr.open(method, target, async);

    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

    const csrf_token = getCsrfTokenCookie();

    if (csrf_token) {
        xhr.setRequestHeader("X-CSRFToken", csrf_token);
    }

    xhr.send(data);
}