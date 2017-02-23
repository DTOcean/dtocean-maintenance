
import pytest

@pytest.mark.skipif(False,
                    reason="forced test to skip")

def test_logistics_import():
    
    from dtocean_maintenance import LOGISTICS_main

    # All tests must have an assertion (i.e something we made == something we
    # expect).
    # Here we just assert True as the function will fail if the import is not
    # possible
    assert True
