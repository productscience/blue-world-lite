jQuery(document).ready(function($) {
  var mymap = L.map('collection-map').setView([51.557853, -0.073096], 13);
  var popup = L.popup();

  L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/streets-v9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoibXJjaHJpc2FkYW1zIiwiYSI6InFobnRZRzQifQ.jLPeG4HV4RiCL8RVNPBTwg', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
    maxZoom: 18,
  }).addTo(mymap);

  function showLocation(e) {
      // update popup to show name
      var p = this.popup, loc = this.loc, mymap = this.leafletmap;
      p.setContent("<p><strong>" + loc.name + "</strong></p><p><small>" + loc.location + "</small></p>");
      p.setLatLng(e.latlng);
      p.openOn(mymap);
  }

  // accepts a set of coordinates and returns a leaflet marker if they're
  // usable
  function createMarker(loc) {

    // check for None's coming through from django
    if (loc.longitude === "None" || loc.latitude == "None"){
      return false
    }
    // if we have both coords, we can create a marker
    if (loc.longitude && loc.latitude) {
      return L.marker([loc.latitude, loc.longitude])
    }
    // otherwise assume we didn't have the required attributes
    return false
  }

  GC.markers = {}
  GC.activeMarker = "";
  
  $.each(GC.locations, function(k, loc) {
    // only try to place a marker if we have coords to place with
    newMarker = createMarker(loc)
    if (newMarker) {
      newMarker
        .addTo(mymap)
        .bindPopup("<p><strong>" + loc.name + "</strong></p><p><small>" + loc.location + "</small></p>");
      GC.markers[k] = { id: k, marker: newMarker};
    }

    // add listener on the inputs
    $('.collection-points ul li').on('mouseover', function(event) {
      var marker = $(this).find('input').attr('id');

      if (marker !== GC.activeMarker){
        GC.activeMarker = marker;
        GC.markers[marker].marker.fire('click');
      }
    })
  })


  // add listener to find marker with the `id_collection_point_0` id,
  // so it is highlighted when selected.

});
