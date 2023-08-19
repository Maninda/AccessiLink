var parkingSpots = [];

$(document).ready(function () {
    var locationInput = $('#locationInput');
    var suggestionsContainer = $('.suggestions');
    var longitudeElement = $('#longitude');
    var latitudeElement = $('#latitude');
    locationInput.on('input', function () {
        var searchQuery = locationInput.val();
    
        $.ajax({
            url: 'https://nominatim.openstreetmap.org/search',
            data: {
                q: searchQuery,
                format: 'json',
                limit: 1 // Fetch only one result for simplicity
            },
            dataType: 'json',
            success: function (data) {
                if (data.length > 0) {
                    var result = data[0]; // Assuming the first result is the relevant one
                    var longitude = parseFloat(result.lon);
                    var latitude = parseFloat(result.lat);
    
                    longitudeElement.text(longitude);
                    latitudeElement.text(latitude);
                }
            },
            error: function () {
                console.log('Error fetching location suggestions from the API');
            }
        });
    });


    // Handle suggestion click
    suggestionsContainer.on('click', '.suggestion-item', function () {
        var suggestionText = $(this).text();

        // Update the input value with the selected suggestion
        locationInput.val(suggestionText);

        // Get the longitude and latitude from the suggestion's data and update the elements
        var longitude = $(this).data('longitude');
        var latitude = $(this).data('latitude');

        longitudeElement.text(longitude);
        latitudeElement.text(latitude);

        // Hide the suggestions dropdown
        suggestionsContainer.hide();
    });

    // Hide suggestions when clicking outside the input and suggestions
    $(document).on('click', function (e) {
        if (!locationInput.is(e.target) && !suggestionsContainer.is(e.target)
                && suggestionsContainer.has(e.target).length === 0) {
            suggestionsContainer.hide();
        }
    });

    // Handle form submission
    $('#locationForm').on('submit', function (event) {
        event.preventDefault();

        var searchQuery = locationInput.val();
        var longitude = parseFloat(longitudeElement.text());
        var latitude = parseFloat(latitudeElement.text());


        // Make an AJAX POST request to Flask's /person route
        $.ajax({
            url: 'http://127.0.0.1:8080/person', // Update with the correct URL
            method: 'GET',
            data: {
                longitude: longitude,
                latitude: latitude,
                availability: true // Set this based on your availability logic
            },
            success: function (response) {
                console.log(response.closest_parks);
                console.log(response.closest_parks);
                // Update the parkingSpots variable with the response data
                parkingSpots = response.closest_parks;

                // Render the updated parking spots
                renderParkingSpots();
            },
            error: function (error) {
                console.error('Error:', error);
            }
        });
    });


    const parkingList = $('#parkingList');

    // Function to render parking spots
    function renderParkingSpots() {
        parkingList.empty();
        parkingSpots.forEach(function (spot) {
            const spotElement = $('<div class="parking-spot"></div>');
            spotElement.html(`
                <span>${spot.CARPARK_NAME} (${spot.URL})</span>
                ${spot.reserved ? '<button class="unreserve-btn">Unreserve</button>' : '<button class="reserve-btn">Reserve</button>'}
            `);
            parkingList.append(spotElement);
        });
    }

    renderParkingSpots();

    // Event handlers for reserving/unreserving spots
    parkingList.on('click', '.reserve-btn', function () {
        var spotName = $(this).closest('.parking-spot').find('span').text().split(' (')[0]; // Extracting the spot name
        var availability = true; // Assuming you want to reserve the spot

        // Make an AJAX POST request to Flask's /allocate route
        $.ajax({
            url: 'http://127.0.0.1:8080/allocate', // Update with the correct URL
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                carParkName: spotName,
                availability: availability
            }),
            success: function (response) {
                if (response.success) {
                    console.log(response.message);
                    // Update the reserved status in the parkingSpots array
                    updateReservedStatus(spotName, true);
                } else {
                    console.error(response.message);
                }
            },
            error: function (error) {
                console.error('Error:', error);
            }
        });
    });

    // Function to update the reserved status in parkingSpots array
    function updateReservedStatus(spotName, reserved) {
        var spotToUpdate = parkingSpots.find(function (spot) {
            console.log('sps')
            console.log(spotName)
            console.log(spot.CARPARK_NAME)
            return spot.CARPARK_NAME.includes(spotName);
        });
        console.log(spotToUpdate)
        if (spotToUpdate) {
            spotToUpdate.reserved = reserved;
            renderParkingSpots(); // Update the UI with the updated data
        }
    }


});
