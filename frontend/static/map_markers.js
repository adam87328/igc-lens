// Create a global interface to update map theme
const mapThemeInterface = (() => {
    let map;
  
    // Light and dark map tile layers
    const lightTiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    });
    const darkTiles = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png', {
      attribution: '&copy; CartoDB'
    });
  
    // Initialize the map
    const initMap = (markerList,cornerNE,cornerSW) => { // markerList=markerList, cornerNE=cornerNE, cornerSW=cornerSW
        map = map = L.map('map').fitBounds([cornerNE,cornerSW]);
        // set tile layer according to current <html data-bs-theme="dark">
        updateMapTheme(document.documentElement.getAttribute('data-bs-theme'));
        // add markers
        markerList.forEach(markerData => {
            const coordinates = markerData.geometry.coordinates;
            const popupContent = markerData.properties.popupContent;
            const iconUrl = markerData.properties.iconUrl;
            // Create a marker with the selected custom icon and add it to the map
            // Bind a popup with the provided content
            L.marker(
                [coordinates[1], coordinates[0]], 
                { icon: L.icon(
                    {iconUrl: iconUrl,
                        iconSize: [25, 41],
                        iconAnchor: [0, 41],
                        popupAnchor: [1, -34]})
                }).addTo(map).bindPopup(popupContent);
        });
    };

    // Update the map's tile layer based on the theme
    const updateMapTheme = (theme) => {
      if (!map) return;
  
      if (theme === 'dark') {
        map.removeLayer(lightTiles);
        map.addLayer(darkTiles);
      } else {
        map.removeLayer(darkTiles);
        map.addLayer(lightTiles);
      }
    };
      
    return {
      initMap,
      updateMapTheme
    };
  })();