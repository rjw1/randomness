var centre_lat, centre_long, map;
var positions = [], markers = [];
var base_url = "http://pubology.co.uk/";
var icons = {};

var gicon = L.Icon.extend( {
    shadowUrl: null,
    iconSize: new L.Point( 32, 32 ),
    iconAnchor: new L.Point( 15, 32 ),
    popupAnchor: new L.Point( 0, -40 )
} );
var icon_base_url = 'http://maps.google.com/mapfiles/ms/micons/';

icons.open = new gicon( icon_base_url + 'green-dot.png' );
icons.closed = new gicon( icon_base_url + 'yellow-dot.png' );
icons.demolished = new gicon( icon_base_url + 'red-dot.png' );

$(
  function() {
    map = new L.Map( 'map_canvas' );
    var map_centre = new L.LatLng( centre_lat, centre_long );
    var tile_layer;

    if ( use_gmaps ) {
      tile_layer = new L.Google( 'ROADMAP' );
    } else {
      var mq_url = 'http://{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.png';
      var subdomains = [ 'otile1', 'otile2', 'otile3', 'otile4' ];
      var attrib = 'Data, imagery and map information provided by <a href="http://open.mapquest.co.uk" target="_blank">MapQuest</a>, <a href="http://www.openstreetmap.org/" target="_blank">OpenStreetMap</a> and contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/" target="_blank">CC-BY-SA</a>';

      tile_layer = new L.TileLayer( mq_url, { maxZoom: 18, attribution: attrib, subdomains: subdomains } );
    }

    map.setView( map_centre, 13 ).addLayer( tile_layer );

    add_markers();
  }
);

function add_marker( i, pub ) {
  var content, icon, marker, position;

  if ( pub.not_on_map ) {
    return;
  }

  position = new L.LatLng( pub.lat, pub.long );

  if ( pub.demolished ) {
    icon = icons.demolished;
  } else if ( pub.closed ) {
    icon = icons.closed;
  } else {
    icon = icons.open;
  }

  marker = new L.Marker( position, { icon: icon } );
  map.addLayer( marker );

  content = '<a href="' + base_url + 'pubs/' + pub.id + '.html">' +
            pub.name + '</a>';
  if ( pub.demolished ) {
    content = content + ' (demolished)';
  } else if ( pub.closed ) {
    content = content + ' (closed)';
  }
  content = content + '<br>' + pub.address;

  marker.bindPopup( content );

  markers[ i ] = marker;
  positions[ i ] = position;
}

function show_marker( i ) {
  markers[ i ].openPopup();
  map.panTo( positions[ i ] );
  return false;
}

