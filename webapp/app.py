#!/usr/bin/env python3
"""
Earthquake Aftershock Analysis Web App
Author: Edward Xiong
Diamond Bar High School, 11th Grade
NHSJS Research Project: Testing Omori's Law

Interactive visualization of earthquake aftershock sequences
and Omori's Law fits.
"""

from flask import Flask, render_template, jsonify
import json
import os
import numpy as np

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
ANALYSIS_DIR = os.path.join(os.path.dirname(__file__), '..', 'analysis')


def load_data():
    """Load earthquake data and analysis results."""
    eq_data = None
    analysis_results = []

    eq_path = os.path.join(DATA_DIR, 'earthquake_data.json')
    if os.path.exists(eq_path):
        with open(eq_path) as f:
            eq_data = json.load(f)

    analysis_path = os.path.join(ANALYSIS_DIR, 'analysis_results.json')
    if os.path.exists(analysis_path):
        with open(analysis_path) as f:
            analysis_results = json.load(f)

    return eq_data, analysis_results


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/sequences')
def get_sequences():
    """Get list of analyzed earthquake sequences."""
    _, analysis_results = load_data()

    sequences = []
    for r in analysis_results:
        if r.get('fit_success'):
            sequences.append({
                'id': r['mainshock_id'],
                'magnitude': r['mainshock_magnitude'],
                'place': r['mainshock_place'],
                'time': r['mainshock_time'],
                'aftershocks': r['total_aftershocks'],
                'p': r.get('p'),
                'r_squared': r.get('r_squared')
            })

    return jsonify(sequences)


@app.route('/api/sequence/<seq_id>')
def get_sequence(seq_id):
    """Get detailed data for a specific sequence."""
    eq_data, analysis_results = load_data()

    # Find in analysis results
    analysis = None
    for r in analysis_results:
        if r['mainshock_id'] == seq_id:
            analysis = r
            break

    if not analysis:
        return jsonify({'error': 'Sequence not found'}), 404

    return jsonify(analysis)


@app.route('/api/summary')
def get_summary():
    """Get summary statistics."""
    _, analysis_results = load_data()

    good_fits = [r for r in analysis_results if r.get('fit_success') and r.get('r_squared', 0) > 0.5]

    if not good_fits:
        return jsonify({'error': 'No analysis results available'}), 404

    p_values = [r['p'] for r in good_fits]
    r2_values = [r['r_squared'] for r in good_fits]

    return jsonify({
        'total_sequences': len(analysis_results),
        'good_fits': len(good_fits),
        'mean_p': np.mean(p_values),
        'std_p': np.std(p_values),
        'min_p': min(p_values),
        'max_p': max(p_values),
        'mean_r_squared': np.mean(r2_values),
        'results': analysis_results
    })


INDEX_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Omori's Law Analysis</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #eee;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header {
            text-align: center;
            padding: 40px 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            margin-bottom: 30px;
        }
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #ff6b6b, #ffd93d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .subtitle { color: #aaa; font-size: 1.1rem; }
        .author { margin-top: 15px; color: #888; }
        .grid {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255,255,255,0.08);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h2 { color: #ff6b6b; margin-bottom: 15px; font-size: 1.3rem; }
        select {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: none;
            background: rgba(255,255,255,0.1);
            color: #fff;
            font-size: 1rem;
            margin-bottom: 15px;
            cursor: pointer;
        }
        select option { background: #1a1a2e; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        .stat-box {
            background: rgba(255,107,107,0.15);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-value { font-size: 1.8rem; font-weight: bold; color: #ff6b6b; }
        .stat-label { color: #888; font-size: 0.9rem; margin-top: 5px; }
        .chart-container { height: 500px; }
        .full-width { grid-column: 1 / -1; }
        .formula {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            margin: 15px 0;
            font-size: 1.2rem;
            text-align: center;
        }
        .methodology p { line-height: 1.8; color: #ccc; margin-bottom: 15px; }
        footer { text-align: center; padding: 30px; color: #666; margin-top: 30px; }
        @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Mathematics of Earthquake Aftershocks</h1>
            <p class="subtitle">Testing Omori's Law (1894) with Modern Seismic Data</p>
            <p class="author">Edward Xiong | Diamond Bar High School | NHSJS Research Project</p>
        </header>

        <div class="grid">
            <div class="card">
                <h2>Select Earthquake</h2>
                <select id="seqSelect" onchange="loadSequence()">
                    <option value="">Loading sequences...</option>
                </select>
                <div id="seqStats" class="stats-grid" style="margin-top: 20px;"></div>
            </div>
            <div class="card">
                <h2>Aftershock Rate Decay</h2>
                <div id="decayChart" class="chart-container"></div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>Research Summary</h2>
                <div id="summaryStats" class="stats-grid"></div>
            </div>
            <div class="card">
                <h2>p-Value Distribution</h2>
                <div id="pDistChart" class="chart-container" style="height: 350px;"></div>
            </div>
        </div>

        <div class="card methodology">
            <h2>Omori's Law</h2>
            <div class="formula">n(t) = K / (c + t)<sup>p</sup></div>
            <p>
                <strong>Omori's Law</strong>, discovered by Japanese seismologist Fusakichi Omori in 1894,
                describes how the rate of aftershocks decays following a major earthquake. The modified
                Omori-Utsu formula includes three parameters:
            </p>
            <p>
                <strong>K</strong> - Productivity parameter (controls overall aftershock count)<br>
                <strong>c</strong> - Characteristic time delay (typically 0.01-0.5 days)<br>
                <strong>p</strong> - Decay exponent (typically 0.9-1.5, with p=1 being classical Omori)
            </p>
            <p>
                A higher p value means faster decay of aftershock activity. This research tests whether
                Omori's 130-year-old law still accurately describes modern earthquake sequences.
            </p>
        </div>

        <footer>
            <p>Data sourced from USGS Earthquake Catalog API | Analysis powered by Python + SciPy</p>
            <p>&copy; 2026 Edward Xiong | Diamond Bar High School</p>
        </footer>
    </div>

    <script>
        let sequencesData = [];
        let summaryData = null;

        async function init() {
            const seqResponse = await fetch('/api/sequences');
            sequencesData = await seqResponse.json();

            const seqSelect = document.getElementById('seqSelect');
            seqSelect.innerHTML = '<option value="">Select an earthquake...</option>';
            sequencesData.forEach(seq => {
                const option = document.createElement('option');
                option.value = seq.id;
                option.textContent = `M${seq.magnitude.toFixed(1)} - ${seq.place.substring(0, 40)}`;
                seqSelect.appendChild(option);
            });

            const summaryResponse = await fetch('/api/summary');
            summaryData = await summaryResponse.json();
            updateSummary();
            drawPDistribution();
        }

        async function loadSequence() {
            const seqId = document.getElementById('seqSelect').value;
            if (!seqId) return;

            const response = await fetch(`/api/sequence/${seqId}`);
            const data = await response.json();

            if (data.error) return;

            updateSeqStats(data);
            drawDecayChart(data);
        }

        function updateSeqStats(data) {
            const container = document.getElementById('seqStats');
            container.innerHTML = `
                <div class="stat-box">
                    <div class="stat-value">M${data.mainshock_magnitude.toFixed(1)}</div>
                    <div class="stat-label">Magnitude</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${data.total_aftershocks}</div>
                    <div class="stat-label">Aftershocks</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${data.p?.toFixed(2) || 'N/A'}</div>
                    <div class="stat-label">p (decay)</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${data.r_squared?.toFixed(3) || 'N/A'}</div>
                    <div class="stat-label">R²</div>
                </div>
            `;
        }

        function drawDecayChart(data) {
            if (!data.t_data || !data.rate_data) return;

            const t_data = data.t_data;
            const rate_data = data.rate_data;

            const traces = [{
                x: t_data,
                y: rate_data,
                mode: 'markers',
                name: 'Observed',
                marker: { size: 10, color: '#ff6b6b' }
            }];

            if (data.K && data.c && data.p) {
                const t_smooth = [];
                const rate_fit = [];
                const tMin = Math.min(...t_data);
                const tMax = Math.max(...t_data);
                for (let i = 0; i <= 100; i++) {
                    const t = tMin * Math.pow(tMax/tMin, i/100);
                    t_smooth.push(t);
                    rate_fit.push(data.K / Math.pow(data.c + t, data.p));
                }
                traces.push({
                    x: t_smooth,
                    y: rate_fit,
                    mode: 'lines',
                    name: `Omori fit (p=${data.p.toFixed(2)})`,
                    line: { width: 3, color: '#ffd93d' }
                });
            }

            const layout = {
                title: `${data.mainshock_place}`,
                xaxis: { title: 'Time after mainshock (hours)', type: 'log', color: '#888' },
                yaxis: { title: 'Aftershock rate (events/hour)', type: 'log', color: '#888' },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0.2)',
                font: { color: '#eee' },
                legend: { x: 1, y: 1, xanchor: 'right' }
            };

            Plotly.newPlot('decayChart', traces, layout, { responsive: true });
        }

        function updateSummary() {
            if (!summaryData) return;
            const container = document.getElementById('summaryStats');
            container.innerHTML = `
                <div class="stat-box">
                    <div class="stat-value">${summaryData.total_sequences}</div>
                    <div class="stat-label">Sequences Analyzed</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${summaryData.good_fits}</div>
                    <div class="stat-label">Good Fits</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${summaryData.mean_p?.toFixed(2) || 'N/A'}</div>
                    <div class="stat-label">Mean p</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${summaryData.mean_r_squared?.toFixed(3) || 'N/A'}</div>
                    <div class="stat-label">Mean R²</div>
                </div>
            `;
        }

        function drawPDistribution() {
            if (!summaryData || !summaryData.results) return;

            const p_values = summaryData.results
                .filter(r => r.fit_success && r.r_squared > 0.5)
                .map(r => r.p);

            const trace = {
                x: p_values,
                type: 'histogram',
                marker: { color: '#ff6b6b' },
                nbinsx: 15
            };

            const layout = {
                title: 'Distribution of Decay Exponent (p)',
                xaxis: { title: 'p value', color: '#888' },
                yaxis: { title: 'Count', color: '#888' },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0.2)',
                font: { color: '#eee' },
                shapes: [{
                    type: 'line',
                    x0: 1, x1: 1, y0: 0, y1: 1, yref: 'paper',
                    line: { color: '#ffd93d', dash: 'dash', width: 2 }
                }]
            };

            Plotly.newPlot('pDistChart', [trace], layout, { responsive: true });
        }

        init();
    </script>
</body>
</html>
'''

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
os.makedirs(TEMPLATE_DIR, exist_ok=True)
with open(os.path.join(TEMPLATE_DIR, 'index.html'), 'w') as f:
    f.write(INDEX_HTML)

if __name__ == '__main__':
    print("=" * 60)
    print("EARTHQUAKE AFTERSHOCK VISUALIZATION")
    print("=" * 60)
    print("\nStarting web server...")
    print("Open http://localhost:5001 in your browser")
    app.run(debug=True, port=5001)
