let map;
let routingControl;

function initMap(lat, lng) {
    map = L.map('map').setView([lat, lng], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
}

function showRoute(fromLat, fromLng, toLat, toLng) {
    if (routingControl) {
        map.removeControl(routingControl);
    }

    routingControl = L.Routing.control({
        waypoints: [
            L.latLng(fromLat, fromLng),
            L.latLng(toLat, toLng)
        ],
        routeWhileDragging: false,
        show: false
    }).addTo(map);
}

function addMarker(lat, lng, title) {
    L.marker([lat, lng])
        .bindPopup(title)
        .addTo(map);
}