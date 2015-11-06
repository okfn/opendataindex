define(['jquery', 'bootstrap', 'sexyTables'], function($, bootstrap, sexy) {

    function initializeUI() {
        $('.download-action').on('click', function() {
            $("#tell-us").modal();
        });

        $(document).ready(function() {
            sexyTables();
        })
    }

    return {
        init: initializeUI,
    };

});
