# steps to deploy on eoastest5.xyz:8000

1. `ssh n3jov`
2. `cd ~/repos/ocgy-dataviewer`
3. git fetch from the raw branch then update:
    - git fetch https://github.com/fhmjones/ocgy-dataviewer raw
    - git reset --hard origin/raw
5. `docker-compose build ocgy_dash`
6. `docker-compose down`
7. `docker-compose up -d`
