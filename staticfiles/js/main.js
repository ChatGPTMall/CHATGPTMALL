$(document).ready(function(){
  $('#loading').fadeOut(2000,function(){
    $('body').css('overflow','visible')
  });
   var api_value = $("#api_key").text();
   if(api_value == ""){
        $("#api_key").hide();
        $("#delete_token").hide();
   }
   $("#generate_new_key").on("click", (e)=>{
      $.ajax({
        type: "GET",
        url: `/create/api_key/`,
        success: function (data) {
          $("#api_key").show();
          $("#delete_token").show();
          $("#api_key").text(data)
        },
      });
   });

   $('#google_translate_element').bind('DOMNodeInserted', function(event) {
      $('.goog-te-menu-value span:first').html('LANGUAGE');
      $('.goog-te-menu-frame.skiptranslate').load(function(){
        setTimeout(function(){
          $('.goog-te-menu-frame.skiptranslate').contents().find('.goog-te-menu2-item-selected .text').html('LANGUAGE');
        }, 100);
      });
    });

   $("#delete_token").on("click", (e)=>{
      $.ajax({
        type: "GET",
        url: `/delete_key/`,
        success: function (data) {
          $("#api_key").hide();
          $("#delete_token").hide();
          $("#api_key").text("")
        },
      });
   });
   $("#show_ai").hide();
   $("#loader").hide();
   $('#inputEmail4').keypress(function() {
        var dInput = this.value;
        $("#show_ai").show();

//        $("#show_ai").attr("href", `/api/text_to_text/?item=How to use ${dInput}`)

   })
   $("#show_ai").on("click", (e)=>{
        $("#loader").show();
        $("#inputAddress").hide();
        var item_value = $('#inputEmail4').val();
        $.ajax({
                type: "GET",
                url: `/api/get_text/?text=How to use ${item_value}`,
                success: function (data) {
                    $("#loader").hide();
                    $("#inputAddress").show();
                    $("#inputAddress").text(data);
                }
            });
   });

    $("#redeem_button").on("click", (e)=>{
        var price = $("#total_price").val();
        console.log(price, typeof(price))
        var coupon_code = $("#coupon_code").val()
        if(coupon_code == ""){
            alert("Please enter valid coupon code")
        }else{
            $.ajax({
                type: "GET",
                url: `/validate/coupon_code/coupon_code=${coupon_code}/`,
                success: function (data) {
                    if(data[0] == "invalid"){
                        alert("invalid coupon code or expired")
                    }else{
                       var discount = data[1]
                       var p = parseInt(price);
                       if(discount > p){
                        alert("invalid coupon code or expired")
                       }else{
                            $("#coupon_price").text(discount);
                            $("#total_price").val(p-discount);
                            $("#cp").text(coupon_code);
                            $("#price").text("$"+(p-discount));
                            $("#show_coupon").show();
                       }
                    }
                },
            });
        }
    });

$(function () {
  $('[data-toggle="tooltip"]').tooltip({
    trigger: 'click'
  })
})

});


$('.loop').owlCarousel({
  center: true,
  items:1,
  loop:true,
  margin:10,
  responsive:{
      600:{
          items:1
      }
  }
});

$('.owl-theme').owlCarousel({
  loop:false,
  margin:10,
  nav:true,
  responsive:{
      0:{
          items:1
      },
      600:{
          items:3
      },
      1000:{
          items:3
      }
  }
})

//function get_data(url){
//  console.log(url)
//  document.getElementById(`${url}`).select();
//  document.execCommand("copy");
//}




  $(document).ready(function(){

  });

