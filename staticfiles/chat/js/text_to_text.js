$(document).ready(function() {
    document.querySelector('#text_to_text_btn').onclick = function() {
        var text_to_text = $("#text_to_text_input").val();
        var no_of_words = $("#no_of_words").val();
        if(no_of_words == ""){
            no_of_words = 50
        }
        if(text_to_text == ""){
            alert("Please Enter Something");
        }else{
         var xhr = new XMLHttpRequest();
         xhr.open('GET', `/api/get_voice/?text=${text_to_text}&words=${no_of_words}`, true);
         xhr.onreadystatechange = function() {
              if (this.readyState == 4 && this.status == 200) {
                    var resp = this.responseText;
                    $("#text_to_text_show").html(resp)
              }
         };
         xhr.send();

        }
    }
});