FROM debian

RUN apt-get update && apt-get install -y apt-utils make gcc python3 python3-venv python3-dev git
