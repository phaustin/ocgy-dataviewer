# steps to deploy on eoastest5.xyz:8000

1. `ssh n3jov`
2. `cd ~/repos/ocgy-dataviewr`
3. git fetch and update raw branch
4. `docker-compose build ocgy_dash`
5. `docker-compose down`
6. `docker-compose up -d`
