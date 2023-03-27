window.onload = function () {
    connect_cloud();
    document.getElementById("json").value = JSON.stringify(token_json);
};

function connect_cloud() {
    display_content("state_connecting");

    var host = document.getElementById("host").value;
    if (host == "") host = "http://localhost:12345/";

    var url = host + (host.endsWith("/") ? "" : "/") + "connect_cloud";
    postJsonAndParseJson(
        url,
        token_json, 
        function (json_response) {
            if (json_response.error) {
                console.error(json_response);
                display_content("state_connect_failed");
            } else {
                display_content("state_connected");
            }
        },
        function (failed_request) {
            display_content("state_request_failed");
        }
    );
}

function display_content(id) {
    var contents = document.querySelectorAll(".content");
    for (var c of contents) c.classList.add("hidden");
    document.getElementById(id).classList.remove("hidden");
}

function postJsonAndParseJson(url, data, callback, error_callback) {
    var cb = function (responseText) { callback(JSON.parse(responseText)); };
    var ecb = function (x) { error_callback(x); };

    var x = new XMLHttpRequest();
    x.open("POST", url, true);
    x.onreadystatechange = function () {
        if (x.readyState == XMLHttpRequest.DONE) {
            if (x.status == 200)
                cb(x.responseText);
            else
                ecb(x);
        }
    };
    x.setRequestHeader('Content-Type', 'application/json');
    x.send(JSON.stringify(data));
}
