$(document).ready(function(){

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

