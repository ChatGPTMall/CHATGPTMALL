$(document).ready(function() {
    $("#loading").hide();
    $("#img").hide();
    $("#myTextarea").hide();
    $("#send_post_community").hide();
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
                        $("#send_post_community").show();
                        $("#img").show();
                        console.log(response)
                        var url = response.url
                        var url2 = response.url2
                        $("#image_input").val(url2)
                        $("#image_response").val(url)
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