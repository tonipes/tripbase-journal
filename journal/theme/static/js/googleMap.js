var point = {lat: 0, lng: 0};

function setPoint(latitude, longitude) {
  point.lat = latitude;
  point.lng = longitude;
}

function initMap() {
  var map = new google.maps.Map(document.getElementById('map'), {
    zoom: 14,
    center: point
  });
  var marker = new google.maps.Marker({
    position: point,
    map: map
  });
}

// window.addEventListener('resize', function(event){
//   var m = document.getElementById('map');
//   m.style.height = m.style.width;
// });
