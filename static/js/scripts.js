$(document).ready(function()
{
	$(".parent_width").width( $(".parent_width").parent().width() );
	$(".parent_height").height( $(".parent_width").parent().height() );
	$(".fullheight").height($(window).height());
	$(".fullwidth").width($(window).width());
});

$(window).on('resize', function(){
	var win = $(this); //this = window
	$(".fullheight").height($(window).height());
	$(".fullwidth").width($(window).width());

	$(".parent_width").width( $(".parent_width").parent().width() );
	$(".parent_height").height( $(".parent_width").parent().height() );
});

/* ALERTS */
var alert_timer='';
function responsive_alert(message,alert_class,timeout){
	timeout = typeof timeout !== 'undefined' ? timeout : 8000;
	message = typeof message !== 'undefined' ? message : 'No message defined.';
	alert_class = typeof messaalert_classge !== 'undefined' ? mealert_classssage : 'alert-info';
	$( ".alert" ).remove();
	$( "#responsive_alert_background" ).remove();
	window.clearInterval(alert_timer);
	$( "body" ).append("<div id='responsive_alert_background' class='animated fadeInLeft fullwidth fullheight' style=' -webkit-animation-duration: 0.5s;position:absolute;top:0; left:0;width:100%;height:100%;background:rgba(255,255,255,0.8);z-index:80;'></div>");
	$( "body" ).append( "<div class='alert text-center "+alert_class+" center_horizontal center_vertical animated fadeInDown' role='alert' style='position:absolute;font-size:1.2em;z-index:100;'><p style='text-align:center;'>"+message+"</p><br/><div onclick='close_responsive_alert();' class='btn btn-info grow'><span class='glyphicon glyphicon-remove'></span></div></div>" );
	$(".alert").css("left", (($(window).width() - $(".center_horizontal").outerWidth()) / 2) + $(window).scrollLeft() + "px");
	$(".alert").css("top", (($(window).height() - $(".center_vertical").outerHeight()) / 2) + ($(window).scrollTop()) + "px");
	alert_timer=window.setInterval(close_responsive_alert, timeout);
}
function close_responsive_alert(){
	$( "#responsive_alert_background" ).addClass("animated fadeOut");
	$( "#responsive_alert_background" ).animate({
		opacity: 0,
		width: 0
		}, 400, function() {
			$( "#responsive_alert_background" ).remove();
	});

	$( ".alert" ).animate({
		opacity: 0,
		top: "-=60"
		}, 400, function() {
			$( ".alert" ).remove();
	});


	$( ".alert" ).addClass("animated fadeOutUp");
	
	window.clearInterval(alert_timer);
}


//* CENTER ELEMENT */
$(document).ready(function()
{
	centering();
});

$(window).on('resize', function()
{
	centering();
});
$(window).on('scroll', function()
{
	centering();
});

$(window).on("orientationchange",function(event){
	centering();
});

function centering(){
	$(".center_horizontal").css("left", (($(window).width() - $(".center_horizontal").outerWidth()) / 2) + $(window).scrollLeft() + "px");
	$(".center_vertical").css("top", (($(window).height() - $(".center_vertical").outerHeight()) / 2) + ($(window).scrollTop()) + "px");
}

function get_window_size(){
	if ($(window).width()<768){
		return('xs');
	} 
	else if ($(window).width()>=768 && $(window).width()<=970){
		return('sm');
	}
	else if ($(window).width()>=970 && $(window).width()<=1170){
		return('md');
	}
	else if ($(window).width()>1170){
		return('lg');
	}
}

$(document).ready(function()
{
  /* Bootstrap Tooltip Not Touch Device Only */
  if(!('ontouchstart' in window))
  {
    $(function () {
      $('[data-toggle="tooltip"]').tooltip({
        placement: 'auto'
      })
    })
  }
  /* Bootstrap Tooltip */

  /* datepicker */
  $('.datepicker').datepicker({
      format: 'dd-mm-yyyy',
      autoclose: true,
      todayHighlight: true,
      language: 'es',
      todayBtn: false,
      zIndexOffset: 200
  });

});

/* Disable enter key on table search input */
$(document).ready(function()
{
	// Disable enter key on table search
	$('.pull-right.search').on('keyup keypress', function(e) {
		var keyCode = e.keyCode || e.which;
		if (keyCode === 13) { 
			e.preventDefault();
			return false;
		}
	});
});

/* Compatibility Checks Modernizr */
$(document).ready(function()
{
  message = '';
  if (Modernizr.cookies == false) { message = 'Es necesario que actives las cookies en tu navegador para continuar.'; }
  if (Modernizr.svg == false) { message = 'Estás utilizando un navegador obsoleto, por favor actualiza tu navegador para un mejor funcionamiento.'; } 
  if (Modernizr.cssanimations == false) { message = 'Estás utilizando un navegador obsoleto, por favor actualiza tu navegador para un correcto funcionamiento.'; } 
  if (Modernizr.lastchild == false) { message = 'Estás utilizando un navegador obsoleto, por favor actualiza tu navegador para un correcto funcionamiento.'; } 
  if (Modernizr.rgba == false) { message = 'Estás utilizando un navegador obsoleto, por favor actualiza tu navegador para un correcto funcionamiento.'; } 
  if (Modernizr.svgasimg == false) { message = 'Estás utilizando un navegador obsoleto, por favor actualiza tu navegador para un correcto funcionamiento.'; } 
  if (Modernizr.inlinesvg == false) { message = 'Estás utilizando un navegador obsoleto, por favor actualiza tu navegador para un correcto funcionamiento.'; } 
  if (message){ $( "body" ).prepend( "<div class='alert alert-warning text-center' style='margin:0';><a href='https://www.google.com/chrome/'><p>" + message + "</p></a></div>" ); }
});


$(document).ready(function()
{
  $('.checkboxpicker').checkboxpicker({
    html: true,
    offLabel: '<span class="glyphicon glyphicon-remove">',
    onLabel: '<span class="glyphicon glyphicon-ok">'
  });
});


function validate_submit_crear_cliente(){
  var form = document.forms['crear-cliente']
  var elements = form.getElementsByTagName("input");
  for (i=0; i<elements.length; i++){
    $( elements[i] ).parent().removeClass( "has-error" );
    //$( elements[i] ).parent().addClass( "has-success" );
  }
  error = 0;
  if (form.rut.value === "")
  {
    $( form.rut ).parent().addClass( "has-error" );
    error = 1;
  }
  if (form.razon_social.value === "")
  {
    $( form.razon_social ).parent().addClass( "has-error" );
    error = 1;
  }
  if (form.telefono.value === "")
  {
    $( form.telefono ).parent().addClass( "has-error" );
    error = 1;
  }
  if (error){
    return False;
  }

  form.submit();
}
