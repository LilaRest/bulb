import {AJAXRequest} from "../../utils/js/ajax.js";

window.addEventListener("load", function () {
    const search_bar_box = document.querySelector("div#search-bar-box");
    const search_bar = search_bar_box.querySelector("input#search-bar");
    const initial_tbody = document.querySelector("table tbody#initial-tbody")
    const search_tbody = document.querySelector("table tbody#search-tbody")
    let search_value = null;
    let timeout = null;
    let loaded_instances = 20;
    const loader = document.querySelector("div#loader");
    const no_more_message = document.querySelector("p#no-more-message");
    let results_number = null;


    function clear_search_results () {
        for (const element of document.querySelectorAll("p.search-results-message")) {
            element.parentElement.removeChild(element);
        }

        for (const element of document.querySelectorAll("p#no-more-message")) {
            element.setAttribute("hidden", "hidden");
        }

        search_tbody.innerHTML = "";

        for (const element of document.querySelectorAll("p.no-results-message")) {
            element.parentElement.removeChild(element);
        }
    }


    function insertResults (response) {
        clear_search_results();

        if (search_value !== "") {

            if (response.length !== 0) {

                // Add a results message.
                const number_of_results = response[response.length - 1]["count"];

                const results_count_message = document.createElement("p");
                results_count_message.classList.add("search-results-message");
                results_count_message.innerHTML = `<b>${number_of_results}</b> results for "<b>${search_value}</b>"`;
                search_bar_box.appendChild(results_count_message);

                // Remove the "count" dict of the response to let only instances didts.
                response.pop()

                for (const instance of response) {
                    // Create a row for the new instance.
                    const row = document.createElement("tr");

                    // Create cell for each property.
                    for (const value of Object.values(instance)) {
                        const cell = document.createElement("td");

                        // False and true cells support
                        if (value === "True") {
                            cell.classList.add("true_td");
                        }
                        else if (value === "False") {
                            cell.classList.add("false_td");
                        }

                        // Create the cell content.
                        const cell_link = document.createElement("a");
                        cell_link.setAttribute("href", window.location.pathname + "/" + instance.uuid);
                        cell_link.innerText = value.substring(0, 40);

                        // Add the link to the cell.
                        cell.appendChild(cell_link)

                        // Add the cell to the row.
                        row.appendChild(cell);
                    }

                    // Add the row to the table's body.
                    search_tbody.append(row)
                }

                loader.setAttribute("hidden", "hidden");
            }

            else {
                loader.setAttribute("hidden", "hidden");
                const no_results_message = document.createElement("p");
                no_results_message.classList.add("no-results-message");
                no_results_message.innerHTML = `No results found for "<b>${search_value}</b>"`;
                search_bar_box.appendChild(no_results_message)
            }

            window.addEventListener("scroll", more_results_on_scroll)
        }
    }


    function insertNewInstances(instances) {

        if (search_value !== "") {

            if (instances.length !== 0) {

                loaded_instances += instances.length;

                for (const instance of instances) {
                    // Create a row for the new instance.
                    const row = document.createElement("tr");

                    // Create cell for each property.
                    for (const value of Object.values(instance)) {
                        const cell = document.createElement("td");

                        // False and true cells support
                        if (value === "True") {
                            cell.classList.add("true_td");
                        }
                        else if (value === "False") {
                            cell.classList.add("false_td");
                        }

                        // Create the cell content.
                        const cell_link = document.createElement("a");
                        cell_link.setAttribute("href", window.location.pathname + "/" + instance.uuid);
                        cell_link.innerText = value.substring(0, 40);

                        // Add the link to the cell.
                        cell.appendChild(cell_link)

                        // Add the cell to the row.
                        row.appendChild(cell);
                    }

                    // Add the row to the table's body.
                    search_tbody.append(row)
                }

                loader.setAttribute("hidden", "hidden");
            }

            else {
                loader.setAttribute("hidden", "hidden");
                no_more_message.removeAttribute("hidden")
            }

            // When the Ajax process is done, set up again the scroll event.
            window.addEventListener("scroll", more_results_on_scroll)
        }
    }


    function more_results_on_scroll () {
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {

            // Prevent mutliple bottom scroll event.
            window.removeEventListener("scroll", more_results_on_scroll);

            const data = new FormData();
            data.append("value", search_value);
            data.append("loaded_instances", loaded_instances);

            loader.removeAttribute("hidden");
            no_more_message.setAttribute("hidden", "hidden");

            AJAXRequest("POST", window.location.pathname + "/recherche", insertNewInstances, true, data);
        }

    }


    function makeSearch (value) {
        const data = new FormData();
        data.append("value", value);
        AJAXRequest("POST", window.location.pathname + "/recherche", insertResults, true, data);
    }


    search_bar.addEventListener("input", function (e) {
        search_value = e.target.value;
        clearTimeout(timeout);

        if (e.target.value) {
            clear_search_results();
            initial_tbody.style.display = "none";
            loader.removeAttribute("hidden")
            timeout = setTimeout(makeSearch.bind(this, search_value), 300)
        }

        else {
            clearTimeout(timeout)
            clear_search_results();
            initial_tbody.style.display = "table-row-group";
            loader.setAttribute("hidden", "hidden")
        }
    });
});
