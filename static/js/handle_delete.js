$(function () {
    function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        var csrftoken = getCookie('csrftoken');
        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    $(document).on('click', '.delete-relais', function (e) {
        e.preventDefault();

        var id = $(this).parent().parent().find('th').text();
        var row = $(this).parent().parent();
        $.post("delete_relais/", {'delete_id': id})
            .fail(function () {
                console.log('failed to delete relais number: ' + id);
            })
            .done(function () {
                $(row).remove();
            });
    });

    $(document).on('click', '.delete-sensor', function (e) {
        e.preventDefault();

        var id = $(this).parent().parent().find('th').text();
        var row = $(this).parent().parent();
        $.post("delete_sensor/", {'delete_id': id})
            .fail(function () {
                console.log('failed to delete sensor with number: ' + id);
            })
            .done(function () {
                $(row).remove();
            });
    });
});