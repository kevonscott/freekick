document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("settings-form");
    const defaultLeague = document.getElementById("default_league");
    const defaultModel = document.getElementById("default_model");
    const workspace = document.getElementById("workspace");

    try {
        const response = await fetch('/api/settings/setting');
        const data = await response.json();

        defaultLeague.value = data.default_league;
        workspace.value = data.workspace;
        models = data.models;

        populateModels(data.default_league, data.default_model, models);

        defaultLeague.addEventListener("change", () => {
            populateModels(defaultLeague.value, data.default_model, models);
        });

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const updatedSettings = {
                default_league: defaultLeague.value,
                default_model: defaultModel.value,
                workspace: workspace.value
            };

            await fetch('/api/settings/setting', {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(updatedSettings)
            });

            alert("Settings saved successfully!");
        });

    } catch (error) {
        console.error("Error fetching settings:", error);
    }
});

function populateModels(league, default_model, models) {
    console.log(models);
    const defaultModel = document.getElementById("default_model");
    defaultModel.innerHTML = "";
    models.forEach(model => {
        const option = document.createElement("option");
        option.value = model;
        option.textContent = model;
        defaultModel.appendChild(option);
    });
}