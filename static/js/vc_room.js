$(document).ready(function() {
    const socket = io();

    // ローカルストリームを表示するvideo要素を取得する
    const localVideo = document.getElementById('local-video');

    // リモートストリームを表示するvideo要素を取得する
    const remoteVideo = document.getElementById('remote-video');

    const connectTo = document.getElementById('connectTo');
    console.log(connectTo)
    const connectFrom = document.getElementById('connectFrom');
    console.log(connectFrom)

    var offer_recieved = false;

    navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        .then((stream) => {
            // ローカルストリームを表示するvideo要素にストリームを割り当てる
            localVideo.srcObject = stream;
        })
        .catch((error) => {
            console.error('Failed to get user media', error);
        });

    // getUserMediaメソッドを使用して、ローカルストリームを取得する
    navigator.mediaDevices.getUserMedia({ video: true, audio: { echoCancellation: true } })
        .then((stream) => {

            // Peer Connectionを作成する
            const pc = new RTCPeerConnection();

            // ローカルストリームをPeer Connectionに追加する
            stream.getTracks().forEach((track) => {
                pc.addTrack(track, stream);
            });

            // リモートストリームを受信した場合の処理を定義する
            pc.ontrack = (event) => {
                // リモートストリームを表示するvideo要素にストリームを割り当てる
                remoteVideo.srcObject = event.streams[0];
            };

            // シグナリングサーバーと接続する
            socket.emit('connect_rtc', connectFrom.value, connectTo.value);
            console.log(connectFrom.value,connectTo.value);
            const offer = function(){
                if(offer_recieved == true)
                {
                    return;
                }
                // Offerを作成し、シグナリングサーバーに送信する
                pc.createOffer()
                    .then((offer) => {
                        return pc.setLocalDescription(offer);
                    })
                    .then(() => {
                        console.log('offer sent')
                        socket.emit('offer', { sdp: pc.localDescription }, connectTo.value);
                    })
                    .catch((error) => {
                        console.error('Failed to create offer', error);
                });
            };

            setInterval(offer,3000);

            // シグナリングサーバーからOfferが送信された場合の処理を定義する
            socket.on('offer_data', (data) => {
                // Remote Descriptionを作成し、Peer Connectionに設定する
                pc.setRemoteDescription(new RTCSessionDescription(data.sdp))
                    .then(() => {
                        // Answerを作成し、シグナリングサーバーに送信する
                        return pc.createAnswer();
                    })
                    .then((answer) => {
                        return pc.setLocalDescription(answer);
                    })
                    .then(() => {
                        socket.emit('answer', { sdp: pc.localDescription }, connectTo.value);
                        console.log('answer sent');
                        offer_recieved = true;
                    })
                    .catch((error) => {
                        console.error('Failed to create answer', error);
                    });
            });

            // シグナリングサーバーからAnswerが送信された場合の処理を定義する
            socket.on('answer_data', (data) => {
                // Remote Descriptionを設定する
                pc.setRemoteDescription(new RTCSessionDescription(data.sdp))
                    .catch((error) => {
                        console.error('Failed to set remote description', error);
                    });
            });

            // シグナリングサーバーからCandidateが送信された場合の処理を定義する
            socket.on('candidate_data', (data) => {
                // ICE Candidateを追加する
                offer_recieved = true;
                pc.addIceCandidate(new RTCIceCandidate(data.candidate))
                    .catch((error) => {
                        console.error('Failed to add ICE candidate', error);
                    });
            });
        })
        .catch((error) => {
            console.error('Failed to get user media', error);
        });
});