function reassure() {
  document.getElementById( 'upload_msg' ).innerHTML='Uploading... please be patient, this may take a little while.';
  return true;
}

var map;
var markers = [];
var content = [];
var infowindow;
var base_url = "http://pubology.co.uk/";

function initialise( centre_lat, centre_long ) {
  var map_centre = new google.maps.LatLng( centre_lat, centre_long );
  var map_options = {
                      zoom: 12,
                      center: map_centre,
                      mapTypeId: google.maps.MapTypeId.ROADMAP
                    };
  map = new google.maps.Map( document.getElementById( "map_canvas" ),
                                 map_options );
  infowindow = new google.maps.InfoWindow();
}

function add_marker( i, pub ) {
  var icon;
  var position;

  if ( pub.not_on_map ) {
    return;
  }

  position = new google.maps.LatLng( pub.lat, pub.long );
  icon = "http://maps.google.com/mapfiles/ms/micons/";
  if ( pub.demolished ) {
    icon = icon + "red";
  } else if ( pub.closed ) {
    icon = icon + "yellow";
  } else {
    icon = icon + "green";
  }
  icon = icon + "-dot.png";
  markers[ i ] = new google.maps.Marker({
      position: position,
      title: pub.name,
      map: map,
      icon: icon
  });
  content[ i ] = '<a href="' + base_url + 'pubs/' + pub.id + '.html">' +
                 pub.name + '</a>';
  if ( pub.demolished ) {
    content[ i ] = content[ i ] + ' (demolished)';
  } else if ( pub.closed ) {
    content[ i ] = content[ i ] + ' (closed)';
  }
  content[ i ] = content[ i ] + '<br>' + pub.address;
  google.maps.event.addListener( markers[ i ], "click", function() {
    infowindow.setContent( content[ i ] );
    infowindow.open( map, markers[ i ] );
  } );
}

function open_marker( i ) {
  infowindow.setContent( content[ i ] );
  infowindow.open( map, markers[ i ] );
  map.panTo( markers[ i ].getPosition() );
  return false;
}

