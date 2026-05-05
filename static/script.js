let gaugeChart, pieChart, barChart;
let map;

// Predict AQI
function predictAQI() {

    const data = {
        pm25: document.getElementById("pm25").value,
        pm10: document.getElementById("pm10").value,
        no2: document.getElementById("no2").value,
        co: document.getElementById("co").value,
        o3: document.getElementById("o3").value,
    };

    fetch("/predict", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {

        if(result.error){
            document.getElementById("result").innerText = result.error;
            return;
        }

        document.getElementById("result").innerHTML = `
            <div class="model">RF: ${result.random_forest} (${result.rf_status})</div>
            <div class="model">XGB: ${result.xgboost} (${result.xgb_status})</div>
            <div class="model">DT: ${result.decision_tree} (${result.dt_status})</div>
        `;

        renderCharts(result, data);
        showHealthAdvisory(result.random_forest);
        updateMap(result.random_forest);
    });
}

// Charts
function renderCharts(result, input){

    if(gaugeChart) gaugeChart.destroy();
    gaugeChart = new Chart(document.getElementById("gaugeChart"), {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [result.random_forest, 500 - result.random_forest]
            }]
        },
        options: {
            rotation: -90,
            circumference: 180
        }
    });

    if(pieChart) pieChart.destroy();
    pieChart = new Chart(document.getElementById("pieChart"), {
        type: 'pie',
        data: {
            labels: ["PM2.5","PM10","NO2","CO","O3"],
            datasets: [{
                data: [input.pm25,input.pm10,input.no2,input.co,input.o3]
            }]
        }
    });

    if(barChart) barChart.destroy();
    barChart = new Chart(document.getElementById("barChart"), {
        type: 'bar',
        data: {
            labels: ["RF","XGB","DT"],
            datasets: [{
                data: [result.random_forest,result.xgboost,result.decision_tree]
            }]
        }
    });
}

// Map init
function initMap(lat, lon){
    map = L.map('map').setView([lat, lon], 10);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
        .addTo(map);

    setTimeout(() => {
        map.invalidateSize();
    }, 200);
}

// Update map
function updateMap(aqi){
    if(!navigator.geolocation){
        alert("Geolocation not supported");
        return;
    }

    navigator.geolocation.getCurrentPosition(pos => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        if(!map){
            initMap(lat, lon);
        } else {
            map.setView([lat, lon], 10);
        }

        L.marker([lat, lon]).addTo(map)
            .bindPopup("AQI: " + aqi)
            .openPopup();

    }, () => {
        alert("Location permission denied");
    });
}

// Health advisory
function showHealthAdvisory(aqi){

    let msg = "";

    if(aqi <= 50) msg = "Good";
    else if(aqi <= 100) msg = "Moderate";
    else if(aqi <= 200) msg = "Unhealthy";
    else if(aqi <= 300) msg = "Very Unhealthy";
    else msg = "Hazardous";

    document.getElementById("advisory").innerText = msg;
}