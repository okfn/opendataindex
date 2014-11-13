define(['jquery', 'bootstrap', 'chroma', 'tablesorter'], function($, bootstrap, chroma, tablesorter) {

    var placeCount = placeCount || 260,
        colorSteps = ['#ff0000', '#edcf3b', '#7ab800'],
        colorScale = chroma.scale(colorSteps).domain([0, 100]),
        naString = 'n/a',
        $dataTable = $('.data-table'),
        $visiblePopover,
        $scoreDisplay = $('.score'),
        popover_tmpl = '<div class="popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>';

    $('#places_overview_table').tablesorter({sortList: [[0,0], [1,1], [12,0]]});
    $('#datasets_overview_table').tablesorter({sortList: [[0,0], [1,1], [4,0]]});
    $('#slice-table').tablesorter({sortList: [[0,0], [1,1], [7,0]]});

    function sortPlace(a, b) {

        return $(a).data('place').toUpperCase().localeCompare($(b).data('place').toUpperCase());

    }

    function sortScore(a, b) {

        var comp = parseInt($(b).data('score'), 10) - parseInt($(a).data('score'), 10);
        return comp !== 0 ? comp : sortPlace(a, b);

    }

    function sortTable(table, sortBy, $actor) {

        var sortFunc;

        if (sortBy === 'score') {
            sortFunc = sortScore;
        } else {
            sortFunc = sortPlace;
        }

        $actor.attr('checked', true);
        table.find('tbody tr').sort(sortFunc).appendTo(table);

    }

    function filterTable(table, query, $actor) {

        table.find('tbody tr').each(function(index, value) {

            if (query.length < 2) {
                $(this).show();
            } else if (query.length >= 2) {
                if ($(this).data('place').indexOf(query) === -1) {
                    $(this).hide();
                } else {
                    $(this).show();
                }
            }

        }) ;

    }


    function setInteractions() {

        $("[data-toggle='tooltip']").tooltip({html: true});
        $('[data-toggle="popover"]').popover({
            trigger: 'click',
            'placement': 'bottom',
            'html': true,
            'show': true,
            'template': popover_tmpl
        });

        $('[data-toggle="popover"]').on('click', function() {
            $('[data-toggle="popover"]').not(this).popover('hide');
        });

        $('body').on('click', 'td.showpopover', function() {
            var $this = $(this);

            // check if the one clicked is now shown
            if ($this.data('popover').tip().hasClass('in')) {

                // if another was showing, hide it
                if ($visiblePopover) {
                    $visiblePopover.popover('hide');
                }

                // then store reference to current popover
                $visiblePopover = $this;

            } else { // if it was hidden, then nothing must be showing
                $visiblePopover = '';
            }
        });

        $('.sort-table').on('click', function() {

            var $this = $(this),
                value = $this.val();
            if ($this.is(':checked')) {
                sortTable($dataTable, value, $this);
            }

        });

        $('.filter-table').on('keyup', function() {

            var $this = $(this),
                query = $this.val().toLowerCase().replace(' ', '-').replace(',', '');

            filterTable($dataTable, query, $this);

        });

        $.each($scoreDisplay, function(index, el) {
            var score,
                $el = $(el);
            if ($el.data('score') === naString) {
                score = 0;
            } else {
                score = parseInt($el.data('score'), 10);
            }
            $el.css({
              'background-color': colorScale(score).hex(),
              'color': 'white'
            });
        });

    }

    function setColumnTHWidths() {
        $('.table-header-stuck th')
            .each(function () {
                var width = $(this).outerWidth();
                $(this).css('width', width);
            });
    }

    function initializeTable() {
        setInteractions();
        setColumnTHWidths();
    }

    return {
        init: initializeTable,
    };

});
