(function localFileVideoPlayer() {
    'use strict';

    var URL = window.URL || window.webkitURL;

    var displayMessage = function (message, isError) {
        var element = document.querySelector('#message');
        element.innerHTML = message;
        element.className = isError ? 'error' : 'success'
    };

    var playSelectedFile = function (event) {
        $('.loader').toggle();

        var file = this.files[0];
        var type = file.type;
        var videoNode = document.querySelector('video');
        var canPlay = videoNode.canPlayType(type);

        if (canPlay === '') canPlay = 'no';

        var message = 'Can play type "' + type + '": ' + canPlay;
        var isError = canPlay === 'no';
        displayMessage(message, isError);

        if (isError) {
            return
        }

        videoNode.src = URL.createObjectURL(file);

        $.ajax({
            type:"POST",
            url:"/run_emotion_recog/",
            data: {
                'video': $("#myvideo").val()
            },
            success: function(response) {
            },
            error: function (xhr, ajaxOptions, thrownError) {
                alert(xhr.status);
                alert(thrownError);
            }
        })
    };

    window.onload=function(){
        var inputNode = document.querySelector('#myvideo');
        if(inputNode) {
            inputNode.addEventListener('change', playSelectedFile, false);
        }
    }
})();

window.onload=function() {
    $('#select_video').on('change', function() {
        $('.loader').toggle();
        var file_name = this.value;
        var URL = window.URL || window.webkitURL;
        var videoNode = document.querySelector('video');

        videoNode.src = 'http://127.0.0.1:8001/static/proto1/video/' + file_name;

        // Query to get the video emotions
        $.ajax({
            type:"POST",
            url:"/run_emotion_recog/",
            data: {
                'video_name': file_name
            },
            success: function(response) {
                $('.loader').toggle();
                var context = JSON.parse(response);
                $('#original-text').html(context['original-text']);
                $('#emo-original-text').html(context['emo-original-text']);
                $('#emo-video-status').html("The facial emotion detection in the video is being processed." +
                    "Click on the button below to get the status and the results.");
                $('#emo-video-progress').html("Progress: 0%");
                $('#microsoft-text').html(context['microsoft-text']);
                $('#emo-microsoft-text').html(context['emo-microsoft-text']);
                $('#yandex-text').html(context['yandex-text']);
                $('#emo-yandex-text').html(context['emo-yandex-text']);
                // $('#api-response').html(context['api-response']);
                $('#url-results').html(context['url-results']);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                alert(xhr.status);
                alert(thrownError);
            }
        });
    });

    $('#import_video').on('change', function() {
        var file = this.files[0];
        $.ajax({
            type:"POST",
            url:"/import_video/",
            file: file,
            data: file,
            // data: {
            //     'video': file,
            //     'type': file.type
            // },
            success: function(response) {
                var context = JSON.parse(response);

                $('#select_video').empty();

                $each(context["list_video"], function(value) {
                    new Element('option')
                        .set('text', value)
                        .inject($('#select_video'));
                });
            },
            error: function (xhr, ajaxOptions, thrownError) {
                alert(xhr.status);
                alert(thrownError);
            }
        });
    });

};


function showClass(){
    $('.emotion').toggle();
}


function getVideoEmo(){

    var url_results = $("#url-results")[0].textContent;

    $.ajax({
        type:"POST",
        url:"/get_video_results/",
        data: {
            'url-results': url_results
        },
        success: function(response) {
            // var response_modified = response.replace("\\r\\n\"", "").replace("\"{", "{").replace("\\\"", "\"");
            var response_json = JSON.parse(response);
            var status = response_json['status'];
            $('#emo-video-progress').html("Progress: " + response_json['progress'] + "%");
            if (status == "Running") {
                $('#emo-video-status').addClass("running");
            } else if (status == "Succeeded"){
                $('#emo-video').toggle();
                $('#emo-video-status').html("Success");
                $('#emo-video-status').addClass("success");
                $('#emo-video-status').removeClass("running");
                var scores = jsonPath(response_json, "$..windowMeanScores");

                var emo_graph = document.getElementById('emo-video');

                var scores_graph = [];

                if (scores.length > 0) {
                    for (var emo in scores[0]) {
                        scores_graph.push({x:[], y:[], name:emo})
                    }
                    var emo_index = 0;
                    for (emo in scores[0]) {
                        for (var instant in scores) {
                            scores_graph[emo_index]['y'].push(scores[instant][emo]);
                            scores_graph[emo_index]['x'].push(instant);
                        }
                        emo_index += 1;
                    }
                }

                Plotly.plot( emo_graph, scores_graph, { margin: { t: 0 } } );
            } else {
                $('#emo-video-status').addClass("error");
            }
        },
        error: function (xhr, ajaxOptions, thrownError) {
            alert(xhr.status);
            alert(thrownError);
        }
    });
}