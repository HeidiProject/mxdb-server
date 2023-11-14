# Timeout for pymongo to try to connect to Mongo server
MONGO_CONNECT_TIMEOUT = 2000 #ms

# If using NGINX, put here the valiue of 'proxy_read_timeout' from nginx.conf
# If NGINX is not used in the deployment, set it to 10. It decides how many attempts will be made when trying to recconect to Mongo server
NGINX_UPSTREAM_SERVER_TIMEOUT = 10 #s, 10s default, check nginx.conf is settting was changed