// https://gis.stackexchange.com/questions/360293/add-something-into-l-circlemarker
function circleWithText2(latLng, txt, radius, borderWidth, circleClass) {
    var size = radius * 2;
    var style = 'style="width: ' + size + 'px; height: ' + size + 'px; border-width: ' + borderWidth + 'px;"';
    var iconSize = size + (borderWidth * 2);
    var icon = L.divIcon({
      html: '<span class="' + 'circle ' + circleClass + '" ' + style + '>' + txt + '</span>',
      className: '',
      iconSize: [iconSize, iconSize]
    });
    var marker = L.marker(latLng, {
      icon: icon
    });
    return(marker);
  }

// circleWithText2([44.6, 22.6], '67', 30, 3, 'circle1').addTo(map);
// circleWithText2([44.6, 22.5], '89', 20, 2, 'circle2').addTo(map);