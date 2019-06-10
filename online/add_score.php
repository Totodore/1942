<?php 
    if (isset($_POST["json"])) {
        if (file_put_contents("scores.json", $_POST["json"]))
            header("HTTP/1.1 202");
        else
            header("HTTP/1.1 500");
    }
?>