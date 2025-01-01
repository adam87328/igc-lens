// Wait for the window to load
window.onload = function() {
    // Initial coordinates and zoom level
    const map = L.map('map').fitBounds([cornerNE,cornerSW]);

    // 2. Add a tile layer (OpenStreetMap, or another provider)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // 4. Add an event listener for the 'load' event
    map.on('load', function() {

        // 5. Add markers to the map after the map has fully loaded
        markerList.forEach(markerData => {
            const coordinates = markerData.geometry.coordinates;
            const popupContent = markerData.properties.popupContent;
            const iconUrl = markerData.properties.iconUrl;

            // Create a marker with the selected custom icon and add it to the map
            L.marker(
                [coordinates[1], coordinates[0]], 
                { icon: L.icon(
                    {iconUrl: iconUrl,
                     iconSize: [25, 41],
                     iconAnchor: [0, 41],
                     popupAnchor: [1, -34]})
             }).addTo(map).bindPopup(popupContent); // Bind a popup with the provided content
        });
    });

    // 6. Trigger the 'load' event manually once the tile layer is added
    map.whenReady(function() {
        map.fire('load');
    });
};