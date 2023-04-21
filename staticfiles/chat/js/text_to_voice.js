




// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function() {
    $('#speak').hide();
    $('#stop').hide();
    $('#resume').hide();
    document.querySelector('#resume').onclick = function() {
        speechSynthesis.resume();
    }
    document.querySelector('#stop').onclick = function() {
        $('#resume').show();
        speechSynthesis.pause();
    }
    document.querySelector('#speak').onclick = function() {
                       $('#stop').show();
                     var content = $("#response").text()
                     var msg = new SpeechSynthesisUtterance(content);
                     var voices = window.speechSynthesis.getVoices();
                     msg.voice = voices[9];
                     msg.volume = 1; // From 0 to 1
                     msg.rate = 1; // From 0.1 to 10
                     msg.pitch = 1; // From 0 to 2
                     msg.lang = "en-US";
                     speechSynthesis.speak(msg);
    }

    document.querySelector('#voice_text_btn').onclick = function() {
         $("#loading").show();
         var text_voice = $("#voice_text").val();
         var page = "voice_to_text"
         var xhr = new XMLHttpRequest();
         xhr.open('GET', `/api/get_voice/?text=${text_voice}&page=${page}`, true);
         xhr.onreadystatechange = function() {
              if (this.readyState == 4 && this.status == 200) {
                    $("#loading").hide();
                    $('#speak').show()
                    var resp = this.responseText;
                    $("#response").html(resp)
              }
         };
         xhr.send();

    }
});