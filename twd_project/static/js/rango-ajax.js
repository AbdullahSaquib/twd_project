$('#likes').click( function() {
  $('#like_counts').html('Updating...');
  var catid;
  catid = $(this).attr('data-catid');
  $.get('/rango/like_category/', {category_id : catid}, function(data){
    $('#like_counts').html(data);
    $('#likes').hide();
  });
});
