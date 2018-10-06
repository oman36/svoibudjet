"use strict";

function is_route(url_name, app_name) {
    if (route.url_name !== url_name) {
        return false;
    }
    return route.app_names[0] === app_name;
}

function alertUnknownError(resoponse) {
    alert(
        resoponse.status + ' ' + resoponse.statusText + '\n' +
        resoponse.getResponseHeader('content-type') +
        ' (' + resoponse.getResponseHeader('content-length') + ')'
    )
}

(function () {
    $(document).ready(function () {
        if (is_route('new_check', 'app')) {
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

            var updateQrCodeProgressBar = function (percent) {
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
            }, 100);
        }

        if (is_route('qr_strings', 'app')) {
            $('.qr_string').each(function (n, el) {
                var $qrString = $(el);
                var id = $qrString.data('id');
                var $qrStringInput = $('.qr-string-input', $qrString);

                $('.delete-qr-data', $qrString).on('submit', function (e) {
                    e.preventDefault();

                    if (!confirm('Delete ' + $qrStringInput.data('original') + ' ?')) {
                        return this;
                    }

                    $.ajax({
                        url: $(this).attr('action'),
                        type: $(this).attr('method'),
                        data: new FormData(this),
                        dataType: 'json',
                        cache: false,
                        contentType: false,
                        processData: false,
                        success: function () {
                            $qrString.hide()
                        },
                        error: alertUnknownError
                    });

                });
            })
        }
    });
})();