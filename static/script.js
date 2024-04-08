let chart = null;
let lastEntry = null;

const baseURL = "http://10.42.0.1:8000";

const x    = document.getElementById("x");
const y    = document.getElementById("y");
const z    = document.getElementById("z");
const temp = document.getElementById("temp");

const ctx       = document.getElementById('tempDiv');
const ledBtn    = document.getElementById("ledBtn");
const trashBtn  = document.getElementById("trashBtn");
const pauseBtn  = document.getElementById("pauseBtn");
const pauseImg  = document.getElementById("pauseImg");
const trashIcon = document.getElementById("trashIcon");


function debounce(func, delay) {
    let timerId;

    return (...args) => {
        clearTimeout(timerId);
        timerId = setTimeout(() => func(...args), delay);
    }
}

function getLive() {
    fetch(`${baseURL}/live`)
        .then(res => res.json())
        .then(data => {
            x.innerText    = data["x"];
            y.innerText    = data["y"];
            z.innerText    = data["z"];
            temp.innerText = data["temp"];

            if (chart.data.labels.at(-1) != lastEntry) {
                chart.data.labels.push(data["created_at"]);
                chart.data.datasets[0].data.push(data["temp"]);

                lastEntry = data["created_at"];
                chart.update();
            }
        })
}

function updateLED(input) {
    ledBtn.src = `/static/img/led${input.checked ? '': '_off'}.webp`
    fetch(`${baseURL}/led?state=${input.checked ? "ON": "OFF"}`, { method: "POST" });
}

function clearData() {
    trashBtn.checked = false;
    trashIcon.src = "/static/img/trash.webp";
    
    chart.data.labels = [];
    chart.data.datasets[0].data = [];

    chart.update();
}

function toggleClear() {
    trashIcon.src = `/static/img/${trashIcon.src.endsWith('trash.webp') ? 'cancel': 'trash'}.webp`
}

let refreshRate = 1000;
let intervalId = setInterval(getLive, refreshRate);

let changeInterval = debounce((value) => {
    clearInterval(intervalId);
    intervalId = setInterval(getLive, value);
}, 500);

function setRefreshRate(el) {
    refreshRate = el.value;
    el.nextElementSibling.value = `${el.value}ms`

    if (!pauseBtn.checked) {
        changeInterval(el.value);
    }
}

function toggleAutoRefresh(state) {
    if (state) {
        pauseImg.src = `/static/img/play.webp`;
        clearInterval(intervalId);
    } else {
        pauseImg.src = `/static/img/pause.webp`;
        intervalId = setInterval(getLive, refreshRate);
    }
}

document.onkeyup = (e) => {
    if (e.key === " ") {
        pauseBtn.checked = !pauseBtn.checked;
        toggleAutoRefresh(pauseBtn.checked);
    }
}

Chart.defaults.color = '#ccc';
Chart.defaults.borderColor = '#888';
Chart.defaults.font.size = 14;
Chart.defaults.font.weight = "bold";

fetch(`${baseURL}/temps`)
    .then(res => res.json())
    .then(data => {
        lastEntry = data.at(-1)["created_at"];

        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(e => e['created_at']),
                datasets: [{
                    tension: 0.2,
                    pointBackgroundColor: "#ccc",
                    data: data.map(e => e['temp']),
                }]
            },
            options: {
                radius: 5,
                responsive: true,
                plugins: {legend: false },
                scales: {
                    y: {
                        ticks: {
                            callback: (val) => { return `${val}°C` }
                        },
                    }
                }
            }
        })
    })
