

$(document).ready(function () {
    // Initialisation DataTables
    const table = $('#correlationTable').DataTable({
        pageLength: 10,
        order: [[6, 'asc']],
        responsive: true,
        language: {
            search: "Rechercher :",
            lengthMenu: "Afficher _MENU_ résultats",
            info: "Affichage de _START_ à _END_ sur _TOTAL_ résultats",
            zeroRecords: "Aucun résultat correspondant",
            emptyTable: "Aucune relation significative détectée",
            paginate: {
                previous: "Précédent",
                next: "Suivant"
            }
        }
    });
    // ==========================================
    // INITIALISATION DU GRAPHIQUE
    // ==========================================

    const chartCanvas = document.getElementById('correlationChart');

    const chartLabels = [
        'Numérique - Numérique',
        'Catégorielle - Numérique',
        'Catégorielle - Catégorielle'
    ];

    const chartTypes = [
        'Numeric-Numeric',
        'Categorical-Numeric',
        'Categorical-Categorical'
    ];

    const correlationChart = new Chart(chartCanvas, {
        type: 'doughnut',

        data: {
            labels: chartLabels,

            datasets: [{
                label: 'Nombre de relations',

                data: [0, 0, 0],

                backgroundColor: [
                    '#0d6efd',
                    '#0dcaf0',
                    '#ffc107'
                ],

                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    position: 'bottom'
                },

                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return context.label + ': ' + context.raw;
                        }
                    }
                }
            }
        }
    });
    // Une seule fonction personnalisée pour la taille d'effet
    let selectedStrength = '';

    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {

        if (settings.nTable.id !== 'correlationTable') {
            return true;
        }

        const row = table.row(dataIndex).node();

        if (!row) return true;

        const effect = parseFloat(row.dataset.effect);

        if (selectedStrength === '') return true;

        if (Number.isNaN(effect)) return false;

        switch (selectedStrength) {

            case 'weak':
                return effect >= 0.10 && effect < 0.30;

            case 'moderate':
                return effect >= 0.30 && effect < 0.50;

            case 'strong':
                return effect >= 0.50;

            default:
                return true;
        }
    });


    // Filtre par type de relation
    $('#filterRelationship').on('change', function () {

        table.column(2).search(
            this.value ? '^' + escapeRegex(this.value) + '$' : '',
            true,
            false
        ).draw();

        updateIndicators();
    });


    // Filtre par test statistique
    $('#filterTest').on('change', function () {

        table.column(3).search(
            this.value ? '^' + escapeRegex(this.value) + '$' : '',
            true,
            false
        ).draw();

        updateIndicators();
    });


    // Filtre par taille d'effet
    $('#filterStrength').on('change', function () {

        selectedStrength = this.value;

        table.draw();

        updateIndicators();
    });


    // Échapper les caractères spéciaux des expressions régulières
    function escapeRegex(value) {
        return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }


    // Mise à jour des statistiques
    function updateIndicators() {

        const rows = table.rows({
            search: 'applied'
        }).nodes().toArray();

        let strong = 0;

        const types = new Set();

        // Compter les relations par catégorie
        const counts = {
            'Numeric-Numeric': 0,
            'Categorical-Numeric': 0,
            'Categorical-Categorical': 0
        };

        rows.forEach(row => {

            const effect = parseFloat(row.dataset.effect);

            const relationship = row.dataset.relationship;

            // Relations fortes
            if (!Number.isNaN(effect) && effect >= 0.50) {
                strong++;
            }

            // Nombre de types distincts
            types.add(relationship);

            // Distribution des relations
            if (Object.prototype.hasOwnProperty.call(counts, relationship)) {
                counts[relationship]++;
            }
        });

        // Actualiser les indicateurs
        $('#totalRelations').text(rows.length);
        $('#significantRelations').text(rows.length);
        $('#strongRelations').text(strong);
        $('#relationshipTypes').text(types.size);

        // Actualiser le graphique
        correlationChart.data.datasets[0].data = chartTypes.map(
            type => counts[type]
        );

        correlationChart.update();
    }


    // Réinitialisation
    $('#resetFilters').on('click', function () {

        $('#filterRelationship').val('');
        $('#filterTest').val('');
        $('#filterStrength').val('');

        selectedStrength = '';

        table.search('');
        table.columns().search('');

        table.draw();

        updateIndicators();

    });


    // Actualiser les indicateurs lors d'une recherche textuelle
    table.on('draw', function () {
        updateIndicators();
    });

    updateIndicators();

});
