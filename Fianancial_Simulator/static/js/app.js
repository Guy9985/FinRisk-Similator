// Application principale FinRisk Simulator - VERSION COMPLÈTE CORRIGÉE
class FinRiskApp {
    constructor() {
        this.baseUrl = window.location.origin;
        this.charts = {};
        this.currentUser = null;
        this.portfolios = [];
        this.simulations = [];
        this.scenarios = [];

        this.uiManager = new UIManager();
        this.init();
    }

    async init() {
        console.log('🚀 Initialisation FinRisk Simulator...');

        // Initialiser d'abord l'interface
        this.setupEventListeners();

        // Ensuite vérifier l'authentification
        await this.checkAuth();

        console.log('✅ Application initialisée');
    }

    async checkAuth() {
        try {
            console.log('🔍 Vérification authentification...');
            const response = await fetch('/api/current_user');

            if (response.ok) {
                const userData = await response.json();
                this.currentUser = userData;
                console.log('✅ Utilisateur connecté:', userData.username);
                this.showApp();
                await this.loadInitialData();
            } else {
                console.log('❌ Utilisateur non connecté');
                this.showLogin();
            }
        } catch (error) {
            console.log('❌ Erreur vérification auth:', error);
            this.showLogin();
        }
    }

    showLogin() {
        console.log('🔐 Affichage page login');
        document.getElementById('login-page').style.display = 'flex';
        document.getElementById('app-page').style.display = 'none';
    }

    showApp() {
        console.log('🚀 Affichage application');
        document.getElementById('login-page').style.display = 'none';
        document.getElementById('app-page').style.display = 'block';

        // Mettre à jour le message de bienvenue
        if (this.currentUser) {
            const welcomeElement = document.getElementById('user-welcome');
            if (welcomeElement) {
                welcomeElement.textContent = `Bienvenue ${this.currentUser.username}`;
            }
        }

        this.showSection('dashboard');
    }

    async loadInitialData() {
        if (!this.currentUser) return;

        try {
            this.uiManager.showLoading('Chargement des données...');

            // Chargement parallèle des données
            await Promise.all([
                this.loadPortfolios(),
                this.loadScenarios(),
                this.loadSimulations()
            ]);

            // Initialisation du tableau de bord
            await this.loadDashboardData();

            this.uiManager.showSuccess('Données chargées avec succès');

        } catch (error) {
            this.uiManager.showError('Erreur chargement données', error.message);
        } finally {
            this.uiManager.hideLoading();
        }
    }

    async loadDashboardData() {
        try {
            const response = await fetch('/api/dashboard/metrics');
            if (!response.ok) throw new Error('Erreur API');

            const metrics = await response.json();
            this.updateDashboard(metrics);
            this.setupCharts(metrics);

        } catch (error) {
            this.uiManager.showError('Erreur chargement dashboard', error.message);
        }
    }

    async loadPortfolios() {
        try {
            const response = await fetch('/api/portfolios');
            if (!response.ok) throw new Error('Erreur API portfolios');

            this.portfolios = await response.json();
            this.updatePortfoliosList();

        } catch (error) {
            this.uiManager.showError('Erreur chargement portefeuilles', error.message);
        }
    }

    async loadScenarios() {
        try {
            const response = await fetch('/api/scenarios');
            if (!response.ok) throw new Error('Erreur API scénarios');

            this.scenarios = await response.json();

        } catch (error) {
            this.uiManager.showError('Erreur chargement scénarios', error.message);
        }
    }

    async loadSimulations() {
        try {
            const response = await fetch('/api/simulations');
            if (!response.ok) throw new Error('Erreur API simulations');

            this.simulations = await response.json();
            this.updateSimulationsTable();
            this.updateSimulationsList();

        } catch (error) {
            this.uiManager.showError('Erreur chargement simulations', error.message);
        }
    }

    updateDashboard(metrics) {
        // Mise à jour des métriques
        this.uiManager.updateMetric('[data-metric="var"]', metrics.current_var, this.formatCurrency);
        this.uiManager.updateMetric('[data-metric="stress"]', metrics.stress_loss, this.formatCurrency);
        this.uiManager.updateMetric('[data-metric="scr"]', metrics.scr_coverage, val => val + '%');
        this.uiManager.updateMetric('[data-metric="portfolio"]', metrics.portfolio_value, this.formatCurrency);

        // Mise à jour de l'allocation d'actifs
        this.updateAllocationChart(metrics.asset_allocation);
    }

    setupCharts(metrics) {
        // Graphique d'allocation
        this.setupAllocationChart(metrics.asset_allocation);

        // Graphique de risque
        this.setupRiskChart(metrics);
    }

    setupAllocationChart(allocationData) {
        const ctx = document.getElementById('allocation-chart');
        if (!ctx) return;

        if (this.charts.allocation) {
            this.charts.allocation.destroy();
        }

        const labels = Object.keys(allocationData);
        const data = Object.values(allocationData);
        const backgroundColors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
        ];

        this.charts.allocation = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: backgroundColors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    title: {
                        display: true,
                        text: 'Allocation d\'Actifs',
                        font: { size: 16 }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.parsed}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    setupRiskChart(metrics) {
        const ctx = document.getElementById('risk-chart');
        if (!ctx) return;

        if (this.charts.risk) {
            this.charts.risk.destroy();
        }

        this.charts.risk = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['VaR 95%', 'Stress Test', 'Expected Shortfall'],
                datasets: [{
                    label: 'Exposition au Risque',
                    data: [
                        metrics.current_var,
                        metrics.stress_loss,
                        metrics.current_var * 1.3
                    ],
                    backgroundColor: ['#FF6384', '#FF9F40', '#FFCD56'],
                    borderColor: ['#FF6384', '#FF9F40', '#FFCD56'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Profil de Risque',
                        font: { size: 16 }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                return `${context.dataset.label}: ${this.formatCurrency(context.parsed.y)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => this.formatCurrency(value)
                        }
                    }
                }
            }
        });
    }

    updateAllocationChart(allocationData) {
        if (!this.charts.allocation) return;

        const labels = Object.keys(allocationData);
        const data = Object.values(allocationData);

        this.charts.allocation.data.labels = labels;
        this.charts.allocation.data.datasets[0].data = data;
        this.charts.allocation.update();
    }

    // MÉTHODE CRÉATION PORTEFEUILLE
    async createPortfolio(portfolioData) {
        try {
            this.uiManager.showLoading('Création du portefeuille...');
            console.log('📤 Envoi données portefeuille:', portfolioData);

            const response = await fetch('/api/portfolios', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(portfolioData)
            });

            const result = await response.json();
            console.log('📥 Réponse serveur:', result);

            if (result.success) {
                this.hideAllModals();
                this.loadPortfolios();
                this.loadDashboardData();
                this.uiManager.showSuccess(result.message || 'Portefeuille créé avec succès');
            } else {
                const errorMsg = result.errors ? result.errors.join(', ') : result.error;
                throw new Error(errorMsg || 'Erreur inconnue');
            }

        } catch (error) {
            console.error('❌ Erreur création portefeuille:', error);
            this.uiManager.showError('Erreur création portefeuille', error.message);
        } finally {
            this.uiManager.hideLoading();
        }
    }

    // MÉTHODE EXÉCUTION SIMULATION - VERSION CORRIGÉE
    async runSimulation(simulationData) {
        try {
            this.uiManager.showLoading('Lancement de la simulation...');
            console.log('🚀 Données simulation:', simulationData);

            // VALIDATION RENFORCÉE
            if (!simulationData.portfolio_id) {
                throw new Error('Veuillez sélectionner un portefeuille');
            }

            if (simulationData.type === 'stress_test' && !simulationData.parameters.scenario_id) {
                throw new Error('Veuillez sélectionner un scénario de stress');
            }

            const response = await fetch('/api/simulations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(simulationData)
            });

            const result = await response.json();
            console.log('📊 Résultat simulation:', result);

            if (!response.ok) {
                throw new Error(result.error || 'Erreur lors de la simulation');
            }

            if (result.success) {
                this.hideAllModals();
                this.showSimulationResults({
                    ...result,
                    simulation_id: result.simulation_id,
                    type: simulationData.type,
                    created_at: result.created_at
                });
                await this.loadSimulations();
                await this.loadDashboardData();
                this.uiManager.showSuccess('Simulation terminée avec succès!');
            } else {
                throw new Error(result.error || 'Erreur inconnue lors de la simulation');
            }

        } catch (error) {
            console.error('❌ Erreur simulation:', error);
            this.uiManager.showError('Erreur lors de la simulation', error.message);
        } finally {
            this.uiManager.hideLoading();
        }
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('data-section');
                this.showSection(section);
            });
        });

        // Boutons d'action
        document.getElementById('new-simulation-btn')?.addEventListener('click', () => {
            this.showSimulationModal();
        });

        document.getElementById('new-simulation-btn-2')?.addEventListener('click', () => {
            this.showSimulationModal();
        });

        document.getElementById('new-portfolio-btn')?.addEventListener('click', () => {
            this.showPortfolioModal();
        });

        document.getElementById('refresh-data-btn')?.addEventListener('click', () => {
            this.loadDashboardData();
        });

        // Connexion
        document.getElementById('login-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        document.getElementById('register-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });

        document.getElementById('logout-btn')?.addEventListener('click', () => {
            this.handleLogout();
        });

        // Fermeture modales
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                this.hideAllModals();
            });
        });

        // Clic outside modal
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideAllModals();
                }
            });
        });

        // Changement type simulation
        document.querySelector('select[name="type"]')?.addEventListener('change', (e) => {
            this.updateSimulationParams(e.target.value);
        });
    }

    showSection(sectionId) {
        // Masquer toutes les sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });

        // Afficher la section demandée
        const targetSection = document.getElementById(`${sectionId}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Mettre à jour la navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-section') === sectionId) {
                link.classList.add('active');
            }
        });

        // Charger les données spécifiques à la section
        if (sectionId === 'simulations') {
            this.loadSimulations();
        } else if (sectionId === 'portfolios') {
            this.loadPortfolios();
        }
    }

    async handleLogin() {
        const form = document.getElementById('login-form');
        const formData = new FormData(form);

        const credentials = {
            username: formData.get('username'),
            password: formData.get('password')
        };

        try {
            this.uiManager.showLoading('Connexion...');
            console.log('🔐 Tentative connexion:', credentials.username);

            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(credentials)
            });

            const result = await response.json();
            console.log('📨 Réponse login:', result);

            if (result.success) {
                this.currentUser = result.user;
                console.log('✅ Connexion réussie pour:', result.user.username);
                this.showApp();
                this.loadInitialData();
                this.uiManager.showSuccess(`Bienvenue ${result.user.username} !`);
            } else {
                throw new Error(result.error || 'Erreur de connexion');
            }

        } catch (error) {
            console.error('❌ Échec connexion:', error);
            this.uiManager.showError('Échec de la connexion', error.message);
        } finally {
            this.uiManager.hideLoading();
        }
    }

    async handleRegister() {
        const form = document.getElementById('register-form');
        const formData = new FormData(form);

        const userData = {
            username: formData.get('username'),
            email: formData.get('email'),
            password: formData.get('password')
        };

        try {
            this.uiManager.showLoading('Création du compte...');

            const response = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });

            const result = await response.json();

            if (result.success) {
                this.currentUser = result.user;
                this.showApp();
                this.loadInitialData();
                this.uiManager.showSuccess(`Compte créé avec succès ! Bienvenue ${result.user.username}`);
            } else {
                throw new Error(result.error || 'Erreur lors de la création du compte');
            }

        } catch (error) {
            this.uiManager.showError('Échec de la création du compte', error.message);
        } finally {
            this.uiManager.hideLoading();
        }
    }

    async handleLogout() {
        try {
            console.log('🚪 Déconnexion...');
            await fetch('/logout', { method: 'POST' });
            this.currentUser = null;
            this.showLogin();
            this.uiManager.showSuccess('Déconnexion réussie');
        } catch (error) {
            console.error('❌ Erreur déconnexion:', error);
            this.uiManager.showError('Erreur lors de la déconnexion', error.message);
        }
    }

    showSimulationModal() {
        document.getElementById('simulation-modal').classList.add('active');
        this.updateSimulationForm();
    }

    showPortfolioModal() {
        document.getElementById('portfolio-modal').classList.add('active');
        this.resetPortfolioForm();
    }

    hideAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
    }

    updateSimulationForm() {
        // Mettre à jour la liste des portefeuilles
        const portfolioSelect = document.getElementById('simulation-portfolio');
        if (portfolioSelect && this.portfolios.length > 0) {
            portfolioSelect.innerHTML = this.portfolios.map(portfolio =>
                `<option value="${portfolio.id}">${portfolio.name} (${this.formatCurrency(portfolio.total_value)})</option>`
            ).join('');
        } else {
            portfolioSelect.innerHTML = '<option value="">Aucun portefeuille disponible</option>';
        }

        // Mettre à jour la liste des scénarios
        const scenarioList = document.getElementById('scenarios-list');
        if (scenarioList && this.scenarios.length > 0) {
            scenarioList.innerHTML = this.scenarios.map(scenario => `
                <label class="scenario-item">
                    <input type="radio" name="scenario" value="${scenario.id}" required>
                    <div class="scenario-info">
                        <div class="scenario-name">${scenario.name}</div>
                        <div class="scenario-desc">${scenario.description}</div>
                    </div>
                </label>
            `).join('');
        }

        // Initialiser les paramètres
        const simulationType = document.querySelector('select[name="type"]').value;
        this.updateSimulationParams(simulationType);
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

    resetPortfolioForm() {
        const form = document.getElementById('portfolio-form');
        if (form) {
            form.reset();
            document.getElementById('assets-container').innerHTML = '';
            this.addAssetField();
        }
    }

    addAssetField() {
        const container = document.getElementById('assets-container');
        const index = container.children.length;

        const assetHtml = `
            <div class="asset-item" data-index="${index}">
                <div class="asset-header">
                    <h4>Actif ${index + 1}</h4>
                    <button type="button" class="btn-remove-asset" onclick="finRiskApp.removeAssetField(${index})">
                        <i class="fas fa-trash"></i> Supprimer
                    </button>
                </div>
                <div class="asset-grid">
                    <div class="form-group">
                        <label>Nom de l'actif *</label>
                        <input type="text" name="asset_name_${index}" class="form-input" placeholder="ex: Apple Inc." required>
                    </div>
                    <div class="form-group">
                        <label>Symbole</label>
                        <input type="text" name="asset_symbol_${index}" class="form-input" placeholder="ex: AAPL">
                    </div>
                    <div class="form-group">
                        <label>Type *</label>
                        <select name="asset_type_${index}" class="form-select" required>
                            <option value="equity">Action</option>
                            <option value="bond">Obligation</option>
                            <option value="real_estate">Immobilier</option>
                            <option value="commodities">Matières premières</option>
                            <option value="credit">Crédit</option>
                            <option value="cash">Liquidités</option>
                            <option value="other">Autre</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Quantité *</label>
                        <input type="number" name="asset_quantity_${index}" class="form-input" step="0.001" min="0.001" required>
                    </div>
                    <div class="form-group">
                        <label>Prix d'achat (€) *</label>
                        <input type="number" name="asset_price_${index}" class="form-input" step="0.01" min="0" required>
                    </div>
                </div>
            </div>
        `;

        container.insertAdjacentHTML('beforeend', assetHtml);
    }

    removeAssetField(index) {
        const item = document.querySelector(`.asset-item[data-index="${index}"]`);
        if (item && document.querySelectorAll('.asset-item').length > 1) {
            item.remove();
            this.renumberAssetFields();
        } else {
            this.uiManager.showWarning('Un portefeuille doit contenir au moins un actif');
        }
    }

    renumberAssetFields() {
        document.querySelectorAll('.asset-item').forEach((item, index) => {
            item.setAttribute('data-index', index);
            item.querySelector('h4').textContent = `Actif ${index + 1}`;
        });
    }

    updatePortfoliosList() {
        const container = document.getElementById('portfolios-list');
        if (!container) return;

        if (this.portfolios.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-wallet fa-3x"></i>
                    <h3>Aucun portefeuille</h3>
                    <p>Créez votre premier portefeuille pour commencer</p>
                    <button class="btn btn-primary" onclick="finRiskApp.showPortfolioModal()">
                        <i class="fas fa-plus"></i> Créer un portefeuille
                    </button>
                </div>
            `;
            return;
        }

        container.innerHTML = this.portfolios.map(portfolio => `
            <div class="portfolio-card">
                <div class="portfolio-header">
                    <h3>${portfolio.name}</h3>
                    <div class="portfolio-actions">
                        <button class="btn btn-sm btn-outline" onclick="finRiskApp.viewPortfolio('${portfolio.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </div>
                <p class="portfolio-desc">${portfolio.description || 'Aucune description'}</p>
                <div class="portfolio-value">${this.formatCurrency(portfolio.total_value)}</div>
                <div class="portfolio-assets">
                    <h4>Actifs (${portfolio.assets.length})</h4>
                    <div class="assets-list">
                        ${portfolio.assets.map(asset => `
                            <div class="asset-tag">
                                <span class="asset-name">${asset.name}</span>
                                <span class="asset-value">${this.formatCurrency(asset.current_value)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `).join('');
    }

    updateSimulationsTable() {
        const tbody = document.getElementById('simulations-table-body');
        if (!tbody) return;

        if (this.simulations.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center py-4">
                        <div class="empty-state">
                            <i class="fas fa-calculator fa-2x"></i>
                            <p>Aucune simulation effectuée</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.simulations.map(sim => `
            <tr>
                <td>${sim.name}</td>
                <td>
                    <span class="badge ${this.getSimulationBadgeClass(sim.type)}">
                        ${this.formatSimulationType(sim.type)}
                    </span>
                </td>
                <td>${new Date(sim.created_at).toLocaleDateString('fr-FR')}</td>
                <td>
                    <span class="badge badge-success">Terminée</span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="finRiskApp.viewSimulation('${sim.id}')">
                        <i class="fas fa-eye"></i> Voir
                    </button>
                </td>
            </tr>
        `).join('');
    }

    updateSimulationsList() {
        const tbody = document.getElementById('simulations-list');
        if (!tbody) return;

        if (this.simulations.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center py-4">
                        <div class="empty-state">
                            <i class="fas fa-calculator fa-2x"></i>
                            <p>Aucune simulation effectuée</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.simulations.map(sim => `
            <tr>
                <td>${sim.name}</td>
                <td>
                    <span class="badge ${this.getSimulationBadgeClass(sim.type)}">
                        ${this.formatSimulationType(sim.type)}
                    </span>
                </td>
                <td>${new Date(sim.created_at).toLocaleDateString('fr-FR')}</td>
                <td>
                    <span class="badge badge-success">Terminée</span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="finRiskApp.viewSimulation('${sim.id}')">
                        <i class="fas fa-eye"></i> Voir
                    </button>
                </td>
            </tr>
        `).join('');
    }

    getSimulationBadgeClass(type) {
        const classes = {
            'var': 'badge-error',
            'stress_test': 'badge-warning',
            'solvency_ii': 'badge-info'
        };
        return classes[type] || 'badge-info';
    }

    formatCurrency(amount) {
        if (amount === null || amount === undefined) return '€0';

        const numAmount = parseFloat(amount);
        if (isNaN(numAmount)) return '€0';

        if (numAmount >= 1e9) {
            return '€' + (numAmount / 1e9).toFixed(2) + 'B';
        } else if (numAmount >= 1e6) {
            return '€' + (numAmount / 1e6).toFixed(2) + 'M';
        } else if (numAmount >= 1e3) {
            return '€' + (numAmount / 1e3).toFixed(1) + 'K';
        } else {
            return '€' + numAmount.toFixed(0);
        }
    }

    formatSimulationType(type) {
        const types = {
            'var': 'Value at Risk',
            'stress_test': 'Test de Stress',
            'solvency_ii': 'Solvabilité II'
        };
        return types[type] || type;
    }

    viewSimulation(simulationId) {
        const simulation = this.simulations.find(s => s.id === simulationId);
        if (simulation) {
            this.showSimulationResults({
                ...simulation,
                success: true
            });
        }
    }

    viewPortfolio(portfolioId) {
        console.log('Voir portefeuille:', portfolioId);
        this.uiManager.showInfo('Fonctionnalité en développement');
    }

    showSimulationResults(result) {
        const modal = document.getElementById('results-modal');
        const content = document.getElementById('results-content');

        if (!modal || !content) return;

        content.innerHTML = this.formatSimulationResults(result);
        modal.classList.add('active');
    }

    formatSimulationResults(result) {
        const results = result.results;
        let html = `
            <div class="results-header">
                <h3>Résultats de la Simulation</h3>
                <p><strong>Nom:</strong> ${result.name}</p>
                <p><strong>Type:</strong> ${this.formatSimulationType(result.type)}</p>
                <p><strong>Date:</strong> ${new Date(result.created_at).toLocaleString('fr-FR')}</p>
            </div>
        `;

        if (result.type === 'stress_test') {
            html += `
                <div class="results-grid">
                    <div class="result-card">
                        <div class="result-value">${this.formatCurrency(results.remaining_value)}</div>
                        <div class="result-label">Valeur après stress</div>
                    </div>
                    <div class="result-card error">
                        <div class="result-value">${this.formatCurrency(results.total_loss)}</div>
                        <div class="result-label">Perte totale</div>
                    </div>
                    <div class="result-card warning">
                        <div class="result-value">${results.loss_percentage}%</div>
                        <div class="result-label">Impact</div>
                    </div>
                </div>

                <div class="scenario-details">
                    <h4>Détails par actif - ${results.scenario_name}</h4>
                    <div class="table-container">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Actif</th>
                                    <th>Valeur initiale</th>
                                    <th>Choc</th>
                                    <th>Perte</th>
                                    <th>Valeur finale</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${Object.entries(results.losses_by_asset).map(([assetName, assetData]) => `
                                    <tr>
                                        <td>${assetName}</td>
                                        <td>${this.formatCurrency(assetData.original_value)}</td>
                                        <td>${assetData.shock_percentage}%</td>
                                        <td class="error">${this.formatCurrency(assetData.loss)}</td>
                                        <td>${this.formatCurrency(assetData.remaining_value)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } else if (result.type === 'var') {
            html += `
                <div class="results-grid">
                    <div class="result-card">
                        <div class="result-value">${this.formatCurrency(results.var_95)}</div>
                        <div class="result-label">VaR 95%</div>
                    </div>
                    <div class="result-card warning">
                        <div class="result-value">${this.formatCurrency(results.var_99)}</div>
                        <div class="result-label">VaR 99%</div>
                    </div>
                    <div class="result-card error">
                        <div class="result-value">${this.formatCurrency(results.expected_shortfall)}</div>
                        <div class="result-label">Expected Shortfall</div>
                    </div>
                </div>
                <div class="results-info">
                    <p><strong>Niveau de confiance:</strong> ${(results.confidence_level * 100)}%</p>
                </div>
            `;
        } else if (result.type === 'solvency_ii') {
            html += `
                <div class="results-grid">
                    <div class="result-card">
                        <div class="result-value">${this.formatCurrency(results.scr)}</div>
                        <div class="result-label">SCR</div>
                    </div>
                    <div class="result-card ${results.coverage_ratio >= 100 ? 'success' : 'error'}">
                        <div class="result-value">${results.coverage_ratio}%</div>
                        <div class="result-label">Couverture SCR</div>
                    </div>
                    <div class="result-card">
                        <div class="result-value">${this.formatCurrency(results.mcr)}</div>
                        <div class="result-label">MCR</div>
                    </div>
                </div>

                <div class="risk-breakdown">
                    <h4>Décomposition des risques</h4>
                    <div class="table-container">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Type de risque</th>
                                    <th>Montant</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Risque de marché</td>
                                    <td>${this.formatCurrency(results.market_risk)}</td>
                                </tr>
                                <tr>
                                    <td>Risque de souscription</td>
                                    <td>${this.formatCurrency(results.underwriting_risk)}</td>
                                </tr>
                                <tr>
                                    <td>Risque de contrepartie</td>
                                    <td>${this.formatCurrency(results.counterparty_risk)}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        html += `
            <div class="results-actions">
                <button class="btn btn-primary" onclick="finRiskApp.downloadReport('${result.simulation_id || result.id}')">
                    <i class="fas fa-file-pdf mr-2"></i>Télécharger le rapport PDF
                </button>
                <button class="btn btn-outline" onclick="finRiskApp.hideAllModals()">
                    Fermer
                </button>
            </div>
        `;

        return html;
    }

    async downloadReport(simulationId) {
        try {
            this.uiManager.showLoading('Génération du rapport PDF...');

            const response = await fetch(`/api/simulations/${simulationId}/download-pdf`);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erreur lors du téléchargement');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `rapport_simulation_${simulationId}.pdf`;

            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }

            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.uiManager.showSuccess('Rapport PDF téléchargé avec succès');

        } catch (error) {
            console.error('❌ Erreur téléchargement PDF:', error);
            this.uiManager.showError('Erreur téléchargement rapport', error.message);
        } finally {
            this.uiManager.hideLoading();
        }
    }
}

// CLASSE GESTIONNAIRE D'INTERFACE
class UIManager {
    constructor() {
        this.loadingElement = document.getElementById('loading-overlay');
        this.notificationContainer = document.getElementById('notification-container');
    }

    showLoading(message = 'Chargement...') {
        if (this.loadingElement) {
            this.loadingElement.innerHTML = `
                <div class="loading-content">
                    <div class="spinner"></div>
                    <p>${message}</p>
                </div>
            `;
            this.loadingElement.style.display = 'flex';
        }
    }

    hideLoading() {
        if (this.loadingElement) {
            this.loadingElement.style.display = 'none';
        }
    }

    showNotification(message, type = 'info', duration = 5000) {
        if (!this.notificationContainer) return;

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        this.notificationContainer.appendChild(notification);

        setTimeout(() => notification.classList.add('show'), 10);

        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.classList.remove('show');
                    setTimeout(() => notification.remove(), 300);
                }
            }, duration);
        }

        return notification;
    }

    showSuccess(message, duration = 5000) {
        this.showNotification(message, 'success', duration);
    }

    showError(message, detail = null, duration = 0) {
        const fullMessage = detail ? `${message}<br><small>${detail}</small>` : message;
        const notification = this.showNotification(fullMessage, 'error', duration);

        if (duration === 0 && notification) {
            const closeBtn = notification.querySelector('.notification-close');
            closeBtn.style.display = 'block';
        }
    }

    showWarning(message, duration = 5000) {
        this.showNotification(message, 'warning', duration);
    }

    showInfo(message, duration = 3000) {
        this.showNotification(message, 'info', duration);
    }

    updateMetric(selector, value, formatter = null) {
        const element = document.querySelector(selector);
        if (element) {
            const formattedValue = formatter ? formatter(value) : value;
            element.textContent = formattedValue;

            element.classList.add('metric-update');
            setTimeout(() => element.classList.remove('metric-update'), 500);
        }
    }

    confirmAction(message, confirmText = 'Confirmer', cancelText = 'Annuler') {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'modal active';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Confirmation</h3>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-outline" id="confirm-cancel">${cancelText}</button>
                        <button class="btn btn-primary" id="confirm-ok">${confirmText}</button>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            modal.querySelector('#confirm-ok').addEventListener('click', () => {
                modal.remove();
                resolve(true);
            });

            modal.querySelector('#confirm-cancel').addEventListener('click', () => {
                modal.remove();
                resolve(false);
            });

            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                    resolve(false);
                }
            });
        });
    }
}

// GESTIONNAIRES D'ÉVÉNEMENTS POUR LES FORMULAIRES
function setupFormHandlers() {
    // Formulaire portfolio
    const portfolioForm = document.getElementById('portfolio-form');
    if (portfolioForm) {
        portfolioForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('📝 Soumission formulaire portefeuille');

            const formData = new FormData(this);

            const portfolioData = {
                name: formData.get('name').trim(),
                description: formData.get('description').trim(),
                assets: []
            };

            let hasErrors = false;
            const assetItems = document.querySelectorAll('.asset-item');

            assetItems.forEach((item, index) => {
                const name = item.querySelector(`input[name="asset_name_${index}"]`)?.value.trim();
                const symbol = item.querySelector(`input[name="asset_symbol_${index}"]`)?.value.trim();
                const type = item.querySelector(`select[name="asset_type_${index}"]`)?.value;
                const quantity = item.querySelector(`input[name="asset_quantity_${index}"]`)?.value;
                const purchase_price = item.querySelector(`input[name="asset_price_${index}"]`)?.value;

                if (!name) {
                    window.finRiskApp.uiManager.showError(`L'actif ${index + 1} doit avoir un nom`);
                    hasErrors = true;
                    return;
                }

                if (!quantity || parseFloat(quantity) <= 0) {
                    window.finRiskApp.uiManager.showError(`L'actif ${index + 1} doit avoir une quantité valide`);
                    hasErrors = true;
                    return;
                }

                if (!purchase_price || parseFloat(purchase_price) < 0) {
                    window.finRiskApp.uiManager.showError(`L'actif ${index + 1} doit avoir un prix valide`);
                    hasErrors = true;
                    return;
                }

                portfolioData.assets.push({
                    name: name,
                    symbol: symbol || '',
                    type: type,
                    quantity: parseFloat(quantity),
                    purchase_price: parseFloat(purchase_price)
                });
            });

            if (hasErrors) return;

            if (portfolioData.assets.length === 0) {
                window.finRiskApp.uiManager.showError('Ajoutez au moins un actif au portefeuille');
                return;
            }

            console.log('✅ Données prêtes pour envoi:', portfolioData);
            window.finRiskApp.createPortfolio(portfolioData);
        });
    }

    // Formulaire simulation - VERSION CORRIGÉE
    const simulationForm = document.getElementById('simulation-form');
    if (simulationForm) {
        simulationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(e.target);

            const simulationData = {
                name: formData.get('name').trim(),
                portfolio_id: formData.get('portfolio_id'),
                type: formData.get('type'),
                parameters: {}
            };

            // VALIDATION DU NOM
            if (!simulationData.name) {
                window.finRiskApp.uiManager.showError('Veuillez donner un nom à la simulation');
                return;
            }

            // Récupérer les paramètres spécifiques au type de simulation - CORRECTION COMPLÈTE
            if (simulationData.type === 'var') {
                simulationData.parameters = {
                    confidence_level: parseFloat(formData.get('confidence_level')),
                    time_horizon: parseInt(formData.get('time_horizon')),
                    method: formData.get('var_method')
                };
            } else if (simulationData.type === 'stress_test') {
                const selectedScenario = formData.get('scenario');
                if (!selectedScenario) {
                    window.finRiskApp.uiManager.showError('Veuillez sélectionner un scénario de stress');
                    return;
                }
                simulationData.parameters = {
                    scenario_id: selectedScenario
                };
            } else if (simulationData.type === 'solvency_ii') {
                // CORRECTION: Solvabilité II n'a pas besoin de scénario
                simulationData.parameters = {
                    calculate_mcr: formData.get('calculate_mcr') === 'true'
                };
            }

            console.log('🚀 Données simulation préparées:', simulationData);
            window.finRiskApp.runSimulation(simulationData);
        });
    }

    // Bouton ajouter actif
    const addAssetBtn = document.getElementById('add-asset-btn');
    if (addAssetBtn) {
        addAssetBtn.addEventListener('click', () => {
            window.finRiskApp.addAssetField();
        });
    }
}

// INITIALISATION DE L'APPLICATION
let finRiskApp;

document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM chargé - Initialisation application...');

    try {
        finRiskApp = new FinRiskApp();
        window.finRiskApp = finRiskApp;

        setupFormHandlers();

        window.addEventListener('error', function(e) {
            console.error('💥 Erreur globale:', e.error);
            if (finRiskApp && finRiskApp.uiManager) {
                finRiskApp.uiManager.showError('Erreur inattendue', e.error.message);
            }
        });

        window.addEventListener('unhandledrejection', function(e) {
            console.error('💥 Promesse rejetée:', e.reason);
            if (finRiskApp && finRiskApp.uiManager) {
                finRiskApp.uiManager.showError('Erreur asynchrone', e.reason.message);
            }
        });

        console.log('🎉 Application FinRisk Simulator prête!');

    } catch (error) {
        console.error('❌ Erreur critique initialisation:', error);

        document.body.innerHTML = `
            <div class="error-container">
                <div class="error-content">
                    <h1>🚨 Erreur Critique</h1>
                    <p>L'application n'a pas pu démarrer correctement.</p>
                    <p><strong>Détails:</strong> ${error.message}</p>
                    <button onclick="window.location.reload()" class="btn btn-primary">
                        <i class="fas fa-refresh"></i> Recharger l'application
                    </button>
                </div>
            </div>
        `;
    }
});

// FONCTIONS UTILITAIRES GLOBALES
function formatPercentage(value) {
    if (value === null || value === undefined) return '0%';
    return `${parseFloat(value).toFixed(2)}%`;
}

function formatNumber(value, decimals = 2) {
    if (value === null || value === undefined) return '0';
    return parseFloat(value).toFixed(decimals);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FinRiskApp, UIManager };
}