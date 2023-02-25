$(document).ready(function(){
  $('#loading').fadeOut(2000,function(){
    $('body').css('overflow','visible')
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