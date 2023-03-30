$(document).ready(function() {
    var post_text;
    var post_images;
    $("#loading").hide();
    $("#send_post_community").hide();
    document.querySelector('#send_post_community').onclick = function() {
        var xhr = new XMLHttpRequest();
         xhr.open('GET', `/send/post/community/?question=${post_text}&images=${post_images}`, true);
         xhr.onreadystatechange = function() {
              if (this.readyState == 4 && this.status == 200) {
                var resp = this.responseText;
                alert(resp);
              }
         };
         xhr.send();
    }
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
                    $("#send_post_community").show();
                    var images = JSON.parse(this.responseText);
                    post_text = text_to_text
                    post_images = images
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