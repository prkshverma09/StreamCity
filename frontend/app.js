document.addEventListener("DOMContentLoaded", () => {
    // --- Map Initialization ---
    const map = L.map('map').setView([40.7128, -74.0060], 12); // Default to NYC

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    // --- Vehicle Marker Management ---
    const vehicleMarkers = {}; // To store markers by vehicle_id

    function createOrUpdateMarker(data) {
        const vehicleId = data.VEHICLE_ID;
        const lat = data.LATITUDE;
        const lon = data.LONGITUDE;
        const type = data.TYPE;
        const lastUpdated = data.LAST_UPDATED;
        const passengerCount = data.PASSENGER_COUNT;

        const popupContent = `
            <b>ID:</b> ${vehicleId}<br>
            <b>Type:</b> ${type}<br>
            <b>Passengers:</b> ${passengerCount}<br>
            <b>Last Updated:</b> ${lastUpdated}
        `;

        if (vehicleMarkers[vehicleId]) {
            // Marker exists, update its position and popup
            vehicleMarkers[vehicleId]
                .setLatLng([lat, lon])
                .setPopupContent(popupContent);
        } else {
            // Marker doesn't exist, create a new one
            const marker = L.marker([lat, lon]).addTo(map)
                .bindPopup(popupContent);
            vehicleMarkers[vehicleId] = marker;
        }
    }

    // --- WebSocket Connection ---
    const statusDiv = document.getElementById('connection-status');
    const socket = new WebSocket("ws://localhost:8000/ws");

    socket.onopen = function(e) {
        console.log("[open] Connection established");
        statusDiv.textContent = "Connected";
        statusDiv.className = "connected";
    };

    socket.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            console.log("[message] Data received from server:", data);

            // ksqlDB may send a payload with all caps keys
            // Normalize keys to be consistent
            const normalizedData = {};
            for (const key in data) {
                normalizedData[key.toUpperCase()] = data[key];
            }

            if (normalizedData.VEHICLE_ID && normalizedData.LATITUDE && normalizedData.LONGITUDE) {
                createOrUpdateMarker(normalizedData);
            }

        } catch (error) {
            console.error("Error parsing message data:", error);
        }
    };

    socket.onclose = function(event) {
        if (event.wasClean) {
            console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
        } else {
            console.error('[close] Connection died');
        }
        statusDiv.textContent = "Disconnected. Trying to reconnect...";
        statusDiv.className = "disconnected";
        // Optional: Implement reconnection logic here
        setTimeout(function() {
          // Add reconnection logic if desired
        }, 5000);
    };

    socket.onerror = function(error) {
        console.error(`[error] ${error.message}`);
        statusDiv.textContent = "Connection Error";
        statusDiv.className = "disconnected";
    };
});