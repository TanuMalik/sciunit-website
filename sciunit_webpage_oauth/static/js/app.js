$(document).ready(function(){
    var $root = $('html, body');
    $('#stickyContents li').on('click','a', function(e){ 
       e.preventDefault();
       let href = $.attr(this, 'href');
       $root.animate({
           scrollTop: $(href).offset().top
       }, 500)
       return false;
    });
    
    
    $('.abstract-toggle').click(function(){
        console.log('toggle');
        $(this).parent().children('.paper-abstract').toggle("display")
    })
})
