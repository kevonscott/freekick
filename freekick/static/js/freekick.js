window.onload = function(){
    document.getElementById("predictgame").addEventListener("click", predictGame);
    document.getElementById("predictmatchday").addEventListener("click", predictMatchDay);
}

function predictGame(){
    var homeTeam = document.getElementById("homeTeam").value
    var awayTeam = document.getElementById("awayTeam").value
    var league = document.getElementById("league").value
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
        "league": league
    }
    fetch('/api/match', {
        method: "POST",
        body: JSON.stringify(body),
        headers: { "Content-type": "application/json; charset=UTF-8"  }
    })
    .then(function (response) {
        return response.json();
    }).then(function (text) {
        console.log('GET response:');
        console.log(text);
        document.getElementById("result").innerText = JSON.stringify(text)
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
        console.log('GET response:');
        console.log(text);
        document.getElementById("result").innerText = JSON.stringify(text)
    });
}
