// Wait for the window to load
window.onload = function() {
    // Initial coordinates and zoom level
    const map = L.map('map').fitBounds([cornerNE,cornerSW]);

    // 2. Add a tile layer (OpenStreetMap, or another provider)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // 3. Define custom icons
    const iconLocalFlight = L.icon({
        iconUrl: iconUrlLocalFlight,
        iconSize: [25, 41],
        iconAnchor: [0, 41],
        popupAnchor: [1, -34]
    });

    const iconFreeFlight = L.icon({
        iconUrl: iconUrlFreeFlight,
        iconSize: [25, 41],
        iconAnchor: [0, 41],
        popupAnchor: [1, -34]
    });

    const iconFlatTriangle = L.icon({
        iconUrl: iconUrlFlatTriangle,
        iconSize: [25, 41],
        iconAnchor: [0, 41],
        popupAnchor: [1, -34]
    });

    const iconFaiTriangle = L.icon({
        iconUrl: iconUrlFaiTriangle,
        iconSize: [25, 41],
        iconAnchor: [0, 41],
        popupAnchor: [1, -34]
    });

    const iconClosedFlatTriangle = L.icon({
        iconUrl: iconUrlClosedFlatTriangle,
        iconSize: [25, 41],
        iconAnchor: [0, 41],
        popupAnchor: [1, -34]
    });

    const iconClosedFaiTriangle = L.icon({
        iconUrl: iconUrlClosedFaiTriangle,
        iconSize: [25, 41],
        iconAnchor: [0, 41],
        popupAnchor: [1, -34]
    });

    // 4. Add an event listener for the 'load' event
    map.on('load', function() {

        // 5. Add markers to the map after the map has fully loaded
        markerList.forEach(markerData => {
            const coordinates = markerData.geometry.coordinates;
            const popupContent = markerData.properties.popupContent;
            const markerType = markerData.properties.markerType;

            // Choose the icon based on the 'type' property
            let chosenIcon;
            if (markerType === 'Local Flight') {
                chosenIcon = iconLocalFlight;
            } else if (markerType === 'Free Flight') {
                chosenIcon = iconFreeFlight;
            } else if (markerType === 'Free Triangle') {
                chosenIcon = iconFlatTriangle;
            }else if (markerType === 'FAI Triangle') {
                chosenIcon = iconFaiTriangle;
            }else if (markerType === 'Closed Free Triangle') {
                chosenIcon = iconClosedFlatTriangle;
            }else if (markerType === 'Closed FAI Triangle') {
                chosenIcon = iconClosedFaiTriangle;
            } else {
                chosenIcon = L.icon()
            }
            // Create a marker with the selected custom icon and add it to the map
            L.marker([coordinates[1], coordinates[0]], { icon: chosenIcon })
                .addTo(map)
                .bindPopup(popupContent); // Bind a popup with the provided content
        });
    });

    // 6. Trigger the 'load' event manually once the tile layer is added
    map.whenReady(function() {
        map.fire('load');
    });
};