console.log('Hello!');

var endpoint = "https://2qvuuoe0j9.execute-api.us-west-2.amazonaws.com/prod/flatten_json";

$(document).ready(function() {
    $('#button1').click(function() {
        $('#button1').html('Processing...');
        $("#output").html("Processing...")
        var url = document.getElementById("url").value;
        var json_object = {"json_url": url};
        var package = JSON.stringify(json_object);
                
        var xhr = new XMLHttpRequest();
        var url = endpoint;
        xhr.open("POST", url, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                console.log(xhr.responseText);
                $("#output").html(xhr.responseText)
                $('#button1').html('Submit');
            }
        };
        xhr.send(package); 
    });
});

function readSingleFile(evt) {
    $("#output").html("Processing...")
    var f = evt.target.files[0]; 

    if (f) {
      var r = new FileReader();
      r.onload = function(e) { 
        var contents = e.target.result;
        try {
            json = JSON.parse(contents);
            package = JSON.stringify(json);
        }
        catch(err) {
            $("#output").html("Valid JSON data was not provided.");
        }
        var xhr = new XMLHttpRequest();
        var url = endpoint;
        xhr.open("POST", url, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                $("#output").html(xhr.responseText)
            }
        };
        xhr.send(package);

      }
      r.readAsText(f);
    } else { 
      alert("Failed to load file");
    }
  }

window.onload = function() {
    document.getElementById("fileinput").addEventListener('change', readSingleFile, false);
}

function myFunction(num) {
    base_url = "https://s3-us-west-1.amazonaws.com/datacoral-challenge/sample_files/"
    switch(num) {
        case 1:
            url = base_url + 'accounts.json'
            break;
        case 2:
            url = base_url + 'donuts.json'
            break;
        case 3:
            url = base_url + 'startups.json'
    }
    document.getElementById("url").value = url;
}