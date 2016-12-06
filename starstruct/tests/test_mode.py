import pytest

from starstruct import Mode


def test_from_byte_order():
    assert Mode.from_byteorder('little') == Mode.Little
    assert Mode.from_byteorder('big') == Mode.Big
    assert Mode.from_byteorder('native') == Mode.Native
    assert Mode.from_byteorder('network') == Mode.Network

    with pytest.raises(TypeError):
        Mode.from_byteorder('random thing')
