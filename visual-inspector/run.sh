set -e
docker run -ti -v $(pwd)/data:/www-main/data -p 8000:8000 sherlock-inspector
