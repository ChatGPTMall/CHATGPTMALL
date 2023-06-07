/**
* Template Name: Logis
* Updated: Mar 10 2023 with Bootstrap v5.2.3
* Template URL: https://bootstrapmade.com/logis-bootstrap-logistics-website-template/
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/
document.addEventListener('DOMContentLoaded', () => {
  "use strict";

  /**
   * Preloader
   */
  const preloader = document.querySelector('#preloader');
  if (preloader) {
    window.addEventListener('load', () => {
      preloader.remove();
    });
  }

  /**
   * Sticky header on scroll
   */
  const selectHeader = document.querySelector('#header');
  if (selectHeader) {
    document.addEventListener('scroll', () => {
      window.scrollY > 100 ? selectHeader.classList.add('sticked') : selectHeader.classList.remove('sticked');
    });
  }

  /**
   * Scroll top button
   */
  const scrollTop = document.querySelector('.scroll-top');
  if (scrollTop) {
    const togglescrollTop = function() {
      window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
    }
    window.addEventListener('load', togglescrollTop);
    document.addEventListener('scroll', togglescrollTop);
    scrollTop.addEventListener('click', window.scrollTo({
      top: 0,
      behavior: 'smooth'
    }));
  }

  /**
   * Mobile nav toggle
   */
  const mobileNavShow = document.querySelector('.mobile-nav-show');
  const mobileNavHide = document.querySelector('.mobile-nav-hide');

  document.querySelectorAll('.mobile-nav-toggle').forEach(el => {
    el.addEventListener('click', function(event) {
      event.preventDefault();
      mobileNavToogle();
    })
  });

  function mobileNavToogle() {
    document.querySelector('body').classList.toggle('mobile-nav-active');
    mobileNavShow.classList.toggle('d-none');
    mobileNavHide.classList.toggle('d-none');
  }

  /**
   * Hide mobile nav on same-page/hash links
   */
  document.querySelectorAll('#navbar a').forEach(navbarlink => {

    if (!navbarlink.hash) return;

    let section = document.querySelector(navbarlink.hash);
    if (!section) return;

    navbarlink.addEventListener('click', () => {
      if (document.querySelector('.mobile-nav-active')) {
        mobileNavToogle();
      }
    });

  });

  /**
   * Toggle mobile nav dropdowns
   */
  const navDropdowns = document.querySelectorAll('.navbar .dropdown > a');

  navDropdowns.forEach(el => {
    el.addEventListener('click', function(event) {
      if (document.querySelector('.mobile-nav-active')) {
        event.preventDefault();
        this.classList.toggle('active');
        this.nextElementSibling.classList.toggle('dropdown-active');

        let dropDownIndicator = this.querySelector('.dropdown-indicator');
        dropDownIndicator.classList.toggle('bi-chevron-up');
        dropDownIndicator.classList.toggle('bi-chevron-down');
      }
    })
  });

  /**
   * Initiate pURE cOUNTER
   */
  new PureCounter();

  /**
   * Initiate glightbox
   */
  const glightbox = GLightbox({
    selector: '.glightbox'
  });

  /**
   * Init swiper slider with 1 slide at once in desktop view
   */
  new Swiper('.slides-1', {
    speed: 600,
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false
    },
    slidesPerView: 'auto',
    pagination: {
      el: '.swiper-pagination',
      type: 'bullets',
      clickable: true
    },
    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    }
  });

  /**
   * Animation on scroll function and init
   */
  function aos_init() {
    AOS.init({
      duration: 1000,
      easing: 'ease-in-out',
      once: true,
      mirror: false
    });
  }
  window.addEventListener('load', () => {
    aos_init();
  });

});

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
   $("#formFileurl").hide();
   $("#show_ai_image").hide();
   $("#div_img_query").hide();
   $("#div_query").hide();
   $("#loader").hide();
   $("#img_loader").hide();
   $('#inputEmail4').keypress(function() {
        var dInput = this.value;
        $("#show_ai").show();
        $("#show_ai_image").show();
   })


   $("#show_ai").on("click", (e)=>{
        $("#inputAddress").hide();
        $("#show_ai").hide();
        $("#div_query").show();
   });
   $("#btn_query").on("click", (e)=>{
        $("#div_query").hide();
        $("#loader").show();
        var item_value = $('#query').val();
        $.ajax({
                type: "GET",
                url: `/api/get_text/?text=${item_value}`,
                success: function (data) {
                    $("#loader").hide();
                    $("#inputAddress").show();
                    $("#inputAddress").text(data);
                    $("#query_label").text(item_value);
                }
            });
   });

   $("#div_img_query").hide();
   $("#show_ai_image").on("click", (e)=>{
        $("#formFile").hide();
        $("#show_ai_image").hide();
        $("#div_img_query").show();
   });
   $("#img_btn_query").on("click", (e)=>{
        $("#div_img_query").hide();
        $("#img_loader").show();
        var item_value = $('#img_query').val();
        $.ajax({
                type: "GET",
                url: `/api/get_image/?text=${item_value}`,
                success: function (data) {
                console.log(data)
                    $("#img_loader").hide();
                    $("#formFile").hide();
                    $("#formFileurl").show();
                    $("#formFileurl").val(data);
                    $("#img_label").text(item_value);
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


function get_data(text){
  // Create a temporary textarea element
  const textarea = document.createElement('textarea');
  textarea.value = text;

  // Make the textarea invisible
  textarea.style.position = 'fixed';
  textarea.style.top = 0;
  textarea.style.left = 0;
  textarea.style.width = '1px';
  textarea.style.height = '1px';
  textarea.style.opacity = 0;

  // Append the textarea to the document
  document.body.appendChild(textarea);

  // Select the text in the textarea
  textarea.select();

  // Copy the selected text to the clipboard
  document.execCommand('copy');

  // Remove the textarea from the document
  document.body.removeChild(textarea);
}