from importlib import import_module


def build_main_graph():
    return import_module("graph.graph").build_main_graph()


__all__ = ["build_main_graph"]
