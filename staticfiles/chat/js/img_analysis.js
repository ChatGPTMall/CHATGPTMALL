$(document).ready(function() {
    $("#loading").hide();
    $("#myTextarea").hide();
    $('body').on('submit','#upload-file',function(e){
               $("#loading").show();
               e.preventDefault()
               var formData = new FormData(this);
               $.ajax({
                     url:'/analysis/image/save/',
                     type: 'POST',
                     data: formData,
                     success: function (response) {
                        const data = JSON.stringify({
                            "url": response
                        });
                        const xhr = new XMLHttpRequest();
                        xhr.withCredentials = true;
                        xhr.addEventListener("readystatechange", function () {
                            if (this.readyState === this.DONE) {
                                $("#loading").hide();
                                $("#myTextarea").show();
                                var data = JSON.stringify(JSON.parse(this.responseText), undefined, 4);
                                $('#myTextarea').text(data);
                            }
                        });
                        xhr.open("POST", "https://microsoft-computer-vision3.p.rapidapi.com/describe?language=en&maxCandidates=1&descriptionExclude%5B0%5D=Celebrities");
                        xhr.setRequestHeader("content-type", "application/json");
                        xhr.setRequestHeader("X-RapidAPI-Key", "3ec1eef879msh365ea5d96552e49p15a7e9jsn95f1d7c21fd9");
                        xhr.setRequestHeader("X-RapidAPI-Host", "microsoft-computer-vision3.p.rapidapi.com");

                        xhr.send(data);
                     },
                     error: function (response) {
                     },
                    cache: false,
                    contentType: false,
                    processData: false
               });
    });
});