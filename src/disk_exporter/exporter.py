import argparse
import logging
from disk_exporter.collector import DiskCollector
from http.server import HTTPServer
from prometheus_client import MetricsHandler, REGISTRY, GC_COLLECTOR, PROCESS_COLLECTOR, PLATFORM_COLLECTOR

def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()

    parser.add_argument(
            "--listen-address", "-l",
            default="0.0.0.0",
            help="Address for HTTP server to listen on"
            )

    parser.add_argument(
            "--listen-port", "-p",
            default="9313",
            help="Port for HTTP server to listen on",
            type=int
            )

    args = parser.parse_args()

    REGISTRY.register(DiskCollector())

    # disable default metrics
    REGISTRY.unregister(GC_COLLECTOR)
    REGISTRY.unregister(PROCESS_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)

    logging.info(f"Starting to listen to '{args.listen_address}' on port {args.listen_port}... " +
                 f"(http://{args.listen_address}:{args.listen_port})")
    HTTPServer((args.listen_address, args.listen_port), MetricsHandler).serve_forever()
