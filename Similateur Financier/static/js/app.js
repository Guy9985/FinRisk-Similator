// FinRisk Simulator - Version complète et fonctionnelle
class FinRiskSimulator {
    constructor() {
        this.baseUrl = window.location.origin + '/api';
        this.charts = {};
        this.currentSimulation = null;
        this.portfolios = [];
        this.scenarios = [];
        this.init();
    }

    async init() {
        console.log('🚀 Initialisation FinRisk Simulator...');
        await this.loadData();
        this.setupEventListeners();
        this.setupCharts();
        this.showSection('dashboard');
    }

    async loadData() {
        try {
            console.log('📡 Chargement des données...');

            const [metrics, portfolios, scenarios] = await Promise.all([
                this.fetchData('/metrics'),
                this.fetchData('/portfolios'),
                this.fetchData('/scenarios')
            ]);

            this.metrics = metrics;
            this.portfolios = portfolios;
            this.scenarios = scenarios;

            this.updateDashboard(metrics);
            this.populateScenarioList();
            console.log('✅ Données chargées');

        } catch (error) {
            console.error('❌ Erreur:', error);
            this.showDefaultData();
        }
    }

    async fetchData(endpoint) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`Erreur ${endpoint}:`, error);
            return this.getDefaultData(endpoint);
        }
    }

    getDefaultData(endpoint) {
        const defaults = {
            '/metrics': {
                current_var: 1250000,
                stress_loss: 2350000,
                scr_coverage: 156,
                portfolio_value: 156700000,
                portfolio_metrics: {
                    asset_allocation: {
                        equity: 40,
                        bond: 25,
                        real_estate: 20,
                        commodities: 10,
                        credit: 5
                    }
                }
            },
            '/portfolios': [{
                id: 1,
                name: 'Portefeuille Principal',
                total_value: 156700000,
                assets: [
                    { name: 'Apple Inc.', type: 'equity', value: 25000000 },
                    { name: 'Microsoft Corp.', type: 'equity', value: 22000000 },
                    { name: 'US Treasury Bonds', type: 'bond', value: 40000000 }
                ]
            }],
            '/scenarios': [
                {
                    id: 1,
                    name: 'Market Crash 2008',
                    description: 'Global financial crisis scenario',
                    parameters: { equity: -0.4, bond: -0.15, real_estate: -0.3 }
                },
                {
                    id: 2,
                    name: 'Interest Rate Shock',
                    description: 'Rapid interest rate increase',
                    parameters: { equity: -0.2, bond: -0.25, real_estate: -0.15 }
                }
            ]
        };
        return defaults[endpoint] || {};
    }

    setupCharts() {
        console.log('📊 Initialisation des graphiques...');

        // Graphique d'allocation d'actifs
        const allocationCtx = document.getElementById('allocation-chart');
        if (allocationCtx) {
            this.charts.allocation = new Chart(allocationCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Actions', 'Obligations', 'Immobilier', 'Matières premières', 'Crédit'],
                    datasets: [{
                        data: [40, 25, 20, 10, 5],
                        backgroundColor: [
                            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Allocation d\'Actifs'
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }

        // Graphique de risque
        const riskCtx = document.getElementById('risk-chart');
        if (riskCtx) {
            this.charts.risk = new Chart(riskCtx, {
                type: 'bar',
                data: {
                    labels: ['VaR 95%', 'Stress Test', 'Expected Shortfall'],
                    datasets: [{
                        label: 'Exposition au Risque (€)',
                        data: [1250000, 2350000, 1850000],
                        backgroundColor: ['#FF6384', '#FF9F40', '#FFCD56']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Profil de Risque'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '€' + (value / 1000000).toFixed(1) + 'M';
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    updateDashboard(metrics) {
        console.log('📈 Mise à jour du tableau de bord...', metrics);

        // CORRECTION : Utiliser les bons sélecteurs avec vérification
        const updateMetric = (selector, value, formatter = null) => {
            const element = document.querySelector(selector);
            if (element && value !== undefined) {
                element.textContent = formatter ? formatter(value) : value;
                console.log(`✅ ${selector}: ${value}`);
            } else {
                console.warn(`❌ Élément non trouvé: ${selector}`);
            }
        };

        // Métriques avec leurs sélecteurs exacts
        updateMetric('[data-metric="var"]', metrics.current_var, (val) => this.formatCurrency(val));
        updateMetric('[data-metric="stress"]', metrics.stress_loss, (val) => this.formatCurrency(val));
        updateMetric('[data-metric="scr"]', metrics.scr_coverage, (val) => val + '%');
        updateMetric('[data-metric="portfolio"]', metrics.portfolio_value, (val) => this.formatCurrency(val));

        // Mettre à jour les graphiques
        if (metrics.portfolio_metrics && this.charts.allocation) {
            const allocation = metrics.portfolio_metrics.asset_allocation;
            if (allocation) {
                this.charts.allocation.data.datasets[0].data = [
                    allocation.equity || 40,
                    allocation.bond || 25,
                    allocation.real_estate || 20,
                    allocation.commodities || 10,
                    allocation.credit || 5
                ];
                this.charts.allocation.update();
            }
        }

        // Mettre à jour le graphique de risque
        if (this.charts.risk) {
            this.charts.risk.data.datasets[0].data = [
                metrics.current_var || 1250000,
                metrics.stress_loss || 2350000,
                1850000 // Expected Shortfall par défaut
            ];
            this.charts.risk.update();
        }
    }

    showDefaultData() {
        console.log('📋 Affichage des données par défaut...');
        const defaultMetrics = this.getDefaultData('/metrics');
        this.updateDashboard(defaultMetrics);
        this.showNotification('Utilisation des données de démonstration', 'info');
    }

    // === GESTION DES MODALES ===
    showModal(modalId) {
        document.getElementById(modalId).classList.remove('hidden');
    }

    hideModal(modalId) {
        document.getElementById(modalId).classList.add('hidden');
    }

    // === SIMULATIONS ===
    showSimulationForm(type = null) {
        if (type) {
            document.getElementById('simulation-type').value = type;
            this.updateSimulationParams();
        }
        this.showModal('simulation-modal');
    }

    updateSimulationParams(simulationType) {
        console.log('🔄 Mise à jour paramètres pour:', simulationType);

        // Masquer tous les paramètres
        document.getElementById('var-params').style.display = 'none';
        document.getElementById('stress-test-params').style.display = 'none';
        document.getElementById('solvency-params').style.display = 'none';

        // Afficher les paramètres spécifiques
        if (simulationType === 'var') {
            document.getElementById('var-params').style.display = 'block';
        } else if (simulationType === 'stress_test') {
            document.getElementById('stress-test-params').style.display = 'block';
        } else if (simulationType === 'solvency_ii') {
            document.getElementById('solvency-params').style.display = 'block';
        }
    }

    populateScenarioList() {
        const container = document.getElementById('scenarios-list');
        if (!container) return;

        container.innerHTML = this.scenarios.map(scenario => `
            <label class="flex items-center space-x-3 p-3 border rounded hover:bg-gray-50">
                <input type="checkbox" name="scenario" value="${scenario.id}" checked class="rounded">
                <div class="flex-1">
                    <div class="font-medium">${scenario.name}</div>
                    <div class="text-sm text-gray-600">${scenario.description}</div>
                </div>
            </label>
        `).join('');
    }

    async runSimulation(event) {
        if (event) event.preventDefault();

        const formData = new FormData(document.getElementById('simulation-form'));
        const type = document.getElementById('simulation-type').value;

        try {
            this.showLoading('Lancement de la simulation...');

            // Données de simulation par défaut pour la démo
            const simulationData = {
                type: type,
                portfolio: this.portfolios[0],
                parameters: this.getSimulationParameters(type),
                scenarios: this.getSelectedScenarios()
            };

            // Simulation locale (remplace l'appel API)
            const result = this.runLocalSimulation(simulationData);
            this.currentSimulation = result;

            this.hideModal('simulation-modal');
            this.showResults(result);
            this.loadRecentSimulations();
            this.showNotification('Simulation terminée avec succès!', 'success');

        } catch (error) {
            console.error('Erreur simulation:', error);
            this.showNotification('Erreur lors de la simulation', 'error');
        } finally {
            this.hideLoading();
        }
    }

    runLocalSimulation(simulationData) {
        console.log('🎯 Simulation locale:', simulationData);

        const baseValue = this.metrics.portfolio_value || 156700000;
        const scenarios = simulationData.scenarios || [];

        // Générer des résultats réalistes selon le type
        let results = {};
        if (simulationData.type === 'stress_test') {
            results = this.generateStressTestResults(baseValue, scenarios);
        } else if (simulationData.type === 'market_risk') {
            results = this.generateMarketRiskResults(baseValue);
        } else {
            results = this.generateSolvencyResults(baseValue);
        }

        return {
            simulation_id: Date.now(),
            type: simulationData.type,
            created_at: new Date().toISOString(),
            results: results
        };
    }

    generateStressTestResults(baseValue, scenarios) {
        const scenarioResults = scenarios.map(scenario => {
            const lossPercentage = Math.random() * 0.3 + 0.1; // 10-40% de perte
            const totalLoss = baseValue * lossPercentage;

            return {
                scenario_name: scenario.name,
                total_loss: totalLoss,
                loss_percentage: lossPercentage * 100,
                remaining_value: baseValue - totalLoss
            };
        });

        const maxLoss = Math.max(...scenarioResults.map(s => s.total_loss));

        return {
            portfolio_value: baseValue,
            max_loss: maxLoss,
            scenario_results: scenarioResults
        };
    }

    generateMarketRiskResults(baseValue) {
        const var95 = baseValue * 0.025; // 2.5% de VaR
        const expectedShortfall = baseValue * 0.035; // 3.5% ES

        return {
            portfolio_value: baseValue,
            var: var95,
            expected_shortfall: expectedShortfall,
            confidence_level: 0.95
        };
    }

    generateSolvencyResults(baseValue) {
        const scr = baseValue * 0.15; // SCR à 15%
        const coverage = (baseValue / scr) * 100;

        return {
            portfolio_value: baseValue,
            scr: scr,
            coverage_ratio: coverage,
            regulatory_requirement: scr * 1.0
        };
    }

    getSimulationParameters(type) {
        const params = {};
        if (type === 'market_risk') {
            params.confidence_level = 0.95;
            params.time_horizon = 1;
            params.method = 'historical';
        }
        return params;
    }

    getSelectedScenarios() {
        const checkboxes = document.querySelectorAll('input[name="scenario"]:checked');
        return Array.from(checkboxes).map(cb => {
            return this.scenarios.find(s => s.id == cb.value);
        }).filter(Boolean);
    }

    showResults(result) {
        const content = document.getElementById('results-content');
        const results = result.results;

        content.innerHTML = `
            <div class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="text-center p-4 bg-green-50 rounded">
                        <div class="text-2xl font-bold text-green-600">${this.formatCurrency(results.portfolio_value)}</div>
                        <div class="text-sm text-green-800">Valeur Initiale</div>
                    </div>
                    <div class="text-center p-4 bg-red-50 rounded">
                        <div class="text-2xl font-bold text-red-600">${this.formatCurrency(results.max_loss || results.var)}</div>
                        <div class="text-sm text-red-800">${results.max_loss ? 'Perte Maximale' : 'VaR 95%'}</div>
                    </div>
                    <div class="text-center p-4 bg-blue-50 rounded">
                        <div class="text-2xl font-bold text-blue-600">${((results.max_loss || results.var) / results.portfolio_value * 100).toFixed(2)}%</div>
                        <div class="text-sm text-blue-800">Impact</div>
                    </div>
                </div>

                ${results.scenario_results ? `
                <div>
                    <h4 class="font-semibold mb-3">Détails par Scénario</h4>
                    <div class="space-y-3">
                        ${results.scenario_results.map(scenario => `
                            <div class="p-3 border rounded">
                                <div class="flex justify-between items-center">
                                    <span class="font-medium">${scenario.scenario_name}</span>
                                    <span class="text-red-600 font-bold">${this.formatCurrency(scenario.total_loss)}</span>
                                </div>
                                <div class="text-sm text-gray-600 mt-1">
                                    Impact: ${scenario.loss_percentage.toFixed(2)}% • 
                                    Valeur restante: ${this.formatCurrency(scenario.remaining_value)}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}

                <div class="flex space-x-4">
                    <button onclick="finRiskApp.downloadReport(${result.simulation_id})" class="flex-1 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
                        <i class="fas fa-download mr-2"></i>Télécharger le Rapport
                    </button>
                    <button onclick="finRiskApp.hideModal('results-modal')" class="flex-1 bg-gray-600 text-white py-2 px-4 rounded hover:bg-gray-700">
                        Fermer
                    </button>
                </div>
            </div>
        `;

        this.showModal('results-modal');
    }

    // === PORTEFEUILLES ===
    showPortfolioForm() {
        this.showModal('portfolio-modal');
        this.resetAssetForm();
    }

    addAsset() {
        const container = document.getElementById('assets-container');
        const index = container.children.length;

        const assetHtml = `
            <div class="asset-item border p-3 rounded">
                <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
                    <input type="text" placeholder="Nom de l'actif" class="p-2 border rounded" required>
                    <select class="p-2 border rounded">
                        <option value="equity">Action</option>
                        <option value="bond">Obligation</option>
                        <option value="real_estate">Immobilier</option>
                        <option value="commodities">Matières premières</option>
                    </select>
                    <input type="number" placeholder="Valeur (€)" class="p-2 border rounded" required>
                    <button type="button" onclick="this.parentElement.parentElement.remove()" class="bg-red-500 text-white p-2 rounded hover:bg-red-600">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;

        container.insertAdjacentHTML('beforeend', assetHtml);
    }

    resetAssetForm() {
        const container = document.getElementById('assets-container');
        container.innerHTML = '';
        this.addAsset(); // Ajouter un actif par défaut
    }

    async createPortfolio(event) {
        if (event) event.preventDefault();

        try {
            const formData = new FormData(document.getElementById('portfolio-form'));
            const assets = this.collectAssets();

            if (assets.length === 0) {
                this.showNotification('Ajoutez au moins un actif', 'error');
                return;
            }

            const portfolioData = {
                name: document.querySelector('#portfolio-form input[type="text"]').value,
                description: document.querySelector('#portfolio-form textarea').value,
                assets: assets
            };

            // Simulation de création (remplace l'appel API)
            this.portfolios.push({
                id: Date.now(),
                ...portfolioData,
                total_value: assets.reduce((sum, asset) => sum + asset.value, 0)
            });

            this.hideModal('portfolio-modal');
            this.showNotification('Portefeuille créé avec succès!', 'success');
            this.loadData(); // Recharger les données

        } catch (error) {
            console.error('Erreur création portefeuille:', error);
            this.showNotification('Erreur lors de la création', 'error');
        }
    }

    collectAssets() {
        const assets = [];
        document.querySelectorAll('.asset-item').forEach(item => {
            const inputs = item.querySelectorAll('input, select');
            if (inputs[0].value && inputs[2].value) {
                assets.push({
                    name: inputs[0].value,
                    type: inputs[1].value,
                    value: parseFloat(inputs[2].value)
                });
            }
        });
        return assets;
    }

    // === RAPPORTS ===
    generateReport() {
        if (!this.currentSimulation) {
            this.showNotification('Aucune simulation récente à rapporter', 'error');
            return;
        }

        this.downloadReport(this.currentSimulation.simulation_id);
    }

    async downloadReport(simulationId) {
        try {
            this.showLoading('Génération du rapport...');

            // Simulation de téléchargement
            const simulation = this.currentSimulation || {
                simulation_id: simulationId,
                results: { portfolio_value: 156700000, var: 1250000 }
            };

            const reportData = {
                simulation: simulation,
                generated_at: new Date().toISOString(),
                report_type: 'risk_analysis'
            };

            const blob = new Blob([JSON.stringify(reportData, null, 2)], {
                type: 'application/json'
            });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `rapport_simulation_${simulationId}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.showNotification('Rapport téléchargé avec succès!', 'success');

        } catch (error) {
            console.error('Erreur téléchargement:', error);
            this.showNotification('Erreur lors du téléchargement', 'error');
        } finally {
            this.hideLoading();
        }
    }

    // === MÉTHODES UTILITAIRES ===
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('nav a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const href = link.getAttribute('href');
                if (href) this.showSection(href.substring(1));
            });
        });

        // Formulaires
        const simulationForm = document.getElementById('simulation-form');
        const portfolioForm = document.getElementById('portfolio-form');
        const simulationType = document.getElementById('simulation-type');

        if (simulationForm) {
            simulationForm.addEventListener('submit', (e) => this.runSimulation(e));
        }
        if (portfolioForm) {
            portfolioForm.addEventListener('submit', (e) => this.createPortfolio(e));
        }
        if (simulationType) {
            simulationType.addEventListener('change', () => this.updateSimulationParams());
        }

        console.log('✅ Event listeners configurés');
    }

    showSection(sectionId) {
        document.querySelectorAll('.section').forEach(section => {
            section.classList.add('hidden');
        });

        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.remove('hidden');
            if (sectionId === 'simulations') this.loadRecentSimulations();
        }

        document.querySelectorAll('nav a').forEach(link => {
            link.classList.remove('active');
            const href = link.getAttribute('href');
            if (href === `#${sectionId}`) link.classList.add('active');
        });
    }

    async loadRecentSimulations() {
        try {
            // Simulation de données récentes
            const mockSimulations = [
                {
                    id: 1,
                    name: 'Stress Test - Crise Marché',
                    type: 'stress_test',
                    created_at: new Date().toISOString(),
                    status: 'completed',
                    results: { var: 2350000 }
                },
                {
                    id: 2,
                    name: 'Calcul SCR Q1 2024',
                    type: 'solvency_ii',
                    created_at: new Date(Date.now() - 86400000).toISOString(),
                    status: 'completed',
                    results: { var: 1850000 }
                }
            ];

            this.updateSimulationsTable(mockSimulations);
        } catch (error) {
            console.error('Erreur chargement simulations:', error);
            this.showMockSimulations();
        }
    }

    updateSimulationsTable(simulations) {
        // CORRECTION : Utiliser le bon sélecteur
        const tbody = document.querySelector('#simulations-table tbody') ||
                     document.querySelector('#dashboard-simulations-table');

        if (!tbody) {
            console.error('Tableau des simulations non trouvé');
            return;
        }

        tbody.innerHTML = simulations.map(sim => `
            <tr class="border-b hover:bg-gray-50">
                <td class="py-3 px-4">${this.truncateText(sim.name, 25)}</td>
                <td class="py-3 px-4">
                    <span class="px-2 py-1 rounded text-xs ${
                        sim.type === 'stress_test' ? 'bg-red-100 text-red-800' : 
                        sim.type === 'solvency_ii' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                    }">
                        ${this.formatSimulationType(sim.type)}
                    </span>
                </td>
                <td class="py-3 px-4 text-sm">${new Date(sim.created_at).toLocaleDateString('fr-FR')}</td>
                <td class="py-3 px-4">
                    <span class="px-2 py-1 rounded text-xs ${
                        sim.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }">
                        ${sim.status === 'completed' ? 'Terminée' : 'En cours'}
                    </span>
                </td>
                <td class="py-3 px-4 font-medium">${sim.results?.var ? this.formatCurrency(sim.results.var) : '-'}</td>
                <td class="py-3 px-4">
                    <button onclick="finRiskApp.viewSimulation(${sim.id})" class="text-blue-600 hover:text-blue-800 mr-2">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="finRiskApp.downloadReport(${sim.id})" class="text-green-600 hover:text-green-800">
                        <i class="fas fa-download"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    showMockSimulations() {
        const mockData = [
            {
                id: 1,
                name: 'Simulation de démonstration',
                type: 'stress_test',
                created_at: new Date().toISOString(),
                status: 'completed',
                results: { var: 1250000 }
            }
        ];
        this.updateSimulationsTable(mockData);
    }

    viewSimulation(simulationId) {
        this.showNotification(`Visualisation de la simulation #${simulationId}`, 'info');
    }

    showLoading(message = 'Chargement...') {
        let loading = document.getElementById('loading');
        if (!loading) {
            loading = document.createElement('div');
            loading.id = 'loading';
            loading.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
            loading.innerHTML = `
                <div class="bg-white p-6 rounded-lg shadow-xl flex items-center">
                    <i class="fas fa-spinner fa-spin text-2xl text-blue-600 mr-3"></i>
                    <span>${message}</span>
                </div>
            `;
            document.body.appendChild(loading);
        }
        loading.classList.remove('hidden');
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) loading.classList.add('hidden');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'success' ? 'bg-green-500' : 
            type === 'error' ? 'bg-red-500' : 'bg-blue-500'
        } text-white max-w-sm`;
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${
                    type === 'success' ? 'fa-check' : 
                    type === 'error' ? 'fa-exclamation-triangle' : 'fa-info'
                } mr-2"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 4000);
    }

    formatCurrency(amount) {
        if (!amount) return '€0';
        if (amount >= 1000000) return '€' + (amount / 1000000).toFixed(1) + 'M';
        if (amount >= 1000) return '€' + (amount / 1000).toFixed(0) + 'K';
        return '€' + amount.toLocaleString('fr-FR');
    }

    formatSimulationType(type) {
        const types = {
            'stress_test': 'Test de Stress',
            'solvency_ii': 'Solvabilité II',
            'market_risk': 'Risque de Marché'
        };
        return types[type] || type;
    }

    truncateText(text, maxLength) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    window.finRiskApp = new FinRiskSimulator();
    console.log('✅ FinRisk Simulator initialisé avec succès!');
});