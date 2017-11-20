$(document).ready(function(){
    let click = false;
    var $root = $('html, body');
    $('#stickyContents li').on('click','a', function(e){ 
       e.preventDefault();
       let href = $.attr(this, 'href');
       $root.animate({
           scrollTop: $(href).offset().top
       }, 600)
       return false;
    });
    
    
    $('.abstract-toggle').click(function(){
        $(this).parent().children('.paper-abstract').toggle("display")
    });
})
