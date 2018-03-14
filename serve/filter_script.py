name_filter = """
    <script>
    function select_chapters(filterstring) {
        if (typeof(filterstring)==='undefined') filterstring = $("#txt_filter").val();

        var filterregex = new RegExp(filterstring, "i");

        // uncheck everything
        $('.keepchapter')
            .each(function(index) {$(this).attr("checked", false);});

        // check those with matching regex
        $(".character-score:visible")
            .filter(function() {

                return $(this).data("character").match(filterregex);
            })
            .each(function(index) {
            lbl = $(this).closest("label");
                checkbox_id = lbl.attr('for');
                console.log('#' + checkbox_id);
                $('#' + checkbox_id)[0].checked =  true;
            });
    }
    </script>
    <span>
        <input type="text" id="txt_filter"
            onkeydown = "if (event.keyCode == 13) select_chapters()"/>
        <button type="button" onclick="select_chapters()">Filter by Regex</button>
    </span>
"""

rank_control = """
    <script>
    function update_visibility_by_rank(show_n) {
        if (typeof(show_n)==='undefined') show_n = $("#txt_rank_control").val();
        $(".character-score").each(function(index){
            var rank = $(this).data("rank");
            if (rank >= show_n) {
                $(this).hide();
            } else {
                $(this).show();
            }
        });
    }
    </script>
    <span>
        <span>show top:</span>
        <input type="number" id="txt_rank_control" value="1" min="1"
            title="Max number of guesses to display"
            oninput="update_visibility_by_rank()"/>
    </span>
"""



code = name_filter + "\n\n" + rank_control
