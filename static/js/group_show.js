var socket = null;
var room_id = null;
$(document).ready(function() {
    const button = document.getElementById('mybutton');
    const username = document.getElementById('username');
    const groupid = document.getElementById('groupid');
    const content = document.getElementById('content');
    button.addEventListener('click',function() {
        socket.emit('send_group', username.value, groupid.value, content.value,room_id);
    });
    socket = io();
    socket.on('connect', function() {
        socket.emit('join_room',groupid.value);
    });
    socket.on('send_room_no', function(data) {
        room_id = data;
    });
    socket.on('server response', function() {
        location.reload();
    });
});