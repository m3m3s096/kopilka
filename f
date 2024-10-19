    <div class="container">
        <h1>{{ fund.title }}</h1>
        <center>
        <div class="progress-bar-container">
            <div class="progress-bar" style="
                width: {{ (fund.total_amount / fund.goal_amount) * 100 }}%; 
                background-color: 
                    {% if fund.total_amount >= fund.goal_amount %}
                        #8A2BE2
                    {% elif fund.total_amount >= fund.goal_amount * 0.75 %}
                        #7366BD
                    {% elif fund.total_amount >= fund.goal_amount * 0.5 %}
                        #9370D8
                    {% else %}
                        #8673A1
                    {% endif %};">
            </div>
        </div>
    </center>


    <script>
        function copyLink() {
            const copyText = document.getElementById("shareLink");
            copyText.select();
            copyText.setSelectionRange(0, 99999); // For mobile devices
            document.execCommand("copy");
            alert("Link copied: " + copyText.value);
        }
    </script>




<a href="{{ url_for('dashboard') }}">Back to Dashboard</a>