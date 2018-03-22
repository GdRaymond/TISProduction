$(function(){
    alert('begin orders.js');
    $.get(
        '/product/get_list_ajax/',
        function(data,status){
            $('#id_product').html(data);
        }
    );
});