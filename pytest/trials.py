from main import main

def test_full_process_1():
    main(r"C:\Users\Inter\PycharmProjects\Lexicon\pytest\vape_shop.eal")
    assert {'categoryHigh': 25, 'mangoChill': {'prise': 25, 'prises': {'categoryHigh': 49}, 'quantity': 560}}

def test_full_process_2():
    main(r"C:\Users\Inter\PycharmProjects\Lexicon\pytest\server_config.eal")
    assert {'Database': {'maxPoolSize': 20, 'port': 5432}, 'Server': {}, 'Settings': {'maxConnections': 100, 'retryAttempts': 5, 'timeout': 30}}
