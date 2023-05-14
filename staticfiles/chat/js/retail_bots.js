$(document).ready(function() {
    var videoStream;
    $("#loading").hide();
    $("#camera_div").hide();
    $("#key_board_div").hide();
    $("#ocr").hide();
    $("#analysis").hide();
    $("#input_text_area").hide();
    $("#input_btn").hide();


    function start_video(){
                // Get access to the camera and display the video stream
            navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                var videoElement = document.getElementById('video');
                videoElement.srcObject = stream;
                videoStream = stream;
            })
            .catch(function(error) {
                console.error('Error accessing the camera:', error);
            });
        }

    document.getElementById('open_camera').addEventListener('click', function() {
        $("#camera_div").show();
        $("#key_board_div").hide();
        console.log("hello")
        start_video();
    });
    document.getElementById('open_keyboard').addEventListener('click', function() {
        $("#camera_div").hide();
        $("#key_board_div").show();
    });
    document.getElementById('open_microphone').addEventListener('click', function() {
        $("#record").show();
    });

    // Capture the photo and send it to the server
    document.getElementById('capture_photo').addEventListener('click', function() {
            $("#loading").show();
            var videoElement = document.getElementById('video');
            var canvas = document.createElement('canvas');
            canvas.width = videoElement.videoWidth;
            canvas.height = videoElement.videoHeight;
            canvas.getContext('2d').drawImage(videoElement, 0, 0, canvas.width, canvas.height);
            var photoData = canvas.toDataURL('image/jpeg');
            // Send the photo data to the server using AJAX
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/capture/save_photo/', true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                        $("#input_text_area").show();
                        $("#input_btn").show();
                        var url = this.responseText;
//                      OCR
                       var xhr3 = new XMLHttpRequest();
                        xhr3.open('POST', '/analysis/ocr/image/', true);
                        xhr3.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                        xhr3.onreadystatechange = function() {
                            if (xhr3.readyState === 4 && xhr3.status === 200) {
                                $("#loading").hide();
                                $("#ocr").show();
                                $('#ocr').text(this.responseText);
                            }
                        }
                        xhr3.send('image_data=' + encodeURIComponent(photoData));
//                      analysis
                        const data = JSON.stringify({
                            "url": url
                        });
                        const xhr2 = new XMLHttpRequest();
                        xhr2.withCredentials = true;
                        xhr2.addEventListener("readystatechange", function () {
                            if (this.readyState === this.DONE) {
                                $("#analysis").show();
                                var data = JSON.stringify(JSON.parse(this.responseText), undefined, 4);
                                $('#analysis').text(data)
                            }
                        });
                        xhr2.open("POST", "https://microsoft-computer-vision3.p.rapidapi.com/describe?language=en&maxCandidates=1&descriptionExclude%5B0%5D=Celebrities");
                        xhr2.setRequestHeader("content-type", "application/json");
                        xhr2.setRequestHeader("X-RapidAPI-Key", "3ec1eef879msh365ea5d96552e49p15a7e9jsn95f1d7c21fd9");
                        xhr2.setRequestHeader("X-RapidAPI-Host", "microsoft-computer-vision3.p.rapidapi.com");

                        xhr2.send(data);
                       window.scrollTo(0, 900);
                }
            };
            xhr.send('photo=' + encodeURIComponent(photoData));
        });


    document.querySelector('#input_btn').onclick = function() {
        $("#loading").show();
        var input  = $('#input_text_area').val();
        const data = new FormData();
        data.append("input", input)
        if(input == ""){
            alert("please enter something")
        }else{
            $.ajax({
                     url:`/ocr/content/generate/`,
                     type: 'POST',
                     data: data,
                     success: function (text) {
                        $("#loading").hide();
                        $("#send_post_community").show();
                        $('#speak').show();
                        $('#stop').show();
                        $('#resume').show();
                        $('#result').text(text);
                     },
                     error: function (response) {
                     },
                    cache: false,
                    contentType: false,
                    processData: false
               });
        }
    }

    document.querySelector('#input_btn_keyboard').onclick = function() {
        $("#loading").show();
        var input  = $('#keyboard_input').val();
        const data = new FormData();
        data.append("input", input)
        if(input == ""){
            alert("please enter something")
        }else{
            $.ajax({
                     url:`/ocr/content/generate/`,
                     type: 'POST',
                     data: data,
                     success: function (text) {
                        $("#loading").hide();
                        $("#send_post_community").show();
                        $('#speak').show();
                        $('#stop').show();
                        $('#resume').show();
                        $('#result').text(text);
                     },
                     error: function (response) {
                     },
                    cache: false,
                    contentType: false,
                    processData: false
               });
        }
    }
});