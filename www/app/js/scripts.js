"use strict";

var Templaters = {
    qr_data: function (qr_data) {
        return `
            <tr class="table-${ qr_data.check_model__id ? 'success' : 'danger'}" data-id="${qr_data.id}">
                <td>
                    ${ qr_data.qr_string }
                </td>
                <td class="text-${qr_data.is_valid ? 'success' : 'danger'}">
                    ${ qr_data.is_valid ? 'Valid' : 'Not valid'}
                </td>
                <td>${ moment(qr_data.created_at).format('DD/MM/YYYY HH:mm:ss')}</td>
            </tr>`
    },
    additionalForTree: function (data) {
        var node = data.node;
        return `
            <div class="jqtree-additional">
                <div class="jqtree-additional-inner">
                    <span class="jqtree-additional__title">
                        ${node.name} 
                    </span>
                    <a href="/category_edit/${node.id}/" class="jqtree-additional__edit btn btn-sm btn-success">
                        edit
                    </a>
                </div>
            </div>`
    }
};

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
            var get_qr_data_list_html = function (qr_data_list) {
                return qr_data_list.reduce(function (result, qr_data) {
                    return result + Templaters.qr_data(qr_data)
                });
            };

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
                        $list.html(get_qr_data_list_html(response))
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

                $('.update-qr-string', $qrString).on('submit', function (e) {
                    e.preventDefault();

                    if ($qrStringInput.data('original') === $qrStringInput.val()) {
                        return this;
                    }

                    if (!confirm('Change ' + $qrStringInput.data('original') + ' to ' + $qrStringInput.val() + ' ?')) {
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
                            $qrStringInput.data('original', $qrStringInput.val());
                        },
                        error: function (response) {
                            if (response.responseJSON && response.responseJSON.message) {
                                return alert(response.responseJSON.message)
                            }

                            alertUnknownError(response)
                        }
                    });
                });
            })
        }

        if (is_route('search_products', 'app')) {
            var $paginator_form = $('.paginator form');
            var $product_form = $('#product_form');
            var name = $('input[name=name]', $product_form).val();
            $paginator_form.append('<input type="hidden" name="name" value="' + name + '">')
        }

        if (is_route('category_edit', 'app') || is_route('category_new', 'app')) {
            var $tree = $('#tree1');
            var $parentIdInput = $('input[name=parent_id]');

            $tree.tree({
                onCreateLi: function (node, $li) {
                    $li.find('.jqtree-element').append(Templaters.additionalForTree({node: node}));
                }
            });
            $tree.on('tree.init', function (e) {
                var node = $tree.tree('getNodeById', $parentIdInput.val() || null);
                $tree.tree('selectNode', node);
                $(':focus').blur();
            });


            $tree.on('tree.select', function (e) {
                if (e.node) {
                    $parentIdInput.val(e.node.id)
                } else {
                    $parentIdInput.val('')
                }
            });

            $('#category_edit_form').on('submit', function (e) {
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
            });
        }

        if (is_route('product_edit', 'app') || is_route('product_new', 'app')) {
            var $tree = $('#tree1');
            var categoryIdInput = $('input[name=category_id]');

            $tree.tree({
                onCreateLi: function (node, $li) {
                    $li.find('.jqtree-element').append(Templaters.additionalForTree({node: node}));
                }
            });
            $tree.on('tree.init', function (e) {
                var node = $tree.tree('getNodeById', categoryIdInput.val() || null);
                $tree.tree('selectNode', node);
                $(':focus').blur();
            });


            $tree.on('tree.select', function (e) {
                if (e.node) {
                    categoryIdInput.val(e.node.id)
                } else {
                    categoryIdInput.val('')
                }
            });

            $('#product_form').on('submit', function (e) {
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
            });
        }

        if (is_route('category_list', 'app') || is_route('product_edit', 'app')) {
            $('#tree1').tree({
                onCreateLi: function (node, $li) {
                    $li.find('.jqtree-element').append(Templaters.additionalForTree({node: node}));
                }
            });
        }
    });
})();