# The API used for Blastboard

Create config.ini file and add in database credentials

Add to sites-available:

- Create new file `/etc/apache2/sites-available/blasboard-api.conf`
```
<VirtualHost *:5555>
    ServerName ec2-18-210-177-61.compute-1.amazonaws.com

    WSGIDaemonProcess blastboard-api threads=5
    WSGIScriptAlias / /var/www/blastboard-api/blastboard.wsgi

    <Directory /var/www/blastboard-api>
        WSGIProcessGroup blastboard-api
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
</VirtualHost>
```
Enable the new site with `a2ensite blastboard-api.conf`

Note: Do not forget to add the port running the api to apache's `ports.conf` with `Listen <port_num>`
