
## Run
### Docker
```sh=
docker build -t letus-archive .
docker run -it --rm -v "$PWD"/config.yaml:/usr/src/app/config.yaml letus-archive user=1234567 pass=password
```

### Local
```sh=
python src/main.py user=1234567 pass=password
```

### pipenv
```sh=
pipenv run python src/main.py user=1234567 pass=password
```