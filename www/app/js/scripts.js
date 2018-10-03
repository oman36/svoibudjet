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
                    updateQrList();
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
        });

        var $qr_code_progress = $('#qr_code_progress');
        var qrUpdateTimeout = 5000;

        var updateQrList = (function () {
            var $list = $('#qr_code_list');
            var url = $list.data('url');
            return function () {
                $qr_code_progress.data('next', new Date().getTime() + qrUpdateTimeout);

                $.get(url, function (response) {
                    $list.html(response)
                })
            }
        })();

        var updateQrCodeProgressBar = function(percent) {
          $qr_code_progress.css('width', percent + '%');
          $qr_code_progress.attr('aria-valuenow', percent);
        };

        setInterval(function () {
            var remainedTime = $qr_code_progress.data('next') - new Date().getTime();
            if (remainedTime > 0) {
                updateQrCodeProgressBar(Math.round((qrUpdateTimeout - remainedTime) / qrUpdateTimeout * 100))
            } else {
                $qr_code_progress.data('next', new Date().getTime() + qrUpdateTimeout);
                updateQrList();
                updateQrCodeProgressBar(0);
            }
        }, 100)
    });
})();