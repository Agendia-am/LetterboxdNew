// Film Fanatic - Frontend JavaScript

const API_BASE = 'http://localhost:5005/api';

// State
let currentUsername = '';
let currentFilms = [];
let currentRecommendations = [];
let chartInstances = {};

// Elements
const homeScreen = document.getElementById('homeScreen');
const loadingScreen = document.getElementById('loadingScreen');
const dashboardScreen = document.getElementById('dashboardScreen');

const usernameInput = document.getElementById('usernameInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const backBtn = document.getElementById('backBtn');
const refreshRecommendations = document.getElementById('refreshRecommendations');

const errorMessage = document.getElementById('errorMessage');
const loadingTitle = document.getElementById('loadingTitle');
const loadingMessage = document.getElementById('loadingMessage');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');

// Event Listeners
analyzeBtn.addEventListener('click', handleAnalyze);
backBtn.addEventListener('click', goHome);
refreshRecommendations.addEventListener('click', loadRecommendations);

usernameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleAnalyze();
});

// Main Functions
async function handleAnalyze() {
    const username = usernameInput.value.trim();
    
    if (!username) {
        showError('Please enter a username');
        return;
    }
    
    currentUsername = username;
    hideError();
    showScreen('loading');
    
    // Start simulated progress bar
    let progress = 0;
    const progressInterval = setInterval(() => {
        if (progress < 90) {
            progress += Math.random() * 3;
            updateLoading('Scraping Profile...', `Processing films from ${username}'s profile`, Math.min(90, progress));
        }
    }, 500);
    
    try {
        // Step 1: Scrape profile
        updateLoading('Scraping Profile...', `Collecting films from ${username}'s profile`, 5);
        
        const scrapeResponse = await fetch(`${API_BASE}/scrape`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        
        clearInterval(progressInterval);
        
        if (!scrapeResponse.ok) {
            const error = await scrapeResponse.json();
            throw new Error(error.error || 'Failed to scrape profile');
        }
        
        const scrapeData = await scrapeResponse.json();
        currentFilms = scrapeData.films;
        
        updateLoading('Processing Data...', 'Analyzing your viewing habits', 92);
        
        // Populate dashboard
        populateDashboard(scrapeData);
        
        updateLoading('Generating Recommendations...', 'Finding movies you might love', 95);
        
        // Load recommendations in background
        loadRecommendations();
        
        updateLoading('Complete!', 'Loading your dashboard', 100);
        
        setTimeout(() => {
            showScreen('dashboard');
        }, 500);
        
    } catch (error) {
        clearInterval(progressInterval);
        console.error('Error:', error);
        showError(error.message);
        showScreen('home');
    }
}

async function loadRecommendations() {
    const recommendationsGrid = document.getElementById('recommendationsGrid');
    const recommendationsLoading = document.getElementById('recommendationsLoading');
    const recommendationsError = document.getElementById('recommendationsError');
    
    // Show loading
    recommendationsGrid.innerHTML = '';
    recommendationsLoading.classList.remove('hidden');
    recommendationsError.classList.add('hidden');
    
    try {
        const response = await fetch(`${API_BASE}/recommendations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUsername, top_n: 10 })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate recommendations');
        }
        
        const data = await response.json();
        currentRecommendations = data.recommendations;
        
        // Display recommendations
        displayRecommendations(currentRecommendations);
        
    } catch (error) {
        console.error('Recommendations error:', error);
        recommendationsError.textContent = 'Could not load recommendations. Click refresh to try again.';
        recommendationsError.classList.remove('hidden');
    } finally {
        recommendationsLoading.classList.add('hidden');
    }
}

function populateDashboard(data) {
    // Update title
    document.getElementById('dashboardTitle').textContent = `📊 ${currentUsername}'s Dashboard`;
    
    // Update stats cards
    document.getElementById('totalFilms').textContent = data.total_films.toLocaleString();
    document.getElementById('avgRating').textContent = data.stats.average_rating.toFixed(1) + '/5';
    document.getElementById('totalRuntime').textContent = Math.round(data.stats.total_runtime / 60) + 'h';
    document.getElementById('ratedFilms').textContent = data.stats.with_ratings.toLocaleString();
    
    // Populate charts
    populateCharts(data);
    
    // Populate top lists
    populateTopLists(data.stats);
}

function populateCharts(data) {
    // Destroy all existing chart instances before creating new ones
    destroyAllCharts();
    
    console.log('Populating charts with data:', data);
    
    // 1. Countries Map Chart (horizontal bar showing countries)
    const countryCounts = {};
    data.films.forEach(film => {
        const countries = film.country || film.countries;
        if (countries && Array.isArray(countries)) {
            countries.forEach(country => {
                countryCounts[country] = (countryCounts[country] || 0) + 1;
            });
        }
    });
    const topCountries = Object.entries(countryCounts)
        .sort((a, b) => b[1] - a[1]);
    
    console.log('Country chart data:', topCountries);
    createGeoChart('countryMapChart', topCountries);
    
    // 2. Personal Rating by Genre (bar chart)
    const genreRatings = {};
    data.films.forEach(film => {
        if (film.genres && film.personal_rating) {
            film.genres.forEach(genre => {
                if (!genreRatings[genre]) genreRatings[genre] = [];
                genreRatings[genre].push(parseFloat(film.personal_rating));
            });
        }
    });
    
    const genreAvgs = Object.entries(genreRatings)
        .map(([genre, ratings]) => [genre, ratings.reduce((a, b) => a + b, 0) / ratings.length])
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15);
    
    const genreColors = [
        '#e74c3c', '#9b59b6', '#3498db', '#1abc9c', '#f1c40f',
        '#e91e63', '#00bcd4', '#ff5722', '#8bc34a', '#ff9800',
        '#673ab7', '#00e676', '#ffc107', '#ff6f00', '#26c6da'
    ];
    
    createColorfulHorizontalBarChart('genreRatingChart',
        genreAvgs.map(g => g[0]),
        genreAvgs.map(g => g[1].toFixed(2)),
        'Avg Personal Rating',
        genreColors
    );
    
    // 3. Language Pie Chart
    const langCounts = {};
    data.films.forEach(film => {
        if (film.language) {
            const langs = Array.isArray(film.language) ? film.language : [film.language];
            langs.forEach(lang => {
                langCounts[lang] = (langCounts[lang] || 0) + 1;
            });
        }
    });
    const topLangs = Object.entries(langCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    createPieChart('languagePieChart',
        topLangs.map(l => l[0]),
        topLangs.map(l => l[1])
    );
    
    // 4. Personal Ratings by Decade (Candlestick-style chart)
    const decadeData = {};
    data.films.forEach(film => {
        const year = film.year || film.release_date;
        if (year && film.personal_rating) {
            const decade = Math.floor(parseFloat(year) / 10) * 10;
            if (!decadeData[decade]) decadeData[decade] = [];
            decadeData[decade].push(parseFloat(film.personal_rating));
        }
    });
    
    const sortedDecades = Object.keys(decadeData).sort();
    createCandlestickChart('decadeRatingsChart', sortedDecades, decadeData);
    
    // 5. Actor-Director Collaborations with Avg Community Rating
    const actorDirectorCollabs = {};
    data.films.forEach(film => {
        if (film.directors && film.actors && film.average_rating) {
            film.directors.forEach(director => {
                film.actors.slice(0, 3).forEach(actor => { // Top 3 actors per film
                    const key = `${actor} + ${director}`;
                    if (!actorDirectorCollabs[key]) {
                        actorDirectorCollabs[key] = { ratings: [], count: 0 };
                    }
                    actorDirectorCollabs[key].ratings.push(parseFloat(film.average_rating));
                    actorDirectorCollabs[key].count++;
                });
            });
        }
    });
    
    const topActorDirector = Object.entries(actorDirectorCollabs)
        .filter(([_, data]) => data.count >= 2) // At least 2 films together
        .map(([collab, data]) => [
            collab, 
            data.ratings.reduce((a, b) => a + b, 0) / data.ratings.length,
            data.count
        ])
        .sort((a, b) => b[2] - a[2]) // Sort by count
        .slice(0, 20);
    
    createBubbleChart('actorDirectorChart', topActorDirector, 'Actor-Director Collaborations', '#9b59b6');
    
    // 6. Composer-Director Collaborations with Avg Rating
    const composerDirectorCollabs = {};
    data.films.forEach(film => {
        if (film.directors && film.composer && film.average_rating) {
            film.directors.forEach(director => {
                const key = `${film.composer} + ${director}`;
                if (!composerDirectorCollabs[key]) {
                    composerDirectorCollabs[key] = { ratings: [], count: 0 };
                }
                composerDirectorCollabs[key].ratings.push(parseFloat(film.average_rating));
                composerDirectorCollabs[key].count++;
            });
        }
    });
    
    const topComposerDirector = Object.entries(composerDirectorCollabs)
        .filter(([_, data]) => data.count >= 2) // At least 2 films together
        .map(([collab, data]) => [
            collab, 
            data.ratings.reduce((a, b) => a + b, 0) / data.ratings.length,
            data.count
        ])
        .sort((a, b) => b[2] - a[2]) // Sort by count
        .slice(0, 20);
    
    createBubbleChart('composerDirectorChart', topComposerDirector, 'Composer-Director Collaborations', '#e74c3c');
    
    // 7. Studios Average Community Rating
    const studioRatings = {};
    data.films.forEach(film => {
        if (film.studios && film.average_rating) {
            film.studios.forEach(studio => {
                if (!studioRatings[studio]) studioRatings[studio] = [];
                studioRatings[studio].push(parseFloat(film.average_rating));
            });
        }
    });
    
    const studioAvgs = Object.entries(studioRatings)
        .filter(([_, ratings]) => ratings.length >= 3) // At least 3 films
        .map(([studio, ratings]) => [
            studio, 
            ratings.reduce((a, b) => a + b, 0) / ratings.length,
            ratings.length
        ])
        .sort((a, b) => b[1] - a[1]) // Sort by rating
        .slice(0, 15);
    
    const studioColors = [
        '#e74c3c', '#9b59b6', '#3498db', '#1abc9c', '#f1c40f',
        '#e91e63', '#00bcd4', '#ff5722', '#8bc34a', '#ff9800',
        '#673ab7', '#00e676', '#ffc107', '#ff6f00', '#26c6da'
    ];
    
    createColorfulHorizontalBarChart('studioRatingChart',
        studioAvgs.map(s => `${s[0]} (${s[2]})`),
        studioAvgs.map(s => s[1].toFixed(2)),
        'Avg Community Rating',
        studioColors
    );
    
    // 8. Runtime vs Personal Rating (Scatter Plot)
    const runtimeRatingData = data.films
        .filter(f => f.runtime && f.personal_rating)
        .map(f => {
            const match = String(f.runtime).match(/(\d+)/);
            if (match) {
                return {
                    x: parseInt(match[1]),
                    y: parseFloat(f.personal_rating)
                };
            }
            return null;
        })
        .filter(d => d !== null);
    
    console.log('Runtime vs Rating data points:', runtimeRatingData.length);
    if (runtimeRatingData.length > 0) {
        createScatterChart('runtimeRatingChart',
            runtimeRatingData.map(d => d.x),
            runtimeRatingData.map(d => d.y),
            'Runtime (minutes)',
            'Personal Rating'
        );
    }
    
    // 9. Personal vs Average Ratings Area Chart (by year)
    const yearlyRatings = {};
    data.films.forEach(film => {
        if (film.personal_rating && film.average_rating) {
            const year = parseInt(film.year || film.release_date);
            if (!year || isNaN(year)) return;
            
            if (!yearlyRatings[year]) {
                yearlyRatings[year] = { personalRatings: [], avgRatings: [], count: 0 };
            }
            yearlyRatings[year].personalRatings.push(parseFloat(film.personal_rating));
            yearlyRatings[year].avgRatings.push(parseFloat(film.average_rating));
            yearlyRatings[year].count++;
        }
    });
    
    const ratingsComparison = Object.entries(yearlyRatings)
        .map(([year, data]) => ({
            year: parseInt(year),
            personal: data.personalRatings.reduce((a, b) => a + b, 0) / data.personalRatings.length,
            average: data.avgRatings.reduce((a, b) => a + b, 0) / data.avgRatings.length,
            count: data.count
        }))
        .sort((a, b) => a.year - b.year);
    
    createAreaComparisonChart('personalVsAvgChart', ratingsComparison);
}

function displayRecommendations(recommendations) {
    const grid = document.getElementById('recommendationsGrid');
    grid.innerHTML = '';
    
    recommendations.forEach((rec, index) => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        
        const yearVal = rec.year || rec.release_date;
        const year = yearVal ? (typeof yearVal === 'number' ? yearVal : Math.floor(parseFloat(yearVal))) : 'N/A';
        const rating = rec.average_rating ? parseFloat(rec.average_rating).toFixed(1) : 'N/A';
        const genres = rec.genres ? rec.genres.slice(0, 3).join(', ') : 'N/A';
        const directors = rec.directors ? rec.directors.slice(0, 2).join(', ') : 'N/A';
        
        card.innerHTML = `
            <h4>${index + 1}. ${rec.title} (${year})</h4>
            <div class="info">
                <span class="rating">⭐ ${rating}/5</span> • 
                <span>🎭 ${genres}</span>
            </div>
            <div class="info">🎬 Director: ${directors}</div>
            ${rec.reasons ? rec.reasons.slice(0, 2).map(r => 
                `<div class="reason">💡 ${r}</div>`
            ).join('') : ''}
            <a href="${rec.url}" target="_blank">View on Letterboxd →</a>
        `;
        
        grid.appendChild(card);
    });
}

function populateTopLists(stats) {
    // Top Genres
    const genresList = document.getElementById('topGenresList');
    genresList.innerHTML = stats.top_genres.slice(0, 15).map(([name, count]) => `
        <div class="list-item">
            <span class="list-item-name">${name}</span>
            <span class="list-item-count">${count}</span>
        </div>
    `).join('');
    
    // Top Directors
    const directorsList = document.getElementById('topDirectorsList');
    directorsList.innerHTML = stats.top_directors.slice(0, 15).map(([name, count]) => `
        <div class="list-item">
            <span class="list-item-name">${name}</span>
            <span class="list-item-count">${count}</span>
        </div>
    `).join('');
    
    // Top Actors
    const actorsList = document.getElementById('topActorsList');
    const actorCounts = {};
    currentFilms.forEach(film => {
        if (film.actors) {
            film.actors.forEach(actor => {
                actorCounts[actor] = (actorCounts[actor] || 0) + 1;
            });
        }
    });
    const topActors = Object.entries(actorCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15);
    
    actorsList.innerHTML = topActors.map(([name, count]) => `
        <div class="list-item">
            <span class="list-item-name">${name}</span>
            <span class="list-item-count">${count}</span>
        </div>
    `).join('');
    
    // Top Studios
    const studiosList = document.getElementById('topStudiosList');
    const studioCounts = {};
    currentFilms.forEach(film => {
        if (film.studios) {
            film.studios.forEach(studio => {
                studioCounts[studio] = (studioCounts[studio] || 0) + 1;
            });
        }
    });
    const topStudios = Object.entries(studioCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15);
    
    studiosList.innerHTML = topStudios.map(([name, count]) => `
        <div class="list-item">
            <span class="list-item-name">${name}</span>
            <span class="list-item-count">${count}</span>
        </div>
    `).join('');
}

// Chart Creation Functions
function destroyAllCharts() {
    // Destroy tracked instances
    Object.keys(chartInstances).forEach(key => {
        if (chartInstances[key]) {
            try {
                chartInstances[key].destroy();
            } catch (e) {
                console.warn('Error destroying chart:', e);
            }
        }
    });
    chartInstances = {};
    
    // Also destroy any Chart.js instances on all canvas elements and reset them
    document.querySelectorAll('canvas').forEach(canvas => {
        try {
            const existingChart = Chart.getChart(canvas);
            if (existingChart) {
                existingChart.destroy();
            }
        } catch (e) {
            // Chart.getChart might fail, reset canvas manually
        }
        
        // Reset the canvas by replacing it with a clone (removes all Chart.js bindings)
        const parent = canvas.parentNode;
        const newCanvas = canvas.cloneNode(true);
        parent.replaceChild(newCanvas, canvas);
    });
}

function createBarChart(canvasId, labels, data, label) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: '#00e054',
                borderColor: '#00e054',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { 
                    beginAtZero: true,
                    ticks: { color: '#9ab' },
                    grid: { color: '#456' }
                },
                x: {
                    ticks: { color: '#9ab' },
                    grid: { display: false }
                }
            }
        }
    });
}

function createLineChart(canvasId, labels, data, label) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                borderColor: '#00e054',
                backgroundColor: 'rgba(0, 224, 84, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { 
                    beginAtZero: true,
                    ticks: { color: '#9ab' },
                    grid: { color: '#456' }
                },
                x: {
                    ticks: { color: '#9ab' },
                    grid: { display: false }
                }
            }
        }
    });
}

function createColorfulHorizontalBarChart(canvasId, labels, data, label, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(c => c),
                borderWidth: 2
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { 
                    beginAtZero: true,
                    ticks: { color: '#9ab' },
                    grid: { color: '#456' }
                },
                y: {
                    ticks: { color: '#9ab', font: { size: 11 } },
                    grid: { display: false }
                }
            }
        }
    });
}

function createHorizontalBarChart(canvasId, labels, data, label, color) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: color || '#ff8000',
                borderColor: color || '#ff8000',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { 
                    beginAtZero: true,
                    ticks: { color: '#9ab' },
                    grid: { color: '#456' }
                },
                y: {
                    ticks: { color: '#9ab' },
                    grid: { display: false }
                }
            }
        }
    });
}

function createHistogramChart(canvasId, data) {
    // Create bins for runtime distribution
    const bins = [0, 30, 60, 90, 120, 150, 180, 240, 300];
    const counts = new Array(bins.length - 1).fill(0);
    
    data.forEach(runtime => {
        for (let i = 0; i < bins.length - 1; i++) {
            if (runtime >= bins[i] && runtime < bins[i + 1]) {
                counts[i]++;
                break;
            }
        }
    });
    
    const labels = bins.slice(0, -1).map((bin, i) => 
        `${bin}-${bins[i + 1]} min`
    );
    
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const existingChart = Chart.getChart(canvas);
    if (existingChart) existingChart.destroy();
    const ctx = canvas.getContext('2d');
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Films',
                data: counts,
                backgroundColor: '#00e054',
                borderColor: '#00e054',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { 
                    beginAtZero: true,
                    ticks: { color: '#9ab' },
                    grid: { color: '#456' }
                },
                x: {
                    ticks: { color: '#9ab', maxRotation: 45, minRotation: 45 },
                    grid: { display: false }
                }
            }
        }
    });
}

function createScatterChart(canvasId, xData, yData, xLabel, yLabel) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Create data points
    const dataPoints = xData.map((x, i) => ({ x, y: yData[i] }));
    
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Films',
                data: dataPoints,
                backgroundColor: 'rgba(0, 224, 84, 0.6)',
                borderColor: '#00e054',
                borderWidth: 1,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    title: { display: true, text: xLabel, color: '#9ab' },
                    ticks: { color: '#9ab' },
                    grid: { color: '#456' }
                },
                y: {
                    title: { display: true, text: yLabel, color: '#9ab' },
                    ticks: { color: '#9ab' },
                    grid: { color: '#456' }
                }
            }
        }
    });
}

function createBoxPlot(canvasId, labels, dataDict) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Since Chart.js doesn't have native box plot, we'll create a modified bar chart
    // showing min, Q1, median, Q3, max as stacked bars
    const datasets = [];
    const colors = ['#ff6b6b', '#4ecdc4', '#00e054', '#95e1d3', '#f38181'];
    
    // Calculate statistics for each category
    const stats = labels.map(label => {
        const values = dataDict[label].sort((a, b) => a - b);
        const n = values.length;
        return {
            min: values[0],
            q1: values[Math.floor(n * 0.25)],
            median: values[Math.floor(n * 0.5)],
            q3: values[Math.floor(n * 0.75)],
            max: values[n - 1]
        };
    });
    
    // Create data showing median values with error bars simulated
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Median Rating',
                data: stats.map(s => s.median),
                backgroundColor: '#00e054',
                borderColor: '#00e054',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true, labels: { color: '#9ab' } },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const stat = stats[context.dataIndex];
                            return [
                                `Min: ${stat.min.toFixed(1)}`,
                                `Q1: ${stat.q1.toFixed(1)}`,
                                `Median: ${stat.median.toFixed(1)}`,
                                `Q3: ${stat.q3.toFixed(1)}`,
                                `Max: ${stat.max.toFixed(1)}`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    ticks: { color: '#9ab' },
                    grid: { color: '#456' }
                },
                x: {
                    ticks: { color: '#9ab' },
                    grid: { display: false }
                }
            }
        }
    });
}

function createPieChart(canvasId, labels, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Generate colors for pie slices
    const colors = [
        '#00e054', '#ff8000', '#40bcf4', '#ff69b4', '#9b59b6',
        '#e74c3c', '#f39c12', '#3498db', '#1abc9c', '#95a5a6'
    ];
    
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, data.length),
                borderColor: '#14181c',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#9ab',
                        font: { size: 11 },
                        padding: 10
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.raw / total) * 100).toFixed(1);
                            return `${context.label}: ${context.raw} films (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function createAreaComparisonChart(canvasId, ratingsData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Create labels (years)
    const labels = ratingsData.map(d => d.year);
    
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Personal Rating',
                    data: ratingsData.map(d => d.personal),
                    backgroundColor: 'rgba(0, 224, 84, 0.5)',
                    borderColor: '#00e054',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#00e054',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                },
                {
                    label: 'Community Average',
                    data: ratingsData.map(d => d.average),
                    backgroundColor: 'rgba(255, 128, 0, 0.5)',
                    borderColor: '#ff8000',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#ff8000',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Average Ratings by Year: Personal vs Community',
                    color: '#9ab',
                    font: { size: 14 }
                },
                legend: {
                    display: true,
                    labels: { color: '#9ab' }
                },
                tooltip: {
                    callbacks: {
                        title: (context) => {
                            const index = context[0].dataIndex;
                            return `Year: ${ratingsData[index].year}`;
                        },
                        afterTitle: (context) => {
                            const index = context[0].dataIndex;
                            return `${ratingsData[index].count} film${ratingsData[index].count !== 1 ? 's' : ''} rated`;
                        },
                        label: (context) => {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)}/5`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: { 
                        display: true, 
                        text: 'Year', 
                        color: '#9ab' 
                    },
                    ticks: { 
                        color: '#9ab',
                        maxRotation: 45,
                        minRotation: 0
                    },
                    grid: { display: false }
                },
                y: {
                    beginAtZero: true,
                    max: 5,
                    title: { 
                        display: true, 
                        text: 'Average Rating', 
                        color: '#9ab' 
                    },
                    ticks: { 
                        color: '#9ab',
                        stepSize: 0.5
                    },
                    grid: { color: '#456' }
                }
            }
        }
    });
}

function createCandlestickChart(canvasId, labels, dataDict) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Calculate OHLC-style data (Open, High, Low, Close → Min, Max, Q1, Q3)
    const stats = labels.map(label => {
        const values = dataDict[label].sort((a, b) => a - b);
        const n = values.length;
        return {
            min: values[0],
            q1: values[Math.floor(n * 0.25)],
            median: values[Math.floor(n * 0.5)],
            q3: values[Math.floor(n * 0.75)],
            max: values[n - 1],
            count: n
        };
    });
    
    // Create floating bars to simulate candlesticks
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.map(l => `${l}s`),
            datasets: [
                {
                    label: 'Range (Min-Max)',
                    data: stats.map(s => [s.min, s.max]),
                    backgroundColor: 'rgba(100, 100, 100, 0.3)',
                    borderColor: '#666',
                    borderWidth: 1,
                    barPercentage: 0.3
                },
                {
                    label: 'IQR (Q1-Q3)',
                    data: stats.map(s => [s.q1, s.q3]),
                    backgroundColor: 'rgba(0, 224, 84, 0.7)',
                    borderColor: '#00e054',
                    borderWidth: 2,
                    barPercentage: 0.6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { 
                    display: true,
                    labels: { color: '#9ab' }
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const stat = stats[context.dataIndex];
                            return [
                                `Films: ${stat.count}`,
                                `Min: ${stat.min.toFixed(1)}`,
                                `Q1: ${stat.q1.toFixed(1)}`,
                                `Median: ${stat.median.toFixed(1)}`,
                                `Q3: ${stat.q3.toFixed(1)}`,
                                `Max: ${stat.max.toFixed(1)}`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    title: { display: true, text: 'Personal Rating', color: '#9ab' },
                    ticks: { color: '#9ab' },
                    grid: { color: '#456' }
                },
                x: {
                    title: { display: true, text: 'Decade', color: '#9ab' },
                    ticks: { color: '#9ab' },
                    grid: { display: false }
                }
            }
        }
    });
}

function createTreemapChart(canvasId, data, title, baseColor) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Prepare treemap data with size based on count and color based on rating
    const treemapData = data.map(item => ({
        label: item.label,
        value: item.count,
        rating: item.rating,
        count: item.count
    }));
    
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'treemap',
        data: {
            datasets: [{
                label: title,
                tree: treemapData,
                key: 'value',
                groups: ['label'],
                spacing: 1,
                borderWidth: 2,
                borderColor: '#14181c',
                backgroundColor: (ctx) => {
                    if (!ctx.raw) return baseColor;
                    const rating = ctx.raw._data.rating;
                    // Color gradient based on rating (darker = lower, brighter = higher)
                    const alpha = 0.4 + (rating / 5) * 0.6;
                    return baseColor + Math.floor(alpha * 255).toString(16).padStart(2, '0');
                },
                labels: {
                    display: true,
                    formatter: (ctx) => {
                        if (!ctx.raw) return '';
                        const words = ctx.raw._data.label.split(' ');
                        // Split long labels into multiple lines
                        if (words.length > 3) {
                            const mid = Math.ceil(words.length / 2);
                            return [words.slice(0, mid).join(' '), words.slice(mid).join(' ')];
                        }
                        return ctx.raw._data.label;
                    },
                    color: '#fff',
                    font: {
                        size: 11,
                        weight: 'bold'
                    },
                    padding: 3
                }
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: title,
                    color: '#9ab',
                    font: { size: 14 }
                },
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: (context) => {
                            return context[0].raw._data.label;
                        },
                        label: (context) => {
                            const data = context.raw._data;
                            return [
                                `Films together: ${data.count}`,
                                `Avg Rating: ${data.rating.toFixed(2)}/5`
                            ];
                        }
                    }
                }
            }
        }
    });
}

function createBubbleChart(canvasId, collaborations, title, color) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Transform collaboration data into bubble chart format
    const bubbleData = collaborations.map(([collab, rating, count]) => ({
        x: rating,
        y: count,
        r: Math.sqrt(count) * 5,
        label: collab,
        rating: rating,
        count: count
    }));
    
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bubble',
        data: {
            datasets: [{
                label: title,
                data: bubbleData,
                backgroundColor: color + 'cc',
                borderColor: color,
                borderWidth: 3,
                hoverBackgroundColor: color + 'ff',
                hoverBorderWidth: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: title,
                    color: '#9ab',
                    font: { size: 14 }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: (context) => {
                            return context[0].raw.label;
                        },
                        label: (context) => {
                            const data = context.raw;
                            return [
                                `Films together: ${data.count}`,
                                `Avg Rating: ${data.rating.toFixed(2)}/5`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Average Community Rating',
                        color: '#9ab'
                    },
                    min: 2,
                    max: 5,
                    ticks: {
                        color: '#9ab',
                        stepSize: 0.5
                    },
                    grid: {
                        color: '#456'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Number of Films Together',
                        color: '#9ab'
                    },
                    beginAtZero: true,
                    ticks: {
                        color: '#9ab',
                        stepSize: 1
                    },
                    grid: {
                        color: '#456'
                    }
                }
            }
        }
    });
}

function createGeoChart(canvasId, countryData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Country name mapping for common variations
    const countryNameMap = {
        'usa': 'United States of America',
        'united states': 'United States of America',
        'us': 'United States of America',
        'uk': 'United Kingdom',
        'britain': 'United Kingdom',
        'great britain': 'United Kingdom',
        'england': 'United Kingdom',
        'south korea': 'South Korea',
        'korea': 'South Korea',
        'russia': 'Russia',
        'soviet union': 'Russia',
        'ussr': 'Russia',
        'czech republic': 'Czechia',
        'netherlands': 'Netherlands',
        'holland': 'Netherlands',
        'germany': 'Germany',
        'west germany': 'Germany',
        'east germany': 'Germany',
        'france': 'France',
        'spain': 'Spain',
        'italy': 'Italy',
        'japan': 'Japan',
        'china': 'China',
        'hong kong': 'China',
        'india': 'India',
        'canada': 'Canada',
        'australia': 'Australia',
        'mexico': 'Mexico',
        'brazil': 'Brazil',
        'argentina': 'Argentina',
        'sweden': 'Sweden',
        'norway': 'Norway',
        'denmark': 'Denmark',
        'poland': 'Poland',
        'ireland': 'Ireland',
        'new zealand': 'New Zealand',
        'belgium': 'Belgium',
        'switzerland': 'Switzerland',
        'austria': 'Austria',
        'portugal': 'Portugal',
        'greece': 'Greece',
        'turkey': 'Turkey',
        'iran': 'Iran',
        'egypt': 'Egypt',
        'south africa': 'South Africa',
        'taiwan': 'Taiwan'
    };
    
    // Load world map data
    fetch('https://unpkg.com/world-atlas@2/countries-50m.json')
        .then(response => response.json())
        .then(worldData => {
            const countries = ChartGeo.topojson.feature(worldData, worldData.objects.countries).features;
            
            // Create a map of standardized country names to film counts
            const countryMap = {};
            countryData.forEach(([name, count]) => {
                const normalizedName = name.toLowerCase().trim();
                const standardName = countryNameMap[normalizedName] || name;
                if (countryMap[standardName]) {
                    countryMap[standardName] += count;
                } else {
                    countryMap[standardName] = count;
                }
            });
            
            console.log('Country mapping:', countryMap);
            
            // Map the data to country features
            const chartData = countries.map(country => {
                const countryName = country.properties.name;
                const value = countryMap[countryName] || 0;
                return {
                    feature: country,
                    value: value
                };
            });
            
            chartInstances[canvasId] = new Chart(ctx, {
                type: 'choropleth',
                data: {
                    labels: countries.map(c => c.properties.name),
                    datasets: [{
                        label: 'Films Watched',
                        data: chartData,
                        backgroundColor: (context) => {
                            if (!context.raw || !context.raw.value) return 'rgba(100, 100, 100, 0.2)';
                            const value = context.raw.value;
                            const maxValue = Math.max(...countryData.map(c => c[1]));
                            const intensity = value / maxValue;
                            // Vibrant green to cyan gradient
                            const r = Math.floor(0 + (0 * intensity));
                            const g = Math.floor(188 + (224 - 188) * intensity);
                            const b = Math.floor(212 + (84 - 212) * intensity);
                            return `rgba(${r}, ${g}, ${b}, ${0.5 + intensity * 0.5})`;
                        },
                        borderColor: '#456',
                        borderWidth: 0.5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        title: {
                            display: true,
                            text: ['Films by Country of Origin', '(Co-productions counted for each country)'],
                            color: '#9ab',
                            font: { size: 14 }
                        },
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const value = context.raw.value;
                                    if (value === 0) return 'No films watched';
                                    return `${value} film${value !== 1 ? 's' : ''}`;
                                }
                            }
                        }
                    },
                    scales: {
                        projection: {
                            axis: 'x',
                            projection: 'equalEarth'
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading map data:', error);
            // Fallback to horizontal bar chart
            const topCountries = countryData.slice(0, 20);
            createHorizontalBarChart(canvasId,
                topCountries.map(c => c[0]),
                topCountries.map(c => c[1]),
                'Films Watched',
                '#00e054'
            );
        });
}

// Utility Functions
function showScreen(screen) {
    homeScreen.classList.remove('active');
    loadingScreen.classList.remove('active');
    dashboardScreen.classList.remove('active');
    
    if (screen === 'home') homeScreen.classList.add('active');
    else if (screen === 'loading') loadingScreen.classList.add('active');
    else if (screen === 'dashboard') dashboardScreen.classList.add('active');
}

function updateLoading(title, message, progress) {
    loadingTitle.textContent = title;
    loadingMessage.textContent = message;
    progressFill.style.width = `${progress}%`;
    progressText.textContent = `${progress}%`;
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    errorMessage.classList.add('hidden');
}

function goHome() {
    usernameInput.value = '';
    currentUsername = '';
    currentFilms = [];
    currentRecommendations = [];
    destroyAllCharts();
    showScreen('home');
}

// Initialize
console.log('Film Fanatic initialized');
