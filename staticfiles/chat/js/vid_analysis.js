$(document).ready(function() {
    $("#loading").hide();
    $("#myTextarea").hide();
    $('body').on('submit','#upload-file',function(e){
               $("#loading").show();
               e.preventDefault()
               var formData = new FormData(this);
               $.ajax({
                     url:'/analysis/video/',
                     type: 'POST',
                     data: formData,
                     success: function (response) {

                     },
                     error: function (response) {
                     },
                    cache: false,
                    contentType: false,
                    processData: false
               });
    });
});