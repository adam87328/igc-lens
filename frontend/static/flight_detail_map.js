// Wait for the window to load
window.onload = function() {

    const base1 = L.tileLayer(
        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxNativeZoom: 17,
    });
    const base2 = L.tileLayer(
        'https://tile.opentopomap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',
        maxNativeZoom: 17,
    });
    const base3 = L.tileLayer(
        'https://mapsneu.wien.gv.at/basemap/bmapgelaende/grau/google3857/{z}/{y}/{x}.jpeg', {
        attribution: 'Datenquelle: <a href="https://www.basemap.at">basemap.at</a>',
        maxNativeZoom: 19,
    });
    const base4 = L.tileLayer(
        'https://mapsneu.wien.gv.at/basemap/bmapoberflaeche/grau/google3857/{z}/{y}/{x}.jpeg', {
        attribution: 'Datenquelle: <a href="https://www.basemap.at">basemap.at</a>',
        maxNativeZoom: 19,
    });
    const base5 = L.tileLayer(
        'https://mapsneu.wien.gv.at/basemap/bmaphidpi//grau/google3857/{z}/{y}/{x}.jpeg', {
        attribution: 'Datenquelle: <a href="https://www.basemap.at">basemap.at</a>',
        maxNativeZoom: 19,
        crossOrigin: "anonymous" // seems not to support it
    });
    const base6 = L.tileLayer(
        'https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg', {
        attribution: '&copy; <a href="https://www.swisstopo.admin.ch/">swisstopo</a>',
        maxNativeZoom: 18,
    });

    // generic properties popup
    function onEachFeature(feature, layer) {
        if (feature.properties) {
            // Start building the popup content
            let popupContent = '<b>Properties:</b><br>';
            // Loop through all properties and add them to the popup content
            for (const key in feature.properties) {
                if (feature.properties.hasOwnProperty(key)) {
                    popupContent += `<b>${key}</b>: ${feature.properties[key]}<br>`;
                }
            }
            layer.bindPopup(popupContent);
        }
    }

    // glide popup generator
    function onEachGlide(feature, layer) {
        // Convert glide ratio to the common convention with positive sign
        // The raw value is negative when altitude change is negative.
        if (feature.properties.glide_ratio < 0) {
            feature.properties.glide_ratio = 
                `${-feature.properties.glide_ratio.toFixed(1)}`;
        } else {
            // zero or altitude gain
            feature.properties.glide_ratio = 'inf';
        }
        // popup content
        let c = `<b>Glide #${feature.id}</b><br>`;
        c+=`<b>Duration</b>: ${(feature.properties.duration/60).toFixed(1)} min<br>`;
        c+=`<b>Altitude change</b>: ${feature.properties.alt_change.toFixed(0)} m<br>`;
        c+=`<b>Glide ratio</b>: ${feature.properties.glide_ratio}<br>`;
        layer.bindPopup(c);
    }

    // thermal popup generator
    function onEachThermal(feature, layer) {
        let c = `<b>Thermal #${feature.id}</b><br>`;
        c+=`<b>Duration</b>: ${(feature.properties.duration/60).toFixed(1)} min<br>`;
        c+=`<b>Altitude gain</b>: ${feature.properties.alt_change.toFixed(0)} m<br>`;
        c+=`<b>Average climb</b>: ${feature.properties.vertical_velocity.toFixed(1)} m/s<br>`;
        c+=`<b>Turn direction</b>: ${feature.properties.direction}<br>`;
        layer.bindPopup(c);
    }

    const styleGood = {
        color: "#00a706",
        weight: 3
    };
    const styleNeutral = {
        color: "#00bbff",
        weight: 3
    };
    const styleBad = {
        color: "#ff3300",
        weight: 4
    };

    // glide style
    function glideStyle(feature) {
        let x = feature.properties.glide_ratio;
        // convert to positive glide ratio to avoid mindfuck
        if ( x > 0 ){ x = 100; }
        if ( x < 0 ){ x = -x; }
        // categorize
        if ( x > 10 ) {
            return styleGood;
        } else if ( x > 7.5 ) {
            return styleNeutral;
        } else {
            return styleBad;
        }
    }

    // thermal style
    function thermalStyle(feature) {
        let x = feature.properties.vertical_velocity;
        // categorize
        if ( x > 2.5 ) {
            return styleGood;
        } else if ( x > 1.5 ) {
            return styleNeutral;
        } else {
            return styleBad;
        }
    }
    
    const xcscore = L.geoJSON(geoXcscore, {
        style: style_xcscore,
        onEachFeature: onEachFeature
    });
    const glides = L.geoJSON(geoGlides, {
        style: glideStyle,
        onEachFeature: onEachGlide
    });
    const thermals = L.geoJSON(geoThermals, {
        style: thermalStyle,
        onEachFeature: onEachThermal
    });
    const track = L.layerGroup([glides,thermals]);

    // groups for layer control
    const baseMaps = {
        "openstreetmap": base1,
        "opentopomap": base2,
        "basemap.at terrain": base3,
        "basemap.at surface": base4,
        "basemap.at highDPI": base5,
        "swisstopo": base6 
    };
    const overlayMaps = {
        "Track": track,
        "XC Score": xcscore
    };

    // init map
    const map = L.map('map').fitBounds([cornerNE,cornerSW]);
    // default show
    base1.addTo(map)
    track.addTo(map)
    // layers selector
    var layerControl = L.control.layers(baseMaps, overlayMaps).addTo(map);
};