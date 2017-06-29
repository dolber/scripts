<?php
echo 'Client IP Address: '. getenv('GEOIP_ADDR')."<br>";
echo 'Client Country Code: '. getenv('GEOIP_COUNTRY_CODE')."<br>";
echo 'Client Country Name: '. getenv('GEOIP_COUNTRY_NAME').'<br>';
?>