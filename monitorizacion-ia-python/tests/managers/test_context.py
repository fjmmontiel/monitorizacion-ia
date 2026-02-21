"""Modulo de tests para el contexto"""

import pytest
import json
from app.managers.context import ToolCallFormatter, ToolCall, Context
from app.managers.items import ContextItem

# --------------------------
# TOOL CALL TESTS
# --------------------------


def test_toolcallformatter_format_basic():
    """Modulo"""

    class DummyToolCall:
        """Modulo"""

        tool_name = "mi_funcion"
        params = {"x": 1, "y": "hola"}

    formatted = ToolCallFormatter.format(DummyToolCall())
    assert formatted == "mi_funcion(x=1, y='hola')\n"


def test_toolcall_initializes_and_formats():
    """Modulo"""
    call = ToolCall(
        tool_name="calcular", params={"a": 10, "b": 5}, successful=True, result=15
    )

    assert call.tool_name == "calcular"
    assert call.successful is True
    assert call.result == 15
    assert call.formatted_call == "calcular(a=10, b=5)\n"


# --------------------------
# CONTEXT TESTS
# --------------------------


class DummyItem(ContextItem):
    """Modulo"""

    def __init__(self, name, tab="", item_type="dummy"):
        """Modulo"""
        super().__init__(name=name, id=name, data={"foo": "bar"}, tab=tab)
        self.item_type = item_type

    def get_llm_str(self):
        """Modulo"""
        return f"LLM_STR_{self.name}"

    def to_json(self):
        """Modulo"""
        return json.dumps(
            {
                "id": self.get_id(),
                "name": self.name,
                "item_type": self.item_type,
                "tab": self.tab,
                "data": self.data,
            }
        )


class DummyToolCallLog:
    """Modulo"""

    def __init__(self):
        """Modulo"""
        self.calls = []

    def add(self, tool_call):
        """Modulo"""
        self.calls.append(tool_call)

    def to_string(self):
        """Modulo"""
        return "\n".join([c.tool_name for c in self.calls])

    def to_json(self):
        """Modulo"""
        return json.dumps([{"tool_name": c.tool_name} for c in self.calls])


@pytest.fixture
def context(monkeypatch):
    """Modulo"""
    ctx = Context()
    ctx.tool_call_log = DummyToolCallLog()
    return ctx


def test_update_add_item(context):
    """Modulo"""
    item = DummyItem("test1")
    context.update(item, "add")
    assert context.get_item(item.get_id()) == item
    assert "[ADD_CONTEXT" in context.conversation_outputs[0]


def test_update_update_item(context):
    """Modulo"""
    item = DummyItem("test1")
    context.update(item, "add")
    item2 = DummyItem("test1")
    context.update(item2, "update")
    assert context.get_item(item2.get_id()) == item2
    assert any("[UPDATE_CONTEXT" in out for out in context.conversation_outputs)


def test_update_remove_item(context):
    """Modulo"""
    item = DummyItem("test1")
    context.update(item, "add")
    context.update(item, "remove")
    assert item.get_id() not in context.items
    assert any("[REMOVE_CONTEXT" in out for out in context.conversation_outputs)


def test_update_invalid_change_type_raises(context):
    """Modulo"""
    item = DummyItem("test1")
    with pytest.raises(ValueError):
        context.update(item, "invalid")


def test_get_llm_str(context):
    """Modulo"""
    item = DummyItem("itemA")
    context.update(item, "add")
    tc = ToolCall(tool_name="toolX", params={}, successful=True, result="ok")
    context.add_tool_call(tc)
    result = context.get_llm_str()
    assert "LLM_STR_itemA" in result
    assert "toolX" in result


def test_to_json_and_get_tool_call_json(context):
    """Modulo"""
    item = DummyItem("itemB")
    context.update(item, "add")
    tc = ToolCall(tool_name="toolY", params={}, successful=True, result="ok")
    context.add_tool_call(tc)

    ctx_json = json.loads(context.to_json())
    assert "items" in ctx_json
    assert "tool_call_log" in ctx_json

    tc_json = json.loads(context.get_tool_call_json())
    assert "tool_call_log" in tc_json


def test_conversation_outputs(context):
    """Modulo"""
    context.add_conversation_output("hello")
    assert context.conversation_output_is_not_empty()
    popped = context.pop_convertation_output_element()
    assert popped == "hello"
    assert context.conversation_output_is_empty()
