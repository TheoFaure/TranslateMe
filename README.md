# TranslateMe

This is a draft, sorry if it's not organied at all


To put in production, don't forget to:
* Create a foler SentimentalTranslator_Proto1/static
* run `python manage.py collectstatic`
* Set the http.conf of Apache as follows.
* Set the site enabled to apache, with the command `sudo a2ensite SentimentalTranslator_Proto1`
* Reload your Apache server each time you modify something: `service apache2 restart`
* And many more... Like setting your virtualenv, installing mod_wsgi for python3...


http.conf file:
```
<VirtualHost *:80>
ServerName servtheo
ServerAdmin theo@translateme.westeurope.cloudapp.azure.com
ServerAlias translateme.westeurope.cloudapp.azure.com

WSGIScriptAlias / /home/theo/SentimentalTranslator_Proto1/SentimentalTranslator_Proto1/wsgi.py

<Directory /home/theo/SentimentalTranslator_Proto1/SentimentalTranslator_Proto1>
<Files wsgi.py>
Require all granted
</Files>
</Directory>

<Directory /var/www/SentimentalTranslator_Proto1/static>
    Options Indexes FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>

Alias /static /var/www/SentimentalTranslator_Proto1/static
<Location "/static/">
  Options -Indexes
</Location>

</VirtualHost>

WSGIPythonHome /home/theo/SentimentalTranslator_Proto1/myvenv
WSGIPythonPath /home/theo/SentimentalTranslator_Proto1

WSGIDaemonProcess translateme.westeurope.cloudapp.azure.com python-home=/home/theo/SentimentalTranslator_Proto1/myvenv python-path=/home/theo/SentimentalTranslator_Proto1
WSGIProcessGroup translateme.westeurope.cloudapp.azure.com
```
