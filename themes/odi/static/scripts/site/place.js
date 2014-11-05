define(['jquery', 'bootstrap', 'chroma'], function($, bootstrap, chroma) {

    var colorBoundaries = ['#dd3d3a', '#8bdd3a'],
        colorScale = chroma.scale(colorBoundaries).domain([0, 100]),
        $placeOpeness = $('.place-openness'),
        naString = 'n/a',
        score;

    function initializePlace() {

        $.each($placeOpeness, function(index, el) {
            var $el = $(el);
            if ($el.data('score') === naString) {
                score = 0;
            } else {
                score = parseInt($el.data('score'), 10);
            }
            $el.css('backgroundColor', colorScale(score).hex());
        });

    }

    return {
        init: initializePlace,
    };

});
