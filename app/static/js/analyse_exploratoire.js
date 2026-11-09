document.addEventListener("DOMContentLoaded", function () {

    const columnSelect = document.getElementById("columnSelect");

    const cards = document.querySelectorAll(".column-card");

    const columnsContainer = document.getElementById("columnsContainer");

    const canvas = document.getElementById("distributionChart");

    let distributionChart = null;


    // Sélection d'une variable
    columnSelect.addEventListener("change", function () {

        const selectedIndex = this.value;

        // Masquer toutes les statistiques
        cards.forEach(card => {
            card.style.display = "none";
        });

        // Détruire le graphique précédent
        if (distributionChart) {
            distributionChart.destroy();
            distributionChart = null;
        }

        // Si aucune variable n'est sélectionnée
        if (selectedIndex === "") {

            columnsContainer.style.display = "none";

            return;
        }

        // Récupérer la carte correspondante
        const selectedCard = document.querySelector(
            `.column-card[data-index="${selectedIndex}"]`
        );

        if (!selectedCard) {
            columnsContainer.style.display = "none";
            return;
        }

        // Afficher le conteneur
        columnsContainer.style.display = "flex";

        // Afficher les statistiques
        selectedCard.style.display = "block";

        // Récupérer les informations
        const variableName = selectedCard
            .querySelector(".card-header h5")
            .textContent.trim();

        const variableType = selectedCard.dataset.type.toLowerCase();

        const distribution = JSON.parse(
            selectedCard.dataset.distribution
        );

        // Créer le graphique correspondant
        if (
            variableType.includes("int") ||
            variableType.includes("float")
        ) {

            createNumericChart(variableName, distribution);

        } else {

            createCategoricalChart(variableName, distribution);

        }

    });


    // =====================================
    // GRAPHIQUE NUMÉRIQUE
    // =====================================

    function createNumericChart(name, distribution) {

        const ctx = canvas.getContext("2d");

        distributionChart = new Chart(ctx, {

            type: "bar",

            data: {

                labels: distribution.labels,

                datasets: [{

                    label: "Effectif",

                    data: distribution.values,

                    backgroundColor: "rgba(13, 110, 253, 0.7)",

                    borderColor: "#0d6efd",

                    borderWidth: 1,

                    borderRadius: 4

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    title: {
                        display: true,
                        text: "Distribution de " + name
                    }

                },

                scales: {

                    x: {
                        title: {
                            display: true,
                            text: "Intervalles"
                        }
                    },

                    y: {
                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        },

                        title: {
                            display: true,
                            text: "Effectifs"
                        }
                    }

                }

            }

        });

    }


    // =====================================
    // GRAPHIQUE CATÉGORIEL
    // =====================================

    function createCategoricalChart(name, distribution) {

        const ctx = canvas.getContext("2d");

        const labels = distribution.map(item => item.value);

        const frequencies = distribution.map(
            item => item.frequency
        );

        const percentages = distribution.map(
            item => item.percentage
        );

        distributionChart = new Chart(ctx, {

            type: "bar",

            data: {

                labels: labels,

                datasets: [{

                    label: "Fréquence",

                    data: frequencies,

                    backgroundColor: "rgba(25, 135, 84, 0.7)",

                    borderColor: "#198754",

                    borderWidth: 1,

                    borderRadius: 5

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                indexAxis: "y",

                plugins: {

                    title: {
                        display: true,
                        text: "Distribution de " + name
                    },

                    tooltip: {

                        callbacks: {

                            label: function (context) {

                                const index = context.dataIndex;

                                return [
                                    "Effectif : " + frequencies[index],
                                    "Pourcentage : " + percentages[index] + "%"
                                ];

                            }

                        }

                    }

                },

                scales: {

                    x: {
                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        },

                        title: {
                            display: true,
                            text: "Effectifs"
                        }
                    },

                    y: {
                        title: {
                            display: true,
                            text: "Catégories"
                        }
                    }

                }

            }

        });

    }

});
