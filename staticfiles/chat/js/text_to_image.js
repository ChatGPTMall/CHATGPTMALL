$(document).ready(function() {
$("#loading").hide();
    document.querySelector('#text_to_text_btn').onclick = function() {
        var text_to_text = $("#text_to_text_input").val();
        $("#loading").show();
        if(text_to_text == ""){
            alert("Please Enter Something");
        }else{
         var xhr = new XMLHttpRequest();
         xhr.open('GET', `/upload_voice/?text=${text_to_text}`, true);
         xhr.onreadystatechange = function() {
              if (this.readyState == 4 && this.status == 200) {
                    $("#loading").hide();
                    var images = JSON.parse(this.responseText);
                    for(let i=0; i < images.length; i++){
                                $("#images_row").append(`
                                    <div class="col-md-4">
                                        <div class="card" style="width: 18rem;">
                                            <a href="${images[i]}" class="download_images" download>Download</a>
                                             <img id="card-images" class="card-img-top" src="${images[i]}" >
                                        </div>
                                    </div>
                                `)
                               }
              }
         };
         xhr.send();

        }
    }
});