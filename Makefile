
install:
	git clone https://github.com/HeidiProject/mxdb-server.git
	VERSION=$(version) docker-compose build

clean:
	rm -rf mxdb-server
