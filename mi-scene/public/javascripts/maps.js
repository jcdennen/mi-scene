// In the following example, markers appear when the user clicks on the map.
// Each marker is labeled with a single alphabetical character.

// var labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
// var labelIndex = 0;

window.initMap = function() {
  // centers each map on the continental United States
  var center = { lat: 37.0393707, lng: -96.4017335 };
  var currentAritst;
  var currentFollower;
  var currentFollowerCoords;
  var polygons = [];
  var maps = [];
  var polygon;
  var polygonCoords;
  var map;

  // loop through each artist object and set up its map
  for (var object in artistObjects) {
    currentAritst = artistObjects[object];
    map = new google.maps.Map(document.getElementById(currentAritst["username"]), {
      zoom: 3,
      center: center
    });

    // draw a ploygon on each artist's map for each influential follower they have
    for (var follower in currentAritst["top_followers"]) {
      currentFollower = currentAritst["top_followers"][follower];
      currentFollowerCoords = currentFollower["status"]["place"]["bounding_box"]["coordinates"];
      console.log(currentFollower["status"]["place"]["full_name"]);

      polygonCoords = [
        {lat: currentFollowerCoords[0][0][1], lng: currentFollowerCoords[0][0][0]},
        {lat: currentFollowerCoords[0][1][1], lng: currentFollowerCoords[0][1][0]},
        {lat: currentFollowerCoords[0][2][1], lng: currentFollowerCoords[0][2][0]},
        {lat: currentFollowerCoords[0][3][1], lng: currentFollowerCoords[0][3][0]},
        {lat: currentFollowerCoords[0][0][1], lng: currentFollowerCoords[0][0][0]}
      ];

      polygon = new google.maps.Polygon({
        paths: polygonCoords,
        strokeColor: '#FF0000',
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: '#FF0000',
        fillOpacity: 0.10
      });

      polygon.setMap(map);
    }
  }


  // This event listener calls addMarker() when the map is clicked.
  // google.maps.event.addListener(map, 'click', function(event) {
  //   addMarker(event.latLng, map);
  // });

  // Add a marker at the center of the map.
  // addMarker(bangalore, map);
}

// Adds a marker to the map.
// function addMarker(location, map) {
//   // Add the marker at the clicked location, and add the next-available label
//   // from the array of alphabetical characters.
//   var marker = new google.maps.Marker({
//     position: location,
//     // label: labels[labelIndex++ % labels.length],
//     map: map
//   });
// }

// google.maps.event.addDomListener(window, 'load', initialize);
