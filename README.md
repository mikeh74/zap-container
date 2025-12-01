# OWASP ZAP

Running OWASP ZAP in docker: https://www.zaproxy.org/docs/docker/about/

We've added a compose file and a .env file to make it more straightforward to run the reports.

In the .env you set the following variables:

* SCAN_TYPE - generally `baseline` or `full_scan`
* SCAN_TARGET - The domain to be scanned (eg www.example.com)

Once you have set these then run the compose.yml:

```
docker compose up
```

## Scan Types 

You can read more about the scane types here:
* [Baseline](https://www.zaproxy.org/docs/docker/baseline-scan/)
* [Full Scan](https://www.zaproxy.org/docs/docker/full-scan/)

Or for more of an overview see the main [docker page](https://www.zaproxy.org/docs/docker/) for Zap

## Mounts

We mount reports/ to output the reports into.

## Webswing

You can run the full ZAP GUI using webswing, docs here:
<https://www.zaproxy.org/docs/docker/webswing/>

Example:
```
docker run -u zap -p 8080:8080 -p 8090:8090 -i owasp/zap2docker-stable zap-webswing.sh
```