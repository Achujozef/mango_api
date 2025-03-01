$(document).ready(function(){
    $(".down-menu").hover(function () { 
   
      
      $(".dropdown").toggle();
    });
    $(".down-menu1").click(function () { 
   
      
      $(".dropdown1").slideToggle();
    });
    $("#stainlesss").hover(function () { 
   
      
      $("#desc1").slideToggle();
    });
    $("#Wildforest-img").hover(function () { 
   
      
      $("#Wildforest").slideToggle();
    });
    $("#Multifloral-img").hover(function () { 
   
      
      $("#Multifloral").slideToggle();
    });
  });
  $(document).ready(function() {
    $(".fa-bars").click(function(e) {
        $(".mobile-nav").slideToggle(); // Show/hide the mobile-nav menu
    });
    $('#lightSlider').lightSlider({
      gallery: true,
      item: 1,
      loop: true,
      slideMargin: 0,
      thumbItem: 3
  });
});
$(document).ready(function(){
  $(".fa-eye-slash").click(function(){
    var passwordField = $(this).closest(".input-group").find("input[type='password']");
    passwordField.attr("type", "text");
    $(this).hide();
    $(this).siblings(".fa-eye").show();
    $(this).addClass("form-control:focus");
  });
  
  $(".fa-eye").click(function(){
    var passwordField = $(this).closest(".input-group").find("input[type='text']");
    passwordField.attr("type", "password");
    $(this).hide();
    $(this).siblings(".fa-eye-slash").show();
  });
});
$(document).ready(function(){
  $(".box").hover(function(){
      $(this).find(".product-wrapper.backward").show().css({
          "position": "absolute",
          "top": "-px"
      });
      $(this).find(".product-img img").addClass("filter");
      $(this).find(".fa-trash").show();
  });
  $(".box").mouseleave(function(){
    $(this).find(".product-wrapper.backward").show().css({
        "position": "absolute",
        "top": "-px"
    });
    $(this).find(".product-img img").remove("filter");
    $(this).find(".fa-trash").hide();
});
$(".fa-trash").click(function(){
  $(this).closest(".box").remove();
});
$(".qtybtn").click(function(){
  var $row = $(this).closest("tr"); 
  var proprice = parseFloat($row.find(".pro-price span").text().replace("₹", ""));
  var proqty = parseFloat($row.find(".pro-quantity input").val());
  var prosubtotal = proprice * proqty;
  $row.find(".pro-subtotal span").html("₹" + prosubtotal.toFixed(2)); 
  
  $(this).closest('tr').find('.pro-subtotal span').text('₹' + subtotal.toFixed(2));
});

$(".fa-trash-o").click(function(){
  $(this).closest('tr').remove();
});

function updateTotal() {
  var total = 0;
  $(".money").each(function() {
    var currency = $(this).data("currency");
    var amountText = $(this).data("currency-" + currency);
    var amount = parseFloat(amountText.replace("₹", ""));
    total += amount;
  });
  $("#total").text("₹ " + total.toFixed(2));
}

// Call updateTotal initially to calculate total amount
updateTotal();

});

$(document).ready(function() {
  var count = 0;
  var limit = 100; // Set your desired limit here

  // Function to update the count
  function updateCount() {
      if (count < limit) {
          count++;
          $('.count').text(count + '%');
      } else {
          clearInterval(interval); // Stop the interval when the limit is reached
      }
  }

  // Call updateCount() every second
  var interval = setInterval(updateCount, 20); // 1000 milliseconds = 1 second
});

$(document).ready(function() {
  var count = 0;
  var limit = 100; // Set your desired limit here

  // Function to update the count
  function updateCount() {
      if (count < limit) {
          count++;
          $('.count1').text(count + '%');
      } else {
          clearInterval(interval); // Stop the interval when the limit is reached
      }
  }

  // Call updateCount() every second
  var interval = setInterval(updateCount, 20); // 1000 milliseconds = 1 second
});

$(document).ready(function() {
  var count = 100;
  var limit = 0; // Set your desired limit here

  // Function to update the count
  function updateCount() {
      if (count > limit) {
          count--;
          $('.count2').text(count + '%');
      } else {
          clearInterval(interval); // Stop the interval when the limit is reached
      }
  }

  // Call updateCount() every second
  var interval = setInterval(updateCount, 20); // 1000 milliseconds = 1 second
});

$(document).ready(function() {
  var count = 0;
  var limit = 100; // Set your desired limit here

  // Function to update the count
  function updateCount() {
      if (count < limit) {
          count++;
          $('.count3').text(count + '%');
      } else {
          clearInterval(interval); // Stop the interval when the limit is reached
      }
  }

  // Call updateCount() every second
  var interval = setInterval(updateCount, 20); // 1000 milliseconds = 1 second
});