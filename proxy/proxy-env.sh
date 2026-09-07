# source this in the shell where you launch claude / pi
export HTTP_PROXY=http://127.0.0.1:8080
export HTTPS_PROXY=http://127.0.0.1:8080
# Appends the mitm CA to the default trust store. Do NOT use SSL_CERT_FILE here:
# it *replaces* the bundle, so any host mitmproxy blind-tunnels (real cert) fails
# with UNABLE_TO_GET_ISSUER_CERT_LOCALLY, surfacing in pi as "Error: fetch failed".
export NODE_EXTRA_CA_CERTS="$HOME/.mitmproxy/mitmproxy-ca-cert.pem"
