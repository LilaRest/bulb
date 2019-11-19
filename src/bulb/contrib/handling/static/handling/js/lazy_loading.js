import {AJAXRequest} from "../../utils/js/ajax.js";

window.addEventListener("load", function () {
    // Default loaded instances
    let loaded_instances = 20;
    const loader = document.querySelector("div#loader");
    const no_more_message = document.querySelector("p#no-more-message");

    function insertNewInstances(instances_json) {
        const instances = JSON.parse(instances_json);

        if (instances.length !== 0) {
            loaded_instances += instances.length;

            const instances_prefix = Object.keys(instances[0])[0][0];

            const instances_tbody = document.querySelector("table tbody");

            for (const instance of instances) {

                // Reproduce the instance and insert it.
                const instance_tr = document.createElement("tr");

                for (const [property_name, property_value] of Object.entries(instance)) {
                    const instance_td = document.createElement("td");

                    if (property_value === true || property_value === "True") {
                        instance_td.classList.add("true_td")
                    }
                    else if (property_value === false || property_value === "False") {
                        instance_td.classList.add("false_td")
                    }

                    instance_td.innerHTML = `<a href="${window.location + '/' + instance["uuid"]}">${property_value.substring(0, 40)}</a>`;
                    instance_tr.appendChild(instance_td);
                }

                // Insert the instance.
                instances_tbody.appendChild(instance_tr)
            }

            loader.setAttribute("hidden", "hidden");
        }

        else {
            loader.setAttribute("hidden", "hidden");
            no_more_message.removeAttribute("hidden")
        }

        // When the Ajax process is done, set up again the scroll event.
        window.addEventListener("scroll", load_on_scroll)

    }

    function load_on_scroll () {
        // Prevent search bar's scroll loading collision.
        const search_bar = document.querySelector("input#search-bar");
        if (search_bar.value === "") {

            if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {

                // Prevent mutliple bottom scroll event.
                window.removeEventListener("scroll", load_on_scroll);

                const data = new FormData();
                data.append("loaded_instances", loaded_instances);

                loader.removeAttribute("hidden");
                no_more_message.setAttribute("hidden", "hidden");

                AJAXRequest("POST", window.location, insertNewInstances, true, data);
            }
        }
    }

    window.addEventListener("scroll", load_on_scroll);

    // Search the new instances if the user is already at the bottom of the page when the page is loaded.
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
        load_on_scroll()
    }
});
