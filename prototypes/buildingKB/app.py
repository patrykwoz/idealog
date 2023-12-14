from build_kb import get_news_links, from_urls_to_kb, save_network_html, generate_net, write_net_html


news_links = get_news_links("Beaver", pages=1, max_links=5)
kb = from_urls_to_kb(news_links, verbose=True)
filename = "network_test.html"
net = generate_net(kb)

nodes, edges, heading, height, width, options = net.get_network_data()