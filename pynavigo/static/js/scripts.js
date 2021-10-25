var x=document.getElementById("geolocation");
function getLocation()
  {
  if (navigator.geolocation)
    {
    navigator.geolocation.getCurrentPosition(showPosition,showError);
    }
  else{x.innerHTML="Geolocation is not supported by this browser.";}
  }

function showPosition(position)
  {
  map = new OpenLayers.Map("mapitinerary");
  map.addLayer(new OpenLayers.Layer.OSM());

  var size = new OpenLayers.Size(21,25);
  var size_man = new OpenLayers.Size(42,50);
  var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
  var man_green = new OpenLayers.Icon('static/img/man-green.png', size_man, offset);

  var user_position = new OpenLayers.Layer.Markers("Your position");
  map.addLayer(user_position);

  var centerLonLat = new OpenLayers.LonLat(position.coords.longitude, position.coords.latitude)
    .transform(
       new OpenLayers.Projection("EPSG:4326"), // from WGS 1984
       map.getProjectionObject() // to Spherical Mercator
    );
  var positionLonLat = new OpenLayers.LonLat(position.coords.longitude, position.coords.latitude)
    .transform(
       new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
       map.getProjectionObject() // to Spherical Mercator Projection
    );

  user_position.addMarker(new OpenLayers.Marker(positionLonLat, man_green.clone()));

  map.setCenter(centerLonLat, 12);

  if(document.getElementById("departure"))
    {
      document.getElementById("departure").value = position.coords.latitude +
      ", " + position.coords.longitude;
    }

  if(document.getElementById("myposition"))
    {
      document.getElementById("myposition").innerHTML="(" + position.coords.latitude +
      ", " + position.coords.longitude + ")";
    }
  }

function showError(error)
  {
  switch(error.code)
    {
    case error.PERMISSION_DENIED:
      x.innerHTML="User denied the request for Geolocation."
      break;
    case error.POSITION_UNAVAILABLE:
      x.innerHTML="Location information is unavailable."
      break;
    case error.TIMEOUT:
      x.innerHTML="The request to get user location timed out."
      break;
    case error.UNKNOWN_ERROR:
      x.innerHTML="An unknown error occurred."
      break;
    }
  }
