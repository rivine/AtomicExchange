all:
	rm -r dist && mkdir dist && cd AtomicExchange.Ui && qmake && make && cd .. && cp AtomicExchange.Ui/atomicExchange ./dist && chmod +x dist/atomicExchange && cp -R exchangeNodes dist