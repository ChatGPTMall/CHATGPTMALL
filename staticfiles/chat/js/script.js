$('#chat-form').on('submit', function(event){
    event.preventDefault();

    $.ajax({
        url : 'post/',
        type : 'POST',
        data : { 'msgbox' : $('#chat-msg').val() },

        success : function(json){
            $('#chat-msg').val('');
            $('#msg-list').append('<li class="text-right list-group-item">' + json.msg + '</li>');
            var chatlist = document.getElementById('msg-list-div');
            chatlist.scrollTop = chatlist.scrollHeight;
        }
    });
});




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
    $("#loading").hide();
    $('#send').attr('disabled','disabled');
    $('#chat-msg').keyup(function() {
        if($(this).val() != '') {
            $('#send').removeAttr('disabled');
        }
        else {
            $('#send').attr('disabled','disabled');
        }
    });

});

$(document).ready(function(){
            function captureUserMedia(mediaConstraints, successCallback, errorCallback) {
                navigator.mediaDevices.getUserMedia(mediaConstraints).then(successCallback).catch(errorCallback);
            }

            var mediaConstraints = {
                audio: true
            };

            document.querySelector('#start-recording').onclick = function() {
                this.disabled = true;
                captureUserMedia(mediaConstraints, onMediaSuccess, onMediaError);
            };

            document.querySelector('#stop-recording').onclick = function() {
                this.disabled = true;
                mediaRecorder.stop();
                mediaRecorder.stream.stop();

                while (audiosContainer.firstChild) {
                    audiosContainer.removeChild(audiosContainer.firstChild);
                }

                document.querySelector('#pause-recording').disabled = true;
                document.querySelector('#start-recording').disabled = false;
            };

            document.querySelector('#pause-recording').onclick = function() {
                this.disabled = true;
                mediaRecorder.pause();

                document.querySelector('#resume-recording').disabled = false;
            };

            document.querySelector('#resume-recording').onclick = function() {
                this.disabled = true;
                mediaRecorder.resume();

                document.querySelector('#pause-recording').disabled = false;
            };

//            {#document.querySelector('#save-recording').onclick = function() {#}
//            {#    this.disabled = true;#}
//            {#    mediaRecorder.save();#}
//            {##}
//            {#    // alert('Drop WebM file on Chrome or Firefox. Both can play entire file. VLC player or other players may not work.');#}
//            {#};#}

            var mediaRecorder;

            function onMediaSuccess(stream) {
                var audio = document.createElement('audio');

                audio = mergeProps(audio, {
                    controls: true,
                    muted: true
                });
                audio.srcObject = stream;
                audio.play();

                audiosContainer.appendChild(audio);
                audiosContainer.appendChild(document.createElement('hr'));

                mediaRecorder = new MediaStreamRecorder(stream);
                mediaRecorder.stream = stream;


                mediaRecorder.recorderType = StereoAudioRecorder;
                mediaRecorder.mimeType = 'audio/wav';


                // don't force any mimeType; use above "recorderType" instead.
                // mediaRecorder.mimeType = 'audio/webm'; // audio/ogg or audio/wav or audio/webm

                mediaRecorder.audioChannels = true;
                mediaRecorder.ondataavailable = function(blob) {
                    var a = document.createElement('a');
                    a.target = '_blank';
                    a.innerHTML = 'Open Recorded Audio No. ' + (index++) + ' (Size: ' + bytesToSize(blob.size) + ') Time Length: ' + getTimeLength(timeInterval);

                    a.href = URL.createObjectURL(blob);

//                    {#audiosContainer.appendChild(a);#}
//                    {#audiosContainer.appendChild(document.createElement('hr'));#}

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
                        $("#loading").show();
                        var csrftoken = getCookie('csrftoken');
                        var xhr = new XMLHttpRequest();
                        xhr.open('POST', '/upload_voice/', true);
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        xhr.setRequestHeader("MyCustomHeader", "Put anything you need in here, like an ID");
                        xhr.onreadystatechange = function() {
                           if (this.readyState == 4 && this.status == 200) {
                               $("#loading").hide();
                               var images = JSON.parse(this.responseText);
                               for(let i=0; i < images.length; i++){
                                $("#openai").append(`
                                    <div class="col-md-4">
                                        <div class="card" style="width: 18rem;">
                                             <img id="card-images" class="card-img-top" src="${images[i]}" >
                                        </div>
                                    </div>
                                `)
                               }
                           }
                        };
                        xhr.send(blob);
                };

                var timeInterval = 10000;
                if (timeInterval) timeInterval = parseInt(timeInterval);
                else timeInterval = 5 * 1000;

                // get blob after specific time interval
                mediaRecorder.start(timeInterval);

                document.querySelector('#stop-recording').disabled = false;
                document.querySelector('#pause-recording').disabled = false;
                document.querySelector('#save-recording').disabled = false;
            }

            function onMediaError(e) {
                console.error('media error', e);
            }

            var audiosContainer = document.getElementById('audios-container');
            var index = 1;

            // below function via: http://goo.gl/B3ae8c
            function bytesToSize(bytes) {
                var k = 1000;
                var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
                if (bytes === 0) return '0 Bytes';
                var i = parseInt(Math.floor(Math.log(bytes) / Math.log(k)), 10);
                return (bytes / Math.pow(k, i)).toPrecision(3) + ' ' + sizes[i];
            }

            // below function via: http://goo.gl/6QNDcI
            function getTimeLength(milliseconds) {
                var data = new Date(milliseconds);
                return data.getUTCHours() + " hours, " + data.getUTCMinutes() + " minutes and " + data.getUTCSeconds() + " second(s)";
            }

            window.onbeforeunload = function() {
                document.querySelector('#start-recording').disabled = false;
            };
});