# BlankEclair's Spidersite

This is my personal spidersite! Currently available at
https://blankeclair.github.io.

## Build
1. `pip3 install -r requirements.txt`
2. `rm -r public; python3 generate.py`

## Live reload
```shell
while sleep 0.1
do
find raw -type f | entr -s -d 'rm -r public; python3 generate.py'
done
```
