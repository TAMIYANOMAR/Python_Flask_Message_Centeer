var socket = null;
var room_id = null;
$(document).ready(function() {
    const button = document.getElementById('mybutton');
    const postFrom = document.getElementById('postFrom');
    const postTo = document.getElementById('postTo');
    const message = document.getElementById('message');
    button.addEventListener('click',function() {
        socket.emit('send', postFrom.value, postTo.value, message.value,room_id);
    });
    socket = io();
    socket.on('connect', function() {
        socket.emit('join',postFrom.value,postTo.value);
    });
    socket.on('send_room_no', function(data) {
        room_id = data;
    });
    socket.on('server response', function() {
        location.reload();
    });
});