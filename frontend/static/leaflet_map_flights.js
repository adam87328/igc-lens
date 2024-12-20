function map_init(map, options) {
    // popup handler
    function onEachFeature(feature, layer) {
      // does this feature have a property named popupContent?
      if (feature.properties && feature.properties.popupContent) {
          layer.bindPopup(feature.properties.popupContent);
      }
    }
    // add the GeoJSON layer
    L.geoJSON(feature_list, {onEachFeature: onEachFeature}).addTo(map);
    // center on the Alps
    map.setView([45.87, 10.87], 6);
}