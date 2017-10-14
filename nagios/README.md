cp -pr check_url.py /usr/lib64/nagios/plugins/
chmod +x /usr/lib64/nagios/plugins/check_url.py

define service {
        use                             local-service
        host_name                       localhost
        service_description             <command_description>
        check_command                   <command_name>
        }


define command{
        command_name    check_url
        command_line    $USER1$/check_url.py $ARG1$
        }
