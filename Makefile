all:
	rm -r dist || true && mkdir dist && cd AtomicExchange.Ui && qmake && make && cd .. && cd AtomicExchange.Scripts && make && cd .. && cp AtomicExchange.Ui/atomicExchange ./dist && cp -r AtomicExchange.Ui/scripts dist/ && chmod +x dist/atomicExchange && cp -R AtomicExchange.Scripts dist && cp -R Multinodes dist
docker:
	cp -R dist AtomicExchange.Docker/ && cd AtomicExchange.Docker && docker-compose build && docker-compose up
docker-prepare:
	cp -R dist AtomicExchange.Docker/ 
