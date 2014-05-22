sendMessage = function( message) {
  $.ajax({
    type: "POST",
    url: '/message',
    data: {uid: user_id, message: message},
  });
};

onMessage = function(m) {
  newMessage = JSON.parse(m.data);
  console.log(newMessage);
  $('#chat .list-group').append(newMessage.message)
}

socket = channel.open();
socket.onmessage = onMessage;

jQuery('#submit').click(function() {
  var val = $('#chattext').val();
  if (val) {
    sendMessage(val);
    $('#chattext').val('');
  }
});

