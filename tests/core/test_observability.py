from app.core.observability import NoopTrace, Observability


def test_observability_uses_noop_when_disabled():
    observability = Observability(enabled=False)

    trace = observability.start_trace(name="test", metadata={"case": "disabled"})

    trace.update(output={"ok": True})
    trace.end()

    assert isinstance(trace, NoopTrace)


def test_observability_context_manager_is_safe_when_disabled():
    observability = Observability(enabled=False)

    with observability.trace(name="request", metadata={}) as trace:
        trace.update(input={"message": "hello"})

    assert isinstance(trace, NoopTrace)
