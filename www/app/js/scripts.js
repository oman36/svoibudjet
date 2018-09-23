"use strict";

(function () {
    $(document).ready(function () {
        $('#add_check_form').on('submit', function (e) {
            e.preventDefault();
            var formData = new FormData(this);
			var action = $(this).attr('action');
			var method = $(this).attr('method');

			var $btn = $(this).find('button').prop('disabled', true);
            var $error = $('#error').hide();
            var $success = $('#success').hide();
			$.ajax({
                url: action,
                type: method,
                data: formData,
                dataType: 'json',
                cache: false,
                contentType: false,
                processData: false,
                complete: function () {
                    $btn.removeAttr('disabled');
                },
                success: function (data) {
                    $success.show();
                    setTimeout(function () {
                        $success.fadeOut()
                    }, 1400)
                },
                error: function (err) {
                    $error.html(err.responseJSON.message || 'server error').show();
                }
            });
        })
    });
})();