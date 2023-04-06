$(document).ready(function() {
    $("#loading").hide();
    $("#img").hide();
    $("#myTextarea").hide();
    $('body').on('submit','#upload-file',function(e){
               $("#loading").show();
               e.preventDefault()
               var formData = new FormData(this);
               $.ajax({
                     url:'/objects/detect/',
                     type: 'POST',
                     data: formData,
                     success: function (response) {
                        $("#loading").hide();
                        $("#myTextarea").show();
                        $("#img").show();
                        var url = response.url
                        console.log(url)
                        document.getElementById('img').src = url
                        var str = JSON.stringify(response)
                        var data = JSON.stringify(JSON.parse(str), undefined, 4);
                        $('#myTextarea').text(data);
                     },
                     error: function (response) {
                     },
                    cache: false,
                    contentType: false,
                    processData: false
               });
    });
});