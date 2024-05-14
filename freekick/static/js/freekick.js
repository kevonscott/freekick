window.onload = function(){
    document.getElementById("predictgame").addEventListener("click", predictGame);
    document.getElementById("predictmatchday").addEventListener("click", predictMatchDay);
}

function predictGame(){
    var homeTeam = document.getElementById("homeTeam").value
    var awayTeam = document.getElementById("awayTeam").value
    var league = document.getElementById("league").value
    var attendance = document.getElementById("attendance").value
    console.log(homeTeam, awayTeam)
    if (homeTeam == "null"){
        alert("Home team required!")
        return;
    }
    if (awayTeam == "null"){
        alert("Away team required!")
        return;
    }
    var body = {
        "home": homeTeam,
        "away": awayTeam,
        "league": league,
        "attendance": attendance
    }
    fetch('/api/match', {
        method: "POST",
        body: JSON.stringify(body),
        headers: { "Content-type": "application/json; charset=UTF-8"  }
    })
    .then(function (response) {
        return response.json();
    }).then(function (text) {
        displayTable(text);
    });
}

function predictMatchDay(){
    var league = document.getElementById("league").value
    var body = {
        "league": league
    }
    fetch('/api/matchday',{
        method: "POST",
        body: JSON.stringify(body),
        headers: { "Content-type": "application/json; charset=UTF-8"  }
    })
    .then(function (response) {
        return response.json();
    }).then(function (text) {
        displayTable(text);
    });
}

function displayTable(jsonObj){
    // Create table header
    console.log('object received', jsonObj)
    let tableHead = ['Home Team', 'Away Team', 'Predicted Winner'];

    // Dynamically create a table
    let table = document.createElement("table");
    let att = document.createAttribute("class");
    att.value = "styled-table";
    table.setAttributeNode(att);

    let tr = table.insertRow(-1); // Append to end of row

    // Create table header
    for (let i = 0; i < tableHead.length; i++) {
        let th = document.createElement("th");
        th.innerHTML = tableHead[i];
        tr.appendChild(th);
    }

    // Append json data to table rows
    for (let i = 0; i < jsonObj.length; i++) {
        let tr = table.insertRow(-1);
        for (let j = 0; j < tableHead.length; j++) {
            let cell = tr.insertCell(-1);
            cell.innerHTML = jsonObj[i][tableHead[j].toLowerCase().replace(' ', '_')];
        }
    }

    // Add table to page
    let resultObject = document.getElementById("result");
    resultObject.innerHTML = "";
    resultObject.appendChild(table);
}

function dynamicTeamDropdown(league){
    document.getElementById("homeTeam").options.length = 0;
    document.getElementById("awayTeam").options.length = 0;

    switch(league){
        case "epl":
            teamNames =  ["", "Everton", "Tottenham Hotspur", "Liverpool", "Arsenal", "Aston Villa", "Chelsea", "Crystal Palace", "Leicester City", "Leeds United", "Manchester City", "Manchester United", "Newcastle United", "Norwich", "Southampton", "Watford", "West Brom", "West Ham"];
            teamCodes = ["null", "EVE", "TOT", "LIV", "ARS", "AVL", "CHE", "CRY", "LEI", "LEE", "MCI", "MUN", "NEW", "NOR", "SOU", "WAT", "WBA", "WHU"];

            for (let i = 0; i < teamNames.length; i++){
                document.getElementById("homeTeam").options[i] = new Option(teamNames[i], teamCodes[i])
                document.getElementById("awayTeam").options[i] = new Option(teamNames[i], teamCodes[i])
            }
            break;
        case "bundesliga":
            alert("NOTIMPLEMENTEDRROR");
            break;
            teamNames =  ["", "Bayern Munich", "Arminia Bielefeld", "Borussia Dortmund"];
            teamCodes = ["null", "BAY", "BIE", "DOR"];

            for (let i = 0; i < teamNames.length; i++){
                document.getElementById("homeTeam").options[i] = new Option(teamNames[i], teamCodes[i])
                document.getElementById("awayTeam").options[i] = new Option(teamNames[i], teamCodes[i])
            }
            break;
    }
}
