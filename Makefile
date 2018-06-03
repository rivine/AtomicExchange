all:
	rm -r dist || true && mkdir dist && cd AtomicExchange.Ui && qmake && make && cd .. && cp AtomicExchange.Ui/atomicExchange ./dist && cp -r AtomicExchange.Ui/scripts dist/ && chmod +x dist/atomicExchange && cp -R exchangeNodes dist
docker:
	cp -R dist cryptoDocker/ && cd cryptoDocker && docker-compose build && docker-compose up