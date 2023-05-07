$(document).ready(function() {
    $("#loading").hide();
    $("#img").hide();
    $("#myTextarea").hide();
    $("#myTextareainput").hide();
    $("#input_btn").hide();
    $("#send_post_community").hide();
    $('body').on('submit','#upload-file',function(e){
               $("#loading").show();
               e.preventDefault()
               var formData = new FormData(this);
               $.ajax({
                     url:'/json/ocr/image/',
                     type: 'POST',
                     data: formData,
                     success: function (text) {
                        $("#loading").hide();
                        $("#myTextarea").show();
                        $("#myTextareainput").show();
                        $("#input_btn").show();
//                        $("#send_post_community").show();
                        $('#myTextarea').text(text);
                     },
                     error: function (response) {
                     },
                    cache: false,
                    contentType: false,
                    processData: false
               });
    });

    document.querySelector('#input_btn').onclick = function() {
        $("#loading").show();
        var data1  = $('#myTextarea').text();
        var input  = $('#myTextareainput').val();
        const data = new FormData();
        data.append("data", data1)
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