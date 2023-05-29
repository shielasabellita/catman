/**
 * Created by shiela on 8/24/20.
 */
frappe.provide('erpnext');


$(document).ready(function() {
    $('.layout-side-section').hide();
});

$(document).keydown(function(response) {
  if(response.key === "m" && response.ctrlKey === true && $('div.layout-side-section').is(':hidden')){
       $('.layout-side-section').show();
       $('.col-md-10').css("width", "80.33333%");
  }
  else if(response.key === "m" && response.ctrlKey === true && $('div.layout-side-section').is(':visible')){
       $('.layout-side-section').hide();
       $('.col-md-10').css("width", "100%");
  }
});

//Highlighting an Entire Row.
var cur_focused ;
$(window).click(function(){
   if(cur_focused == undefined){
      cur_focused = $(".dt-cell--focus").parent().children();
      cur_focused.css({"background-color":"#aec6cf"});
   }else{
      cur_focused.css({"background-color":"white"});
      cur_focused = $(".dt-cell--focus").parent().children();
       cur_focused.css({"background-color":"#aec6cf"});
   }
});


// add toolbar icon
$(document).bind('toolbar_setup', function(){
	var title = $('span.avatar').attr('title');
	$('span.ellipsis.toolbar-user-fullname.hidden-xs.hidden-sm').text(title)
});


