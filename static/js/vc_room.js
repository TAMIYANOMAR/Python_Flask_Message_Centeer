$(document).ready(function() {
    const socket = io();
    const shareScreenButton = document.getElementById('share-screen-btn');
    const localVideo = document.getElementById('local-video');
    const remoteVideo = document.getElementById('remote-video');
    const moteVideo = document.getElementById('share-screen-video')
    const connectTo = document.getElementById('connectTo');
    const connectFrom = document.getElementById('connectFrom');

    const video_constraint = {frameRate: {max: 15 }};
    const screen_constraint = {frameRate: {ideal: 30}};

    var count = 0;
    var should_offer = true;

    navigator.mediaDevices.getUserMedia({ video: video_constraint, audio: false })
        .then((stream) => {
            // ローカルストリームを表示するvideo要素にストリームを割り当てる
            localVideo.srcObject = stream;
        })
        .catch((error) => {
            console.error('Failed to get user media', error);
        });
    
    // getUserMediaメソッドを使用して、ローカルストリームを取得する
    navigator.mediaDevices.getUserMedia({ video: video_constraint, audio: { echoCancellation: true } })
        .then((stream) => {
            
            // Peer Connectionを作成する
            const pc = new RTCPeerConnection();

            // ローカルストリームをPeer Connectionに追加する
            stream.getTracks().forEach((track) => {
                pc.addTrack(track, stream);
            });

            // リモートストリームを受信した場合の処理を定義する
            pc.ontrack = (event) => {
                if(event.streams && event.streams[0])
                {
                    // リモートストリームを表示するvideo要素にストリームを割り当てる
                    remoteVideo.srcObject = event.streams[0];
                    if(event.streams.length == 2)moteVideo.srcObject = event.streams[1];
                    console.log(event.streams);
                    console.log('on track');
                    count += 1;
                }
                else
                {
                    let inbound_stream = new MediaStream(event.track)
                    moteVideo.srcObject = inbound_stream;
                    console.log(event.streams);
                }
                
            };

            // シグナリングサーバーと接続する
            socket.emit('connect_rtc', connectFrom.value, connectTo.value);

            const offer = function(){
                if(should_offer == false)
                {
                    return;
                }
                pc.createOffer()
                    .then((offer) => {
                        return pc.setLocalDescription(offer);
                    })
                    .then(() => {
                        console.log('offer sent')
                        socket.emit('offer', { sdp: pc.localDescription }, connectTo.value);
                        if(count >= 2 )
                        {
                            should_offer = false;
                        }
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
                console.log('answer recieved');
            });

            // シグナリングサーバーからCandidateが送信された場合の処理を定義する
            socket.on('candidate_data', (data) => {
                // ICE Candidateを追加する
                pc.addIceCandidate(new RTCIceCandidate(data.candidate))
                    .catch((error) => {
                        console.error('Failed to add ICE candidate', error);
                    });
            });

            shareScreenButton.addEventListener('click', () => {
                navigator.mediaDevices.getDisplayMedia({ video: screen_constraint })
                    .then((stream2) => {
                        // ローカルストリームをPeer Connectionに追加する
                        stream2.getTracks().forEach((track) => {
                            pc.addTrack(track,stream,stream2);
                        });
                        moteVideo.srcObject = stream2;
                        console.log('add track stream');
                        should_offer = true;
                    })
                    .catch((error) => {
                        console.error('Failed to get display media', error);
                    });
            });
        })
        .catch((error) => {
            console.error('Failed to get user media', error);
        });
    
});