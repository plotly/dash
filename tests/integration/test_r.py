

def test_r_sample(dashr_server, dash_br):
    dashr_server()
    import time
    time.sleep(2.5)
    dash_br.server_url = dashr_server.url
    time.sleep(600)
