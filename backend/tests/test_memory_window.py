def test_memory_window():
    messages = list(range(20))
    window = messages[-10:]
    
    assert len(window) == 10
    assert window[0] == 10
    assert window[-1] == 19