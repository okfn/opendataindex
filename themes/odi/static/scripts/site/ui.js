define(['jquery', 'bootstrap'], function($, bootstrap) {

    function initializeUI() {
        $('.download-action').on('click', function() {
            $("#tell-us").modal();
        });
    }

    return {
        init: initializeUI,
    };

});
