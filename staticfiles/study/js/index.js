let markers = []


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Search for the CSRF cookie name
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function createSearchableMap() {
    window.bounds = new google.maps.LatLngBounds();
    var mapOptions = {mapTypeId: 'roadmap'};
    window.gmap = new google.maps.Map(document.getElementById('map'), mapOptions);
    window.gmap.setTilt(45);
    var center = new google.maps.LatLng(35, -5);
    window.gmap.setCenter(center);
    window.gmap.setZoom(5);
}

function addLocations(locations){
    var _markers = [];
    var infoWindowContent = [];
    locations.forEach(function(location) {
      _markers.push([location.name, location.lat, location.lng]);
      
      infoWindowContent.push([`
      <div class="infoWindow">
        <h3>Name: ${location.name}</h3>
        <p>Address: ${location.address}
        <p>Country: ${location.country}</p>
        <p>Email: <a href='mailto:${location.email}'>${location.email}</a></p>
      </div>`]);
    });	    
  
    var infoWindow = new google.maps.InfoWindow(), marker, i;
    
    // Place the _markers on the map
    for (i = 0; i < _markers.length; i++) {
      var position = new google.maps.LatLng(_markers[i][1], _markers[i][2]);
      window.bounds.extend(position);
      marker = new google.maps.Marker({
        position: position,
        map: window.gmap,
        title: _markers[i][0],
      });
      markers.push(marker)
      
      // Add an infoWindow to each marker, and create a closure so that the current
      // marker is always associated with the correct click event listener
      google.maps.event.addListener(marker, 'click', (function(marker, i) {
        return function() {
          infoWindow.setContent(infoWindowContent[i][0]);
          infoWindow.open(window.gmap, marker);
        }
      })(marker, i));
  
      // Only use the bounds to zoom the map if there is more than 1 location shown
      if (locations.length > 1) {
        window.gmap.fitBounds(window.bounds);
      } else {
        var center = new google.maps.LatLng(locations[0].lat, locations[0].lng);
        window.gmap.setCenter(center);
        window.gmap.setZoom(15);
      }
    }
  }
function clearMarkers() {
    for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
    }
    markers = []; // Clear the markers array
}
submit_form = e=>{
    e.preventDefault()
    let address = document.getElementById('address')
    let distance = document.getElementById('distance')
    if(address.value=='')return
    if(distance.value=='')return
    const csrftoken = getCookie('csrftoken');
    fetch('/study/search/',  {
        method: "POST",
        headers: {'X-CSRFToken': csrftoken},
        body: JSON.stringify({
            "address": address.value.split(' ').join('+'),
            "distance": Math.floor(distance.value || 0),
        })})
    .then(res=>res.json())
    .then(data=>{
        console.log(data)
        clearMarkers(markers)
        addLocations(data)
    })
}
window.onload = () => {
    let form = document.getElementById('form')
    let search_button = document.getElementById('search_button')
    form.addEventListener('submit', submit_form)
    search_button.addEventListener('click', submit_form)
    createSearchableMap()
}  