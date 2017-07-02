<?php

echo 'Client IP Address: '. getenv('GEOIP_ADDR')."<br>\n";
echo 'Client Country Code: '. getenv('GEOIP_COUNTRY_CODE')."<br>\n";
echo 'Client Country Name: '. getenv('GEOIP_COUNTRY_NAME')."<br>\n";
echo 'Client User_Agent: '. getenv('HTTP_USER_AGENT')."<br>\n";

?>