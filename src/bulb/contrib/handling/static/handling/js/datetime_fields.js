// This script handle 'date', 'time' and 'datetime' fields.

window.addEventListener("load", function () {
    // Collect all the hidden inputs.
    const hidden_inputs = [
        ...document.getElementsByClassName("datetime-hidden"),
        ...document.getElementsByClassName("date-hidden"),
        ...document.getElementsByClassName("time-hidden")
    ];

// Collect all other needed inputs.
    const day_inputs = [
        ...document.getElementsByClassName("datetime-day"),
        ...document.getElementsByClassName("date-day")
    ];
    const month_inputs = [
        ...document.getElementsByClassName("datetime-month"),
        ...document.getElementsByClassName("date-month")
    ];
    const year_inputs = [
        ...document.getElementsByClassName("datetime-year"),
        ...document.getElementsByClassName("date-year")
    ];
    const hour_inputs = [
        ...document.getElementsByClassName("datetime-hour"),
        ...document.getElementsByClassName("time-hour")
    ];
    const minute_inputs = [
        ...document.getElementsByClassName("datetime-minute"),
        ...document.getElementsByClassName("time-minute")
    ];
    const second_inputs = [
        ...document.getElementsByClassName("datetime-second"),
        ...document.getElementsByClassName("time-second")
    ];

    const global_datetime_inputs_list = [...day_inputs, ...month_inputs, ...year_inputs, ...hour_inputs, ...minute_inputs, ...second_inputs];

// Considering that each hidden datetime input represents one datetime field, loop on each hidden datetime input.
    for (const hidden_input of hidden_inputs) {
        const hidden_input_id = hidden_input.id;

        // Retrieve the inputs objects related to the current hidden datetime input.
        let day_input = null;
        let month_input = null;
        let year_input = null;
        let hour_input = null;
        let minute_input = null;
        let second_input = null;

        let local_datetime_inputs_list = [];

        for (const input of global_datetime_inputs_list) {

            if (input.id === hidden_input_id + "-day") {
                day_input = input;
                local_datetime_inputs_list.push(day_input)
            }

            if (input.id === hidden_input_id + "-month") {
                month_input = input;
                local_datetime_inputs_list.push(month_input)
            }

            if (input.id === hidden_input_id + "-year") {
                year_input = input;
                local_datetime_inputs_list.push(year_input)
            }

            if (input.id === hidden_input_id + "-hour") {
                hour_input = input;
                local_datetime_inputs_list.push(hour_input)
            }

            if (input.id === hidden_input_id + "-minute") {
                minute_input = input;
                local_datetime_inputs_list.push(minute_input)
            }

            if (input.id === hidden_input_id + "-second") {
                second_input = input;
                local_datetime_inputs_list.push(second_input)
            }
        }

        // Render datetime fields values if the database has sent one to the current hidden datetime input.
        if (hidden_input.value) {
            if (hidden_input.getAttribute("class") === "datetime-hidden") {
                day_input.value = hidden_input.value.slice(8, 10);
                month_input.value = hidden_input.value.slice(5, 7);
                year_input.value = hidden_input.value.slice(0, 4);
                hour_input.value = hidden_input.value.slice(11, 13);
                minute_input.value = hidden_input.value.slice(14, 16);
                second_input.value = hidden_input.value.slice(17, 19);
            } else if (hidden_input.getAttribute("class") === "date-hidden") {
                day_input.value = hidden_input.value.slice(8, 10);
                month_input.value = hidden_input.value.slice(5, 7);
                year_input.value = hidden_input.value.slice(0, 4);
            } else if (hidden_input.getAttribute("class") === "time-hidden") {
                hour_input.value = hidden_input.value.slice(0, 2);
                minute_input.value = hidden_input.value.slice(3, 5);
                second_input.value = hidden_input.value.slice(6, 8);
            }
        }

        for (const input of local_datetime_inputs_list) {

            // Prevent bad default value format.
            if (input.value.length !== input.maxLength) {
                const missing_zeros_number = input.maxLength - input.value.length;
                input.value = "0".repeat(missing_zeros_number) + input.value;
                input.maxLength++;
            } else {
                input.maxLength++;
            }

            input.addEventListener("input", function () {
                const input_value = input.value;
                const input_length = input_value.length;
                const input_max_length = input.maxLength;


                if (input_length === input_max_length - 2) {
                    input.value = "0" + input.value;
                }

                // Force the required format.
                else if (input_length === input_max_length) {
                    if (input_value[0] === "0") {
                        input.value = input.value.slice(1, input_max_length);
                    } else {
                        input.value = input.value.slice(0, input_max_length - 1);
                        const next_datetime_input = input.nextElementSibling.nextElementSibling;

                        if (local_datetime_inputs_list.includes(next_datetime_input)) {
                            input.nextElementSibling.nextElementSibling.focus()
                        }
                    }
                }

                // Assign value to the hidden input.
                if (hidden_input.getAttribute("class") === "datetime-hidden") {
                    hidden_input.value = `${year_input.value}-${month_input.value}-${day_input.value} ${hour_input.value}:${minute_input.value}:${second_input.value}`;
                } else if (hidden_input.getAttribute("class") === "date-hidden") {
                    hidden_input.value = `${year_input.value}-${month_input.value}-${day_input.value}`;
                } else if (hidden_input.getAttribute("class") === "time-hidden") {
                    hidden_input.value = `${hour_input.value}:${minute_input.value}:${second_input.value}`;
                }
            })
        }
    }
});
