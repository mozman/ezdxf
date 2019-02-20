from ezdxf.lldxf.validator import is_valid_layer_name, is_adsk_special_layer


def test_invalid_layer_name():
    assert is_valid_layer_name('Layer Layer') is True
    assert is_valid_layer_name('Layer/') is False
    assert is_valid_layer_name('Layer*') is False
    assert is_valid_layer_name('*Layer') is False
    assert is_valid_layer_name('Layer=') is False
    assert is_valid_layer_name('Layer;') is False
    assert is_valid_layer_name('Layer:') is False
    assert is_valid_layer_name('Layer<') is False
    assert is_valid_layer_name('Layer>') is False
    assert is_valid_layer_name('Layer`') is False
    assert is_valid_layer_name('\\Layer`') is False
    assert is_valid_layer_name('"Layer"') is False
    assert is_valid_layer_name('Layer|Layer') is False


def test_is_adsk_special_layer():
    assert is_adsk_special_layer('*adsk_xyz') is True
    assert is_adsk_special_layer('*ADSK_xyz') is True
    assert is_adsk_special_layer('ADSK_xyz*') is False

