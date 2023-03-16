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