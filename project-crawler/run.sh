set -e
docker run -v ~/src/interview_questions:/main/root/ -v $(pwd)/data:/main/out sherlock-crawler crawl $1

