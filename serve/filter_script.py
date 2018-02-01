code = """
    <script>
    function selectchapters(filterstring) {
        if (typeof(filterstring)==='undefined') filterstring = $("#txt_filter").val();

        var filterregex = new RegExp(filterstring);

        // uncheck everything
        $('.keepchapter')
            .each(function(index) {
                $(this).attr("checked", false);
            });

        // check those with matching regex
        $(".charactername")
            .filter(function() {
                return $(this).text().match(filterregex);
            })
            .each(function(index) {
                checkbox_id = $(this).attr('for');
                console.log('#' + checkbox_id);
                $('#' + checkbox_id)[0].checked =  true;
            });
    }
    </script>
    <input type="text" id="txt_filter"
        onkeydown = "if (event.keyCode == 13) selectchapters()"/>
    <button type="button" onclick="selectchapters()">Filter by Regex</button>
"""

