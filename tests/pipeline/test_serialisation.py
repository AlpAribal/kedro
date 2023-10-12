import pytest

from kedro.io import DataCatalog
from kedro.pipeline import Pipeline
from kedro.pipeline.node import Node
from kedro.runner import SequentialRunner


def func(x: float) -> float:
    """Dummy func to use in tests."""
    return 2**x


@pytest.fixture(name="node")
def fixture_node() -> Node:
    """Dummy node to use in tests."""
    return Node(func=func, inputs="a", outputs="b")


@pytest.fixture(name="pipe")
def fixture_pipe() -> Pipeline:
    """Dummy pipeline to use in tests."""
    n1 = Node(func=func, inputs="a", outputs="b")
    n2 = Node(func=func, inputs="b", outputs="c")
    n3 = Node(func=func, inputs="c", outputs="d")
    n4 = Node(func=func, inputs="e", outputs="f")

    return Pipeline([n1, n2, n3, n4])


def test_node_tojson() -> None:
    """Generated JSON string is correct."""
    n = Node(
        func=func,
        inputs="my-input",
        outputs="my-output",
        namespace="my-ns",
        name="my-name",
        tags=["tag2", "tag1"],
        confirms=["b", "a"],
    )
    assert n.to_dict() == {
        "func": "tests.pipeline.test_serialisation.func",
        "inputs": "my-input",
        "outputs": "my-output",
        "name": "my-name",
        "namespace": "my-ns",
        "tags": ["tag1", "tag2"],
        "confirms": ["a", "b"],
    }


def test_node_roundtrip(node: Node) -> None:
    """Should end up with the very same Node after a JSON roundtrip."""
    s = node.to_dict()
    new_node = Node.from_dict(s)

    assert node is not new_node
    assert node == new_node


def test_node_result(node: Node) -> None:
    """The result of a node should remain the same after a JSON roundtrip."""
    s = node.to_dict()
    new_node = Node.from_dict(s)

    assert new_node.run({"a": 2}) == {"b": 4}
    assert new_node.run({"a": 3}) == {"b": 8}


@pytest.mark.xfail(reason="We keep the initial form of the inputs")
def test_node_input_types() -> None:
    """Should JSON representation of Nodes be the same if their input/output forms are different?"""
    n1 = Node(func=func, inputs="random_name", outputs="b")
    n2 = Node(func=func, inputs=["random_name"], outputs="b")
    n3 = Node(func=func, inputs={"x": "random_name"}, outputs="b")
    assert (
        Node.from_dict(n1.to_dict())
        == Node.from_dict(n2.to_dict())
        == Node.from_dict(n3.to_dict())
    )


def test_pipe_roundtrip(pipe: Pipeline) -> None:
    """Should end up with the very same Pipeline after a JSON roundtrip."""
    s = pipe.dumps()
    new_pipe = Pipeline.loads(s)

    assert pipe is not new_pipe
    assert sorted(new_pipe.nodes) == sorted(pipe.nodes)


def test_pipe_result(pipe: Pipeline) -> None:
    """The result of a pipeline should remain the same after a JSON roundtrip."""
    s = pipe.dumps()
    new_pipe = Pipeline.loads(s)

    cat = DataCatalog(feed_dict={"a": 2, "e": 3})
    exp = {
        "d": 65536,  # 2 ** (2 ** (2 ** 2))
        "f": 8,  # 2 ** 3
    }
    assert SequentialRunner().run(pipeline=new_pipe, catalog=cat) == exp
