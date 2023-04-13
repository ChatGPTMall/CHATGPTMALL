$(document).ready(function() {
    $("#post").hide();
    document.querySelector('#text_to_text_btn').onclick = function() {
        var text_to_text = $("#text_to_text_input").val();
        var no_of_words = $("#no_of_words").val();
        if(no_of_words == ""){
            no_of_words = 2000
        }
        if(text_to_text == ""){
            alert("Please Enter Something");
        }else{
         var xhr = new XMLHttpRequest();
         xhr.open('GET', `/api/get_voice/?text=${text_to_text}&words=${no_of_words}`, true);
         xhr.onreadystatechange = function() {
              if (this.readyState == 4 && this.status == 200) {
                    var resp = this.responseText;
                    $("#text_to_text_show").text(resp)
                    $("#post").show();
              }
         };
         xhr.send();

        }
    }
    document.querySelector('#post').onclick = function() {
        var question = $("#text_to_text_input").val();
        var response = $("#text_to_text_show").text();
        $("#input").val(question)
        $("#response").val(response)
//        var xhr = new XMLHttpRequest();
//         xhr.open('GET', `/send/post/community/?question=${question}&response=${response}`, true);
//         xhr.onreadystatechange = function() {
//              if (this.readyState == 4 && this.status == 200) {
//                var resp = this.responseText;
//                alert(resp);
//              }
//         };
//         xhr.send();
    }
});