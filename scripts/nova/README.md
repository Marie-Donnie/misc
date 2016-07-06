## Get the average duration of db/api methods for both implementations (SqlAlchemy/ROME)

### Use

Meant to be used with my fork of Nova and ROME :

[Nova](https://github.com/Marie-Donnie/nova/tree/disco/mitaka "My Nova Fork")

[ROME](https://github.com/Marie-Donnie/rome "My ROME Fork")

You need to make a usable `/opt/logs` folder :
```bash
mkdir /opt/logs
chown stack:stack /opt/logs
chmod -R a+w /opt/logs
```

Make some tests (unittest or rally) to get the logs :
+ By default, it will generate a log for ROME implementation
+ Change [IMPL](https://github.com/Marie-Donnie/nova/blob/disco/mitaka/nova/db/api.py#L124) to true to switch to SqlAlchemy and launch the tests again

You have now two files in `/opt/logs` : `db_api_mysql` and `db_api_disco`

Simply run `./analyse.sh /opt/logs/` that will generate the results in a text file in the folder where you ran the script.

You can also use the script with `analyse <folder-path>` if you already have the logs elsewhere.